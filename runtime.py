def ligar(device):
    print(f"{device} ligado!")
    log(f"{device} ligado!")

def desligar(device):
    print(f"{device} desligado!")
    log(f"{device} desligado!")

def alerta(device, msg):
    print(f"{device} recebeu o alerta:\n{msg}")
    log(f"{device} recebeu o alerta: {msg}")

def alerta_var(device, msg, var):
    print(f"{device} recebeu o alerta:\n{msg} {var}")
    log(f"{device} recebeu o alerta: {msg} {var}")

def log(message):
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(message + '\n')