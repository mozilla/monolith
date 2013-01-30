.PHONY: docs build test coverage build_rpm clean

ifndef VTENV_OPTS
VTENV_OPTS = "--no-site-packages"
endif

bin/python:
	virtualenv $(VTENV_OPTS) .
	bin/python setup.py develop
	bin/pip install nose

test: bin/python
	bin/nosetests -s 
