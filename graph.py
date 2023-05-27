from dataclasses import dataclass
import pandas as pd
import statistics
from time import time
import networkx as nx
import logging

from .report import AssemblyReport

RED = '\033[0;31m'
NC = '\033[0m'
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
    "close phone box",
    "no action"
]
NO_ACTION_LABEL = len(ACTIONS) - 1
END_ACTION_LABEL = 10
EDGE_NOT_EXIST = 0.01
MIN_TRANS_PROB = 0.01
DEFAULT_CONF = 0.5


class Bucket:
    def __init__(self, stream, radius=3):
        # past         👇 current        future
        # [0    1   2   3   4   5   6   7]
        self.stream = stream
        self.radius = radius
        self.bucket = list([NO_ACTION_LABEL] * (2 * radius + 1))
        self.conf = list([DEFAULT_CONF] * (2 * radius + 1))

    def fill(self, new_data=None):
        try:
            if new_data is None:
                ok, data = next(self.stream)
            else:
                ok, data = True, new_data
            if not ok:
                raise data
            new_state, confidence = data.split()
            new_state, confidence = int(new_state), float(confidence)
        except ValueError:
            # in case state or confidence is malformed
            new_state, confidence = NO_ACTION_LABEL, DEFAULT_CONF
        except Exception as e:
            # stop iteration, keyboard interupt, etc
            raise e

        if new_state not in range(len(ACTIONS)):
            logging.warn(
                f"Invalid state {new_state}, default to [{NO_ACTION_LABEL}] {ACTIONS[NO_ACTION_LABEL]}")
            new_state = NO_ACTION_LABEL

        self.bucket = self.bucket[1:] + [new_state]
        self.conf = self.conf[1:] + [confidence]

    def get_mode(self):
        return statistics.multimode(self.bucket)[-1]

    def get_prev_conf(self):
        return self.conf[self.radius - 1]

    def get_conf(self):
        return self.conf[self.radius]

    def drip(self, new_data=None):
        try:
            self.fill(new_data)
            return self.get_mode(), self.get_prev_conf(), self.get_conf()
        except Exception as e:
            raise e

    def flush(self):
        self.bucket = [NO_ACTION_LABEL for _ in self.bucket]
        self.conf = [DEFAULT_CONF for _ in self.conf]


@dataclass
class StateResult:
    state: int
    has_changed: bool
    is_mistake: bool


class TransitionGraph:
    def __init__(self, hardcode_graph, save_report_as_files=False):
        self.current_state = NO_ACTION_LABEL
        self.report = AssemblyReport(save_as_file=save_report_as_files)

        path = 'data/trans-gt.txt' if hardcode_graph else 'data/trans.txt'
        path = __file__.replace('graph.py', 'data\\trans.txt')
        self.G = nx.from_pandas_edgelist(pd.read_csv(path, sep=' '),  # type: ignore
                                         source='from', target='to', edge_attr='prob',
                                         create_using=nx.DiGraph())

    def update_state(self, new_state: int, confidence):
        if self.current_state == new_state:
            return StateResult(self.current_state, False, False)

        trans_prob = self.G.get_edge_data(self.current_state, new_state,
                                          {'prob': EDGE_NOT_EXIST})['prob']
        trans_prob *= confidence
        current_time = time()
        state_and_label = f"[{new_state}] {ACTIONS[new_state]}"

        if self.current_state == NO_ACTION_LABEL:
            logging.info(f"Start action: {state_and_label}")
            # TODO: How to determine whether this is a mistake
            if new_state == 10:
                return StateResult(self.current_state, False, False)
            else:
                self.report.add(new_state, current_time)
                self.current_state = new_state
                return StateResult(self.current_state, True, False)

        elif new_state == NO_ACTION_LABEL:
            self.report.last().set_endtime(current_time)
            if self.current_state == END_ACTION_LABEL:
                logging.info("Stop action")
                self.reset_state()
                return StateResult(self.current_state, True, False)
            else:
                return StateResult(self.current_state, False, False)

        elif trans_prob > MIN_TRANS_PROB:
            logging.info(f"({trans_prob:3f})\t{state_and_label}")

            self.report.last().set_endtime(current_time)
            self.report.add(new_state, current_time)
            self.current_state = new_state
            return StateResult(self.current_state, True, False)

        else:
            logging.info(f"{RED}({trans_prob:3f})\t{state_and_label}{NC}")

            self.report.last().set_endtime(current_time)
            self.report.add(new_state, current_time)
            self.report.last().toggle_mistake()
            self.current_state = new_state
            return StateResult(self.current_state, True, True)


    def reset_state(self):
        self.current_state = NO_ACTION_LABEL
        self.report.save()
        self.report.clear()
