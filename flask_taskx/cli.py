# -*- coding: utf-8 -*-

import os
import click
import sys
from dotenv import load_dotenv

_cwd = os.getcwd()
sys.path.append(_cwd)

# System

@click.command()
@click.argument('keywords')
@click.option('--remote', '-r', default='localhost', help='Remote message broker url')
def taskx_cli(keywords, remote):

    if keywords == "run":

        dotenv_path = os.path.join(_cwd, '.env')
        load_dotenv(dotenv_path)

        flask_app = os.environ.get("FLASK_APP")

        if not flask_app:

            try:
                module = __import__("app")
            except Exception as e:
                print(e)
        else:

            flask_app = flask_app.replace('.py', '')

            try:
                module = __import__(flask_app)
            except Exception as e:
                print(e)
                return
        
        attrs = dir(module)

        if "app" in attrs:
            app = module.app
        elif "application" in attrs:
            app = module.application
        elif "create_app" in attrs:
            app = module.create_app()
        elif "make_app" in attrs:
            app = module.make_app()

        task_worker = app._task_worker
        task_worker.start()