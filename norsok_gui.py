# -*- coding: utf-8 -*-
"""
    Contient les class pour la GUI dans le cas des essais selon la normes NORSOK

    Source :
        https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter

"""

import tkinter as tk
from tkinter import Label, Entry, PhotoImage, Button, ttk

import os

# import fichier
import datamet
import mainV2


class Norsok_Gui(tk.Frame):
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
        frm_action = tk.Frame(self)
        frm_action.rowconfigure(0, weight=0)
        frm_action.columnconfigure(0, weight=0)
        frm_action.columnconfigure(1, weight=0)
        frm_action.grid(row=0, column=0)
        btn_previous = Button(frm_action, text="Précédent", command=None)
        btn_previous.grid(row=0, column=0)
        btn_suivant = Button(frm_action, text="Suivant", command=None)
        btn_suivant.grid(row=0, column=1)

        # Container va contenir les différentes pages
        container = tk.Frame(self, bg='red')
        container.grid(row=1, column=0, sticky='news')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.frames["norsok_qr"] = Norsok_QR(parent=container, controller=self)
        self.frames["norksok_result"] = Norksok_result(parent=container, controller=self)

        # Page d'acueil :
        self.show_frame("norsok_qr")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        for frame in self.frames.values():
            frame.grid_remove()
        frame = self.frames[page_name]
        frame.event_generate("<<ShowFrame>>")
        frame.grid(row=0, column=0, sticky='nesw')


class Norsok_btn(tk.Frame):
    """
    Pour afficher une barre avec des boutons d'action
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self


class Norsok_QR(tk.Frame):

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


class Norksok_result(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg='green')
        self.parent = parent
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Partie FRC
        self.lbl_frc = Label(self, text="Choix de l'essai FRC")
        self.lbl_frc.grid(row=0, column=0)
        self.lbl_frc_text = Label(self)
        self.lbl_frc_text.grid(row=1, column=0)
        self.tree_frc = ttk.Treeview(self)
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
        self.tree_str = ttk.Treeview(self)
        self.tree_str.heading('#0', text='Liste des sessions', anchor='center')
        self.tree_str.grid(row=6, column=0, sticky='nesw')

        # Event a l'affichage
        self.bind("<<ShowFrame>>", self.on_show_frame)

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
                    for session_path in finded_sessions:
                        session_name = os.path.basename(session_path)
                        self.tree_frc.insert('', 'end', text=session_name, values=(session_path,))
            elif module == "Acquisition d'image":
                if not finded_sessions:
                    self.lbl_str_text.config(text="Pas de sessions trouvé pour ce QR Code")
                else:
                    for session_path in finded_sessions:
                        session_name = os.path.basename(session_path)
                        self.tree_str.insert('', 'end', text=session_name, values=(session_path,))


class norsok_transfert(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
