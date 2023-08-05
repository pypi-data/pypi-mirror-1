from pygnet import client
import time




client.init('localhost', 1979)

connection = None

while not connection:
    client.poll()
    for event_name, args in client.get_events():
        if event_name == 'new_connection':
            connection = args['connection']

for i in xrange(10):
    connection.send_object('hello')
    client.poll()
    for event_name, args in client.get_events():
        print event_name, args
    time.sleep(1)

client.shutdown()

