import simplejson as json

class Observer(object):
    #__metaclass__ = ABCMeta
    def __init__(self, nome, conn):
        self.nome = nome
        self.connection = conn

    def update(self, pub_name, size):
        print("Atualizando cliente "+self.nome)
        resposta = {'tipo': 'update', 'name':pub_name, "size":size}  # caso consiga inscrever, notifica sucesso
        # resultado final da operação, converte string em byte
        self.connection.send(json.dumps(resposta).encode(encoding='utf-8'))
