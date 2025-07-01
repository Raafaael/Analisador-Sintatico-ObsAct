def ligar(device):
    print(f"{device} ligado!")

def desligar(device):
    print(f"{device} desligado!")

def alerta(device, msg):
    print(f"{device} recebeu o alerta:\n{msg}")

def alerta(device, msg, var=''):
    print(f"{device} recebeu o alerta:\n{msg} {var}")
