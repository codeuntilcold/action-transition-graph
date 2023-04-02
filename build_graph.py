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

        df = pd.DataFrame.from_records(
            unique_mapping[0], columns=['from', 'to'])
        df['freq'] = unique_mapping[1]
        # print(df)

        sum_per_action = df.groupby(['from'])['freq'].sum()

        # # visualize
        # for row in df.itertuples():
        #     print(row[1], row[2], "|"*int(row[3]))

        print(' '.join(df.columns.values), 'prob')
        for row in df.itertuples():
            print(row[1], row[2], row[3], '%f' %
                  (row[3] / sum_per_action[row[1]]))


def write_simulated_action_stream():
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
                    noise = random.randint(0, 5)
                    if noise != 0:
                        file.write("%d %f\n" %
                                   (action, random.uniform(0.5, 1.0)))
                    else:
                        random_content = "%d %f\n" % (random.randint(action, action + 5) if action < 5 else random.randint(action - 5, action),
                                                      random.uniform(0.3, 0.4))
                        file.write(random_content)


def draw_transition_graph():
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
    edges, weights = zip(*nx.get_edge_attributes(G, 'prob').items())
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
    edge_weights = [G[u][v]['prob'] for u, v in G.edges()]
    max_weight = max(edge_weights)
    line_widths = [5 * (float(weight) / max_weight) for weight in edge_weights]
    edge_width_dict = dict(zip(G.edges(), line_widths))

    nx.draw_networkx_nodes(G, pos=pos, node_color='w')
    nx.draw_networkx_edges(G, pos, width=line_widths,
                           edge_color='b', edge_cmap=plt.cm.Blues,
                           alpha=0.7, edge_vmin=min(line_widths),
                           edge_vmax=max(line_widths),
                           connectionstyle="arc3,rad=0.5")

    # nx.draw_networkx_edges(G, pos=pos, width=5,
    #                               edge_color=weights,
    #                               edge_cmap=plt.cm.Blues,
    #                               connectionstyle="arc3,rad=0.5")
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


def plot_smoothed_labels():
    smoothed = []
    with open("smoothed_labels.txt", "r") as f:
        for line in f:
            smoothed.append(int(line.strip()))
    raw = []
    with open("sim_8_4_1_20221105.txt", "r") as f:
        for line in f:
            raw.append(int(line.strip().split()[0]))
    raw = raw[:-2]

    x = list(range(len(smoothed)))
    plt.plot(x, smoothed, 'b', linewidth=3, label='smoothed')
    plt.plot(x, raw, '#00ff00', label='raw (simulated)')

    # Add a legend
    plt.legend()

    # Add axis labels and title
    plt.xlabel('frame (30fps)')
    plt.ylabel('label')
    plt.title('Simulated noisy raw frames vs. smoothed frames')

    # Show the plot
    plt.show()


if __name__ == '__main__':
    what = input("Choose what function to run pls: ")
    if what == '1': write_simulated_action_stream()
    elif what == '2': get_transitional_prob()
    elif what == '3': draw_transition_graph()
    else: plot_smoothed_labels()
