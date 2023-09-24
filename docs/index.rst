Flask-TaskX
======================================

.. module:: flask_taskx

In the modern era, a recurrent feature required in a web application is the ability to 
execute non-blocking and asynchronous tasks.

The **Flask-TaskX** extension provides a simple interface to set up task functions 
within your `Flask`_ application and scheduled them for later execution

Links
-----

* `documentation <http://packages.python.org/Flask-TaskX/>`_
* `source <http://github.com/carrasquel/flask-taskx>`_
* :doc:`changelog </changelog>`

Installing Flask-TaskX
---------------------------

Install with **pip** and **easy_install**::

    pip install Flask-TaskX

or download the latest version from version control::

    git clone https://github.com/carrasquel/flask-taskx.git
    cd flask-taskx
    python setup.py install

If you are using **virtualenv**, it is assumed that you are installing flask-taskx
in the same virtualenv as your Flask application(s).

Configuring Flask-TaskX
----------------------------

**Flask-TaskX** is configured through the standard Flask config API. These are the available
options (each is explained later in the documentation):

* **TASKER_ENGINE** : default **'sqlalchemy'**

* **TASKER_DRIVER** : default **'sqlite'**

* **TASKER_LOOP_INTERVAL** : default **5**

* **TASKER_DEBUG** : default **app.debug**


Tasks are managed through an instance one the followings, ``BackgroundTaskWorker`` instance or ``BlockingTaskWorker`` instance::

    from flask import Flask
    from flask_taskx import BackgroundTaskWorker

    app = Flask(__name__)
    task_worker = BackgroundTaskWorker(app)

In this case all tasks will be executed using the configuration values of the application that
was passed to the ``BackgroundTaskWorker`` class constructor.

Alternatively you can set up your ``BackgroundTaskWorker`` instance later at configuration time, using the
**init_app** method::

    task_worker = BackgroundTaskWorker()

    app = Flask(__name__)
    task_worker.init_app(app)


In this case tasks will be executed using the configuration values from Flask's ``current_app``
context global. This is useful if you have multiple applications running in the same
process but with different configuration options.

Running Flask-TaskX
------------------------

Finally, once you have configured your application, you can start your task worker::

    task_worker.start()
    app.run()



Difference between BackgroundTaskWorker and BlockingTaskWorker
--------------------------------------------------------------

**Flask-TaskX** was designed to schedule and execute tasks within the same context
of a `Flask`_ application, this means that inside your tasks definitions, you can
invoke any function, class or method that depends and requires the application
context.

So the decision to choose the background or blocking instance will depend on your
services execution topology, if you are planning to run the `Flask`_ application services
in the same machine as the `Flask-TaskWorker`, the choice in this case is to use an instance
of `BackgroundTaskWorker`, this will not block the `Flask`_ application to start serving.

`Flask`_ application and `Flask-TaskX` application machine::

    task_worker = BackgroudTaskWorker()

    app = Flask(__name__)
    task_worker.init_app(app)

    task_worker.start()
    app.run()

On the other hand, if you are planning to run the `Flask`_ application services
in a different machine than `Flask-TaskX`, the choice in this case is to use an instance
of `BlockingTaskWorker`, this will block the `Flask`_ application to start serving.

`Flask`_ application machine::

    task_worker = BlockingTaskWorker()

    app = Flask(__name__)
    task_worker.init_app(app)

    app.run()

`Flask-TaskX` application machine::

    task_worker = BlockingTaskWorker()

    app = Flask(__name__)
    task_worker.init_app(app)

    task_worker.start()

One machine must execute the application service and the other one the task worker.

Defining tasks
--------------

Tasks are functions to be registered for later execution.

To define a task we have to use the decorator method `define_task` from a task worker::

    @task_worker.define_task
    def email_task(**kwargs):

        msg = send_message(**kwargs)

Execute tasks
-------------

Once a task is dfined in can be executed from a `Flask` application using the `apply` method
from the decorated function::

    from tasks import email_task
    email_task.apply(**payload)

In this task will be executed by the task worker as soon as possible.

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

.. _Flask: http://flask.pocoo.org
.. _GitHub: http://github.com/carrasquel/flask-taskx