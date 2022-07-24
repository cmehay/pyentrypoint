.PHONY: build test

build:
	@docker-compose build

clean:
	docker-compose down --remove-orphans

test: build test-python3.8 test-python3.9 test-python3.10 clean

test-python3.8:
	@docker-compose run --rm testpython3.8

test-python3.9:
	@docker-compose run --rm testpython3.9

test-python3.10:
	@docker-compose run --rm testpython3.10

test-python3:
	@docker-compose run --rm testpython3


publish:
	@python setup.py register && python setup.py sdist upload
