import json
import os


class ActionReport:
    def __init__(self, action_id, starttime, endtime=-1, is_mistake=False):
        self.worker_id = 0
        self.action_id = action_id
        self.starttime = starttime
        self.duration = endtime - starttime
        self.is_mistake = is_mistake

    def set_endtime(self, endtime):
        self.duration = endtime - self.starttime
        return self

    def toggle_mistake(self):
        self.is_mistake = not self.is_mistake
        return self

    def to_dict(self):
        return {
            "worker_id": self.worker_id,
            "action_id": self.action_id,
            "starttime": self.starttime,
            "duration": self.duration,
            "is_mistake": self.is_mistake
        }


class AssemblyReport:
    def __init__(self):
        self.id = 0
        self.report: list[ActionReport] = list()

    def add(self, action):
        self.report.append(action)

    def last(self) -> ActionReport:
        # TODO: Will panic if list has length 0
        return self.report[-1]

    def save(self):
        os.makedirs("report", exist_ok=True)
        with open(f"report/{int(self.report[0].starttime)}.txt", 'w') as f:
            f.write(json.dumps(self.to_dict(), indent=2))

    def clear(self):
        self.report = list()

    def to_dict(self):
        return {
            "id": self.id,
            "report": [act.to_dict() for act in self.report]
        }
