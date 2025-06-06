def ligar(device):
    print(device + " ligado!")

def desligar(device):
    print(device + " desligado!")

def alerta(device, msg):
    print(device + " recebeu o alerta:\n" + msg)

def alerta_var(device, msg, var):
    print(device + " recebeu o alerta:\n" + msg + " " + str(var))
