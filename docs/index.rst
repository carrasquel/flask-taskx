Flask-TaskX
======================================

.. module:: flask_taskx

In the modern era, a recurrent feature required in a web application is the ability to 
execute non-blocking and asynchronous tasks.

The **Flask-TaskX** extension provides a simple interface to set up task functions 
within your `Flask`_ application and scheduled them for immediate or later execution.

Links
-----

* `documentation <http://packages.python.org/Flask-TaskX/>`_
* `source <http://github.com/carrasquel/flask-taskx>`_
* :doc:`changelog </changelog>`

.. contents:: Table of Contents
    :depth: 3

Installing **Flask-TaskX**
--------------------------

Install with **pip** and **easy_install**::

    pip install Flask-TaskX

or download the latest version from version control::

    git clone https://github.com/carrasquel/flask-taskx.git
    cd flask-taskx
    python setup.py install

If you are using **virtualenv**, it is assumed that you are installing ``flask-taskx``
in the same virtualenv as your Flask application(s).

How does **Flask-TaskX** work?
------------------------------

**Flask-TaskX** uses the **APScheduler** library as jobs execution engine, this execution 
that runs the jobs is called **worker** and it manages the execution of scheduled tasks.
In the context of **Flask-TaskX** a **task** is a function that has been decorated in 
order to mark it as task.

This tasks are enqueue and executed by the worker when the scheduled time is met. 
This **queue** is a Database-Backed Queue and it could be defined in the same database 
used by the Flask application or another SQL Relational Database.

Configuring **Flask-TaskX**
---------------------------

**Flask-TaskX** is configured through the standard Flask config API. These are the available
options (each is explained later in the documentation):

* **TASKER_ENGINE** : default **'sqlalchemy'**

* **TASKER_DRIVER** : default **'sqlite'**

* **TASKER_LOOP_INTERVAL** : default **5**

* **TASKER_DEBUG** : default **app.debug**


Tasks are managed by a worker, this can be achieved with 
an instance of one of the followings, ``BackgroundTaskWorker`` 
instance or ``BlockingTaskWorker`` instance::

    from flask import Flask
    from flask_taskx import BackgroundTaskWorker

    app = Flask(__name__)
    task_worker = BackgroundTaskWorker(app)

In this case all tasks will be executed using the configuration values of the application that
was passed to the ``BackgroundTaskWorker`` class constructor.

Alternatively you can set up your ``BackgroundTaskWorker`` instance later at configuration time, using the
``init_app`` method::

    task_worker = BackgroundTaskWorker()

    app = Flask(__name__)
    task_worker.init_app(app)

In this case tasks will be executed using the configuration values from Flask's ``current_app``
context global. This is useful if you have multiple applications running in the same
process but with different configuration options.

Running **Flask-TaskX**
-----------------------

Finally, once you have configured your application, you can start your task worker::

    task_worker.start()
    app.run()


Difference between **BackgroundTaskWorker** and **BlockingTaskWorker**
----------------------------------------------------------------------

**Flask-TaskX** was designed to schedule and execute tasks within the same context
of a `Flask`_ application, this means that inside your tasks definitions, you can
invoke any function, class or method that depends and requires the application
context.

So the decision to choose the background or blocking instance will depend on your
services topology, if you are planning to run the `Flask`_ application service
in the same machine as the **Flask-TaskX** worker, the choice in this case is to use an instance
of `BackgroundTaskWorker`, this will not block the `Flask`_ application to start serving.

`Flask`_ application and `Flask-TaskX` application on the same machine::

    task_worker = BackgroudTaskWorker()

    app = Flask(__name__)
    task_worker.init_app(app)

    task_worker.start()
    app.run()

On the other hand, if you are planning to run the `Flask`_ application service
in a different machine than the **Flask-TaskX** worker, the choice in this case is to use an instance
of ``BlockingTaskWorker``, this will block the `Flask`_ application to start serving.

`Flask`_ application machine::

    task_worker = BlockingTaskWorker()

    app = Flask(__name__)
    task_worker.init_app(app)

    app.run()

**Flask-TaskX** worker machine::

    task_worker = BlockingTaskWorker()

    app = Flask(__name__)
    task_worker.init_app(app)

    task_worker.start()

One machine must execute the application service and the other one the task worker.

Defining tasks
--------------

Tasks are functions to be registered for later execution.

To define a task we have to use the decorator method ``define_task`` from a task worker::

    @task_worker.define_task
    def email_task(**kwargs):

        msg = send_message(**kwargs)

This will turn the same function into a appliable function, then you can import this function 
into another module an schedule the task for inmediate execution by the worker.

Executing tasks
---------------

Once a task is defined it can be executed from anywhere in a `Flask` application using the ``apply`` method
from the decorated function::

    from tasks import email_task
    email_task.apply(**payload)

This call will enqueue a task and it will be executed by the task worker as soon as possible.

Defining cron tasks
-------------------

This is the most powerful of the built-in triggers in `Flask-TaskX`. 
You can specify a variety of different expressions on each field, 
and when determining the next execution time, it finds the earliest 
possible time that satisfies the conditions in every field. 
This behavior resembles the “Cron” utility found in most 
UNIX-like operating systems.::

    from datetime import date

    @task_worker.define_cron_task(month='6-8,11-12', day='3rd fri', hour='0-3')
    def email_task(**kwargs):

        msg = send_message(**kwargs)

Defining date tasks
-------------------

This is the simplest possible method of scheduling a task. It schedules a task to be 
executed once at the specified time. It is `Flask-TaskX` equivalent to the UNIX “at” command.

The ``run_date`` can be given either as a date/datetime object or text (in the ISO 8601 format).::

    from datetime import date

    @task_worker.define_date_task(run_date=date(2009, 11, 6), args=['email@email.com'])
    def email_task(**kwargs):

        msg = send_message(**kwargs)

Queues available in **Flask-TaskX**
-----------------------------------

**Flask-TaskX** has it's own implementation of, it is a queue a Database-Backed Queue, 
this means that the Queue is implemented using a relational database, though we know this is 
an anti-pattern, we have reasons to believe that for some purposes, a queue implemented this way 
is the proper approach to enqueue asynchronous tasks.

Since **Flask-TaskX** was designed to be implemented in **Flask**, most likely if you 
are developing a web application you are using some Relational Database(SQL), by default 
**Flask-TaskX** uses **sqlalchemy** as the database connection engine and **sqlite** as the 
SQL flavour as driver. But you can change this by specifying the configurations parameters.

If **sqlalchemy** is used the connection address is extracted from the same **Flask** 
database configuration value which is the **SQLALCHEMY_DATABASE_URI** setting. Once a task 
worker have started, the queue is defined in this same database as a custom table to 
save and manage the state of each task.

Running **Flask-TaskX** from CLI
--------------------------------

You can execute the task worker from the command line using the ``taskx`` command::

    taskx run

This will try to find a Flask application instance the same way the command ``flask run`` 
does it, using the **FLASK_APP** environment variable or inside a ``app.py`` python module. 
If a task worker has been appropriately instantiated and configured in the codebase, 
the task worker will be found and started.

API
---

.. module:: flask_taskx

.. autoclass:: BackgroundTaskWorker
   :members: init_app

.. autoclass:: BlockingTaskWorker
   :members: init_app

.. autoclass:: BaseTaskWorker
   :members: define_task

.. autoclass:: BaseTaskWorker
   :members: define_cron_task

.. autoclass:: BaseTaskWorker
   :members: define_date_task

.. autoclass:: BaseTask
   :members: apply

.. _Flask: https://flask.pocoo.org
.. _GitHub: https://github.com/carrasquel/flask-taskx
.. _Redis: https://redis.io/
.. _RabbitMQ: https://www.rabbitmq.com/