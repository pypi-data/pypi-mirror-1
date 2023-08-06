# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <02-Mar-2010 07:28:29 PST by rich@noir.com>

default: all

unamem := $(shell uname -m)

venv := sprained-dev
pythonbin := ${venv}/bin

python := ${pythonbin}/python
activate := . ${pythonbin}/activate
pydoctor := ${venv}/bin/pydoctor
epydoc := ${venv}/bin/epydoc

metaserializer_egg := ${venv}/lib/python2.6/site-packages/metaserializer-0.005-py2.6.egg
nevow_egg := ${venv}/lib/python2.6/site-packages/Nevow-0.10.0-py2.6.egg
nose_egg := ${venv}/lib/python2.6/site-packages/nose-0.11.1-py2.6.egg
pyyaml_egg := ${venv}/lib/python2.6/site-packages/PyYAML-3.09-py2.6-linux-${unamem}.egg
spread_egg := ${venv}/lib/python2.6/site-packages/SpreadModule-1.5-py2.6-linux-${unamem}.egg
twisted_egg := ${venv}/lib/python2.6/site-packages/Twisted-9.0.0-py2.6-linux-${unamem}.egg

.PHONY: all
all:
#all: ${spread_egg} ${nose_egg} ${pydoctor} ${pyyaml_egg} ${metaserializer_egg}

metaserializer: ${metaserializer_egg}
${metaserializer_egg}: stamp-apt
	${activate} && easy_install -U metaserializer

yaml: ${pyyaml_egg}
${pyyaml_egg}: stamp-apt
	${activate} && easy_install -U pyyaml

pydoctor: ${pydoctor}
${pydoctor}: stamp-apt ${nevow_egg} ${epydoc}
	bzr get lp:pydoctor pydoctor
	${activate} && cd pydoctor && python setup.py install

epydoc: ${epydoc}
${epydoc}: ${python}
	${activate} && easy_install -U epydoc

nevow: ${nevow_egg}
${nevow_egg}: ${twisted_egg}
	${activate} && easy_install -U nevow

twisted: ${twisted_egg}
${twisted_egg}: ${python}
	${activate} && easy_install -U twisted

spread: ${spread_egg}
${spread_egg}: ${python}
	${activate} && easy_install -U SpreadModule

nose: ${nose_egg}
${nose_egg}: ${python}
	${activate} && easy_install -U nose

stamp-lucid: stamp-apt
	sudo apt-get install --yes python-twisted python-nose
	touch $@-new && mv $@-new $@

.PHONY: ve
ve: ${python}
${python}: stamp-virtualenv
	virtualenv --no-site-packages sprained-dev

stamp-virtualenv: stamp-apt
	sudo easy_install -U virtualenv
	touch $@-new && mv $@-new $@

# firefox is only needed for reading the doc
DEBIANS := \
	apt-file \
	build-essential \
	bzr \
	debhelper \
	firefox \
	libapache2-mod-wsgi \
	libspread1 \
	libspread1-dev \
	python-dev \
	python-epydoc \
	python-nevow \
	python-setuptools \
	python-twisted \
	python-virtualenv \
	python-yaml \
	yaml-mode \
	libyaml-dev \
	spread \

stamp-apt:
	sudo apt-get install --yes ${DEBIANS}
	touch $@-new && mv $@-new $@

.PHONY: clean
clean:
	rm -rf ${venv} stamp-virtualenv stamp-apt pydoctor build \
		dist sprained.egg-info stamp-lucid *.pyc apidocs TAGS

.PHONY: check
check: develop
	${activate} && nosetests -vv

.PHONY: doc
doc: ${pydoctor}
	${activate} && pydoctor --add-module=sprained.py \
		--add-module=test_sprained.py \
		--add-module=test_spread.py \
		&& firefox apidocs/index.html

.PHONY: sdist
sdist: ${python}
	${activate} && python setup.py sdist

.PHONY: develop
develop: ${python}
	${activate} && python setup.py develop

tags: TAGS
TAGS:; etags *.py
