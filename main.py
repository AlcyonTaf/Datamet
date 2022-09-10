# -*- coding: utf-8 -*-

"""
Programme pour récupérer les résultats des observations réaliser avec le logiciel DATAMET

Structure :
   - 1 dossier par "session"
         - Contient quoi qu'il arrive un fichier XXXXXXX_Mesures.txt (XXXXXX semble etre
            l'identifiant de la session) format stryle fichiet de config
         - En fonction de la méthode choisit :
            - 1 fichier de résultats, format CSV, XXXXXXX_Resultats
            - 1 fichier excel mise en forme qui sert de rapport
            - 1 fichier resultats images, format csv, Resultats_Images.txt
                - contient des détails sur les images utilisé pour le calcul je pense

         - Dossier d'images :
            - Images_XXXXXX
                - tous le temps présent
            - Images_Ignores_XXXXXXXX
                - présent en fonction de la méthode
            - Images_Traitement_XXXXX
                - Présent en fonction de la méthode



"""

### Import
# Interface graphique
import tkinter as tk
from tkinter import ttk, Text, OptionMenu, StringVar, filedialog as fd, Label
from tkinter.messagebox import showinfo, showerror, askyesno
# Utilitaire fichier/dossier
import os
# Trouver tous les fichiers d'un dossier
# import glob
# Manipulation de données
# import pandas as pd
# Lecture fichier config
from configparser import ConfigParser


class Details(tk.Frame):
    def __init__(self, parent, master, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.text = Text(self)
        self.text.grid(row=0, column=0, sticky='news')


class FolderTree(tk.Frame):
    def __init__(self, parent, master, folderpath, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(1, weight=1)
        # self.grid_columnconfigure(1, weight=1)

        self.nodes = dict()
        self.tree = ttk.Treeview(self, columns='folder_list', show='headings')
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.column('folder_list', stretch=True, width=300)
        self.tree.heading('folder_list', text='Liste dossier')

        self.tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')
        self.grid()

        abspath = os.path.abspath(folderpath)
        if abspath:
            for p in os.listdir(abspath):
                self.tree.insert('', 'end', values=(p,))


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, bg="red", *args, **kwargs)
        self.parent = parent

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Treeview des dossiers
        #path = os.path.abspath("C:\\Users\\CRMC\\PycharmProjects\\Datamet\\Exemple résultat")
        path = os.path.abspath("E:\\Romain\\Documents\\Romain bidouille\\Informatique\\Taf\\Datamet\\Exemple résultat")
        self.foldertree = FolderTree(self, parent, path)
        self.foldertree.grid(row=0, column=0, sticky='news')

        # Partie Détails des dossier
        self.details = Details(self, parent)
        self.details.grid(row=0, column=1, sticky='news')

        # self.test_result_list = TestResultList(self)
        # self.test_result_list.grid(row=0, column=1, sticky='news')
        # self.details_text = Details(self)
        # self.details_text.grid(row=1, column=1, sticky='news')


class MenuMain(tk.Menu):
    """ Class contenant le menu"""

    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        self.parent = parent
        self.file_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Fichier", underline=0, menu=self.file_menu)
        # self.file_menu.add_command(label="Transmettre les résultats vers SAP", underline=1,
        # command=self.parent.run_ps_popup_window)
        # self.file_menu.add_command(label="Archivage", underline=2, command=self.parent.archive_popup_window)
        self.file_menu.add_command(label="Exit", underline=3, command=self.quit)


class App(tk.Tk):
    """
    Class principal de Tk
    """

    def __init__(self):
        tk.Tk.__init__(self)
        self.menubar = MenuMain(self)
        self.config(menu=self.menubar)

        self.title("Gestion de l'export dans SAP des résultats du logiciel DATAMET")
        #self.geometry('640x480')
        # self.maxsize(1280, 600)
        # self.minsize(300, 400)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # MainApplication(self).pack(side="top", fill="both", expand=True)
        self.main_application = MainApplication(self)
        self.main_application.grid(row=0, column=0, sticky='nswe')
        # OtherFrame(self).pack(side="bottom")

        # Shutdown watchdog
        # self.bind("<Destroy>", self.main_application.test_result_list.shutdown_watchdog)

    # afficher les erreurs
    # Todo : a reactiver
    def report_callback_exception(self, exc, val, tb):
        showerror("Error", message=str(val))


if __name__ == '__main__':
    # Interface Graphique
    app = App()
    app.mainloop()

    # test lecture fichier mesures
    # path = os.path.abspath(
    #     "C:\\Users\\CRMC\\PycharmProjects\\Datamet\\Exemple résultat\\ISO 643_INT_277171_2022-06-07_10-59-04\\277171_Mesures.txt")
    #
    # Mesures = ConfigParser()
    # Mesures.read(path)
    # print(Mesures.get('General', 'Module'))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
