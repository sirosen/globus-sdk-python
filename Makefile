SDK_VERSION=$(shell grep '^__version__' globus_sdk/version.py | cut -d '"' -f2)

# these are just tox invocations wrapped nicely for convenience
.PHONY: lint test docs
lint:
	tox -e lint
test:
	tox
docs:
	tox -e docs

.PHONY: showvars release
showvars:
	@echo "SDK_VERSION=$(SDK_VERSION)"
release:
	git tag -s "$(SDK_VERSION)" -m "v$(SDK_VERSION)"
	tox -e publish-release

.PHONY: clean
clean:
	rm -rf dist build *.egg-info .tox
