# allow specification of python version for devs. Examples:
#    make autoformat PYTHON_VERSION=python3.6
PYTHON_VERSION?=python3
VIRTUALENV=.venv
SDK_VERSION=$(shell grep '^__version__' globus_sdk/version.py | cut -d '"' -f2)

.PHONY: help
help:
	@echo "Globus SDK 'make' targets"
	@echo ""
	@echo "  help:         Show this helptext"
	@echo "  test:         Run the full suite of tests + linting"
	@echo "  autoformat:   Run code autoformatters"
	@echo "  docs:         Clean old HTML docs and rebuild them with sphinx"
	@echo "  release:      create a signed tag, clean old builds, do a fresh build, and upload to pypi"
	@echo "  clean:        Remove typically unwanted files, mostly from [build]"

.PHONY: localdev
localdev: $(VIRTUALENV)
$(VIRTUALENV): setup.py
	# don't recreate it if it already exists -- just run the setup steps
	if [ ! -d "$(VIRTUALENV)" ]; then virtualenv --python=$(PYTHON_VERSION) $(VIRTUALENV); fi
	$(VIRTUALENV)/bin/pip install -U pip setuptools
	$(VIRTUALENV)/bin/pip install -e '.[development]'
	# explicit touch to ensure good update time relative to setup.py
	touch $(VIRTUALENV)

# run outside of tox because specifying a tox environment for py3.6+ is awkward
.PHONY: autoformat
autoformat: $(VIRTUALENV)
	$(VIRTUALENV)/bin/isort --recursive tests/ globus_sdk/ setup.py
	if [ -f "$(VIRTUALENV)/bin/black" ]; then $(VIRTUALENV)/bin/black  tests/ globus_sdk/ setup.py; fi

.PHONY: test
test: $(VIRTUALENV)
	$(VIRTUALENV)/bin/tox
.PHONY: docs
docs: $(VIRTUALENV)
	$(VIRTUALENV)/bin/tox -e docs

.PHONY: showvars
showvars:
	@echo "SDK_VERSION=$(SDK_VERSION)"
.PHONY: release
release: $(VIRTUALENV)
	git tag -s "$(SDK_VERSION)" -m "v$(SDK_VERSION)"
	rm -rf dist
	$(VIRTUALENV)/bin/python setup.py sdist bdist_wheel
	$(VIRTUALENV)/bin/twine upload dist/*

.PHONY: clean
clean:
	rm -rf $(VIRTUALENV) dist build *.egg-info .tox
