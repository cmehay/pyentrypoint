.PHONY: build test

build:
	@docker-compose build

test: build
	@docker-compose up testpython2 testpython3
