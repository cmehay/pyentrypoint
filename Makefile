.PHONY: build test

build:
	@docker-compose build
	@docker-compose -f docker-compose.v3.yml build

clean:
	docker-compose down --remove-orphans
	@docker-compose -f docker-compose.v3.yml down --remove-orphans

test: build test-python2 test-python3 clean

test-python2:
	@docker-compose run --rm testpython2
	@docker-compose -f docker-compose.v3.yml run --rm testpython2

test-python3:
	@docker-compose run --rm testpython3
	@docker-compose -f docker-compose.v3.yml run --rm testpython3


test_debug: build
	@docker-compose up --force-recreate testpython2_debug testpython3_debug
	@docker-compose -f docker-compose.v3.yml up --force-recreate testpython2_debug testpython3_debug

publish:
	@python setup.py register && python setup.py sdist upload
