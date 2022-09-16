# -*- coding: utf-8 -*-
import os
# Manipulation de xml
from lxml import etree as et
# Fichier de configuration
from configparser import ConfigParser


class SapXml(object):
    """
    Class pour la création d'un xml de résultat et/ou d'annexe qui sera ensuite importé dans SAP
    Entrée :

    Fonction :
        xml_result_to_sap

    Question : Sous quel format on récupére les données pour la génération du xml?
    dictionnaire avec list:
    {"Essais":[{détails de l'id SAP,"Eprouvettes":[{Détails eprouvette, "Parametres":[{Détails des résultats}]}]}]

    """

    def __int__(self):
        self.config = ConfigParser()
        self.xml_encoding = 'ISO-8859-1'
        # On créer le nom du fichier xml et on définit ou l'enregistrer
        # Todo : Rajouter timestamp a la fin du fichier (voir fichier résultats traction pdf du scipt PS)
        # self.xml_name = "\IC_PL_ESS_RES_" + essais_id[1] + "_" + essais_id[2] + "_" + essais_id[3] + "_" + essais_id[
        #     4] + "_" + \
        #            essais_id[5] + ".xml"
        self.xml_path_folder_to_save = self.config.get('xmlSAP', 'SaveXMLToSAPFolder')
        self.xml_template_folder = self.config.get('xmlSAP', 'XMLTemplateFolder')

        self.path_to_xml_essais = os.path.join(self.xml_template_folder, 'xml_template_essais.xml')
        self.path_to_xml_eprouvette = os.path.join(self.xml_template_folder, 'xml_template_eprouvette.xml')
        self.path_to_xml_parametre = os.path.join(self.xml_template_folder, 'xml_template_parametre.xml')
        # import des templates
        # Essais
        self.root_essais = et.parse(self.path_to_xml_essais).getroot()
        # Eprouvette
        self.root_eprouvette = et.parse(self.path_to_xml_eprouvette).getroot()
        # Parametre
        self.root_parametre = et.parse(self.path_to_xml_parametre).getroot()

    def xml_result_to_sap(self, valeur_sap, file_path):
        """
        Fonction qui va générer le xml pour sap dans le cas de résultats

        Parameters :
            valeur_sap :
            [{"ESSAI":
                {"./__Essai/Source": "ValeurSource",
                "./__Essai/TimeStamp": "ValeurTimeStamp",
                "./__Essai/NoCommande": "ValeurNoCommande",
                "./__Essai/NoPoste": "ValeurNoPoste",
                "./__Essai/Batch": "ValeurBatch",
                "./__Essai/SequenceLoc": "ValeurSequenceLoc"},
            "Eprouvettes":
                [
                # A répéter pour chaque eprouvette
                {"EPROUVETTE":
                    {"./SeqEssais": "ValeurSeqEssais"},
                    # A répéter pour chaque parametres de l'eprouvette
                    "Parametres":
                        [{"./NumPara": "ValeurNumPara",
                        "./UnitPara": "UnitPara",
                         "./ValuePara": "ValeurValuePara",
                         "./ValueParaT": "ValeurValueParaT",
                         "./SequenceResult": "ValeurSequenceResult",
                         "./SequenceEssEpr": "ValeurSequenceEssEpr"}]}]}]
        return :

        """
        print('result_to_sap fonction')

    def xml_tiff_to_sap(self):
        """
        fonction qui va générer le xml pour sap dans le cas d'annexe
        :return:
        """
        print('xml_tiff_to_sap fonction')


# Copie de la fonction pour générer les XML de tractionPDF
# le but est d'en faire une class qui sera réutilisable dans d'autre projet
def xml_pdf_to_tiff(essais_id, pdf_name):
    """" Fonction qui permet de générer le couple XML/TIFF pour les annexes SAP
        En para :
            essais_id : tuple contenant l'ID sap de l'essai
            pdf_name : nom du pdf à transformer
    """
    xml_encoding = 'ISO-8859-1'
    # On créer le nom du fichier xml et on définit ou l'enregistrer
    xml_name = "\IC_PL_ESS_RES_" + essais_id[1] + "_" + essais_id[2] + "_" + essais_id[3] + "_" + essais_id[4] + "_" + \
               essais_id[5] + ".xml"
    #xml_path_to_save = config.get('Annexe', 'SaveXMLTiffFolder') + xml_name

    xml_template_folder = r"E:\Romain\Documents\Romain bidouille\Informatique\Taf\Datamet\Xml Template"

    path_to_xml_essais = os.path.join(xml_template_folder, 'xml_template_essais.xml')
    path_to_xml_eprouvette = os.path.join(xml_template_folder, 'xml_template_eprouvette.xml')
    path_to_xml_parametre = os.path.join(xml_template_folder, 'xml_template_parametre.xml')
    # import des templates
    # Essais
    root_essais = et.parse(path_to_xml_essais).getroot()
    # Eprouvette
    root_eprouvette = et.parse(path_to_xml_eprouvette).getroot()
    # Parametre
    root_parametre = et.parse(path_to_xml_parametre).getroot()

    # Dans un premier temps on remplie la partie parametre
    # NumPara = 907 pour annexe traction et micro
    root_parametre.find("./NumPara").text = "907"
    # pas de valuePara
    # root_parametre.find("./ValuePara").text = "ValuePara"
    # Ici on doit mettre le nom du fichier
    root_parametre.find("./ValueParaT").text = pdf_name[1:]
    # Pour sequence j'ai mis 1 pour le moment
    root_parametre.find("./SequenceResult").text = "1"
    root_parametre.find("./SequenceEssEpr").text = "1"

    # insert para dans eprouvette
    root_eprouvette.find("./Parametres").insert(0, root_parametre)
    # eprouvette_para.insert(0, root_parametre)

    # On complete eprouvette
    root_eprouvette.find("./SeqEssais").text = essais_id[5]

    # insert eprouvette dans essais
    root_essais.find("./__Essai/Eprouvettes").insert(0, root_eprouvette)

    # On complete essais
    root_essais.find("./__Essai/Source").text = "LABO_IC"
    root_essais.find("./__Essai/TimeStamp").text = datetime.now().strftime('%Y%m%d%H%M%S%f')
    root_essais.find("./__Essai/NoCommande").text = essais_id[1]
    root_essais.find("./__Essai/NoPoste").text = essais_id[2]
    root_essais.find("./__Essai/Batch").text = essais_id[3]
    root_essais.find("./__Essai/SequenceLoc").text = essais_id[4]

    et.indent(root_essais)
    et.ElementTree(root_essais).write(xml_path_to_save, pretty_print=True, encoding=xml_encoding)


if __name__ == '__main__':
    print('sapxml.py')
    dirname = os.path.dirname(__file__)

    testresultat = [{"ESSAI": {"./__Essai/Source": "ValeurSource", "./__Essai/TimeStamp": "ValeurTimeStamp",
                                          "./__Essai/NoCommande": "ValeurNoCommande", "./__Essai/NoPoste": "ValeurNoPoste",
                                          "./__Essai/Batch": "ValeurBatch", "./__Essai/SequenceLoc": "ValeurSequenceLoc"},
                                "Eprouvettes": [{"EPROUVETTE": {"./SeqEssais": "ValeurSeqEssais"},
                                                 "Parametres": [{"./NumPara": "ValeurNumPara",
                                                                 "./UnitPara": "UnitPara",
                                                                 "./ValuePara": "ValeurValuePara",
                                                                 "./ValueParaT": "ValeurValueParaT",
                                                                 "./SequenceResult": "ValeurSequenceResult",
                                                                 "./SequenceEssEpr": "ValeurSequenceEssEpr"}]}]}]

    # print(type(testresultat))
    # print(testresultat)
    # print(testresultat["Essais"])
    # print(type(testresultat["Essais"]))

    #Essai création xml
    xml_template_folder = r"E:\Romain\Documents\Romain bidouille\Informatique\Taf\Datamet\Xml Template"

    path_to_xml_essais = os.path.join(xml_template_folder, 'xml_template_essais.xml')
    path_to_xml_eprouvette = os.path.join(xml_template_folder, 'xml_template_eprouvette.xml')
    path_to_xml_parametre = os.path.join(xml_template_folder, 'xml_template_parametre.xml')
    # import des templates
    # Essais
    root_essais = et.parse(path_to_xml_essais).getroot()
    # Eprouvette
    root_eprouvette = et.parse(path_to_xml_eprouvette).getroot()
    # Parametre
    root_parametre = et.parse(path_to_xml_parametre).getroot()

    print(type(testresultat))
    for essai in testresultat:
        ident_essai = essai['ESSAI']
        # récupération de l'i de l'essai
        for balise_essai in ident_essai:
            print(balise_essai + " - " + str(ident_essai[balise_essai]))
            root_essais.find(balise_essai).text = ident_essai[balise_essai]

        # récupération des Eprouvette de l'essai :
        for eprouvette in essai['Eprouvettes']:
            ident_eprouvette = eprouvette['EPROUVETTE']
            for balise_eprouvette in ident_eprouvette:
                print(balise_eprouvette + " - " + str(ident_eprouvette[balise_eprouvette]))
                root_eprouvette.find(balise_eprouvette).text = ident_eprouvette[balise_eprouvette]

            # récupération des paramétres de l'eprouvette
            for parametre in eprouvette["Parametres"]:
                for balise_parametre in parametre:
                    print(balise_parametre + " - " + parametre[balise_parametre])
                    root_parametre.find(balise_parametre).text = parametre[balise_parametre]

                # On ajoute les parametres dans Eprouvette
                root_eprouvette.find("./Parametres").insert(0, root_parametre)

            # On ajoute les Eprouvettes dans Essais :
            root_essais.find("./__Essai/Eprouvettes").insert(0, root_eprouvette)

        # On crée le fichier xml de l'essai en cours
        et.indent(root_essais)
        et.ElementTree(root_essais).write(os.path.join(dirname, "sap.xml"), pretty_print=True, encoding='ISO-8859-1')


    print(et.tostring(root_essais))
    print(et.tostring(root_eprouvette))
    # print(et.tostring(root_parametre))