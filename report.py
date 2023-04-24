import json
import os
from datetime import datetime
import random
from kafka_connector import KafkaConnector


class ActionReport:
    def __init__(self, action_id, starttime, endtime=-1, is_mistake=False,
                 process_id='default-process-id'):
        self.worker_id = 0
        self.action_id = action_id
        self.starttime = starttime
        self.duration = endtime - starttime
        self.is_mistake = is_mistake
        self.process_id = process_id

    def set_endtime(self, endtime):
        self.duration = endtime - self.starttime
        return self

    def toggle_mistake(self):
        self.is_mistake = not self.is_mistake
        return self

    def to_dict(self):
        return {
            "worker_id": self.worker_id,
            "process_id": self.process_id,
            "action_id": self.action_id,
            "starttime": self.starttime,
            "starttime_human": datetime.fromtimestamp(self.starttime)
                                       .strftime('%Y-%m-%d %H:%M:%S'),
            "duration": self.duration,
            "is_mistake": self.is_mistake
        }


def gen_random_id():
    return '-'.join([str(random.randrange(1000, 9999)) for _ in range(3)])


class AssemblyReport:
    def __init__(self, save_as_file=True):
        self.id = gen_random_id()
        self.report: list[ActionReport] = list()
        if not save_as_file:
            self.kafka = KafkaConnector(topic='worker-0')

    def add(self, action_id, starttime):
        self.report.append(ActionReport(
            action_id, starttime, process_id=self.id))

    def last(self) -> ActionReport:
        # TODO: Will panic if list has length 0
        return self.report[-1]

    def save(self):
        os.makedirs("report", exist_ok=True)
        with open(f"report/{int(self.report[0].starttime)}.txt", 'w') as f:
            f.write(json.dumps(self.to_dict(), indent=2))

    def send(self):
        for report in self.report:
            self.kafka.send(report.to_dict())

    def clear(self):
        self.id = gen_random_id()
        self.report = list()

    def to_dict(self):
        return {
            "report": [act.to_dict() for act in self.report]
        }


if __name__ == '__main__':
    report = AssemblyReport()
    print(report.id)
