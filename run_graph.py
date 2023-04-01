import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import socket
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt="%y-%m-%d %H:%M:%S")

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
        self.previous_conf = 0.01

    def update_state(self):
        try:
            new_state, confidence = next(self.action_stream)
            new_state, confidence = int(new_state), float(confidence)
        except ValueError:
            logging.info("=== END OF ACTION ===")
            self.current_state = None
            return True
        except Exception:
            logging.error("Stop updating state...")
            return False
        
        if new_state not in range(len(ACTIONS)):
            logging.info(f"Ignore invalid state {new_state}")
            return True

        trans_prob = G.get_edge_data(self.current_state, new_state, 
                                    { 'prob': EDGE_NOT_EXIST })['prob']
        trans_prob *= self.previous_conf

        if self.current_state != new_state:
            if self.current_state is None:
                logging.info("=== START NEW ACTION ===")
                logging.info(f"\t\t[{new_state}] {ACTIONS[new_state]}")
                self.current_state = new_state
            elif trans_prob > MIN_TRANS_PROB:
                logging.info(f"({trans_prob:3f})\t[{new_state}] {ACTIONS[new_state]}")
                self.current_state = new_state
            else:
                RED='\033[0;31m'
                NC='\033[0m' # No Color
                logging.info(f"{RED}({trans_prob:3f})\t[{new_state}] {ACTIONS[new_state]}{NC}")
                # self.current_state = new_state
                # pass

        self.previous_conf = confidence
        return True


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
            
            logging.info("Waiting for new client")

            # blocking operation
            self.clientsocket, addr = self.serversocket.accept()
            logging.info(f"Connection from {addr}")

            while True:
                data = self.clientsocket.recv(1024).decode()
                if not data:
                    yield "invalid data"
                    break
                logging.debug(f"Received data: {data} from {addr}")
                yield data.split()

    def close(self):
        # Extra cleanup
        if self.clientsocket:
            self.clientsocket.close()
        self.serversocket.close()


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
    connector = ModelConnector()
    bone = TransitionGraph(connector.get_stream_gen())

    while bone.update_state():
        # visualize transition graph, very slow
        if False:
            edges,weights = zip(*nx.get_edge_attributes(G,'prob').items())
            plt.clf()
            pos = nx.spring_layout(G, seed=42)
            nx.draw(G, pos, 
                    node_color=[
                        "r" if n == bone.current_state else "w" for n in G.nodes()], 
                    width=2, 
                    with_labels=True,
                    edgelist=edges,
                    edge_color=weights, 
                    edge_cmap=plt.cm.Blues)
            plt.pause(1 / 64)

    connector.close()

if __name__ == "__main__":
    main()
