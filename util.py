import subprocess
import re

latency_pattern = re.compile("\\D+=\d+ms")  # Esse pattern é usado para a função getLatency()

def getFormattedSize(bytes_):
    """
    Função para obter um tamanho em bytes formatado.
    """
    types = ["Bytes","KB","MB"]
    index = 0

    while bytes_ > 1024 and index < len(types)-1:
        bytes_ /= 1024
        index += 1
    return bytes_,types[index]


def getLatency(server="www.google.com",timeout=0):
    """
    Função para obter o tempo de resposta de um servidor.
    """
    if timeout:
        output = subprocess.getoutput("ping /n 1 /w %i %s"%(timeout,server))
    else:
        output = subprocess.getoutput("ping /n 1 %s"%(server))
    try:
        output = latency_pattern.findall(output)[0]
        latency = output.split("=")[1].split("ms")[0]
        return latency
    except:
        return None

