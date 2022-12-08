string = "5301530;10;280174.11;10;60;1;FRC;MIC01;955;;;Texte:280174:PS;Texte:280174:PS;TEXTE:280174:PS"

string_split = string.split(';')[0:4]

string = "".join(string.split(';')[0:4])

print(string)




