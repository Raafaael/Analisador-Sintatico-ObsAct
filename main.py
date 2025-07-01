from parser import parser

with open("tests/pdf1.obs", "r", encoding="utf-8") as f:
    texto = f.read()
parser.parse(texto)
