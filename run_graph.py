from time import time
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

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
SIMULATE_FILE_NAME = 'sim_8_4_1_20221105.txt'

G = nx.from_pandas_edgelist(pd.read_csv('trans.txt', sep=' '), 
                            source='from', target='to', edge_attr='prob', 
                            create_using=nx.DiGraph())

# Set the initial state
current_state = None

def read_sim_file():
    for frame, line in enumerate(open(SIMULATE_FILE_NAME, 'r')):
        ele = line.split()
        label, confidence = ele[0], float(ele[1])
        yield frame, label, confidence
simulate_action_stream = read_sim_file()

# Define a function to update the state based on user input
def update_state():
    global current_state
    global simulate_action_stream

    try:
        frame, input_str, confidence = next(simulate_action_stream)
    except StopIteration:
        return False

    if frame == 0:
        print("="*50)
        print(f"\tVideo ID: {SIMULATE_FILE_NAME}")
        print("="*50)

    if input_str == "q":
        return False

    new_state = int(input_str)
    trans_prob = G.get_edge_data(current_state, new_state, 
                                 { 'prob': EDGE_NOT_EXIST })['prob']

    trans_prob *= confidence

    if current_state is None:
        print(f"\t      [{new_state}] {ACTIONS[new_state]} 💵")
        current_state = new_state
    elif current_state == new_state:
        pass
    elif trans_prob > MIN_TRANS_PROB:
        print(f"({trans_prob:3f}) ➡️  [{new_state}] {ACTIONS[new_state]} 💵")
        current_state = new_state
    elif trans_prob <= MIN_TRANS_PROB:
        print(f"({trans_prob:3f}) ➡️  [{new_state}] {ACTIONS[new_state]}")
        # current_state = new_state
        pass
    else:
        print("Invalid input.")
        return False
    
    return True

def main():
    st = time()

    while update_state():
        pass
    #     edges,weights = zip(*nx.get_edge_attributes(G,'prob').items())
    #     plt.clf()
    #     pos = nx.spring_layout(G, seed=1050)
    #     nx.draw(G, pos, 
    #             node_color=["r" if n == current_state else "w" for n in G.nodes()], 
    #             width=2, 
    #             with_labels=True,
    #             edgelist=edges,
    #             edge_color=weights, 
    #             edge_cmap=plt.cm.Blues)
    #     plt.pause(1 / 64)
    # plt.close()

    et = time()
    print(f"=== Total elapsed time is {et - st}")

if __name__ == "__main__":
    main()
