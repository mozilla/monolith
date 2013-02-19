HERE = $(shell pwd)
BIN = $(HERE)/bin
PYTHON = $(BIN)/python

INSTALL = $(BIN)/pip install
VTENV_OPTS ?= --distribute
ES_VERSION ?= 0.20.5

BUILD_DIRS = bin build elasticsearch include lib lib64 man share


.PHONY: all test testjs

all: build

$(PYTHON):
	virtualenv $(VTENV_OPTS) .

build: $(PYTHON) elasticsearch
	$(PYTHON) setup.py develop
	$(INSTALL) monolith[test]

clean:
	rm -rf $(BUILD_DIRS)


test: build
	$(BIN)/nosetests -s -d -v --with-coverage --cover-package monolith monolith

testjs: build
	elasticsearch/bin/elasticsearch -p es.pid
	bin/pserve --pid-file monolith.pid --daemon monolith/tests/monolith.ini
	sleep 5
	-testacular start --single-run
	kill `cat es.pid`
	kill `cat monolith.pid` 
	rm monolith.pid

elasticsearch:
	curl -C - --progress-bar http://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-$(ES_VERSION).tar.gz | tar -zx
	mv elasticsearch-$(ES_VERSION) elasticsearch
	chmod a+x elasticsearch/bin/elasticsearch
	mv elasticsearch/config/elasticsearch.yml elasticsearch/config/elasticsearch.in.yml
	cp elasticsearch.yml elasticsearch/config/elasticsearch.yml
	elasticsearch/bin/elasticsearch -p es.pid; sleep 5
	$(BIN)/python tools/create_es.py 9998
	kill `cat es.pid`
