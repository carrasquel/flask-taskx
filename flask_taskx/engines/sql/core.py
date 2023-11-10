from peewee import SqliteDatabase
from playhouse.db_url import connect

TASKER_DATABASE_URI = "TASKER_DATABASE_URI"
TASKER_DRIVER = "TASKER_DRIVER"
TASKER_INTERVAL_TIME = "TASKER_INTERVAL_TIME"

class NoneDatabaseURIException(Exception):
    "Raised when there is not available database uri defined"
    
    def __init__(self, message="Database uri not defined in Flask Config"):
        self.message = message
        super().__init__(self.message)


class SQLWorker:

    def __init__(self, *args, **kwargs):
        self._app = None
        self._db = None
        self.config = dict()

    def init_app(self, app):
        self._app = app
        self.initialize_db()
        self.create_db()

        if TASKER_INTERVAL_TIME in self._app.config:
            interval_time = int(self._app.config[TASKER_INTERVAL_TIME])
            self.set_interval_time(interval_time)

    def set_database_uri(self, database_uri):
        self.config[TASKER_DATABASE_URI] = database_uri

    def set_driver(self, driver):
        self.config[TASKER_DRIVER] = driver

    def initialize_db(self, *args, **kwargs):
        if TASKER_DATABASE_URI in self._app.config:
            self.set_database_uri(self._app.config[TASKER_DATABASE_URI])

        if TASKER_DRIVER in self._app.config:
            self.set_driver(self._app.config[TASKER_DRIVER])

    def create_db(self, *args, **kwargs):
        driver = self.config[TASKER_DRIVER]
        database_uri = self.config[TASKER_DATABASE_URI]

        if not database_uri:
            try:
                database_uri = self._app.config["SQLALCHEMY_DATABASE_URI"]
            except:
                raise NoneDatabaseURIException

        if driver == "postgres":
            from engines.sql import postgres as database

            db = connect(database_uri)

        elif driver == "mysql":
            from engines.sql import mysql as database

            database_uri = database_uri.replace("mysql+pymysql", "mysql")
            db = connect(database_uri)

        elif driver == "sqlite":
            from engines.sql import sqlite as database

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
                },
            )

        self._db = database
        self._db.proxy.initialize(db)
        self._database = db

    def create_tables(self, *args, **kwargs):
        self._database.create_tables([self._db.Schedule])

    def task_consumer(self, *args, **kwargs):
        pass

    def task_producer(self, *args, **kwargs):
        pass

    def start(self):
        self.create_tables()
