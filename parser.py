import ply.lex as lex
import ply.yacc as yacc

# --- TABELAS GLOBAIS ---
devices = []
variables = {}
output = []

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
    'NUM', 'ID',
    'MAIOR', 'MENOR', 'IGUALIGUAL', 'DIF', 'MAIORIGUAL', 'MENORIGUAL',
    'E',
    'ABRECHAVE', 'FECHACHAVE', 'VIRG',
    'DOISPONTOS', 'IGUAL', 'PONTO',
    'ASPAS', 'ABREPAREN', 'FECHAPAREN'
] + list(reserved.values())

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
t_ASPAS = r'"'
t_ABREPAREN = r'\('
t_FECHAPAREN = r'\)'

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
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
    with open('saida.py', 'w', encoding='utf-8') as f:
        f.write("from runtime import *\n\n")
        for line in output:
            f.write(line + '\n')

def p_devices_multiple(p):
    '''devices : device devices
               | device'''

def p_device(p):
    '''device : DISPOSITIVO DOISPONTOS ABRECHAVE ID VIRG ID FECHACHAVE
              | DISPOSITIVO DOISPONTOS ABRECHAVE ID FECHACHAVE'''
    name = p[4]
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
    output.append(f"ligar('{device}')")

def p_command_desligar(p):
    '''command : DESLIGAR ID'''
    device = p[2]
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
    p[0] = f"{p[1]} {p[2]} {repr(p[3])}"

def p_condition_compound(p):
    '''condition : ID logicop value E condition'''
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
    p[0] = f"ligar('{p[2]}')"

def p_action_desligar(p):
    '''action : DESLIGAR ID'''
    p[0] = f"desligar('{p[2]}')"

def p_command_alert_msg(p):
    '''command : ENVIAR ALERTA ABREPAREN ASPAS mensagem ASPAS FECHAPAREN ID'''
    msg = p[5]
    device = p[8]
    output.append(f"alerta('{device}', \"{msg}\")")

def p_command_alert_msg_var(p):
    '''command : ENVIAR ALERTA ABREPAREN ASPAS mensagem ASPAS VIRG ID FECHAPAREN ID'''
    msg = p[5]
    var = p[8]
    device = p[10]
    output.append(f"alerta_var('{device}', \"{msg}\", {var})")

def p_command_alert_broadcast(p):
    '''command : ENVIAR ALERTA ABREPAREN ASPAS mensagem ASPAS FECHAPAREN PARA TODOS DOISPONTOS lista_ids'''
    msg = p[5]
    ids = p[11]  # CORRETO!
    for device in ids:
        output.append(f"alerta('{device}', \"{msg}\")")

def p_lista_ids(p):
    '''lista_ids : ID VIRG lista_ids
                 | ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_mensagem(p):
    '''mensagem : mensagem ID
                | ID'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + ' ' + p[2]

def p_error(p):
    print(f"[Sintaxe] Erro perto de '{p.value}'" if p else "[Sintaxe] Erro inesperado no fim do arquivo.")

parser = yacc.yacc()