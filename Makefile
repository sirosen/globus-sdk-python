# allow specification of python version and venv loc for devs, so you can
#    make test PYTHON_VERSION=python3.6 VIRTUALENV=.venv36
#    make test PYTHON_VERSION=python2.7 VIRTUALENV=.venv27
# and be happy
# we don't need tox just to do this (though it might make life easier in the
# future, especially now that tests are fast)
PYTHON_VERSION?=python3
VIRTUALENV?=.venv
AUTOFORMAT_TARGETS=tests/ globus_sdk/ setup.py

.PHONY: docs build upload test lint autoformat clean help


help:
	@echo "These are our make targets and what they do."
	@echo "All unlisted targets are internal."
	@echo ""
	@echo "  help:         Show this helptext"
	@echo "  localdev:     Setup local development env with a 'setup.py develop'"
	@echo "  build:        Create the distributions which we like to upload to pypi"
	@echo "  lint:         All linting steps other than 'black'"
	@echo "  autoformat:   Run code autoformatters"
	@echo "  test:         Run the full suite of tests"
	@echo "  docs:         Clean old HTML docs and rebuild them with sphinx"
	@echo "  upload:       [build], but also upload to pypi using twine"
	@echo "  clean:        Remove typically unwanted files, mostly from [build]"
	@echo "  all:          Wrapper for [localdev] + [docs] + [test]"


all: localdev docs test
localdev: $(VIRTUALENV)


$(VIRTUALENV): setup.py
	# don't recreate it if it already exists -- just run the setup steps
	if [ ! -d "$(VIRTUALENV)" ]; then virtualenv --python=$(PYTHON_VERSION) $(VIRTUALENV); fi
	$(VIRTUALENV)/bin/pip install -U pip setuptools
	$(VIRTUALENV)/bin/pip install -e '.[development]'
	# explicit touch to ensure good update time relative to setup.py
	touch $(VIRTUALENV)


build: $(VIRTUALENV)
	$(VIRTUALENV)/bin/python setup.py sdist bdist_wheel

upload: build
	$(VIRTUALENV)/bin/twine upload dist/*


autoformat: $(VIRTUALENV)
	$(VIRTUALENV)/bin/isort --recursive $(AUTOFORMAT_TARGETS)
	if [ -f "$(VIRTUALENV)/bin/black" ]; then $(VIRTUALENV)/bin/black $(AUTOFORMAT_TARGETS); fi


lint: $(VIRTUALENV)
	if [ -f "$(VIRTUALENV)/bin/black" ]; then $(VIRTUALENV)/bin/black --check $(AUTOFORMAT_TARGETS); fi
	$(VIRTUALENV)/bin/flake8
	$(VIRTUALENV)/bin/isort --recursive --check-only $(AUTOFORMAT_TARGETS)


test: $(VIRTUALENV)
	$(VIRTUALENV)/bin/pytest -v --cov=globus_sdk


travis:
	pip install -U pip setuptools
	pip install -e '.[development]'
	$(MAKE) lint
	pytest -v tests/


docs: $(VIRTUALENV)
	. $(VIRTUALENV)/bin/activate && $(MAKE) -C docs/ clean html


clean:
	-rm -r $(VIRTUALENV)
	-rm -r dist
	-rm -r build
	-rm -r *.egg-info
