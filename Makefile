.PHONY: build test

build:
	@docker-compose build

clean:
	docker-compose down --remove-orphans

test: build test-python3.6 test-python3.7 test-python3.8 clean

test-python3.6:
	@docker-compose run --rm testpython3.6

test-python3.7:
	@docker-compose run --rm testpython3.7

test-python3.8:
	@docker-compose run --rm testpython3.8

test-python3:
	@docker-compose run --rm testpython3


publish:
	@python setup.py register && python setup.py sdist upload
