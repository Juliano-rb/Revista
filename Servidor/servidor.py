import _thread
import os
import random
from socket import *

import simplejson as json

from observable import Observable
from observer import Observer

serverPort = 7003
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)


#Observável é a classe
observavel = Observable()


def task(connection, client):
    # passa essa função para thread (várias conexões)
    print(connection)
    print(client)
    id = random.randint(0, 10000)
    while True:
        received = connection.recv(1024)
        print("Servidor recebeu mensagem ", received, " do cliente ", id)
        mensagemjson = json.loads(received)

        # json.loads(json_string) serve pra ler a string e transformá-la em json

        # pega o atributo opcao, json permite acessar partes da string separadamente
        if mensagemjson['opcao'] == str(1):
            print(mensagemjson['nome'])

            cliente = Observer(mensagemjson['nome'], connection)

            # registra um novo inscrito em Observable
            observavel.register(cliente)

            print("Novo cliente inscrito: " + cliente.nome)

            resposta = {'tipo': 'success'}
            # caso consiga inscrever, notifica sucesso
            # resultado final da operação, converte string(json) em byte e envia para o cliente
            connection.send(bytes(json.dumps(resposta), 'utf-8'))

        elif mensagemjson['opcao'] == str(2):

            for x in observavel.observers:
                if mensagemjson['nome'] == x.nome:
                    observador = x

            observavel.unregister(observador)

            for x in observavel.observers:
                print("A nova lista de clientes é: ", x.nome)

            resposta = {'tipo': 'success'}
            connection.send(bytes(json.dumps(resposta), 'utf-8'))


            # converte a lista resultado, para uma array em json
            # connection.send(bytes(json.dumps(resultado), 'utf-8'))

        elif mensagemjson['opcao'] == "file":
            size = mensagemjson['size']

            publication = connection.recv(size)

            file = open(mensagemjson['name'], 'wb')
            file.write(publication)

            file.close()

            observavel.update_observers(mensagemjson['name'], size)

        elif mensagemjson['opcao'] == "file_request":

            #Estrutura responsável por enviar o arquivo para o cliente a partir de uma requisição
            name = mensagemjson['name']
            file = open(name, 'rb')

            #Pega o tamanho do arquivo especificado pelo nome
            statinfo = os.stat(name)
            size = statinfo.st_size

            #Envia o arquivo
            print("Enviando arquivo " + name)
            connection.send(file.read(size))


    connection.close()


print("The server is ready to receive")
while 1:
    connection, addr = serverSocket.accept()
    _thread.start_new_thread(task, (connection, addr))
