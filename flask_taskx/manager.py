# encoding: utf-8
# flask_taskx/manager.py


class TaskManager:
    def __init__(self):
        self.tasks = {} # Stores function by key-value pairs, keys as function ids and values as function objects.
        self.crons = [] # Stores cron function jobs
        self.dates = [] # Stores date function jobs

    def append(self, f, name):
        self.tasks[name] = f

    def run(self, name, payload):
        f = self.tasks[name]
        result = f(**payload)

        return result

    def add_cron(self, f, *args, **kwargs):
        self.crons.append(
            (
                f,
                (
                    args,
                    kwargs,
                ),
            )
        )

    def add_date(self, f, *args, **kwargs):
        self.dates.append(
            (
                f,
                (
                    args,
                    kwargs,
                ),
            )
        )
