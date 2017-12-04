'''
		DEFINIÇÃO DO PROTOCOLO:

--------FORMATO DA MENSAGEM-------

		Formato da mensagem que o cliente pode enviar:
		{
			'opcao':opcao,
		}

		- parametro opcao pode assumir dois valores: 1 e 2
		- opcao == 1, significa que o cliente deseja se inscrever
		- opcao == 2, significa que o cliente deseja se desinscrever
		- opcao == "file", significa que o cliente deseja enviar um arquivo
		- opcao == "file_request"


		Formato da mensagem que o cliente recebe:
		 {
		 	'tipo': "update" | "success",
			'data':
			{
			 	'titulo': titulo,
				'conteudo': conteudo
			}
		 }

--------AÇÕES-------

		O servidor pode:
			- Registrar/Desregistrar Clientes
			- Criar uma nova publicacao
			- Enviar um nova publicacao para os clientes


--------FLUXO DE COMUNICAÇÃO-------
		Primeiro, o cliente precisa mandar uma mensagem solicitando a inscricao
		O servidor cria uma nova publicacao
		Após isso, a nova publicacao no servidor será enviada para o cliente registrado e os anteriores

'''

import simplejson as json
import _thread
import random
import os
from tkinter import filedialog
from tkinter import *

from socket import *

serverName = "localhost"
serverPort = 7003
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

#Thread que fica aguardando as respostas do servidor: aguarda novas publicacoes quando este
# esta registrado e tb espera a confirmação do cancelamento de inscrição
listen = False
def listenResposta(sckt):

    while listen:
        # cliente fica escutando para receber novas publicações
        resposta = clientSocket.recv(512)
        resposta = json.loads(resposta)

        # tratamento de atualizações vindas do servidor
        if resposta['tipo'] == 'update':

            # cliente requisita o download do arquivo
            msg = {"opcao": "file_request", "name": resposta['name']}

            clientSocket.send(json.dumps(msg).encode(encoding='utf-8'))

            # pega o tamanho do arquivo a ser recebido
            file_info = resposta['size']

            print("--------------\nNova publicacao: " + resposta['name'])
            # Recebe e salva o arquivo da publicação
            publicacao = clientSocket.recv(file_info)
            print("Salvando arquivo...")
            file = open(resposta['name'], 'wb')
            file.write(publicacao)
            print("Publicacao salva\nExibindo publicacao...\n--------------\n")

            file.close()

            # Abre o arquivo que foi baixado
            file = open(resposta['name'], 'r')

            line = file.readline()

            print("-----------------------------------")
            while line:
                print("|" + line, end="")
                line = file.readline()
            print("-----------------------------------")

            file.close()

#"Main"
while True:

    #possivel mudança para apenas publicar ou receber publicações
    tipo = input("Você deseja:\n1. Publicar\n2. Receber publicacoes\n")

    if int(tipo) == 1:
        print("Selecione arquivo txt da publicacao: ")

        root = Tk()
        root.withdraw()

        #Usa tkinter para abrir uma janela de dialogo para selecionar o arquivo da publicacao
        root.filename = filedialog.askopenfilename(initialdir="/", title="Selecione um arquivo",
                                                   filetypes=(("Arquivos de texto", "*.txt"), ("all files", "*.*")))

        #Abre o arquivo recebendo como parametro o seu caminho (conseguido pelo tkinter) e o modo "leitura em bytes" (RB)
        publicacao = open(root.filename, 'rb')

        #Pega do caminho apenas a parte final que é o nome do arquivo
        name = root.filename.split('/')
        name = name[len(name) - 1]

        print("Enviando arquivo " + name + "...")

        #Descobre o tamanho do arquivo aberto em bytes
        statinfo = os.stat(root.filename)
        size = statinfo.st_size

        #Forma a mensagem com nome e tamanho do arquivo
        msg = {"opcao": "file", "size": size, "name": name}
        msg = json.dumps(msg)

        #Envia o tamanho do arquivo para o sevidor poder receber
        clientSocket.send(msg.encode(encoding='utf-8'))

        #Envia a publicação(arquivo) para o servidor
        clientSocket.send(publicacao.read(size))

    elif int(tipo) == 2:
        opcao = input("\n\nSelecione uma opcao:\n1. Registrar\n2. Cancelar Registro\n3. Sair\n")

        if int(opcao) == 1 or int(opcao) == 2:
            nome = input("Insira o seu nome: ")
            mensagem = {
                'opcao': opcao,
                'nome': nome
            }

            # transforma json em uma string
            mensagemstr = json.dumps(mensagem)

            # envia a string mensagemstr
            clientSocket.send(mensagemstr.encode(encoding='utf-8'))

            #Se opcao = 2, entao a thread pode parar, o while da thread vai ser falso
            if opcao == 2:
                resposta = clientSocket.recv(1024)
                resposta = json.loads(resposta)
                if resposta['tipo'] == 'success':
                    print("Operação realizada com sucesso!")
                    listen = False
            else:
            #Se nao, continua/começa ouvindo
                listen = True

            resposta = clientSocket.recv(1024)
            resposta = json.loads(resposta)
            if resposta['tipo'] == 'success':
                print("...Operacao efetuada com sucesso!\n")
                _thread.start_new_thread(listenResposta, (clientSocket,))
            else:
                print("...Falha")

            #listenResposta(clientSocket)

        elif int(opcao) == 3:
            break
        else:
            print("Erro, selecione 1, 2 ou3.")

clientSocket.close()
