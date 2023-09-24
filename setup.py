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

setup(
    name="Flask-TaskX",
    version="0.0.1",
    url="https://github.com/carrasquel/flask-taskx",
    license="BSD",
    author="Nelson Carrasquel",
    author_email="carrasquel@outlook.com",
    maintainer="Nelson Carrasquel",
    maintainer_email="carrasquel@outlook.com",
    description="A Flask extension for creating and running tasks",
    long_description=__doc__,
    py_modules=["flask_taskx"],
    zip_safe=False,
    platforms="any",
    install_requires=["Flask", "apscheduler", "peewee"],
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
