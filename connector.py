import socket
from time import sleep
import logging


class ClientDisconnected(Exception):
    pass


class ModelConnector:
    def __init__(self, graph_port=24000):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((socket.gethostname(), graph_port))
        self.serversocket.listen(5)
        self.clientsocket = None

    def get_stream_gen(self):
        while True:
            # accept new client
            if input("Accept new client? [y/n] ").lower() == 'n':
                break
            # blocking operation
            self.clientsocket, addr = self.serversocket.accept()
            logging.info(f"Connection from {addr}")
            while True:
                data = self.clientsocket.recv(1024).decode()
                if not data:
                    logging.info(f"Connection from {addr} closed...")
                    yield False, ClientDisconnected
                    break
                logging.debug(f"Received data: {data} from {addr}")
                yield True, data

    def close(self):
        # Extra cleanup
        if self.clientsocket:
            self.clientsocket.close()
        self.serversocket.close()


class GraphConnector:
    def __init__(self, graph_port=24000):
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientsocket.connect((socket.gethostname(), graph_port))

    def send(self, message):
        self.clientsocket.send(message.encode('ascii'))

    def close(self):
        self.clientsocket.close()


if __name__ == '__main__':
    def read_sim_file():
        for line in open('data/sim_8_4_1_20221105.txt', 'r'):
            yield line

    connector = GraphConnector()

    for message in read_sim_file():
        connector.send(message)
        sleep(1 / 30.0)

    connector.close()
