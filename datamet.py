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
import main
import glob
import os
from datetime import datetime
from configparser import ConfigParser

import pandas as pd
import numpy as np


class DatametToSAP(object):
    """
    Class qui va récupérer et mettre en forme les résultats des mesures pour les transmettres a la class SAPXml
    entrée :

    """

    def __init__(self, path_folder_datamet):
        # Lecture du fichier de résultat
        rst = Resultats()
        rst.set_path(path_folder_datamet)
        rst.read()
        # Lecture du fichier de mesure
        self.df_results = rst.df_results
        self.msr = Mesures()
        self.msr.set_path(path_folder_datamet)

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

    @staticmethod
    def current_time_sap():
        """ Pour renvoyer la date et l'heure au format sap"""
        now = datetime.now()
        now_sap = now.strftime("%Y%m%d%H%M%S%f")
        return now_sap


    def get_datamet_module(self):
        val = self.msr.get('General', 'Module')
        return val

    def set_para_dict(self, para_lst):
        """ permet de créer le dict depuis un liste de para dans un ordre définit :
            NumPara, UnitPara, ValuePara, ValueParaT, SequenceResult, SequenceEssEpr"""

        para_tmp = self.para_tpl
        x = 0
        for key in para_tmp:
            para_tmp[key] = para_lst[x]
            x += 1

        return para_tmp

    def test_para(self):
        # todo : comme il y a beaucoup de para qui ne sont pas transmis, on rajoute une colonne pour savoir ceux a
        #  transmettre

        # Test : on init une liste des para
        all_para_lst = []

        # récupération du module
        module_datamet = self.get_datamet_module()

        # Il va falloir chercher la famille SAP en fonction du module datamet
        # on utilise le fichier excel
        config = ConfigParser()
        config.read('config.ini', encoding='utf-8')
        excel_config_file = config.get('datametToSAP', 'ExcelConfig')
        df_datamet_fam = pd.read_excel(excel_config_file, sheet_name="Famille-methode")
        # on cherche le module pour trouver la famille
        fam_sap = df_datamet_fam.loc[df_datamet_fam['Méthode Datamet'] == module_datamet, 'Famille SAP'].item()
        # print(fam_sap)

        # On récupère la liste des paras pour cette famille
        df_SAP_fam = pd.read_excel(excel_config_file, sheet_name="ZCMT")
        # On sélectionne uniquement la famille et les paras qui sont nécessaires
        df_SAP_fam = df_SAP_fam[(df_SAP_fam['Famille Essai'] == fam_sap) & (df_SAP_fam['Envoie SAP'] == 'Oui')]
        # On fait une liste des parametres pour ensuite filtré les autres df
        lst_paras = list(df_SAP_fam['Paramètre'].values)
        # print(df_SAP_fam)
        # print(df_SAP_fam['Paramètre'].values)

        # On récupère la liste des ZES_PARA_CND_V pour cette famille
        # il s'agit des valeurs pour les listes de choix dans SAP. Elle va dans la balise ValueParaT
        df_SAP_ZES_ParaV = pd.read_excel(excel_config_file, sheet_name="ZES_PARA_CND_V")
        # sélection de la famille en cours et des paras qui sont nécessaires
        df_SAP_ZES_ParaV = df_SAP_ZES_ParaV[(df_SAP_ZES_ParaV['Famille Essai'] == fam_sap)]
        df_SAP_ZES_ParaV = df_SAP_ZES_ParaV[df_SAP_ZES_ParaV['Paramètre'].isin(lst_paras)]
        # print(df_SAP_ZES_ParaV)

        # On récupère la liste de ParaT qui ne sont pas des liste de choix
        # => parametres Qualitatif, par exemple opérateur ou Date
        # Dans la balise ValueParaT
        df_SAP_ParaT = pd.read_excel(excel_config_file, sheet_name="ParaT")
        # sélection de la famille en cours et des paras qui sont nécessaires
        # Todo : est ce que la famille dans ce tableau est réellement utile?
        df_SAP_ParaT = df_SAP_ParaT[df_SAP_ParaT['Famille'] == fam_sap]
        df_SAP_ParaT = df_SAP_ParaT[df_SAP_ParaT['Paramètre'].isin(lst_paras)]
        # print(df_SAP_ParaT)

        # on parcourt les resultats => On cherche une correspondance dans ParaT avec la valeur Datamet pour récupérer
        # la valeur SAP
        # voir si ne peut pas etre fait avec le dataframe plutôt qu'itérer
        # On vérifie qu'on a bien des ParaT :
        if not df_SAP_ParaT.empty:
            print("Traitement des parametres Qualitatif")
            # On filtre df_SAP_fam avec les parametres de df_SAP_ParaT et on itere
            df_tmp = df_SAP_fam[df_SAP_fam['Paramètre'].isin(list(df_SAP_ParaT['Paramètre'].values))]
            for index, row in df_tmp.iterrows():
                print("Traitement du para : " + str(row['Paramètre']) + " - " + str(row['Datamet']))
                # Colonne contenant la valeur a récupérer dans le df_results
                val_parasap = row['Paramètre']
                col_datamet = row['Datamet']
                # récupération de la valeur Datamet
                val_datamet = self.df_results[col_datamet].item()
                # On cherche dans le dataframe de résultats le parametres (nom de colonne) et ça valeur
                # On compare ensuite avec la valeur dans df_SAP_ParaT qui sera transmise a SAP
                # Gestion des ParaT qui doivent avoir un traitement particulier dans le programme
                # Cas uniquement de la Date pour le moment.
                if col_datamet == "Date":
                    print("Gestion de la date")
                    print("date : " + val_datamet)
                    # Todo : Vérifier le format des dates dans le fichier datamet
                    date_essai = datetime.strptime(val_datamet, "%Y/%m/%d %H:%M:%S")
                    # Il faut la transformer dans le format SAP YYYYMMDDHHMMSS
                    date_SAP = date_essai.strftime("%Y%m%d%H%M%S")
                    para_lst = [int(val_parasap), "", "", date_SAP, 1, 1]
                    all_para_lst.append((self.set_para_dict(para_lst).copy()))

                else:
                    # On cherche dans df_SAP_ParaT la valeur datamet pour retourner la valeur SAP
                    print("On cherche : " + val_datamet)
                    df_query = df_SAP_ParaT.query('`Valeur Datamet` == "' + val_datamet + '"')
                    # on vérifie qu'on ne trouve qu'une valeur
                    if len(df_query.index) == 1:
                        if not df_query.empty:
                            print("Valeur a transmettre a SAP : " + df_query['Valeur SAP'].item())
                            para_lst = [int(val_parasap), "", "", df_query['Valeur SAP'].item(), 1, 1]
                            all_para_lst.append(self.set_para_dict(para_lst).copy())
                        else:
                            print('Pas de valeur trouvé dans ParaT il va falloir remonter une erreur')
                    else:
                        print("Plusieurs valeurs trouvé, ce n'est pas normale")

        # On cherche les ParaT qui sont des listes SAP
        # Todo : Faire traitement des para ZES_PARA_CND_V

        # On s'occupe des paras qui reste, normalement que des para quantitatif
        # On va filtrer df_SAP_fam en supprimer les para précédents
        lst_paras_quanti = list(df_SAP_ParaT['Paramètre'].values) + list(df_SAP_ZES_ParaV['Paramètre'].values)
        df_tmp = df_SAP_fam[~df_SAP_fam['Paramètre'].isin(lst_paras_quanti)]
        #print(df_tmp)
        print("Traitement des parametres Qualitatif")
        if not df_tmp.empty:
            for index, row in df_tmp.iterrows():
                print("Traitement du para : " + str(row['Paramètre']) + " - " + str(row['Datamet']))
                # Colonne contenant la valeur à récupérer dans le df_results
                val_parasap = row['Paramètre']
                col_datamet = row['Datamet']
                # récupération de la valeur Datamet
                val_datamet = self.df_results[col_datamet].item()
                print(val_datamet)
                para_lst = [int(val_parasap), "", val_datamet, "", 1, 1]
                all_para_lst.append((self.set_para_dict(para_lst).copy()))


        print(all_para_lst)

    def test_essai(self):
        """ Test pour récupération des informations de l'essai et de l'eprouvette.
        Ces infos sont contenues dans le QR Code qui va devoir etre scanné"""

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
            if not file_exist:
                self.path_resultats_file = None
                raise ValueError('Aucun fichier de mesure trouvé')
        else:
            raise ValueError('Probleme lors de la recherche du fichier *Mesures.txt')

    def read(self):
        # path_result = r"C:\Nobackup\Dev Informatique\GitHub Clone\Datamet\Exemple résultat\ISO 643_INT_277171_2022-06-07_10-59-04\277171_Resultats.txt"
        # print(self.path_resultats_file)
        self.df_results = pd.read_csv(self.path_resultats_file, encoding='ANSI', sep=';')


if __name__ == '__main__':
    # test lecture fichier mesures
    path = r"C:\Nobackup\Dev Informatique\GitHub Clone\Datamet\Exemple résultat\ISO 643_INT_277171_2022-06-07_10-59-04"
    # path = os.path.abspath(
    #    r"E:\Romain\Documents\Romain bidouille\Informatique\Taf\Datamet\Exemple résultat\ISO 643_INT_277171_2022-06-07_10-59-04\277171_Mesures.txt")
    # Mesures = ConfigParser()
    # Mesures.read(path)
    # print(Mesures.get('General', 'Module'))
    # test = Mesures()
    # test.set_path(path_mesures_folder=path)
    # test3 = test.get_sections()
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

    test = DatametToSAP(path)
    #test.current_time_sap()

