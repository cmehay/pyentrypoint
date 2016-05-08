.PHONY: build test

build:
	@docker-compose build

test: build
	@docker-compose up --force-recreate testpython2 testpython3

test_debug: build
	@docker-compose up --force-recreate testpython2_debug testpython3_debug

publish:
	@python setup.py register && python setup.py sdist upload
