HERE = $(shell pwd)
BIN = $(HERE)/bin
PYTHON = $(BIN)/python

INSTALL = $(BIN)/pip install --no-deps
VTENV_OPTS ?= --distribute
ES_VERSION ?= 0.20.6

BUILD_DIRS = bin build elasticsearch include lib lib64 man share


.PHONY: all test testjs

all: build

$(PYTHON):
	virtualenv $(VTENV_OPTS) .

build: $(PYTHON) elasticsearch
	$(INSTALL) -r requirements/prod.txt
	$(INSTALL) -r requirements/dev.txt
	$(INSTALL) -r requirements/test.txt
	$(PYTHON) setup.py develop

clean:
	rm -rf $(BUILD_DIRS)

test: build
	$(BIN)/nosetests -s -d -v --with-coverage --cover-package monolith monolith

testjs: build
	rm -rf elasticsearch/data/monotest/
	elasticsearch/bin/elasticsearch -p es.pid
	bin/pserve --pid-file monolith.pid --daemon monolith/web/tests/monolith.ini
	sleep 10
	$(BIN)/python tools/create_es.py 9998
	-testacular start --single-run
	kill `cat es.pid`
	kill `cat monolith.pid`
	rm -f es.pid
	rm -f monolith.pid

elasticsearch:
	curl -C - --progress-bar http://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-$(ES_VERSION).tar.gz | tar -zx
	mv elasticsearch-$(ES_VERSION) elasticsearch
	chmod a+x elasticsearch/bin/elasticsearch
	mv elasticsearch/config/elasticsearch.yml elasticsearch/config/elasticsearch.in.yml
	cp elasticsearch.yml elasticsearch/config/elasticsearch.yml
