import pandas as pd

file = r"C:\Nobackup\Dev Informatique\GitHub Clone\Datamet\SAP\ParaSAP.xlsx"

ZCMT = pd.read_excel(file, sheet_name=0)
ZES_PARA = pd.read_excel(file, sheet_name=1)
Link = pd.read_excel(file, sheet_name=2)
print(ZCMT)
print(Link)