from time import time
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import socket
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s')

ACTIONS = [
    "open phone box",
    "take out phone",
    "take out instruction paper",
    "take out earphones",
    "take out charger",
    "put in charger",
    "put in earphones",
    "put in instruction paper",
    "inspect phone",
    "put in phone",
    "close phone box"
]

EDGE_NOT_EXIST = 0.01
MIN_TRANS_PROB = 0.05

G = nx.from_pandas_edgelist(pd.read_csv('trans.txt', sep=' '), 
                            source='from', target='to', edge_attr='prob', 
                            create_using=nx.DiGraph())



class TransitionGraph:
    def __init__(self, stream):
        self.action_stream = stream
        self.current_state = None

    def update_state(self):
        try:
            new_state, confidence = next(self.action_stream)
            new_state, confidence = int(new_state), float(confidence)
        except StopIteration:
            return False
        except Exception:
            logging.error("Invalid value, stopping stream...", exc_info=True)
            return False

        trans_prob = G.get_edge_data(self.current_state, new_state, 
                                    { 'prob': EDGE_NOT_EXIST })['prob']
        trans_prob *= confidence

        if self.current_state is None:
            logging.info(f"\t\t[{new_state}] {ACTIONS[new_state]} 💵")
            self.current_state = new_state
        elif self.current_state == new_state:
            pass
        elif trans_prob > MIN_TRANS_PROB:
            logging.info(f"({trans_prob:3f}) ➡️  [{new_state}] {ACTIONS[new_state]} 💵")
            self.current_state = new_state
        elif trans_prob <= MIN_TRANS_PROB:
            # logging.info(f"({trans_prob:3f}) ➡️  [{new_state}] {ACTIONS[new_state]}")
            # self.current_state = new_state
            pass
        else:
            logging.error("Invalid input.")
        
        return True


def notify():
    pass
    # score at time t+
    # = 0 if an action is occuring
    # = 1 * A if it is transitioning
    # = -1 * A if both is starting/ending

    # A
    # = C(label at t+, missing action between t and t+)
    # = cost of performing the missing action after later action


def main():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 24000
    serversocket.bind((host, port))
    serversocket.listen(5)

    # Wait for a client connection
    clientsocket, addr = serversocket.accept()
    logging.info(f"Connection from {addr} has been established!")

    def gen():
        while True:
            # Receive data from the client
            data = clientsocket.recv(1024).decode()
            if not data:
                break
            logging.debug(f"Received data: {data} from {addr}")
            yield data.split()

    st = time()

    bone = TransitionGraph(gen())

    while bone.update_state():    
        if False:
            edges,weights = zip(*nx.get_edge_attributes(G,'prob').items())
            plt.clf()
            pos = nx.spring_layout(G, seed=42)
            nx.draw(G, pos, 
                    node_color=["r" if n == current_state else "w" for n in G.nodes()], 
                    width=2, 
                    with_labels=True,
                    edgelist=edges,
                    edge_color=weights, 
                    edge_cmap=plt.cm.Blues)
            plt.pause(1 / 64)
    plt.close()

    et = time()

    clientsocket.close()

    logging.info(f"=== Total elapsed time is {et - st:3f}")

if __name__ == "__main__":
    main()
