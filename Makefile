dev:
	python3 -m pip install -U poetry
	poetry install

lint:
	poetry run flake8 src tests

test:
	poetry run pytest -q
