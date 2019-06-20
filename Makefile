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
localdev: .venv
.venv:
	virtualenv --python=python3 .venv
	.venv/bin/pip install -U pip setuptools
	.venv/bin/pip install -e '.[development]'
	# explicit touch to ensure good update time relative to setup.py
	touch .venv

# run outside of tox because specifying a tox environment for py3.6+ is awkward
.PHONY: autoformat
autoformat: .venv
	.venv/bin/isort --recursive tests/ globus_sdk/ setup.py
	.venv/bin/black tests/ globus_sdk/ setup.py

.PHONY: test
test: .venv
	.venv/bin/tox
.PHONY: docs
docs: .venv
	.venv/bin/tox -e docs

.PHONY: showvars
showvars:
	@echo "SDK_VERSION=$(SDK_VERSION)"
.PHONY: release
release: .venv
	git tag -s "$(SDK_VERSION)" -m "v$(SDK_VERSION)"
	rm -rf dist
	.venv/bin/python setup.py sdist bdist_wheel
	.venv/bin/twine upload dist/*

.PHONY: clean
clean:
	rm -rf .venv dist build *.egg-info .tox
