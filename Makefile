# allow specification of python version for devs. Examples:
#    make autoformat PYTHON_VERSION=python3.6
PYTHON_VERSION?=python3
VIRTUALENV=.venv

.PHONY: docs build upload localdev test lint autoformat clean help

help:
	@echo "Globus SDK 'make' targets"
	@echo ""
	@echo "  help:         Show this helptext"
	@echo "  build:        Create the distributions which we like to upload to pypi"
	@echo "  upload:       [build] + upload to pypi using twine"
	@echo "  test:         Run the full suite of tests + linting"
	@echo "  autoformat:   Run code autoformatters"
	@echo "  docs:         Clean old HTML docs and rebuild them with sphinx"
	@echo "  clean:        Remove typically unwanted files, mostly from [build]"

localdev: $(VIRTUALENV)
$(VIRTUALENV): setup.py
	# don't recreate it if it already exists -- just run the setup steps
	if [ ! -d "$(VIRTUALENV)" ]; then virtualenv --python=$(PYTHON_VERSION) $(VIRTUALENV); fi
	$(VIRTUALENV)/bin/pip install -U pip setuptools
	$(VIRTUALENV)/bin/pip install -e '.[development]'
	# explicit touch to ensure good update time relative to setup.py
	touch $(VIRTUALENV)

# run outside of tox because specifying a tox environment for py3.6+ is awkward
autoformat: $(VIRTUALENV)
	$(VIRTUALENV)/bin/isort --recursive tests/ globus_sdk/ setup.py
	if [ -f "$(VIRTUALENV)/bin/black" ]; then $(VIRTUALENV)/bin/black  tests/ globus_sdk/ setup.py; fi

test: $(VIRTUALENV)
	$(VIRTUALENV)/bin/tox
docs: $(VIRTUALENV)
	$(VIRTUALENV)/bin/tox -e docs
build: $(VIRTUALENV)
	$(VIRTUALENV)/bin/python setup.py sdist bdist_wheel
upload: build
	$(VIRTUALENV)/bin/twine upload dist/*

clean:
	rm -rf $(VIRTUALENV) dist build *.egg-info .tox
