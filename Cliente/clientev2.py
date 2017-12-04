import simplejson as json
import _thread

from threading import Thread
import threading
from tkinter import filedialog
from tkinter import *
from socket import *

serverName = "localhost"
serverPort = 7003
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

def abrir_arquivo():
    root = Tk()
    root.withdraw()

    print("Selecione arquivo txt da publicacao: ")

    # Usa tkinter para abrir uma janela de dialogo para selecionar o arquivo da publicacao
    root.filename = filedialog.askopenfilename(initialdir="/", title="Selecione um arquivo",
                                               filetypes=(("Arquivos de texto", "*.txt"), ("all files", "*.*")))

    # Abre o arquivo recebendo como parametro o seu caminho (conseguido pelo tkinter) e o modo "leitura em bytes" (RB)
    publicacao = open(root.filename, 'rb')

    # Pega do caminho apenas a parte final que é o nome do arquivo
    name = root.filename.split('/')
    name = name[len(name) - 1]

    # Descobre o tamanho do arquivo aberto em bytes
    statinfo = os.stat(root.filename)
    size = statinfo.st_size

    return (publicacao, name, size)

def listenPublications(socket):
    pass
bgThread = None
while True:
    tipo = input("Você deseja:\n1. Publicar\n2. Receber publicacoes\n")

    if int(tipo) == 1:
        #chama a funcao com a rotina de abrir um arquivo e pegar as informacoes dele
        (pub_file, file_name, file_size) = abrir_arquivo()

        print("Enviando arquivo " + file_name + "...")

        # Forma a mensagem com nome e tamanho do arquivo
        msg = {"opcao": "file", "size": file_size, "name": file_name}
        msg = json.dumps(msg)

        # Envia o tamanho do arquivo para o sevidor poder receber
        clientSocket.send(msg.encode(encoding='utf-8'))

        # Envia a publicação(arquivo) para o servidor
        clientSocket.send(pub_file.read(file_size))

    if int(tipo) == 2:
        opcao = input("\n\nSelecione uma opcao:\n1. Registrar\n2. Cancelar Registro\n3. Sair\n")

        bgThread = Thread(target=listenPublications,  args=(clientSocket,))
        bgThread.daemon = True;
        bgThread.start();

