import pandas as pd

file = r"C:\Nobackup\Dev Informatique\GitHub Clone\Datamet\SAP\ZGVP_Micrographie.xlsx"

test = pd.read_excel(file, sheet_name=0)
test2 = pd.read_excel(file, sheet_name=1)
print(test)