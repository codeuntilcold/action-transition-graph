import numpy as np
import pandas as pd
import random
import networkx as nx
import matplotlib.pyplot as plt

def parse_line(str):
    elems = str.split(" ")
    return elems[0], elems[-2], elems[-1].strip()

def get_transitional_prob():
    with open('all_labels.txt') as f:
        line = f.readlines()
        total_samples = len(line)
        mapping = []
        for i in range(total_samples - 1):
            id_1, _, action_1 = parse_line(line[i])
            id_2, _, action_2 = parse_line(line[i + 1])
            if id_1 == id_2:
                mapping.append((int(action_1), int(action_2)))

        unique_mapping = np.unique(mapping, return_counts=True, axis=0)

        df = pd.DataFrame.from_records(unique_mapping[0], columns=['from', 'to'])
        df['freq'] = unique_mapping[1]
        # print(df)
        
        
        sum_per_action = df.groupby(['from'])['freq'].sum()

        # # visualize
        # for row in df.itertuples():
        #     print(row[1], row[2], "|"*int(row[3]))
        
        print(' '.join(df.columns.values), 'prob')
        for row in df.itertuples():
            print(row[1], row[2], row[3], '%f' % (row[3] / sum_per_action[row[1]]))

def get_actions():
    mapping = []
    with open('all_labels.txt') as f:
        for line in f.readlines():
            id, dur, action = parse_line(line)
            mapping.append((id, int(action), int(dur)))
    # df = pd.DataFrame.from_records(mapping, columns=['id', 'action', 'dur'])
    # bx = df.boxplot(by=['action'])
    # plt.show()

    with open('sim_8_4_1_20221105.txt', 'w') as file:
        for id, action, dur in mapping:
            if id == '8_4_1_20221105':
                for _ in range(dur):
                    noise = 1# random.randint(0, 19)
                    if noise != 0:
                        file.write("%d %f\n" % (action, random.uniform(0.5, 1.0)))
                    else:
                        random_content = "%d %f\n" % (random.randint(0, 10),
                                                      random.uniform(0.3, 0.4))
                        file.write(random_content)


def draw():
    ACTIONS = {
        0: "open phone box",
        1: "take out phone",
        2: "take out instruction paper",
        3: "take out earphones",
        4: "take out charger",
        5: "put in charger",
        6: "put in earphones",
        7: "put in instruction paper",
        8: "inspect phone",
        9: "put in phone",
        10: "close phone box"
    }
    
    trans = pd.read_csv('trans.txt', sep=' ')
    G = nx.from_pandas_edgelist(trans.sort_values(by=['prob']), 
                                source='from', target='to', edge_attr='prob', 
                                create_using=nx.DiGraph())
    edges,weights = zip(*nx.get_edge_attributes(G,'prob').items())
    pos = {
        0: (0, 0),
        1: (1, 0),
        2: (2, 0),
        3: (3, 0),
        4: (4, 0),
        5: (5, -1),
        6: (6, -1),
        7: (7, -1),
        8: (8, -1),
        9: (9, -1),
        10: (10, -1)
    }
    nx.draw_networkx_nodes(G, pos=pos, node_color='w')
    nx.draw_networkx_edges(G, pos=pos, width=5, 
                                  edge_color=weights,
                                  edge_cmap=plt.cm.Blues,
                                  connectionstyle="arc3,rad=0.5")
    nx.draw_networkx_labels(G, pos=pos)
    # nx.draw(G, pos,
    #         node_color=[ "w" for n in G.nodes()], 
    #         labels=ACTIONS,
    #         width=2, 
    #         with_labels=True,
    #         edgelist=edges,
    #         edge_color=weights, 
    #         edge_cmap=plt.cm.Blues
    #         )
    plt.show()                         



if __name__ == '__main__':
    # get_actions()
    # get_transitional_prob()
    draw()
