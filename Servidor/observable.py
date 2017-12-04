from observer import Observer

class Observable(object):

    def __init__(self):
        self.observers = list()

    def register(self, observer):
        if not observer in self.observers:
            self.observers.append(observer)

    def unregister(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def unregister_all(self):
        if self.observers:
            del self.observers[:]

    def update_observers(self, *args, **kwargs):
        print("Atualizando clientes")
        for observer in self.observers:
            observer.update(*args, **kwargs)
