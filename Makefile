REPO=katenary/katenary
VERSION=$(shell curl -s https://api.github.com/repos/$(REPO)/releases/latest | jq -r '.tag_name')
TAR_SHA=$(shell curl -s https://github.com/$(REPO)/archive/refs/tags/$(VERSION).tar.gz | sha256sum | awk '{print $$1}')

SHELL=/bin/bash
.ONE_SHELL:

all: Formula/katenary.rb

Formula/katenary.rb: build-formula.py
	python build-formula.py > $@

