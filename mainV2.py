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

TODO : voir pour créer un suivi de ce qui a été transmis ou non : BD ou juste déplacement dans un autre répertoire?
TODO : Est ce qu'il faut prévoir d'archiver les dossiers? je dirais que oui pour eviter d'avoir une liste trop grande
TODO : Trier la liste des dossiers par date de création, plus récent en 1er


"""

### Import
# Interface graphique
import tkinter as tk
from tkinter import ttk, Text, OptionMenu, StringVar, filedialog as fd, Label, Entry, PhotoImage, Button
from tkinter.messagebox import showinfo, showerror, askyesno, showwarning
# Utilitaire fichier/dossier
import os
import sys
# Log
import logging
logger = logging.getLogger(__name__)

# import fichier
import datamet
import norsok_gui
import scanqr_gui

# Trouver tous les fichiers d'un dossier
# import glob
# Manipulation de données
# import pandas as pd
# Lecture fichier config
from configparser import ConfigParser
from pathlib import Path

# Pour gestion des images
from PIL import Image, ImageTk
# utilitaires
import outils


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
        self.tree = ttk.Treeview(self)
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        # self.tree.column('folder_list', stretch=True, width=300)
        self.tree.heading('#0', text='Liste dossier', anchor='w')

        self.tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')
        self.grid()

        # Treeview event click => Pour affichage des info dans détails
        self.tree.bind("<<TreeviewSelect>>", self.on_select_tree_item)
        # Treeview event click droit => pour affichage popup menu : Désactivé pour le moment
        # self.tree.bind("<Button-3>", self.show_popup_menu)

        # remplissage de la tree view avec les données
        abspath = os.path.abspath(folderpath)
        self.process_directory(abspath)

    def process_directory(self, path):
        root_node = self.tree.insert('', 'end', text="Sessions", open=True)
        # print(os.listdir(path))
        user_folder = {}
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            oid = self.tree.insert(root_node, 'end', text=p, open=False, values=(p,))
            paths = sorted(os.listdir(abspath), key=lambda f: -os.path.getmtime(os.path.join(abspath, f)))
            user_folder[p] = paths
            for f in paths:
                self.tree.insert(oid, 'end', text=f, open=False, values=(p, f,))

        # TODO : voir pour reprendre le fonctionnement de cette fonction pour faire un trie :
        # def get_result_date_list():
        #     """ Fonction qui récupère la liste des dossiers export """
        #     os.chdir(config.get('ResultsFolder', 'SuiviPath'))
        #     result_list = ["En attente export"]
        #     list_folder = [name for name in os.listdir(".") if os.path.isdir(name)]
        #     # On trie la liste des dossiers en fonction de la date, plus récent en 1er
        #     list_folder.sort(key=lambda x: datetime.strptime(x.split(' ')[2], "%d-%m-%y"), reverse=True)
        #     result_list.extend(list_folder)
        #     return result_list

    def on_select_tree_item(self, event):
        """
        Lors de la sélection d'un dossier dans la treeview on va afficher les détails dans la partie text (class Details)
        C'est pour essai pour le moment, on affiche les informations du fichier Mesures. Mais il faudrait faire avec Resultats au final
        """
        if len(self.tree.selection()) > 0:
            ref_item = self.tree.selection()[0]
            item_values = self.tree.item(ref_item, "value")
            if len(item_values) == 2:
                path = config.get('datamet', 'FolderResult')
                path_folder_results = os.path.join(path, item_values[0], item_values[1])
                # Test class Mesures()
                get_mesures.set_path(path_folder_results)
                details_mesures = self.parent.details_mesures.text
                details_mesures.config(state='normal')
                details_mesures.delete('1.0', 'end')
                for x in get_mesures.get_sections():
                    # Non du bloc
                    details_mesures.insert('end', '\n' + str(x[0]))
                    for y in x[1:]:
                        for z in y:
                            # info contenue dans le bloc
                            details_mesures.insert('end', '\n' + str("   " + z[0] + " : " + z[1]))

                # Test class Resultats()
                details_resultats = self.parent.details_resultats.text
                details_resultats.config(state='normal')
                details_resultats.delete('1.0', 'end')
                try:
                    get_resultats = datamet.Resultats()
                    get_resultats.set_path(path_folder_results)
                    get_resultats.read()
                except:
                    pass
                else:
                    df_resultats = get_resultats.df_results
                    if not df_resultats.empty:
                        details_resultats.insert('end', '\n' + str(df_resultats.iloc[0]))


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, bg="red", *args, **kwargs)
        self.parent = parent

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Treeview des dossiers
        # path = os.path.abspath("C:\\Nobackup\\Dev Informatique\\GitHub Clone\\Datamet\Exemple résultat")
        # path = os.path.abspath("E:\\Romain\\Documents\\Romain bidouille\\Informatique\\Taf\\Datamet\\Exemple résultat")
        path = config.get('datamet', 'FolderResult')
        self.folder_tree = FolderTree(self, parent, path)
        self.folder_tree.grid(row=0, column=0, sticky='news')

        # Pour afficher le détails du fichier Mesures
        self.details_mesures = Details(self, parent)
        self.details_mesures.grid(row=0, column=1, sticky='news')

        # Pour afficher le détails du fichier Résutlats
        self.details_resultats = Details(self, parent)
        self.details_resultats.grid(row=0, column=2, sticky='news')

        # self.test_result_list = TestResultList(self)
        # self.test_result_list.grid(row=0, column=1, sticky='news')
        # self.details_text = Details(self)
        # self.details_text.grid(row=1, column=1, sticky='news')


class MenuMain(tk.Menu):
    """ Class contenant le menu"""

    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        self.parent = parent

        # Menu Fichier
        self.file_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Fichier", underline=0, menu=self.file_menu)

        # self.file_menu.add_command(label="Transmettre les résultats vers SAP", underline=1,
        # command=self.parent.run_ps_popup_window)
        # self.file_menu.add_command(label="Archivage", underline=2, command=self.parent.archive_popup_window)
        self.file_menu.add_command(label="Exit", underline=3, command=parent.destroy)

        if parent.__class__.__name__ == "App":
            # Menu Filtre
            self.filtre_menu = tk.Menu(self, tearoff=False)
            self.add_cascade(label='Traitement par lot', underline=0, menu=self.filtre_menu)
            self.add_cascade(label='Scan QR Code', underline=0,
                             command=lambda: self.parent.top_resultbyqr_open(normes='ScanQR'))
            # On va créer une autre interface grahique avec TopLevel
            self.filtre_menu.add_command(label='Norsok', underline=3,
                                         command=lambda: self.parent.top_resultbyqr_open(normes='Norsok'))


class Popup(tk.Toplevel):
    """

    """

    def __init__(self, main_app, norme):
        self.main_app = main_app
        super().__init__(main_app)
        self.norme = norme

        # format de la fenêtre
        #self.geometry('1092x944')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Menu
        self.menubar = MenuMain(self)
        self.config(menu=self.menubar)

        # Gestion de l'affichage de la frame en fonction de la norme :
        if self.norme == "Norsok":
            self.title('Traitement des résultats par lot')
            # self.gui = Norsok_Gui(self, self.main_app)
            self.gui = norsok_gui.NorsokGui(self, self.main_app, script_path, config=config)
            self.gui.grid(row=0, column=0, sticky='news', padx=10, pady=10)
        if self.norme == "ScanQR":
            self.title('Scanner le QR Code')
            self.gui = scanqr_gui.ScanQrGui(self, self.main_app, script_path, config=config)
            self.gui.grid(row=0, column=0, sticky='news', padx=10, pady=10)

        self.center_window()

    def center_window(self):
        self.update()
        windows_width = self.winfo_width()
        windows_height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # print("Windows : " + str(windows_width) + " - " + str(windows_height))
        # print("screen : " + str(screen_width) + " - " + str(screen_height))

        center_x = int(screen_width / 2 - windows_width / 2)
        center_y = int(screen_height / 2 - windows_height / 2) - 40  # - 60 pour tenir compte de la barre windows

        self.geometry(f'+{center_x}+{center_y}')


# Todo : a supprimer
class ScanQR(tk.Frame):

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
        img_barcoderule2 = PhotoImage(file=os.path.join(script_path, 'Pictures\\barcoderule2.gif'))
        self.lbl_img = Label(self, image=img_barcoderule2)
        self.lbl_img.grid(row=0, column=0, sticky='s')
        self.lbl_img.image = img_barcoderule2

        # Input Text pour la valeur du QR CODE :
        self.lbl_qrcode = Label(self, text="Scanner le Code barre si dessus, puis le QR Code sur la feuille de travail")
        self.ety_qrcode = Entry(self, width=100)

        self.lbl_qrcode.grid(row=1, column=0,)
        self.ety_qrcode.grid(row=2, column=0, sticky='n')

        self.btn_valider = Button(self, text="Valider", command=self.valider)
        self.btn_valider.grid(row=3, column=0, sticky='nesw', padx=5, pady=5)

        self.ety_qrcode.focus_set()

    def valider(self):
        if len(self.ety_qrcode.get()) == 0:
            showwarning(message="Pas de valeur de QR CODE",
                                   parent=self.controller)
        else:
            self.controller.show_tab("norksok_result")



class App(tk.Tk):
    """
    Class principal de Tk
    """

    def __init__(self):
        # tk.Tk.__init__(self)
        super().__init__()
        self.menubar = MenuMain(self)
        self.config(menu=self.menubar)

        self.title("Gestion de l'export dans SAP des résultats du logiciel DATAMET")
        # width = self.winfo_screenwidth()
        # height = self.winfo_screenheight()
        # self.geometry("%dx%d" % (width, height))
        self.state('zoomed')
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

        # Gestion des fenêtres TopLevel
        self.top_resultbyqr = None

    # Pour le traitement par LOT avec QR Code
    def top_resultbyqr_open(self, normes):
        if self.top_resultbyqr is None:
            self.top_resultbyqr = Popup(self, norme=normes)
        else:
            self.top_resultbyqr.deiconify()
        self.top_resultbyqr.bind("<Destroy>", self._child_destroyed)

    def _child_destroyed(self, event):
        if event.widget == self.top_resultbyqr:
            # print("Destuction de resultbyQR")
            self.top_resultbyqr = None

    # afficher les erreurs
    # Todo : a reactiver
    # def report_callback_exception(self, exc, val, tb):
    #     showerror("Error", message=str(val))


if __name__ == '__main__':

    if os.path.exists('config.ini'):
        script_path = os.path.dirname(os.path.abspath(__file__))
        # Lecture fichier de configuration
        config = ConfigParser()
        config.read('config.ini', encoding='utf-8')
        # lecture fichier de resultat
        get_mesures = datamet.Mesures()
        # Création du dossier de suivi
        #sys.stdout = open(os.devnull, "w")
        outils.suivi_folder()
        #sys.stdout = sys.__stdout__
        # Log
        logfile = os.path.join(outils.suivi_folder_dict["today"], "log.txt")
        logging.basicConfig(filename=logfile,
                            filemode='a',
                            encoding='utf-8',
                            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S',
                            level=logging.INFO)
        # Loop GUI
        app = App()
        app.mainloop()
    else:
        logging.error("Le fichier config.ini n'est pas présent.")
        showerror("Error", message="Le fichier config.ini n'est pas présent.")
        # quit()

