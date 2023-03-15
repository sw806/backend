ci: req fmt lint test db

all: req fmt test dc

db:
	docker compose build --build-arg COMMIT_HASH=$(shell git rev-parse HEAD)

dc: db
	docker compose up

req:
	pip install -r requirements.txt

run:
	cd ./app/; python3 .

# TODO: Add stricts
lint:
	cd ./app/; mypy . --disallow-subclassing-any --disallow-untyped-calls

fmt:
	python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	python3 -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

test:
	pytest
	./scripts/dc-sanity-check.sh