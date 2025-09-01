sources = netbox_aws_vpc_plugin

.PHONY: test format lint unittest pre-commit clean

test: format lint unittest

format:
	pre-commit run --all-files

lint:
	flake8 $(sources)

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf *.egg-info
	rm -rf .tox dist site
