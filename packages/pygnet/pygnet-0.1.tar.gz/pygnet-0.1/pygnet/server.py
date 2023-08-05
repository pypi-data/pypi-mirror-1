from twisted.internet import protocol, reactor

from protocol import GameProtocol



class GameServer(protocol.ServerFactory):
    def new_connection(self, client):
        pass

    def lost_connection(self, client):
        pass

    def recieve_object(self, client, obj):
        pass

    def send_object(self, client, obj):
        client.send_object(obj)


def run_server(ServerClass, port):
    factory = ServerClass()
    factory.protocol = GameProtocol
    reactor.listenTCP(port, factory)
    reactor.run()


if __name__ == "__main__":
    run_server(GameServer, 1979)
