'''
VALIDAR KEY WORDS
'''

import ply.lex as lex
import ply.yacc as yacc

# --- TABELAS GLOBAIS ---
devices = []
variables = {}
output = []
used_variables = set()
used_devices = set()

# --- TOKENS E PALAVRAS-CHAVE ---
reserved = {
    'dispositivo': 'DISPOSITIVO',
    'set': 'SET',
    'ligar': 'LIGAR',
    'desligar': 'DESLIGAR',
    'se': 'SE',
    'entao': 'ENTAO',
    'senao': 'SENAO',
    'True': 'TRUE',
    'False': 'FALSE',
    'enviar': 'ENVIAR',
    'alerta': 'ALERTA',
    'para': 'PARA',
    'todos': 'TODOS'
}

tokens = [
    'NUM', 'ID', 'STRING',
    'MAIOR', 'MENOR', 'IGUALIGUAL', 'DIF', 'MAIORIGUAL', 'MENORIGUAL',
    'E',
    'ABRECHAVE', 'FECHACHAVE', 'VIRG',
    'DOISPONTOS', 'IGUAL', 'PONTO',
    'ABREPAREN', 'FECHAPAREN'
] + list(reserved.values())

# --- EXPRESSÕES REGULARES DOS TOKENS ---
t_MAIOR = r'>'
t_MENOR = r'<'
t_IGUALIGUAL = r'=='
t_DIF = r'!='
t_MAIORIGUAL = r'>='
t_MENORIGUAL = r'<='
t_E = r'&&'
t_ABRECHAVE = r'\{'
t_FECHACHAVE = r'\}'
t_VIRG = r','
t_DOISPONTOS = r':'
t_IGUAL = r'='
t_PONTO = r'\.'
t_ABREPAREN = r'\('
t_FECHAPAREN = r'\)'

def t_COMMENT(t):
    r'\#.*'
    output.append(f"{t.value}")
    pass

def t_MULTILINE_COMMENT_SINGLE(t):
    r"\'\'\'(.|\n)*?\'\'\'"
    output.append(t.value)
    pass

def t_MULTILINE_COMMENT_DOUBLE(t):
    r'\"\"\"(.|\n)*?\"\"\"'
    output.append(t.value)
    pass

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]
    return t

def t_ID(t):
    r'[a-zA-ZáéíóúâêôãõçÁÉÍÓÚÂÊÔÃÕÇ_][a-zA-Z0-9áéíóúâêôãõçÁÉÍÓÚÂÊÔÃÕÇ_]*'
    if len(t.value) > 100:
        print(f"[Erro] Nome '{t.value}' excede 100 caracteres.")
        exit(1)
    t.type = reserved.get(t.value, 'ID')
    return t

t_ignore = ' \t\r\n'

def t_error(t):
    print(f"[Lex] Caracter inválido: {t.value[0]}")
    t.lexer.skip(1)

lexer = lex.lex()

# --- PARSER ---

def p_program(p):
    '''program : devices commands'''
    for var in used_variables:
        if var not in variables:
            output.insert(1, f"{var} = 0")

    # Verificar dispositivos não utilizados
    unused = set(devices) - used_devices
    for device in unused:
        print(f"[Aviso] O dispositivo '{device}' foi declarado mas não utilizado.")

    with open('saida.py', 'w', encoding='utf-8') as f:
        f.write("from runtime import *\n\n")
        for line in output:
            f.write(line + '\n')

    with open('relatorio.txt', 'w', encoding='utf-8') as r:
        r.write("=== Relatório de Execução ===\n\n")
        r.write("Dispositivos declarados:\n")
        for d in devices:
            r.write(f"- {d}\n")
        r.write("\nVariáveis setadas:\n")
        for k, v in variables.items():
            r.write(f"- {k} = {v}\n")

def p_devices_multiple(p):
    '''devices : device devices
               | device'''

def p_device(p):
    '''device : DISPOSITIVO DOISPONTOS ABRECHAVE ID VIRG ID FECHACHAVE
              | DISPOSITIVO DOISPONTOS ABRECHAVE ID FECHACHAVE'''
    name = p[4]
    if len(name) > 100:
        print(f"[Erro] Nome do dispositivo '{name}' excede 100 caracteres.")
        exit(1)
    if not all(c.isalpha() or c in 'áéíóúâêôãõçÁÉÍÓÚÂÊÔÃÕÇ' for c in name):
        print(f"[Erro] Nome do dispositivo inválido: '{name}' (só pode conter letras)")
        exit(1)
    devices.append(name)
    output.append(f"# dispositivo: {name}")

def p_commands_multiple(p):
    '''commands : command PONTO commands
                | command PONTO'''

def p_command_set(p):
    '''command : SET ID IGUAL value'''
    var = p[2]
    val = p[4]
    variables[var] = val
    output.append(f"{var} = {repr(val)}")

def p_command_ligar(p):
    '''command : LIGAR ID'''
    device = p[2]
    used_devices.add(device)
    output.append(f"ligar('{device}')")

def p_command_desligar(p):
    '''command : DESLIGAR ID'''
    device = p[2]
    used_devices.add(device)
    output.append(f"desligar('{device}')")

def p_command_if(p):
    '''command : SE condition ENTAO action'''
    output.append(f"if {p[2]}:")
    output.append(f"    {p[4]}")

def p_command_if_else(p):
    '''command : SE condition ENTAO action SENAO action'''
    output.append(f"if {p[2]}:")
    output.append(f"    {p[4]}")
    output.append(f"else:")
    output.append(f"    {p[6]}")

def p_condition_simple(p):
    '''condition : ID logicop value'''
    used_variables.add(p[1])
    p[0] = f"{p[1]} {p[2]} {repr(p[3])}"

def p_condition_compound(p):
    '''condition : ID logicop value E condition'''
    used_variables.add(p[1])
    p[0] = f"{p[1]} {p[2]} {repr(p[3])} and {p[5]}"

def p_logicop(p):
    '''logicop : MAIOR
               | MENOR
               | IGUALIGUAL
               | DIF
               | MAIORIGUAL
               | MENORIGUAL'''
    p[0] = p[1]

def p_value(p):
    '''value : NUM
             | TRUE
             | FALSE'''
    if p[1] == 'True':
        p[0] = True
    elif p[1] == 'False':
        p[0] = False
    else:
        p[0] = p[1]

def p_action_ligar(p):
    '''action : LIGAR ID'''
    used_devices.add(p[2])
    p[0] = f"ligar('{p[2]}')"

def p_action_desligar(p):
    '''action : DESLIGAR ID'''
    used_devices.add(p[2])
    p[0] = f"desligar('{p[2]}')"

def p_action_alert(p):
    '''action : ENVIAR ALERTA alert_content ID
              | ENVIAR ALERTA alert_content PARA TODOS DOISPONTOS lista_ids'''
    msg, var = p[3]
    if len(msg) > 100:
        print("[Erro] A mensagem não pode ter mais de 100 caracteres.")
        exit(1)
    if len(p) == 5:
        device = p[4]
        used_devices.add(device)
        if var is None:
            p[0] = f"alerta('{device}', \"{msg}\")"
        else:
            used_variables.add(var)
            p[0] = f"alerta_var('{device}', \"{msg}\", {var})"
    else:
        ids = p[7]
        actions = []
        for device in ids:
            used_devices.add(device)
            if var is None:
                actions.append(f"alerta('{device}', \"{msg}\")")
            else:
                used_variables.add(var)
                actions.append(f"alerta_var('{device}', \"{msg}\", {var})")
        p[0] = '\n'.join(actions)

def p_command_alert(p):
    '''command : ENVIAR ALERTA alert_content ID
               | ENVIAR ALERTA alert_content PARA TODOS DOISPONTOS lista_ids'''
    msg, var = p[3]
    if msg.strip() == "":
        print("[Erro] A mensagem não pode ser vazia.")
        exit(1)
    if len(msg) > 100:
        print("[Erro] A mensagem não pode ter mais de 100 caracteres.")
        exit(1)
    if len(p) == 5:
        device = p[4]
        used_devices.add(device)
        if var is None:
            output.append(f"alerta('{device}', \"{msg}\")")
        else:
            used_variables.add(var)
            output.append(f"alerta_var('{device}', \"{msg}\", {var})")
    else:
        ids = p[7]
        for device in ids:
            used_devices.add(device)
            if var is None:
                output.append(f"alerta('{device}', \"{msg}\")")
            else:
                used_variables.add(var)
                output.append(f"alerta_var('{device}', \"{msg}\", {var})")

def p_alert_content_var(p):
    '''alert_content : ABREPAREN STRING VIRG ID FECHAPAREN'''
    if p[2].strip() == "":
        print("[Erro] A mensagem não pode ser vazia.")
        exit(1)
    if len(p[2]) > 100:
        print("[Erro] A mensagem não pode ter mais de 100 caracteres.")
        exit(1)
    p[0] = (p[2], p[4])
    used_variables.add(p[4])

def p_alert_content_simple(p):
    '''alert_content : ABREPAREN STRING FECHAPAREN'''
    if p[2].strip() == "":
        print("[Erro] A mensagem não pode ser vazia.")
        exit(1)
    if len(p[2]) > 100:
        print("[Erro] A mensagem não pode ter mais de 100 caracteres.")
        exit(1)
    p[0] = (p[2], None)

def p_lista_ids(p):
    '''lista_ids : ID VIRG lista_ids
                 | ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_error(p):
    if p:
        print(f"[Sintaxe] Erro perto de '{p.value}' — Verifique se declarou dispositivos corretamente, se usou ponto no final ou parênteses nas mensagens.")
    else:
        print("[Sintaxe] Erro inesperado no fim do arquivo.")

parser = yacc.yacc()