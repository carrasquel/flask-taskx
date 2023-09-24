# flask-taskx
Flask-TaskX is an extension for [Flask](https://flask.palletsprojects.com/) that adds the capability of running tasks within the context of your Flask applications. If you are familiar with Flask, Flask-TaskX should be easy to pick up. It provides a coherent collection of decorators and tools to define and execute asynchronous tasks.

# Installation

You can install Flask-TaskX with pip:

```
$ pip install flask-taskx
```

or with easy_install:

```
$ easy_install flask-taskx
```

# Quick start

With Flask-TaskX, you define the task worker by instantiating a `BackgroundTaskWorker` and with this instance define all tasks to be executed later in the background.

```python
from flask import Flask
from flask_taskx import BackgroundTaskWorker

app = Flask(__name__)
task_worker = BackgroundTaskWorker(app)


@task_worker.define_task
def email_task(**kwargs):

    response = send_message(**kwargs)
    return response


@app.route('/email_send')
def email_send():
   email_task.apply(email="test@test.com")

task_worker.start()
app.run()
```

# Documentation

The documentation is hosted on [Read the Docs](http://flask-taskx.readthedocs.io/en/latest/)