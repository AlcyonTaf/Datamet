from PIL import Image

im = Image.open(r"C:/Nobackup/Dev Informatique/GitHub Clone/Datamet/Exemple résultat/CAMUS_C/AcquisitionImages_ESSAI "
                r"STR-NORSOK_2022-10-21_10-14-32/Images_Echelle_ESSAI STR-NORSOK/ESSAI STR-NORSOK_Champ_1_1_0.tif")
dict ={}
dict["test"] = im
print(dict)

dict["test"].show()