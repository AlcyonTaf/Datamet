# -*- coding: utf-8 -*-

import tkinter as tk
import os
from tkinter import ttk
from tkinter.ttk import Label
from PIL import ImageTk
from datetime import datetime

root_folder_path = None
suivi_folder_path = None
suivi_folder_path_today = None


def current_time_sap():
    """ Pour renvoyer la date et l'heure au format sap"""
    now = datetime.now()
    now_sap = now.strftime("%Y%m%d%H%M%S%f")
    return now_sap

def suivi_folder():
    """
    Fonction pour la gestion des dossiers de suivi : contient les fichiers xml généré et les logs
    Un dossier par jour.
    Le but est de vérifier si le dossier du jour existe, sinon on le créer.
    Le dossier de suivi est forcément a l'emplacement de l'executable
    """
    global root_folder_path
    global suivi_folder_path
    global suivi_folder_path_today
    root_folder_path = os.path.dirname(__file__)
    suivi_folder_path = os.path.join(root_folder_path, "Suivi")

    now = datetime.now()
    today = now.strftime("%d-%m-%Y")

    suivi_folder_path_today = os.path.join(suivi_folder_path, today)
    print(suivi_folder)

    if not os.path.exists(suivi_folder_path):
        # Création du dossier Suivi
        os.makedirs(suivi_folder_path)
    else:
        if not os.path.exists(suivi_folder_path_today):
            # Création du dossier de suivi du jour
            os.makedirs(suivi_folder_path_today)


class ImagesList(tk.Frame):
    # Todo finir cette classe et remplacer les 2 treeview d'image par elle
    # Todo voir si on ne peux pas intégrer showimage dedans
    """
    Class pour l'affichage d'un treeview avec une liste d'image et annotation et un popup au double clic
    images :
    """

    def __init__(self, parent, controller, images=None):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.images = images if images is not None else []

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Todo : Pour l'instant on laisse comme cela, mais on pourra éventuellement modifier en enlevant la colonne annotations
        self.tree = ttk.Treeview(self, columns=("Annotations"))
        self.tree.heading('#0', text='Liste des images', anchor='center')
        self.tree.heading('Annotations', text="Annotations", anchor='center')
        self.tree.grid(row=0, column=0, sticky='nesw')
        self.tree.bind("<Double-1>", self.on_select_images)

        # Si on fourni la liste d'images lors de la création de l'instance on affiche la liste
        if self.images:
            self.insert(self.images)

    def delete(self):
        self.tree.delete(*self.tree.get_children())

    def insert(self, images_list):
        """
        Pour insérer la liste des images
        """
        self.images = images_list
        self.tree.delete(*self.tree.get_children())
        for image_name in images_list:
            self.tree.insert('', 'end', text=image_name, values=(images_list[image_name][1],))

    def on_select_images(self, event):
        if len(self.tree.selection()) > 0:
            ref_item = self.tree.selection()[0]
            item_values = self.tree.item(ref_item, "text")
            show = ShowImage(self.controller, self, item_values)
            show.grab_set()
            # print(item_values)
            # print(ref_item)


class ShowImage(tk.Toplevel):
    # Todo a modifier pour qu'il soit appeller depuis la class ImageList, peut surement etre intégrer dans la class ImageList
    def __init__(self, main_app, parent, image_name):
        self.main_app = main_app
        self.parent = parent
        super().__init__(main_app)
        self.title("Affichage d'une image")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        image_pil = self.parent.images[image_name][0]

        image_pil.thumbnail((500, 500))

        image = ImageTk.PhotoImage(image_pil)

        # Essai d'enregistrement pour essai => Cela fonctionne!!!
        # image_pil.save('testpillow.tif', compression="packbits", resolution=150)

        lbl = Label(self, image=image)
        lbl.image = image
        lbl.grid(row=0, column=0)
