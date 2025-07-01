from parser import parser

with open("tests/entrada.obs", "r", encoding="utf-8") as f:
    texto = f.read()
parser.parse(texto)
