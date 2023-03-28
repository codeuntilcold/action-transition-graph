import socket
from time import sleep

class GraphConnector:
    def __init__(self, graph_port=24000):
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientsocket.connect((socket.gethostname(), graph_port))

    def send(self, message):
        self.clientsocket.send(message.encode('ascii'))
    
    def close(self):
        self.clientsocket.close()

def read_sim_file():
    for line in open('sim_8_4_1_20221105.txt', 'r'):
        yield line

if __name__ == '__main__':
    connector = GraphConnector()
    for message in read_sim_file():
        connector.send(message)
        sleep(1 / 30.0)
    connector.close()
