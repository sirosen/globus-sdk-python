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
	virtualenv $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install --upgrade pip
	$(VIRTUALENV)/bin/pip install --upgrade setuptools
	$(VIRTUALENV)/bin/python setup.py develop
	# explicit touch to ensure good update time relative to setup.py
	touch $(VIRTUALENV)


build: $(VIRTUALENV)
	$(VIRTUALENV)/bin/python setup.py sdist bdist_wheel

$(VIRTUALENV)/bin/twine: $(VIRTUALENV) upload-requirements.txt
	$(VIRTUALENV)/bin/pip install -U -r upload-requirements.txt
upload: $(VIRTUALENV)/bin/twine build
	$(VIRTUALENV)/bin/twine upload dist/*

$(VIRTUALENV)/bin/flake8 $(VIRTUALENV)/bin/nose2: test-requirements.txt $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install -r test-requirements.txt
	# explicitly touch these files, otherwise we can have a weird thing happen
	# where test-requirements is newer than the binaries, but the pip install
	# command sees that they exist and does not update their mtime
	touch $(VIRTUALENV)/bin/flake8
	touch $(VIRTUALENV)/bin/nose2

test: $(VIRTUALENV)/bin/flake8 $(VIRTUALENV)/bin/nose2
	$(VIRTUALENV)/bin/flake8
	$(VIRTUALENV)/bin/nose2 --verbose

travis:
	pip install --upgrade pip
	pip install --upgrade "setuptools>=29"
	pip install -r test-requirements.txt
	pip install -e .
	flake8
	nose2 --verbose


# docs needs full install because sphinx will actually try to do
# imports! Otherwise, we'll be missing dependencies like `requests`
$(VIRTUALENV)/bin/sphinx-build: $(VIRTUALENV) docs-requirements.txt
	$(VIRTUALENV)/bin/pip install -r docs-requirements.txt
docs: $(VIRTUALENV) $(VIRTUALENV)/bin/sphinx-build
	. $(VIRTUALENV)/bin/activate && $(MAKE) -C docs/ clean html


clean:
	-rm -r $(VIRTUALENV)
	-rm -r dist
	-rm -r build
	-rm -r *.egg-info
