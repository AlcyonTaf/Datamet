# -*- coding: utf-8 -*-
"""
    Contient les class pour la GUI dans le cas des essais selon la normes NORSOK

    Source :
        https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter

"""
import tkinter as tk
from tkinter import Entry, PhotoImage, Button, Text, messagebox
from tkinter.ttk import Label, Notebook, Treeview, Separator
from PIL import Image, ImageTk

import os

# import fichier
import datamet
import mainV2
import outils
import sapxml

# Log
import logging

logger = logging.getLogger(__name__)


class ScanQrGui(tk.Frame):
    def __init__(self, parent, main_app, script_path, config):
        super().__init__(parent)
        self.parent = parent
        self.main_app = main_app
        self.script_path = script_path
        self.config = config

        # self.configure(width=944, height=1092)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Frame avec des buttons d'action
        # frm_action = NorsokBtn(self)
        # frm_action.grid(row=0, column=0, sticky='news')

        # Essai notebook
        self.nb = Notebook(self, width=1092, height=944)
        self.nb.grid(row=1, column=0)
        # Frames
        self.tab = {"qr": [QR(parent=self.nb, controller=self), "QR"],
                    "result": [Result(parent=self.nb, controller=self), "Resultats"]
                    # "transfert": [Transfert(parent=self.nb, controller=self), " Transfert"]
                    }

        self.nb.add(self.tab["qr"][0], text=self.tab["qr"][1])

    def show_tab(self, tab_name):
        tab = self.tab[tab_name][0]
        name = self.tab[tab_name][1]
        print(tab)
        print(name)
        tab.event_generate("<<ShowFrame>>")
        self.nb.add(tab, text=name)
        self.nb.select(tab)
        self.parent.center_window()


class QR(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # self.grid_columnconfigure(1, weight=1)

        # on affiche le code barre pour config la scannette

        # print(os.path.join(self.controller.script_path, "Pictures\\barcoderule2.gif"))
        img_barcoderule2 = PhotoImage(file=os.path.join(self.controller.script_path, 'Pictures\\barcoderule2.gif'))
        self.lbl_img = Label(self, image=img_barcoderule2)
        self.lbl_img.grid(row=0, column=0, sticky='s')
        self.lbl_img.image = img_barcoderule2

        # Input Text pour la valeur du QR CODE :
        self.lbl_qrcode = Label(self, text="Scanner le Code barre si dessus, puis le QR Code sur la feuille de travail")
        self.ety_qrcode = Entry(self, width=100)

        self.lbl_qrcode.grid(row=1, column=0, )
        self.ety_qrcode.grid(row=2, column=0, sticky='n')

        self.btn_valider = Button(self, text="Valider", command=self.valider)
        self.btn_valider.grid(row=3, column=0, sticky='nesw', padx=5, pady=5)

        self.ety_qrcode.focus_set()

    def valider(self):
        if len(self.ety_qrcode.get()) == 0:
            messagebox.showwarning(message="Pas de valeur de QR CODE",
                                   parent=self.controller)
        else:
            self.controller.show_tab("result")


class Result(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

        self.images = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Todo : Modifier ArboEtImage pour juste afficher la treeview et la remplir lors du ShowFrame
        self.tree = outils.ArboEtImages()

        # Event a l'affichage
        self.bind("<<ShowFrame>>", self.on_show_frame)

        print('ini result')

    def on_show_frame(self, event):
        print("on fait quelque chose!")
        # qr_code = self.controller.frames["norsok_qr"].ety_qrcode.get()
        qr_code = self.controller.tab["qr"][0].ety_qrcode.get()
        print(qr_code)

        finded_sessions = datamet.find_session_by_qr(config=self.controller.config,
                                                     qrcode=qr_code, )

        print(finded_sessions)

class Transfert(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.lbl_transfert = Label(self, text="Détails des informations transférées", font=('Ariel', 10))
        self.lbl_transfert.grid(row=0, column=0, columnspan=3)

        # Partie FRC :
        self.lbl_frc = Label(self, text="Essai FRC", font=('Ariel', 10))
        self.lbl_frc.grid(row=1, column=0, columnspan=3)
        self.valeurs_frc = Text(self, height=20)
        self.valeurs_frc.grid(row=2, column=0)
        self.tree_frc_images = outils.ImagesList(self, self.controller)
        self.tree_frc_images.grid(row=2, column=2)

        # separateur
        sep = Separator(self, orient="horizontal")
        sep.grid(row=3, column=0, columnspan=3, sticky='ew', ipadx=200, pady=10)

        sep_frc = Separator(self, orient="vertical")
        sep_frc.grid(row=2, column=1, sticky='ns', ipady=200, padx=10)

        sep_str = Separator(self, orient="vertical")
        sep_str.grid(row=5, column=1, sticky='ns', ipady=200, padx=10)

        # Partie STR :
        self.lbl_str = Label(self, text="Essai STR", font=('Ariel', 10))
        self.lbl_str.grid(row=4, column=0, columnspan=3)
        self.valeurs_str = Text(self, height=20)
        self.valeurs_str.grid(row=5, column=0)
        self.tree_str_images = outils.ImagesList(self, self.controller)
        self.tree_str_images.grid(row=5, column=2)

        # Event a l'affichage
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event):
        # On vide lex Text et Tree
        self.tree_str_images.delete()
        self.tree_frc_images.delete()
        self.valeurs_str.delete('1.0', 'end')
        self.valeurs_frc.delete('1.0', 'end')
        self.datametToSap = datamet.DatametToSAP()

        # creation et envoie du XML
        # Récupération dossier d'export vers SAP:
        self.sap_export_path = self.controller.config.get('xmlSAP', 'SaveXMLToSAPFolder')
        sap_xml = sapxml.SapXml()

        # On récupére les images générer sur la frame result
        # Ok on va afficher une liste des images et le double clic permettra de les affichers
        images_from_result = self.controller.tab['norksok_result'][0].images.images_annot
        images_frc = {}
        images_str = {}
        for image in images_from_result:
            # On cherche l'image pour l'essai FRC car on la annoter "Image pour structure"
            if images_from_result[image][1] == "Image pour structure":
                # Image de l'essai FRC
                images_str[image] = images_from_result[image]

            else:
                # Images de l'essai STR
                images_frc[image] = images_from_result[image]

        self.tree_frc_images.insert(images_frc)
        self.tree_str_images.insert(images_str)

        # On va récupérer le chemin de l'essai FRC sélectionner sur la page NorsokResult
        frc_tree_selected = self.controller.tab['norksok_result'][0].tree_frc.selection()
        if len(frc_tree_selected) > 0:
            frc_tree_id = frc_tree_selected[0]
            frc_values = self.controller.tab['norksok_result'][0].tree_frc.item(frc_tree_id, "value")[0]
            # print(frc_values)
            # On lance la mise en forme des résultats avec la class datamettosap
            self.datametToSap.set_path(frc_values)
            frc_to_sap_values = self.datametToSap.get_all()
            # print(frc_to_sap_values)
            for value in frc_to_sap_values:
                self.valeurs_frc.insert('end', str(value) + "\n")

            # Création du nom du fichier :
            # IC_PL_ESS_RES_NoCommande_NoPoste_UM_SequenceLoc_Timestamp.xml
            qr = self.datametToSap.qr.split(';')

            filename = "IC_PL_ESS_RES_{NoCommande}_{NoPoste}_{UM}_{SequenceLoc}_{Timestamp}.xml".format(
                NoCommande=qr[0],
                NoPoste=qr[1],
                UM=qr[2],
                SequenceLoc=qr[3],
                Timestamp=outils.current_time_sap())

            sap_xml.xml_result_to_sap(frc_to_sap_values, self.sap_export_path, filename)

        # On va récupérer le chemin de l'essai STR sélectionner sur la page NorsokResult
        str_tree_selected = self.controller.tab['norksok_result'][0].tree_str.selection()
        if len(str_tree_selected) > 0:
            str_tree_id = str_tree_selected[0]
            str_values = self.controller.tab['norksok_result'][0].tree_str.item(str_tree_id, "value")[0]
            # print(str_values)
            # On lance la mise en forme des résultats avec la class datamettosap
            self.datametToSap.set_path(str_values)
            str_to_sap_values = self.datametToSap.get_all()
            # print(str_to_sap_values)
            for value in str_to_sap_values:
                self.valeurs_str.insert('end', str(value) + "\n")

            # Création du nom du fichier :
            # IC_PL_ESS_RES_NoCommande_NoPoste_UM_SequenceLoc_Timestamp.xml
            qr = self.datametToSap.qr.split(';')

            filename = "IC_PL_ESS_RES_{NoCommande}_{NoPoste}_{UM}_{SequenceLoc}_{Timestamp}.xml".format(
                NoCommande=qr[0],
                NoPoste=qr[1],
                UM=qr[2],
                SequenceLoc=qr[3],
                Timestamp=outils.current_time_sap())

            sap_xml.xml_result_to_sap(str_to_sap_values, self.sap_export_path, filename)

        # if len(self.tree_frc.selection()) > 0:
        #     ref_item = self.tree_frc.selection()[0]
        #     item_values = self.tree_frc.item(ref_item, "value")[0]
