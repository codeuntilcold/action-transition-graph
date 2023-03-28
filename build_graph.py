import numpy as np
import pandas as pd
import random
# import matplotlib.pyplot as plt
# from graphviz import Digraph

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
                    noise = random.randint(0, 19)
                    if noise != 0:
                        file.write("%d %f\n" % (action, random.uniform(0.5, 1.0)))
                    else:
                        random_content = "%d %f\n" % (random.randint(0, 10),
                                                      random.uniform(0.3, 0.4))
                        file.write(random_content)




if __name__ == '__main__':
    get_actions()
    # get_transitional_prob()
