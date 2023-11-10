

class AMQPWorker:

    def __init__(self, *args, **kwargs):
        pass

    def init_app(self, app):
        pass

    def initialize_amqp(self, *args, **kwargs):
        pass

    def create_queues(self, *args, **kwargs):
        pass

    def task_consumer(self, *args, **kwargs):
        pass

    def task_producer(self, *args, **kwargs):
        pass

    def append_task(self, task, payload):
        self._db.append_task(task, payload)
    
    def start(self):
        pass