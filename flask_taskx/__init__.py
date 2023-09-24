# -*- coding: utf-8 -*-
"""
    flaskext.taskx
    ~~~~~~~~~~~~~

    Flask extension for creating and running tasks.

    :copyright: (c) 2023 by Nelson Carrasquel.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import with_statement

__version__ = "0.0.1"


from .core import (
    BackgroundTaskWorker,
    BaseTask,  # noqa: F401
    BaseTaskWorker,
    BlockingTaskWorker,
)
