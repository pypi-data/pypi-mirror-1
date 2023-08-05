from pygnet import server

class ChatServer(server.GameServer):
    def __init__(self):
        self.clients = []

    def new_connection(self, client):
        print 'New connection', client
        self.clients.append(client)

    def lost_connection(self, client):
        self.clients.remove(client)

    def receive_object(self, client, obj):
        print 'Object received', obj
        for other_client in self.clients:
            other_client.send_object(obj)


server.run_server(ChatServer, 1979)



