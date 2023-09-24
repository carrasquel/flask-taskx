ifndef VENVNAME
  VENVNAME = venv
endif

ifeq ($(OS),Windows_NT)
	CURRENT_DIR = $(shell cd)
	INTERPRETER_DIR = $(CURRENT_DIR)/$(VENVNAME)/Scripts
else
	CURRENT_DIR = $(shell pwd)
	INTERPRETER_DIR = $(CURRENT_DIR)/$(VENVNAME)/bin
endif

PYTHON=$(INTERPRETER_DIR)/python

isort:
	$(PYTHON) -m isort --check-only .

black:
	$(PYTHON) -m black --check .

flake8:
	$(PYTHON) -m flake8 .

lint: isort black flake8

build:
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py bdist_wheel