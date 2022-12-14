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
from tkinter import ttk, Text, OptionMenu, StringVar, filedialog as fd, Label
from tkinter.messagebox import showinfo, showerror, askyesno
# Utilitaire fichier/dossier
import os

# import fichier
import datamet

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

        # Treeview event click => Pour affichage des info dans détails
        self.tree.bind("<<TreeviewSelect>>", self.on_select_tree_item)
        # Treeview event click droit => pour affichage popup menu : Désactivé pour le moment
        #self.tree.bind("<Button-3>", self.show_popup_menu)

        # remplissage de la tree view avec les données
        abspath = os.path.abspath(folderpath)
        if abspath:
            for p in os.listdir(abspath):
                self.tree.insert('', 'end', values=(p,))

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
            folder_name = self.tree.item(ref_item, "value")[0]
            path = config.get('datamet', 'FolderResult')
            path_folder_results = os.path.join(path, folder_name)
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
                details_resultats.insert('end', '\n' + str(df_resultats.iloc[0]))




class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, bg="red", *args, **kwargs)
        self.parent = parent

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Treeview des dossiers
        #path = os.path.abspath("C:\\Nobackup\\Dev Informatique\\GitHub Clone\\Datamet\Exemple résultat")
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

    # afficher les erreurs
    # Todo : a reactiver
    def report_callback_exception(self, exc, val, tb):
        showerror("Error", message=str(val))


if __name__ == '__main__':

    if os.path.exists('config.ini'):
        # Lecture fichier de configuration
        config = ConfigParser()
        config.read('config.ini', encoding='utf-8')
        # lecture fichier de resultat
        get_mesures = datamet.Mesures()
        app = App()
        app.mainloop()
    else:
        showerror("Error", message="Le fichier config.ini n'est pas présent.")
        # quit()





    # path = r"C:\Nobackup\Dev Informatique\GitHub Clone\Datamet\Exemple résultat\ISO 643_INT_277171_2022-06-07_10-59-04\277171_Mesures.txt"
    # test = resultats.Mesures()
    # test.set_path(path)
    # print(test.get_sections())


    # test lecture fichier mesures
    # path = os.path.abspath(
    #     "C:\\Users\\CRMC\\PycharmProjects\\Datamet\\Exemple résultat\\ISO 643_INT_277171_2022-06-07_10-59-04\\277171_Mesures.txt")
    #
    # Mesures = ConfigParser()
    # Mesures.read(path)
    # print(Mesures.get('General', 'Module'))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
