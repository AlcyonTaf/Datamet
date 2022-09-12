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







if __name__ == '__main__':


    # test lecture fichier mesures
    path = os.path.abspath(
        "C:\\Users\\CRMC\\PycharmProjects\\Datamet\\Exemple résultat\\ISO 643_INT_277171_2022-06-07_10-59-04\\277171_Mesures.txt")

    Mesures = ConfigParser()
    Mesures.read(path)
    print(Mesures.get('General', 'Module'))


    # Lecture fichier de résultats
    with open("C:\\Users\\CRMC\\PycharmProjects\\Datamet\\Exemple résultat\\ASTM E112_IMA_283558_2022-06-07_13-44-05\\283558_Resultats.txt", newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            for key in row:
                print(key, ' -> ', row[key])

