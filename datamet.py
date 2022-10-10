# -*- coding: utf-8 -*-

"""
Le fichier de résultats présent a la racine du dossier de la session est un CSV qui contient ces informations
 (Vérifier quelles sont identiques pour chaque type de mesure :
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
from configparser import ConfigParser

import pandas as pd

class DatametToSAP(object):
    """
    Class qui va récupérer et mettre en forme les résultats des mesures pour les transmettres a la class SAPXml
    """

    def __init__(self):
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

    def test(self, module_datamet):
        # Il va falloir chercher la famille SAP en fonction du module datamet
        # on utilise le fichier excel
        config = ConfigParser()
        config.read('config.ini', encoding='utf-8')
        excel_config_file = config.get('datametToSAP', 'ExcelConfig')
        df_datamet_fam = pd.read_excel(excel_config_file, sheet_name="Famille-methode")
        # on cherche le module pour trouver la famille
        fam_sap = df_datamet_fam.loc[df_datamet_fam['Méthode Datamet'] == module_datamet, 'Famille SAP'].item()
        print(fam_sap)

        # On récupère la liste des paras pour cette famille
        df_SAP_fam = pd.read_excel(excel_config_file, sheet_name="ZCMT")
        # On sélectionne uniquement la famille
        df_SAP_fam = df_SAP_fam[df_SAP_fam['Famille Essai'] == fam_sap ]
        print(df_SAP_fam)

        # On récupère la liste des ZES paraV pour cette famille
        df_SAP_ZES_ParaV = pd.read_excel(excel_config_file, sheet_name="ZES_PARA_CND_V")
        # sélection de la famille en cours
        df_SAP_ZES_ParaV = df_SAP_ZES_ParaV[df_SAP_ZES_ParaV['Famille Essai'] == fam_sap]
        print(df_SAP_ZES_ParaV)

        # On récupère la lsite de paraV autre que ZES
        # Opérateur par exemple
        df_SAP_ParaV = pd.read_excel(excel_config_file, sheet_name="ParaV")
        print(df_SAP_ParaV)

        # On va commencer par chercher les paraV, puis les paraV ZES, puis le reste
        df_tmp_SAP_PARA = df_SAP_fam[df_SAP_fam['ParaV'] == 'Oui']
        print(df_tmp_SAP_PARA)

        # on parcours les resultats
        for index, row in df_tmp_SAP_PARA.iterrows():
            print(str(row['Paramètre']) + " - " + str(row['Datamet']))

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
        #path_result = r"C:\Nobackup\Dev Informatique\GitHub Clone\Datamet\Exemple résultat\ISO 643_INT_277171_2022-06-07_10-59-04\277171_Resultats.txt"
        #print(self.path_resultats_file)
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

    # test.mesures.get('General', 'Module')

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

    test = DatametToSAP()
    test.test('Norme ISO 643')
