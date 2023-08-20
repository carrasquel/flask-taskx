# encoding: utf-8
# app/extensions/scheduler/worker.py

import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from peewee import SqliteDatabase, PostgresqlDatabase, MySQLDatabase

FLASK_TASKER_ENGINE = "FLASK_TASKER_ENGINE"
FLASK_TASKER_DRIVER = "FLASK_TASKER_DRIVER"


class _JobsManager:
    def __init__(self):
        self.jobs = {}

    def append(self, f, name):
        self.jobs[name] = f

    def run(self, name, payload):
        f = self.jobs[name]
        result = f(**payload)

        return result


class TaskWorker(BlockingScheduler):
    def __init__(self, app):
        BlockingScheduler.__init__(self)
        self._manager = _JobsManager()
        self._handler = None
        self._app = None
        self._db = None
        self.config = {
            FLASK_TASKER_ENGINE: "",
            FLASK_TASKER_DRIVER: ""
        }

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self._app = app
        self.initialize_db()
        self.create_db()

    def run_job(self, job, payload):
        result = self._manager.run(job, payload)

        return result
    
    def set_engine(self, engine):
        self.config[FLASK_TASKER_ENGINE] = engine

    def set_driver(self, driver):
        self.config[FLASK_TASKER_DRIVER] = driver

    def append_task(self, task, payload):
        self._db.append_task(task, payload)

    def create_db(self):
        engine = self.config[FLASK_TASKER_ENGINE]
        driver = self.config[FLASK_TASKER_DRIVER]
        database_uri = ""

        if not engine == "SQLALCHEMY":
            return
        else:
            database_uri = self._app.config["SQLALCHEMY_DATABASE_URI"]
        
        if driver == "postgres":
            from .models import postgres as database
            db = PostgresqlDatabase(database_uri)

        elif driver == "mysql":
            from .models import mysql as database
            db = MySQLDatabase(database_uri)

        elif driver == "sqlite":
            from .models import sqlite as database
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

    def event_handler(self):

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

    def initialize_db(self, ):
        if FLASK_TASKER_ENGINE in self._app.config:
            self.set_engine(self._app.config[FLASK_TASKER_ENGINE])
        
        if FLASK_TASKER_DRIVER in self._app.config:
            self.set_driver(self._app.config[FLASK_TASKER_DRIVER])

    def start(self):
        
        self.create_tables()
        self.add_job(self.event_handler, "interval", seconds=5)
        BlockingScheduler.start(self)


scheduler = TaskWorker()


def define_task(name):
    def outter(f):
        def inner():
            scheduler._manager.append(f, name)
            return f

        return inner()

    return outter


def append_task(task, payload):

    scheduler.append_task(task, payload)
