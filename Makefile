#!/usr/bin/make

DEFAULT_PYTHON_VERSION ?= 2
VENV ?= $(PWD)/venv

ifeq (2,$(DEFAULT_PYTHON_VERSION))
VENV_CMD = virtualenv
else
VENV_CMD = pyvenv
endif

default: build

$(VENV): requirements.txt
	$(VENV_CMD) $@
	$@/bin/pip install -r requirements.txt

build: $(VENV)


clean: 
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	rm -rf $(VENV)
