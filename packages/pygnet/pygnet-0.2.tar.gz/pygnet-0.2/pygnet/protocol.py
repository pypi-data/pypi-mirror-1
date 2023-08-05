import marshal as encoder

from twisted.protocols import basic



def use_encoder(self, encoder_interface):
    """
    Tell pygnet to use a different module for encoding.
    eg pickle, json or gherkin. Anything that provides loads and dumps
    functions.
    """
    globals()['encoder'] = encoder_interface


class GameProtocol(basic.Int32StringReceiver):
    def connectionMade(self):
        self.factory.new_connection(self)

    def connectionLost(self, reason):
        self.factory.lost_connection(self)

    def stringReceived(self, data):
        obj = encoder.loads(data)
        self.factory.receive_object(self, obj)

    def send_object(self, obj):
        data = encoder.dumps(obj)
        self.sendString(data)





    

