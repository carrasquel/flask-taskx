# encoding: utf-8
# app/extensions/scheduler/models.py

import datetime

from peewee import Model, CharField, DateTimeField, BooleanField, IntegerField, Proxy
from playhouse.postgres_ext import JSONField

proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = proxy


class Schedule(BaseModel):
    class Meta:
        db_table = 'flask_tasker_schedule'

    automation = CharField()
    scheduled_date = DateTimeField(default=datetime.datetime.utcnow)
    completion_date = DateTimeField()

    payload = JSONField()
    output = JSONField()
    busy = BooleanField(default=False)
    done = BooleanField(default=False)
    retries = IntegerField(default=0)
    fail_message = JSONField()


def pop_task():

    with proxy.atomic() as txn:

        _query = Schedule.select().order_by(Schedule.scheduled_date.desc())
        schedule = (
            _query.where(Schedule.done == False)
            .where(Schedule.retries < 3)
            .where(Schedule.busy == False)
            .get_or_none()
        )

        if not schedule:
            return
        
        schedule.busy = True
        schedule.save()

        return schedule


def append_task(task, payload):
    with proxy.atomic() as txn:
        Schedule.create(automation=task, payload=payload)


def complete_task(schedule, result):
    with proxy.atomic() as txn:
        schedule.output = result
        schedule.done = True
        schedule.completion_date = datetime.datetime.utcnow()
        schedule.save()


def pushback_task(schedule, fail_message=None):
    with proxy.atomic() as txn:
        schedule.retries += 1
        schedule.busy = False
        schedule.fail_message = {"message": fail_message}
        schedule.save()
