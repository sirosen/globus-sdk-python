VIRTUALENV=.venv

.PHONY: docs build upload test clean help


help:
	@echo "These are our make targets and what they do."
	@echo "All unlisted targets are internal."
	@echo ""
	@echo "  help:         Show this helptext"
	@echo "  localdev:     Setup local development env with a 'setup.py develop'"
	@echo "  build:        Create the distributions which we like to upload to pypi"
	@echo "  test:         Run the full suite of tests"
	@echo "  docs:         Clean old HTML docs and rebuild them with sphinx"
	@echo "  upload:       [build], but also upload to pypi using twine"
	@echo "  clean:        Remove typically unwanted files, mostly from [build]"
	@echo "  all:          Wrapper for [localdev] + [docs] + [test]"


all: localdev docs test
localdev: $(VIRTUALENV)


$(VIRTUALENV): setup.py
	# don't recreate it if it already exists -- just run the setup steps
	if [ ! -d "$(VIRTUALENV)" ]; then virtualenv $(VIRTUALENV); fi
	$(VIRTUALENV)/bin/pip install -U pip setuptools
	$(VIRTUALENV)/bin/pip install -e '.[development]'
	# explicit touch to ensure good update time relative to setup.py
	touch $(VIRTUALENV)


build: $(VIRTUALENV)
	$(VIRTUALENV)/bin/python setup.py sdist bdist_wheel

upload: build
	$(VIRTUALENV)/bin/twine upload dist/*

test: $(VIRTUALENV)
	$(VIRTUALENV)/bin/flake8
	$(VIRTUALENV)/bin/pytest -v --cov=globus_sdk

travis:
	pip install -U pip setuptools
	pip install -e '.[development]'
	flake8
	pytest -v tests/

docs: $(VIRTUALENV)
	. $(VIRTUALENV)/bin/activate && $(MAKE) -C docs/ clean html

clean:
	-rm -r $(VIRTUALENV)
	-rm -r dist
	-rm -r build
	-rm -r *.egg-info
