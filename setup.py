"""
Flask-TaskX
----------

A Flask extension for creating and running tasks within the context of Flask applications.

Please refer to the online documentation for details.

Links
`````

* `documentation <http://packages.python.org/Flask-TaskX>`_
"""
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="flask-taskx",
    version="1.0",
    url="https://github.com/carrasquel/flask-taskx",
    license="BSD",
    author="Nelson Carrasquel",
    author_email="carrasquel@outlook.com",
    maintainer="Nelson Carrasquel",
    maintainer_email="carrasquel@outlook.com",
    description="A Flask extension for defining and running tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["flask_taskx"],
    zip_safe=False,
    platforms="any",
    entry_points={
        'console_scripts': [
            'taskx = flask_taskx:cli',
        ],
    },
    install_requires=["Flask", "apscheduler", "peewee", "Click==7.0",],
    tests_require=[
        "nose",
        "mock",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
