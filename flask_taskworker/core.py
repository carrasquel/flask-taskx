# encoding: utf-8
# app/extensions/scheduler/worker.py

import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from peewee import MySQLDatabase, PostgresqlDatabase, SqliteDatabase
from playhouse.db_url import connect

TASKER_ENGINE = "TASKER_ENGINE"
TASKER_DRIVER = "TASKER_DRIVER"
TASKER_INTERVAL_TIME = "TASKER_INTERVAL_TIME"


class _TaskManager:
    def __init__(self):
        self.tasks = {}
        self.crons = []
        self.dates = []

    def append(self, f, name):
        self.tasks[name] = f

    def run(self, name, payload):
        f = self.tasks[name]
        result = f(**payload)

        return result

    def add_cron(self, f, *args, **kwargs):
        self.crons.append((f, (args, kwargs,),))

    def add_date(self, f, *args, **kwargs):
        self.dates.append((f, (args, kwargs,),))


class BaseTask:
    def __init__(self, name, scheduler):

        self._name = name
        self._scheduler = scheduler

    def apply(self, payload):
        """Function to schedule a deferred function execution in the tasks scheduler.

        :param payload: a dictionary holding the param names as key and param values as value.
        """

        self._scheduler._append_task(self._name, payload)


class BaseTaskWorker():
    def __init__(self):
        self._manager = _TaskManager()
        self._handler = None
        self._app = None
        self._db = None
        self.config = {
            TASKER_ENGINE: "",
            TASKER_DRIVER: "",
            TASKER_INTERVAL_TIME: 5,
        }

    def init_app(self, app):
        self._app = app
        self.initialize_db()
        self.create_db()

        if TASKER_INTERVAL_TIME in self._app.config:
            interval_time = int(self._app.config[TASKER_INTERVAL_TIME])
            self.set_interval_time(interval_time)

    def run_job(self, job, payload):
        result = self._manager.run(job, payload)

        return result
    
    def set_interval_time(self, time):
        self.config[TASKER_INTERVAL_TIME] = time
    
    def set_engine(self, engine):
        self.config[TASKER_ENGINE] = engine

    def set_driver(self, driver):
        self.config[TASKER_DRIVER] = driver

    def _append_task(self, task, payload):
        self._db.append_task(task, payload)

    def _define_task(self, name):
        def outter(f):
            def inner():
                self._manager.append(f, name)
                return f

            return inner()

        return outter

    def define_task(self, f):
        """Decorator function to define tasks within the context of Flask.

        :param f: a function to be decorated, this function will be used
        for tasks execution.
        """

        def inner():
            name = "{module}.{name}".format(module=f.__module__, name=f.__name__)
            task = BaseTask(name, self)
            self._manager.append(f, name)
            return task

        return inner()

    def get_crons(self):

        return self._manager.crons
    
    def get_dates(self):

        return self._manager.dates
    
    def define_cron_task(self, *args, **kwargs):

        def inner(f):
            self._manager.add_cron(f, *args, **kwargs)
            return f

        return inner()

    def define_date_task(self, *args, **kwargs):

        def inner(f):
            self._manager.add_date(f, *args, **kwargs)
            return f

        return inner()

    def create_db(self):
        engine = self.config[TASKER_ENGINE]
        driver = self.config[TASKER_DRIVER]
        database_uri = ""

        if not engine == "SQLALCHEMY":
            return
        else:
            database_uri = self._app.config["SQLALCHEMY_DATABASE_URI"]
        
        if driver == "postgres":
            from .sql import postgres as database
            db = connect(database_uri)

        elif driver == "mysql":
            from .sql import mysql as database
            database_uri = database_uri.replace("mysql+pymysql", "mysql")
            db = connect(database_uri)

        elif driver == "sqlite":
            from .sql import sqlite as database
            database_uri = database_uri.replace("\\", "/")
            database_uri = database_uri.replace("sqlite:///", "")
            db = SqliteDatabase(
                database_uri,
                pragmas={
                    "journal_mode": "wal",
                    "journal_size_limit": 1024,
                    "cache_size": -1024 * 64,  # 64MB
                    "foreign_keys": 1,
                    "ignore_check_constraints": 0,
                    "synchronous": 0,
                }
            )

        self._db = database
        self._db.proxy.initialize(db)
        self._database = db

    def create_tables(self):
            
        self._database.create_tables([self._db.Schedule])

    def date_executor(self, f):

        def wrapper():
            now = datetime.datetime.utcnow()
            with self._app.app_context():

                f()

        return wrapper

    def cron_executor(self, f):

        def wrapper():
            now = datetime.datetime.utcnow()
            output = None
            fail_message = None
            with self._app.app_context():

                try:
                    output = f()
                except Exception as e:
                    fail_message = str(e)

            later = datetime.datetime.utcnow()

            name = f.__name__
            self._db.save_task(
                name,
                now,
                later,
                output=output,
                fail_message=fail_message
            )

        return wrapper

    def task_executor(self):

        with self._app.app_context():
            now = datetime.datetime.utcnow()
            schedule = self._db.pop_task()

            if not schedule:
                return

            if now < schedule.scheduled_date:
                return
            try:
                automation = schedule.automation
                payload = schedule.payload

                result = self.run_job(automation, payload)
                self._db.complete_task(schedule, result)
            except Exception as e:
                self._db.pushback_task(schedule, str(e))

    def initialize_db(self,):
        if TASKER_ENGINE in self._app.config:
            self.set_engine(self._app.config[TASKER_ENGINE])
        
        if TASKER_DRIVER in self._app.config:
            self.set_driver(self._app.config[TASKER_DRIVER])

    def register_crons(self):

        crons = self.get_crons()

        if not crons:
            return
        
        for cron in crons:
            f, params = cron
            args, kwargs = params

            f = self.cron_executor(f)
            self.add_job(f, 'cron', *args, **kwargs)

    def register_dates(self):

        dates = self.get_dates()

        if not dates:
            return
        
        for date in dates:
            f, params = date
            args, kwargs = params

            f = self.date_executor(f)
            self.add_job(f, 'date', *args, **kwargs)

    def start(self):
        
        self.create_tables()
        interval_time = self.config[TASKER_INTERVAL_TIME]
        self.add_job(self.task_executor, "interval", seconds=interval_time)
        self.register_crons()
        self.register_dates()


class BackgroundTaskWorker(BaseTaskWorker, BackgroundScheduler):
    """Manages scheduled background tasks

    :param app: Flask instance
    """


    def __init__(self, app=None):

        BackgroundScheduler.__init__(self)
        BaseTaskWorker.__init__(self)

        if app:
            BaseTaskWorker.init_app(self, app)

    def init_app(self, app):
        """Initializes your tasks settings from the application settings.

        You can use this if you want to set up your BackgroundTaskWorker instance
        at configuration time.

        :param app: Flask application instance
        """

        BaseTaskWorker.init_app(self, app)

    def start(self):
        BaseTaskWorker.start(self)
        BackgroundScheduler.start(self)


class BlockingTaskWorker(BaseTaskWorker, BlockingScheduler):
    """Manages scheduled tasks

    :param app: Flask instance
    """


    def __init__(self, app=None):

        BlockingScheduler.__init__(self)
        BaseTaskWorker.__init__(self)

        if app:
            BaseTaskWorker.init_app(self, app)

    def init_app(self, app):
        """Initializes your tasks settings from the application settings.

        You can use this if you want to set up your BlockingTaskWorker instance
        at configuration time.

        :param app: Flask application instance
        """

        BaseTaskWorker.init_app(self, app)

    def start(self):
        BaseTaskWorker.start(self)
        BlockingScheduler.start(self)
