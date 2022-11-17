# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Label
from PIL import ImageTk


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
            print(item_values)
            print(ref_item)


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
