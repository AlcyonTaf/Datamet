# -*- coding: utf-8 -*-
"""
    Contient les class pour la GUI dans le cas des essais selon la normes NORSOK

    Source :
        https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter

"""
import tkinter as tk
from tkinter import Entry, PhotoImage, Button, ttk, Text
from tkinter.ttk import Style, Label
from PIL import Image, ImageTk

import os

# import fichier
import datamet
import mainV2
import outils


class NorsokGui(tk.Frame):
    def __init__(self, parent, main_app, script_path, config):
        super().__init__(parent)
        self.parent = parent
        self.main_app = main_app
        self.script_path = script_path
        self.config = config

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Frame avec des buttons d'action
        frm_action = NorsokBtn(self)
        frm_action.grid(row=0, column=0, sticky='news')

        # Container va contenir les différentes pages
        container = tk.Frame(self, bg='red')
        container.grid(row=1, column=0, sticky='news')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.frames["norsok_qr"] = NorsokQR(parent=container, controller=self)
        self.frames["norksok_result"] = NorksokResult(parent=container, controller=self)
        self.frames["norsok_transfert"] = NorsokTransfert(parent=container, controller=self)
        # Page d'acueil :
        self.show_frame("norsok_qr")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        for frame in self.frames.values():
            frame.grid_remove()
        frame = self.frames[page_name]
        frame.event_generate("<<ShowFrame>>")
        frame.grid(row=0, column=0, sticky='nesw')
        self.parent.center_window()


class NorsokBtn(tk.Frame):
    """
    Pour afficher une barre avec des boutons d'action
    # TODO : Voir a l'usage si c'est bien, sinon plutot utiliser un notebook
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        btn_previous = Button(self, text="Précédent", command=None)
        btn_previous.grid(row=0, column=0)
        btn_suivant = Button(self, text="Suivant", command=None)
        btn_suivant.grid(row=0, column=1)


class NorsokQR(tk.Frame):

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
        self.lbl_img.grid(row=0, column=0, sticky='n')
        self.lbl_img.image = img_barcoderule2

        # Input Text pour la valeur du QR CODE :
        self.lbl_qrcode = Label(self, text="Scanner le Code barre si dessus, puis le QR Code sur la feuille de travail")
        self.ety_qrcode = Entry(self, width=100)

        self.lbl_qrcode.grid(row=1, column=0, sticky='n')
        self.ety_qrcode.grid(row=2, column=0, sticky='n')

        self.btn_valider = Button(self, text="Valider", command=self.valider)
        self.btn_valider.grid(row=3, column=0, sticky='n', padx=5, pady=5)

        self.ety_qrcode.focus_set()

    def valider(self):
        self.controller.show_frame("norksok_result")


class NorksokResult(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

        self.images = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Partie FRC
        self.lbl_frc = Label(self, text="Choix de l'essai FRC")
        self.lbl_frc.grid(row=0, column=0)

        self.lbl_frc_text = Label(self)
        self.lbl_frc_text.grid(row=1, column=0)

        self.tree_frc = ttk.Treeview(self, selectmode="browse")
        self.tree_frc.column('#0', stretch=True, width=400)
        self.tree_frc.heading('#0', text='Liste des sessions', anchor='center')
        self.tree_frc.grid(row=2, column=0, sticky='nesw')
        # Treeview event click => Pour affichage des info dans détails
        self.tree_frc.bind("<<TreeviewSelect>>", self.on_select_tree_frc_item)

        self.details_frc = mainV2.Details(self, self.parent)
        self.details_frc.grid(row=0, column=1, rowspan=3)

        # separateur
        sep = ttk.Separator(self, orient="horizontal")
        sep.grid(row=3, column=0, columnspan=2, sticky='ew', ipadx=200, pady=10)

        # Partie STR
        self.lbl_str = Label(self, text="Choix de l'essai STR")
        self.lbl_str.grid(row=4, column=0)

        self.lbl_str_text = Label(self)
        self.lbl_str_text.grid(row=5, column=0)

        self.tree_str = ttk.Treeview(self, selectmode="browse")
        self.tree_str.heading('#0', text='Liste des sessions', anchor='center')
        self.tree_str.grid(row=6, column=0, sticky='nesw')
        self.tree_str.bind("<<TreeviewSelect>>", self.on_select_tree_str_item)

        # self.images_tree_str = ttk.Treeview(self, columns=("Annotations"))
        # self.images_tree_str.heading('#0', text='Liste des images', anchor='center')
        # self.images_tree_str.heading('Annotations', text="Annotations", anchor='center')
        # self.images_tree_str.grid(row=4, column=1, rowspan=3, sticky='nesw')
        # self.images_tree_str.bind("<Double-1>", self.on_select_images_tree_str_item)
        # Test en utilisant une class
        self.images_tree_str = outils.ImagesList(self, self.controller)
        self.images_tree_str.grid(row=4, column=1, rowspan=3, sticky='nesw')

        # Event a l'affichage
        self.bind("<<ShowFrame>>", self.on_show_frame)

        # Bouton pour valider et passer au transfert
        btn_transfert = Button(self, text="Valider", command=self.valider)
        btn_transfert.grid(row=7, column=0, columnspan=2, sticky='esnw', padx=5, pady=5)

    def valider(self):
        self.controller.show_frame("norsok_transfert")

    # def on_select_images_tree_str_item(self, event):
    #     if len(self.images_tree_str.selection()) > 0:
    #         ref_item = self.images_tree_str.selection()[0]
    #         item_values = self.images_tree_str.item(ref_item, "text")
    #         test = NorsokShowImage(self.controller, self, item_values)
    #         test.grab_set()
    #         print(item_values)
    #         print(ref_item)

    def on_select_tree_str_item(self, event):
        if len(self.tree_str.selection()) > 0:
            ref_item = self.tree_str.selection()[0]
            item_values = self.tree_str.item(ref_item, "value")[0]
            print(item_values)
            print(ref_item)
            if item_values:
                self.images = datamet.ImagesDatamet()
                self.images.get_images(item_values)
                self.images.annotation()
                images_list = self.images.images_annot

                # self.images_tree_str.delete(*self.images_tree_str.get_children())
                # for image_name in images_list:
                #     self.images_tree_str.insert('', 'end', text=image_name, values=(images_list[image_name][1],))
                self.images_tree_str.insert(images_list)

    def on_select_tree_frc_item(self, event):
        if len(self.tree_frc.selection()) > 0:
            ref_item = self.tree_frc.selection()[0]
            item_values = self.tree_frc.item(ref_item, "value")[0]
            if item_values:
                details_resultats = self.details_frc.text
                details_resultats.config(state='normal')
                details_resultats.delete('1.0', 'end')
                try:
                    get_resultats = datamet.Resultats()
                    get_resultats.set_path(item_values)
                    get_resultats.read()
                except:
                    pass
                else:
                    df_resultats = get_resultats.df_results
                    if not df_resultats.empty:
                        details_resultats.insert('end', '\n' + str(df_resultats.iloc[0]))

    def on_show_frame(self, event):
        print("on fait quelque chose!")
        qr_code = self.controller.frames["norsok_qr"].ety_qrcode.get()
        print(qr_code)

        # Remplissage des treeview FRC et STR
        module_to_find = ["Par seuillage", "Acquisition d'image"]

        for module in module_to_find:
            print(module)
            finded_sessions = datamet.find_session_by_qr_and_module(config=self.controller.config,
                                                                    qrcode="1327542;30;245777.11;10;70;1;GRN;MIC01;609;;"
                                                                           ";Texte:245777:PS;""Texte:245777:PS"
                                                                           ";TEXTE:245777:PS",
                                                                    module_name=module)
            if module == "Par seuillage":
                if not finded_sessions:
                    self.lbl_frc_text.config(text="Pas de sessions trouvé pour ce QR Code")
                else:
                    # Todo : vérifier si un seul resultat, si c'est le cas on le selectionne automatiquement
                    if len(finded_sessions) == 1:
                        session_name = os.path.basename(finded_sessions[0])
                        id_frc = self.tree_frc.insert('', 'end', text=session_name, values=(finded_sessions[0],))
                        self.tree_frc.selection_set(id_frc)
                        self.tree_frc.focus_set()
                        self.tree_frc.focus(id_frc)
                    else:
                        for session_path in finded_sessions:
                            session_name = os.path.basename(session_path)
                            self.tree_frc.insert('', 'end', text=session_name, values=(session_path,))
            elif module == "Acquisition d'image":
                if not finded_sessions:
                    self.lbl_str_text.config(text="Pas de sessions trouvé pour ce QR Code")
                else:
                    if len(finded_sessions) == 1:
                        session_name = os.path.basename(finded_sessions[0])
                        id_str = self.tree_str.insert('', 'end', text=session_name, values=(finded_sessions[0],))
                        self.tree_str.selection_set(id_str)
                        self.tree_str.focus_set()
                        self.tree_str.focus(id_str)
                    else:
                        for session_path in finded_sessions:
                            session_name = os.path.basename(session_path)
                            self.tree_str.insert('', 'end', text=session_name, values=(session_path,))


# class NorsokShowImage(tk.Toplevel):
#     # Todo a modifier pour qu'il soit appeller depuis la class ImageListAndPopup, peut surement etre intégrer dans la class ImageListAndPopup
#     def __init__(self, main_app, parent, image_name):
#         self.main_app = main_app
#         self.parent = parent
#         super().__init__(main_app)
#         self.title("Affichage d'une image")
#         self.grid_rowconfigure(0, weight=1)
#         self.grid_columnconfigure(0, weight=1)
#
#         image_pil = self.parent.images.images_annot[image_name][0]
#
#         image_pil.thumbnail((500, 500))
#
#         image = ImageTk.PhotoImage(image_pil)
#
#         # Essai d'enregistrement pour essai
#         # image_pil.save('testpillow.tif', compression="packbits", resolution=150)
#
#         lbl = Label(self, image=image)
#         lbl.image = image
#         lbl.grid(row=0, column=0)


class NorsokTransfert(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # Partie FRC :
        self.lbl_frc = Label(self, text="Essai FRC", font=('Ariel', 20))
        self.lbl_frc.grid(row=0, column=0, columnspan=3)
        self.valeurs_frc = Text(self)
        self.valeurs_frc.grid(row=1, column=0)
        self.tree_frc_images = outils.ImagesList(self, self.controller)
        self.tree_frc_images.grid(row=1, column=2, sticky='nesw')

        # separateur
        sep = ttk.Separator(self, orient="horizontal")
        sep.grid(row=2, column=0, columnspan=3, sticky='ew', ipadx=200, pady=10)

        sep_frc = ttk.Separator(self, orient="vertical")
        sep_frc.grid(row=1, column=1, sticky='ns', ipady=200, padx=10)

        sep_str = ttk.Separator(self, orient="vertical")
        sep_str.grid(row=4, column=1, sticky='ns', ipady=200, padx=10)

        # Partie STR :
        self.lbl_str = Label(self, text="essai STR", font=('Ariel', 20))
        self.lbl_str.grid(row=3, column=0, columnspan=3)
        self.valeurs_str = Text(self)
        self.valeurs_str.grid(row=4, column=0)
        self.tree_str_images = outils.ImagesList(self, self.controller)
        self.tree_str_images.grid(row=4, column=2, sticky='nesw')

        # Event a l'affichage
        self.bind("<<ShowFrame>>", self.on_show_frame)


    def on_show_frame(self, event):
        # On récupére les images générer sur la frame result
        # Ok on va afficher une liste des images et le double clic permettra de les affichers
        # Todo : Il faut trouver le moyen de mettre l'image pour l'essai FRC au bon endroit, comment filtrer ? Par la position ? ou par l'annotation?
        images_from_result = self.controller.frames['norksok_result'].images

        # On va récupérer le chemin de l'essai FRC sélectionner sur la page NorsokResult
        frc_tree_selected = self.controller.frames['norksok_result'].tree_frc.selection()
        if len(frc_tree_selected) > 0:
            frc_tree_id = frc_tree_selected[0]
            frc_values = self.controller.frames['norksok_result'].tree_frc.item(frc_tree_id, "value")[0]
            print(frc_values)
            # On lance la mise en forme des résultats avec la class datamettosap
            frc_to_sap = datamet.DatametToSAP(frc_values)
            frc_to_sap_values = frc_to_sap.test_para()
            print(frc_to_sap_values)
            for value in frc_to_sap_values:
                self.valeurs_frc.insert('end', str(value) + "\n")



        # On va récupérer le chemin de l'essai FRC sélectionner sur la page NorsokResult
        str_tree_selected = self.controller.frames['norksok_result'].tree_str.selection()
        if len(str_tree_selected) > 0:
            str_tree_id = str_tree_selected[0]
            str_values = self.controller.frames['norksok_result'].tree_str.item(str_tree_id, "value")[0]
            print(str_values)
            # On lance la mise en forme des résultats avec la class datamettosap
            str_to_sap = datamet.DatametToSAP(str_values)
            str_to_sap_values = str_to_sap.test_para()
            print(str_to_sap_values)
            for value in str_to_sap_values:
                self.valeurs_str.insert('end', str(value) + "\n")




        # if len(self.tree_frc.selection()) > 0:
        #     ref_item = self.tree_frc.selection()[0]
        #     item_values = self.tree_frc.item(ref_item, "value")[0]


# class ImagesListAndPopup(tk.Frame):
#     # Todo finir cette classe et remplacer les 2 treeview d'image par elle
#     # Todo voir si on ne peux pas intégrer showimage dedans
#     """
#     Class pour l'affichage d'un treeview avec une lsite d'image et annotation et un popup au doucle clic
#     """
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.parent = parent
#
#         self.rowconfigure(0, weight=1)
#         self.columnconfigure(0, weight=1)
#
#         self.tree = ttk.Treeview(self, columns=("Annotations"))
#         self.tree.heading('#0', text='Liste des images', anchor='center')
#         self.tree.heading('Annotations', text="Annotations", anchor='center')
#         self.tree.grid(row=0, column=0, sticky='nesw')
#         self.tree.bind("<Double-1>", self.on_select_images_tree_str_item)
#
#     def insert(self, images_list):
#         """
#         Pour insérer la liste des images
#         """
#         self.tree.delete(*self.tree.get_children())
#         for image_name in images_list:
#             self.tree.insert('', 'end', text=image_name, values=(images_list[image_name][1],))
#     def on_select_images_tree_str_item(self, event):
#         if len(self.images_tree_str.selection()) > 0:
#             ref_item = self.images_tree_str.selection()[0]
#             item_values = self.images_tree_str.item(ref_item, "text")
#             test = NorsokShowImage(self.controller, self, item_values)
#             test.grab_set()
#             print(item_values)
#             print(ref_item)
