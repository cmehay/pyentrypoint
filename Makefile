.PHONY: build test

build:
	@docker-compose build

clean:
	docker-compose down --remove-orphans

test: build test-python2 test-python3 clean

test-python2:
	@docker-compose run --rm testpython2

test-python3:
	@docker-compose run --rm testpython3


test_debug: build
	@docker-compose up --force-recreate testpython2_debug testpython3_debug

publish:
	@python setup.py register && python setup.py sdist upload
