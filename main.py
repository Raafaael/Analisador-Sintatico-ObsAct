from parser import parser

with open("entrada.obs", "r", encoding="utf-8") as f:
    texto = f.read()
parser.parse(texto)
