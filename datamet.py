# -*- coding: utf-8 -*-

"""
Le fichier de résultats présent a la racine du dossier de la session est un CSV qui contient ces informations
 (pas forcément le même pour chaque méthodes :
Repere
Coulée
Nuance
Produit
Zone
Attaque chimique
Operateur
Date
Methode
Type_Meth
Grossissement
Unite
Taille_Ima
Taille_Ima (px)
Taille_Pixel
L1
L2
D1
D2
R1
R2
CV
Nb_Images
V1
V5
Surface_Ana
Grain
Indice_Moy => Résultats pour taille de grain ?
Indice_Min
Indice_Max
Indice_EcTy
Indice_GrosGrains
%_GrosGrains
Fraction_Surf
Indice_V_Moy
Indice_V_Min
Indice_V_Max
Indice_V_EcTy
Indice_H_Moy
Indice_H_Min
Indice_H_Max
Indice_H_EcTy
Session

Voir pour faire une table qui permet la relation entre :
methode du fichier csv => Type d'essai SAP => résultat CSV => para SAP
On s'en servira ici pour récupérer les bonnes informations

On fera le XML dans un autre fichier .py

"""
import glob
import os

from pathlib import Path
from datetime import datetime
from configparser import ConfigParser
from PIL import Image, ImageTk, ImageDraw, ImageFont
from copy import deepcopy

import pandas as pd
import numpy as np

import outils
import sapxml

# Log
import logging
logger = logging.getLogger(__name__)


# Pour générer un Tiff à partir d'un PDF
# Todo peut etre désactivé, utilisation de pillow a la place
magick_home = ".\\ImageMagickDLL\\"
os.environ["MAGICK_HOME"] = magick_home
os.environ["MAGICK_CODER_MODULE_PATH"] = magick_home + os.sep + "modules" + os.sep + "coders"
from wand.image import Image as ImageWand
from wand.color import Color
import main



def find_session_by_qr_and_module(config, qrcode, module_name):
    """
    Pour rechercher toutes les sessions datamet qui contiennent la valeur d'identification SAP provenant du QR Code et le module
    Fait pour le cas de Norsok, on on a plusieur essais différent
    Todo :
    """
    # print('test')
    path_sessions = config.get('datamet', 'FolderResult')
    finded_sessions = []
    # On récupère la liste des fichiers de mesures
    mesures_files = [file for file in Path(path_sessions).rglob('*Mesures.txt')]
    # On parcourt la liste des fichiers de mesures
    for file in mesures_files:
        # print(file)
        # On lit le fichier de mesures
        mesures = Mesures()
        mesures.set_path(os.path.dirname(file))
        # récupération de la valeur du QR Code
        # print(mesures.get(section='Echantillon1', para='Commentaire'))
        qr_session = mesures.get(section='Echantillon1', para='Commentaire')
        # Transformation du QR_Code et du qr_session pour comparaison
        # On va vérifier seulement les 4 1er valeur du QR Code pour retrouver avec un seul scan tous les essais
        # Commande;Poste;Um;SequenceLoc
        # Si cela retourne trop de valeur, il faudrat mettre 2 scan de QR code pour Norsok
        qr_session = "".join(qr_session.split(';')[0:4])
        qrcode = "".join(qrcode.split(';')[0:4])
        module_session = mesures.get(section='General', para='Module')
        if qr_session == qrcode and module_session == module_name:
            # print("trouvé")
            finded_sessions.append(os.path.dirname(file))

    return finded_sessions


def find_session_by_qr(config, qrcode):
    """
    Pour rechercher toutes les sessions datamet qui contiennent la valeur d'identification SAP provenant du QR Code
    Ici on utilise le QR Code complet qui contient également l'information sur le type d'essai, il faudra en déduire le MODULE
    Todo : a Finir
    """
    # print('test')
    path_sessions = config.get('datamet', 'FolderResult')
    finded_sessions = []
    # On récupère la liste des fichiers de mesures
    mesures_files = [file for file in Path(path_sessions).rglob('*Mesures.txt')]
    # On parcourt la liste des fichiers de mesures
    for file in mesures_files:
        # print(file)
        # On lit le fichier de mesures
        mesures = Mesures()
        mesures.set_path(os.path.dirname(file))
        # récupération de la valeur du QR Code
        # print(mesures.get(section='Echantillon1', para='Commentaire'))
        qr_session = mesures.get(section='Echantillon1', para='Commentaire')
        if qr_session == qrcode:
            # print("trouvé")
            finded_sessions.append(os.path.dirname(file))

    return finded_sessions


class ImagesDatamet(object):
    """
    Class pour la récupération et le traitement des images
    get_images : récupére les images et renvoie un dict avec le nom de l'image dans la clef, et le fichier image pil
    en valeur. Ceci est stocké dans la variable d'instances self.images
    annotations : Créer les annotations pour l'essai NORSOK.
                    Il faudra peut etre la modifier pour prendre en compte d'autre annotation
    """

    def __init__(self):
        self.path_folder = None
        self.images = {}
        self.images_annot = {}  # chaque clef du dict contient une liste avec l'image ([0]) et l'annotation ([1])
        self.annots = {
            # Todo voir pour mettre ceci dans un fichier de config et en même temps rajouter une ref a l'essai
            "Peau sup": "_1_1_1.tif",
            "1/4 ep": "_1_1_2.tif",
            "Mi ep": "_1_1_3.tif",
            "3/4 ep": "_1_1_4.tif",
            "Peau inf": "_1_1_5.tif"
        }

    def get_images(self, path_folder):
        self.path_folder = path_folder
        folders = os.listdir(self.path_folder)
        founds_folder = [folder for folder in folders if folder.startswith("Images_Echelle_")]
        if len(founds_folder) == 1:
            images_path = [image for image in Path(os.path.join(self.path_folder, founds_folder[0])).rglob('*.tif')]
            # print(images_path)
            images_name = [os.path.basename(name) for name in images_path]
            # print(images_name)

            for image_path in images_path:
                image_name = os.path.basename(image_path)
                # Si on envoie l'image open cela ne fonctionne pas
                image_open = Image.open(image_path)
                # print(type(image_open))
                self.images[image_name] = image_open
                # print(type(self.images[image_name]))

            # print(self.images)
            # return self.images

        else:
            raise ValueError("Probleme : Plusieurs dossier images_echelles")

    def annotation(self):
        """
        Pour ajouter les annotations ds positions sur les images
        Si on a qu'une image, pas d'annotations, sinon il doit en avoir 5 + 1
        """
        if len(self.images) == 6:
            # self.images_annot = self.images
            # cas ou on a 6 images
            # On chercher la valeur de la position dans les nom des images
            find = False
            for image_name in self.images:
                for annot in self.annots:
                    if image_name.endswith(self.annots[annot]):
                        # print(str(image_name) + " - " + str(self.annots[annot]))
                        self.images_annot[image_name] = [self.images[image_name], annot]
                        # On ajoute l'annotation sur l'image
                        add_text = ImageDraw.Draw(self.images_annot[image_name][0])
                        width, heigh = self.images_annot[image_name][0].size
                        font = ImageFont.truetype('arial.ttf', size=50)
                        add_text.text((10, heigh - 20), annot, fill=(255, 0, 0), anchor="ls", font=font)
                        # print(self.images_annot)
                        # self.images_annot[image_name][0].show()
                        find = True

                if not find:
                    self.images_annot[image_name] = [self.images[image_name], 'Image pour structure']

    def conversion(self):
        # Todo : Ne sera surement pas utile car apparent avec pillow je peux sauver dans le bon format
        """ Conversion des PDF en TIFF"""
        tiff_name = "test_conversion.tif"
        # Il faut se remettre dans le dossier du script sinon Wand ne fonctionne pas
        script_path = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        os.chdir(script_path)
        config = ConfigParser()
        config.read('config.ini', encoding='utf-8')

        path_export_tiff = config.get('Annexe', 'SaveXMLTiffFolder') + tiff_name

        res = config.get('TIFF', 'Resolution')

        tiff = ImageWand(filename=os.path.abspath('test'), resolution=200)
        tiff.resize(1240, 1753)
        tiff.format = 'tiff'
        tiff.options['tiff:rows-per-strip'] = '4'
        tiff.background_color = Color("white")
        tiff.alpha_channel = 'remove'
        tiff.type = config.get('TIFF', 'Type')
        tiff.compression = config.get('TIFF', 'Compression')
        tiff.resolution = [int(res), int(res)]

        tiff.save(filename=os.path.abspath(path_export_tiff))
        return tiff_name


class DatametToSAP(object):
    """
    Class qui va récupérer et mettre en forme les résultats des mesures pour les transmettres a la class SAPXml.
    Il faut appeler set_path avec le chemin de la session et éventuellement les images.
    On récupère ensuite la liste à transmettre a SAPXml avec get_all
    """

    def __init__(self):
        self.fam_sap = None
        self.module_datamet = None
        self.msr = None
        self.qr = None
        self.df_results = None
        self.rst = None
        self.images = None

        # Définition des templates
        self.ToSap = ""
        self.essai_tpl = {"ESSAI": {"./__Essai/Source": "",
                                    "./__Essai/TimeStamp": "",
                                    "./__Essai/NoCommande": "",
                                    "./__Essai/NoPoste": "",
                                    "./__Essai/Batch": "",
                                    "./__Essai/SequenceLoc": ""},
                          "Eprouvettes": []}
        self.epr_tpl = {"EPROUVETTE": {"./SeqEssais": "ValeurSeqEssais"},
                        "Parametres": []}
        self.para_tpl = {"./NumPara": "ValeurNumPara",
                         "./UnitPara": "UnitPara",
                         "./ValuePara": "ValeurValuePara",
                         "./ValueParaT": "ValeurValueParaT",
                         "./SequenceResult": "ValeurSequenceResult",
                         "./SequenceEssEpr": "ValeurSequenceEssEpr"}

        # Récupération des infos du fichier excel de config
        # Todo : a finir, on va récupérer toutes les infos sur la config des essais/paras a l'initialisation de l'instance
        # On récupére le différent tableau dans le fichier excel et on les stocks dans des df
        config = ConfigParser()
        config.read('config.ini', encoding='utf-8')
        excel_config_file = config.get('datametToSAP', 'ExcelConfig')
        # Tableau de correspondance entre Famille d'essai SAP et les méthodes de datamet
        self.df_datamet_fam = pd.read_excel(excel_config_file, sheet_name="Famille-methode")
        # Tableau regroupant toutes les familles, paras et info pour savoir quoi récupérer et ou
        self.df_SAP_fam = pd.read_excel(excel_config_file, sheet_name="ZCMT")
        # On récupère la liste des ZES_PARA_CND_V pour cette famille
        # il s'agit des valeurs pour les listes de choix dans SAP. Elle va dans la balise ValueParaT
        self.df_SAP_ZES_ParaV = pd.read_excel(excel_config_file, sheet_name="ZES_PARA_CND_V")
        # On récupère la liste de ParaT qui ne sont pas des liste de choix
        # => parametres Qualitatif, par exemple opérateur ou Date
        # Dans la balise ValueParaT
        self.df_SAP_ParaT = pd.read_excel(excel_config_file, sheet_name="ParaT")


    def set_path(self, path_folder_datamet, images=None):
        self.images = images
        # Lecture du fichier de résultat
        self.rst = Resultats()
        if self.rst.set_path(path_folder_datamet):
            self.rst.read()
            self.df_results = self.rst.df_results
        else:
            self.df_results = []

        # Lecture du fichier de mesure
        self.msr = Mesures()
        self.msr.set_path(path_folder_datamet)

        # Récupération du QR CODE :
        self.qr = self.get_qrcode_value()

        # récupération du module
        self.module_datamet = self.get_datamet_module()
        # print(self.module_datamet)

        # Il va falloir chercher la famille SAP en fonction du module datamet
        # on cherche le module pour trouver la famille
        self.fam_sap = self.df_datamet_fam.loc[
            self.df_datamet_fam['Méthode Datamet'] == self.module_datamet, 'Famille SAP'].item()
        # print(fam_sap)

    def get_all(self):
        # On récupère et on assemble les différentes parties : Essai => Eprouvette => Parametre
        # Uniquement pour les résultats
        essai = self.get_essai()
        epr = self.get_epr()
        paras = self.get_para()


        epr['Parametres'] = paras
        essai['Eprouvettes'].append(epr)
        #print(essai)

        essais = []
        essais.append(essai)

        return essais

    # @staticmethod
    # def current_time_sap():
    #     """ Pour renvoyer la date et l'heure au format sap"""
    #     now = datetime.now()
    #     now_sap = now.strftime("%Y%m%d%H%M%S%f")
    #     return now_sap

    def get_datamet_module(self):
        val = self.msr.get('General', 'Module')
        return val

    def get_qrcode_value(self):
        val = self.msr.get(section='Echantillon1', para='Commentaire')
        return val

    def set_epr_dict(self, epr_lst):
        """ permet de créer le dict depuis une liste des informations de l'eprouvette dans cet ordre  :
            SeqEssais"""

        epr_tmp = deepcopy(self.epr_tpl)
        x = 0
        for key in epr_tmp['EPROUVETTE']:
            epr_tmp['EPROUVETTE'][key] = epr_lst[x]
            x += 1

        return epr_tmp

    def set_essai_dict(self, essai_lst):
        """ permet de créer le dict depuis une liste des informations de l'essai dans cet ordre  :
            Source, TimeStamp, NoCommande, NoPoste, Batch, SequenceLoc"""

        essai_tmp = deepcopy(self.essai_tpl)
        x = 0
        for key in essai_tmp['ESSAI']:
            essai_tmp['ESSAI'][key] = essai_lst[x]
            x += 1

        return essai_tmp

    def set_para_dict(self, para_lst):
        """ permet de créer le dict depuis un liste de para dans un ordre définit :
            NumPara, UnitPara, ValuePara, ValueParaT, SequenceResult, SequenceEssEpr"""

        para_tmp = deepcopy(self.para_tpl)
        x = 0
        for key in para_tmp:
            para_tmp[key] = para_lst[x]
            x += 1

        return para_tmp

    def norsok(self):
        """
        Fonction dans le cas particulier des essais Norsok :
            Il faut transférer des images d'un essai STR dans un para de l'essai FRC
        """
        # Todo ne sera surement pas util

    def get_para(self):
        # Test : on init une liste des para
        all_para_lst = []

        # On sélectionne uniquement la famille et les paras qui sont nécessaires
        df_SAP_fam = self.df_SAP_fam[
            (self.df_SAP_fam['Famille Essai'] == self.fam_sap) & (self.df_SAP_fam['Envoie SAP'] == 'Oui')]
        # On fait une liste des parametres pour ensuite filtré les autres df
        lst_paras = list(df_SAP_fam['Paramètre'].values)
        # print(lst_paras)

        # On récupère la liste des ZES_PARA_CND_V pour cette famille
        # sélection de la famille en cours et des paras qui sont nécessaires
        df_SAP_ZES_ParaV = self.df_SAP_ZES_ParaV[(self.df_SAP_ZES_ParaV['Famille Essai'] == self.fam_sap)]
        df_SAP_ZES_ParaV = df_SAP_ZES_ParaV[df_SAP_ZES_ParaV['Paramètre'].isin(lst_paras)]
        # print(df_SAP_ZES_ParaV)

        # On récupère la liste de ParaT qui ne sont pas des liste de choix
        # => parametres Qualitatif, par exemple opérateur ou Date
        # Dans la balise ValueParaT
        df_SAP_ParaT = self.df_SAP_ParaT[self.df_SAP_ParaT['Paramètre'].isin(lst_paras)]
        # print(df_SAP_ParaT)

        #########################
        # Parametres Qualitatif #
        #########################
        # on parcourt les resultats => On cherche une correspondance dans ParaT avec la valeur Datamet pour récupérer
        # la valeur SAP
        # voir si ne peut pas etre fait avec le dataframe plutôt qu'itérer
        # On vérifie qu'on a bien des ParaT :
        if not df_SAP_ParaT.empty:
            # print("Traitement des parametres Qualitatif")
            # On filtre df_SAP_fam avec les parametres de df_SAP_ParaT et on itere
            df_tmp = df_SAP_fam[df_SAP_fam['Paramètre'].isin(list(df_SAP_ParaT['Paramètre'].values))]
            for index, row in df_tmp.iterrows():
                # print("Traitement du para : " + str(row['Paramètre']) + " - " + str(row['Datamet résultat']))
                # Colonne contenant la valeur a récupérer dans le df_results
                val_parasap = row['Paramètre']
                # récupération de la valeur Datamet
                # Cas ou le fichier de résultat est présent :
                # Todo : Actuellement ajout de try pour lever une exception si probleme,
                #  mais ensuite il faudrait juste mettre un log puis continuer
                if len(self.df_results) > 0:
                    try:
                        col_datamet = row['Datamet résultat']
                        val_datamet = self.df_results[col_datamet].item()
                    except:
                        raise ValueError(" Probleme lors de la récupération du para qualitatif " + str(val_parasap) +
                                         " dans le fichier Résultat.")
                # Cas ou il n'y a pas de fichier de résultat :
                else:
                    # On regarde dans le tableau excel si ils sont disponibles dans le fichier de mesures :
                    try:
                        col_datamet = row['Datamet mesure'].split(',')
                        val_datamet = self.msr.get(col_datamet[0], col_datamet[1])
                    except:
                        raise ValueError(" Probleme lors de la récupération du para qualitatif " + str(val_parasap) +
                                         " dans le fichier Mesure.")

                # On cherche dans le dataframe de résultats le parametres (nom de colonne) et ça valeur
                # On compare ensuite avec la valeur dans df_SAP_ParaT qui sera transmise a SAP
                # Gestion des ParaT qui doivent avoir un traitement particulier dans le programme
                # Cas uniquement de la Date pour le moment.
                # On regarde si col_datamet contient Date
                if "Date" in col_datamet:
                    # print("Gestion de la date")
                    # print("date : " + val_datamet)
                    # Todo : Vérifier le format des dates dans le fichier datamet
                    date_essai = datetime.strptime(val_datamet, "%Y/%m/%d %H:%M:%S")
                    # Il faut la transformer dans le format SAP YYYYMMDDHHMMSS
                    date_SAP = date_essai.strftime("%Y%m%d%H%M%S")
                    para_lst = [int(val_parasap), "", "", date_SAP, 1, 1]
                    all_para_lst.append((self.set_para_dict(para_lst).copy()))

                else:
                    # On cherche dans df_SAP_ParaT la valeur datamet pour retourner la valeur SAP
                    # print("On cherche : " + val_datamet)
                    df_query = df_SAP_ParaT.query('`Valeur Datamet` == "' + val_datamet + '"')
                    # on vérifie qu'on ne trouve qu'une valeur
                    if not df_query.empty:
                        if len(df_query.index) == 1:
                            # print("Valeur a transmettre a SAP : " + df_query['Valeur SAP'].item())
                            para_lst = [int(val_parasap), "", "", df_query['Valeur SAP'].item(), 1, 1]
                            all_para_lst.append(self.set_para_dict(para_lst).copy())
                        else:
                            print("Plusieurs valeurs trouvé, ce n'est pas normale")
                    else:
                        # Il est vide, donc on renvoie la valeur tel quel
                        para_lst = [int(val_parasap), "", "", val_datamet, 1, 1]
                        all_para_lst.append(self.set_para_dict(para_lst).copy())

        # On cherche les ParaT qui sont des listes SAP
        # Todo : Faire traitement des para ZES_PARA_CND_V

        #########################
        # Paramètre Quantitatif #
        #########################
        # On s'occupe des paras qui reste, normalement que des para quantitatif
        # On va filtrer df_SAP_fam en supprimer les para précédents
        lst_paras_quanti = list(df_SAP_ParaT['Paramètre'].values) + list(df_SAP_ZES_ParaV['Paramètre'].values)
        df_tmp = df_SAP_fam[~df_SAP_fam['Paramètre'].isin(lst_paras_quanti)]
        # print(df_tmp)
        # print("Traitement des parametres Qualitatif")
        if not df_tmp.empty:
            for index, row in df_tmp.iterrows():
                # print("Traitement du para : " + str(row['Paramètre']) + " - " + str(row['Datamet résultat']))
                # Colonne contenant la valeur à récupérer dans le df_results
                val_parasap = row['Paramètre']
                try:
                    col_datamet = row['Datamet résultat']
                    # récupération de la valeur Datamet
                    val_datamet = self.df_results[col_datamet].item()
                    # print(val_datamet)
                    para_lst = [int(val_parasap), "", val_datamet, "", 1, 1]
                    all_para_lst.append((self.set_para_dict(para_lst).copy()))
                except:
                    raise ValueError("Erreur lors de la récupération du para quantitafif " + str(val_parasap) +
                                     " dans le fichier Résultats")

        # print(all_para_lst)
        return all_para_lst

    def get_images(self, pictures_name):
        """
        Fonction pour récupérer les informations qui serviront a faire le XML des images
        pictures_name contient le dict des images avec en clef, le nom, en lst[0] l'image, et en lst[1] l'annotation
        """
        # Todo : pour enregistré les images utiliser ceci: image_pil.save('testpillow.tif', compression="packbits", resolution=150)
        paras_lst = []
        # On va chercher dans le tableau ZCMT les paras images a transmettre
        # Cas particulier des images :
        # On connait les para ou il faudra envoyer une image en annexe en ajoutant "images" dans la colonne "Envoie SAP"
        df_SAP_images = self.df_SAP_fam[(self.df_SAP_fam['Famille Essai'] == self.fam_sap) &
                                        (self.df_SAP_fam['Envoie SAP'] == 'images')]
        lst_paras_images = list(df_SAP_images['Paramètre'].values)
        if len(lst_paras_images) == 1:
            for picture_name in pictures_name:
                para_lst = [lst_paras_images[0], "", "", picture_name, 1, 1]
                paras_lst.append((self.set_para_dict(para_lst).copy()))
        else:
            print("Erreur : Il y a plus d'un parametres pour les images")
            logger.error("Il y a plus d'un parametres pour les images")
        # print(lst_paras_images)

        # On assemble toutes les informations
        essai = self.get_essai()
        epr = self.get_epr()

        epr['Parametres'] = paras_lst
        essai['Eprouvettes'].append(epr)

        essais = []
        essais.append(essai)
        print(essai)
        return essais


    def get_essai(self):
        """ Test pour récupération des informations de l'essai.
        Ces infos sont contenues dans le QR Code qui va devoir etre scanné"""
        # print(self.get_qrcode_value())
        # On split le qr Code :
        qr = self.qr.split(';')
        # print(qr)
        # Source, TimeStamp, NoCommande, NoPoste, Batch, SequenceLoc
        # Source = LABO_IC
        essai_dict = self.set_essai_dict(["LABO_IC", outils.current_time_sap(), qr[0], qr[1], qr[2], qr[3]])
        # print(essai_dict)
        return essai_dict

    def get_epr(self):
        """ Test pour récupération des informations de l'eprouvette.
        Ces infos sont contenues dans le QR Code qui va devoir etre scanné"""
        qr = self.qr.split(';')
        epr_dict = self.set_epr_dict([qr[4]])
        # print(epr_dict)
        return epr_dict


class ConfigDatametSap:
    """
    Class pour récupérer les infos de correspondance entre datamet et SAP
    Todo : Pas sur que je vais faire ça ici
    """


class Mesures(object):
    """
    Class pour la lecture des informations des fichiers "Mesures"
    """

    def __init__(self):
        # path = r"C:\Nobackup\Dev Informatique\GitHub Clone\Datamet\Exemple résultat\ISO 643_INT_277171_2022-06-07_10-59-04\277171_Mesures.txt"
        self.mesures = ConfigParser()
        self.path_mesures_file = None
        self.path_folder = None

    def read(self):
        self.mesures.read(self.path_mesures_file)

    def set_path(self, path_mesures_folder):
        self.path_folder = path_mesures_folder
        os.chdir(path_mesures_folder)
        files = [file for file in glob.glob('*Mesures.txt')]
        os.chdir(os.path.dirname(__file__))
        # for file in glob.glob('*Mesures.txt'):
        #     print(file)
        if len(files) == 1:
            self.path_mesures_file = os.path.join(path_mesures_folder, files[0])
            file_exist = self.mesures.read(self.path_mesures_file)
            if not file_exist:
                self.path_mesures_file = None
                raise ValueError('Aucun fichier de mesure trouvé')
        else:
            # Todo : voir pour faire autrement car pour certain essais il n'y a pas de fichier mesures
            raise ValueError('Probleme lors de la recherche du fichier *Mesures.txt')

    def get_sections(self):
        if self.path_mesures_file:
            self.read()
            result = []
            sections = self.mesures.sections()
            for section in sections:
                result.append([section, self.mesures.items(section)])
                # print(section)
                # print(self.mesures.items(section))
            return result

    def get(self, section, para):
        valeur = ""
        if self.path_mesures_file:
            self.read()
            valeur = self.mesures.get(section, para)

        return valeur


class Resultats:
    """
    Class pour la lecture des informations des fichiers "Resultats"
    return : un dataframe avec en colonne le nom des infos et les résultats sur la 1er lignes
    """

    def __init__(self):
        self.df_results = []
        # Todo : a modifier pour ne pas etre obliger d'utiliser Mesures() avant
        self.path_resultats_file = None
        self.path_mesures_folder = None

    def set_path(self, path_mesures_folder):
        """
        Pour test car apres on peut récupérer le chemin du fichier résultats dans le fichier de mesures
        A besoin du dossier contenant tous les fichiers
        """
        self.path_mesures_folder = path_mesures_folder
        os.chdir(path_mesures_folder)
        files = [file for file in glob.glob('*Resultats.txt')]
        os.chdir(os.path.dirname(__file__))
        # for file in glob.glob('*Mesures.txt'):
        #     print(file)
        if len(files) == 1:
            self.path_resultats_file = os.path.join(path_mesures_folder, files[0])
            file_exist = os.path.exists(self.path_resultats_file)
            # Todo : quel est l'intéret de vérifier si le fichier existe ici? => désactivté pour le moment
            # if not file_exist:
            #     self.path_resultats_file = None
            #     raise ValueError('Aucun fichier de mesure trouvé')
            # On retourne vrai si le fichier existe, sinon faux
            return True
        else:
            # raise ValueError('Probleme lors de la recherche du fichier *Resultats.txt')
            return False

    def read(self):
        # path_result = r"C:\Nobackup\Dev Informatique\GitHub Clone\Datamet\Exemple résultat\ISO 643_INT_277171_2022-06-07_10-59-04\277171_Resultats.txt"
        # print(self.path_resultats_file)
        self.df_results = pd.read_csv(self.path_resultats_file, encoding='ANSI', sep=';')


if __name__ == '__main__':
    # test lecture fichier mesures
    path = r"C:\Nobackup\Dev Informatique\GitHub Clone\Datamet\Exemple résultat\CAMUS_C\Fraction Phase_SEU_ESSAI FRC-NORSOK_2022-10-21_09-47-44"
    # Test avec une aquisitiion qui ne contient pas de fichier résultats
    #path = r"C:\Nobackup\Dev Informatique\GitHub Clone\Datamet\Exemple résultat\CAMUS_C\AcquisitionImages_ESSAI STR-NORSOK_2022-10-21_10-14-32"
    # path = os.path.abspath(
    #    r"E:\Romain\Documents\Romain bidouille\Informatique\Taf\Datamet\Exemple résultat\ISO 643_INT_277171_2022-06-07_10-59-04\277171_Mesures.txt")
    # Mesures = ConfigParser()
    # Mesures.read(path)
    # print(Mesures.get('General', 'Module'))
    # test = Mesures()
    # test.set_path(path_mesures_folder=path)
    # test3 = test.get_sections()
    # print(test3)
    # #
    # for sections in test3:
    #     for section in sections:
    #         print(section)
    #
    # result = Resultats(test)
    #
    # print(result.df_results)
    # result.read()

    # print(test.mesures.get('General', 'Module'))
    # print(test.get('General', 'Module'))

    # # Lecture fichier de résultats
    # with open("C:\\Users\\CRMC\\PycharmProjects\\Datamet\\Exemple résultat\\ASTM E112_IMA_283558_2022-06-07_13-44-05\\283558_Resultats.txt", newline='') as csvfile:
    #     reader = csv.DictReader(csvfile, delimiter=";")
    #     for row in reader:
    #         for key in row:
    #             print(key, ' -> ', row[key])

    # Test lecture fichier de résultats
    # path_result =r"C:\Nobackup\Dev Informatique\GitHub Clone\Datamet\Exemple résultat\ISO 643_INT_277171_2022-06-07_10-59-04\277171_Resultats.txt"
    #
    # df = pd.read_csv(path_result, encoding='ANSI', sep=';')
    # print(df)

    # test datamettosap

    # test = DatametToSAP(path)
    # test.test_images()
    # test.current_time_sap()

    # Test class Images
    # test = ImagesDatamet()
    # imgs = test.get_images(
    #     r"C:\Nobackup\Dev Informatique\GitHub Clone\Datamet\Exemple résultat\CAMUS_C\AcquisitionImages_ESSAI STR-NORSOK_2022-10-21_10-14-32")
    #
    # test.annotation()

    # test pour essai et eprouvettes :
    # qr_code = "5301530;10;280174.11;10;60;1;FRC;MIC01;955;;;Texte:280174:PS;Texte:280174:PS;TEXTE:280174:PS"
    # Comme on founi l'emplacement du dossier de session, on va chercher directement dans le fichier mesure la valeur du QRCode
    test = DatametToSAP()
    # test.test_essai()
    # test.test_epr()
    # test.test_para()
    test.set_path(path)


    val = test.get_images()
    print(val)
    # val.append(test.test_tout())
    # print('val')
    # print(val)

