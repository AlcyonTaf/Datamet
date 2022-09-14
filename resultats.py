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

import os
import csv
from configparser import ConfigParser
import pandas as pd


class Mesures(object):
    """
    Class pour la lecture des informations des fichiers "Mesures"
    """

    def __init__(self):
        self.mesures = ConfigParser()
        self.path_mesures_file = None

    def read(self):
        self.mesures.read(self.path_mesures_file)

    def set_path(self, path_mesures_file):
        self.path_mesures_file = path_mesures_file
        file_exist = self.mesures.read(self.path_mesures_file)
        if not file_exist:
            self.path_mesures_file = None
            raise ValueError('Aucun fichier de mesure trouvé')

    def get_sections(self):
        if self.path_mesures_file:
            self.read()
            sections = self.mesures.sections()
            for section in sections:
                print(section)
                print(self.mesures.items(section))
                print(type(self.mesures.items(section)))


if __name__ == '__main__':
    # test lecture fichier mesures
    # path = os.path.abspath(
    #     "C:\\Users\\CRMC\\PycharmProjects\\Datamet\\Exemple résultat\\ISO 643_INT_277171_2022-06-07_10-59-04\\277171_Mesures.txt")
    path = os.path.abspath(
        r"E:\Romain\Documents\Romain bidouille\Informatique\Taf\Datamet\Exemple résultat\ISO 643_INT_277171_2022-06-07_10-59-04\277171_Mesures.txt")
    # Mesures = ConfigParser()
    # Mesures.read(path)
    # print(Mesures.get('General', 'Module'))

    test = Mesures(path)
    # test.read(path)
    # test.mesures.get('General', 'Module')

    # # Lecture fichier de résultats
    # with open("C:\\Users\\CRMC\\PycharmProjects\\Datamet\\Exemple résultat\\ASTM E112_IMA_283558_2022-06-07_13-44-05\\283558_Resultats.txt", newline='') as csvfile:
    #     reader = csv.DictReader(csvfile, delimiter=";")
    #     for row in reader:
    #         for key in row:
    #             print(key, ' -> ', row[key])
