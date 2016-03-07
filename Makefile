.PHONY: build test

build:
	@docker-compose build

test: build
	@docker-compose up --force-recreate testpython2 testpython3
