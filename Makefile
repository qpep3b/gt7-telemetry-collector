start:
	poetry run python main.py

web:
	poetry run uvicorn web:app --reload

graphs:
	poetry run python graphs.py

migrate:
	poetry run alembic upgrade head

install:
	poetry install
	mkdir -p .run/storage/_data
	make migrate

test:
	poetry run pytest -s tests/

format:
	poetry run ruff format src/ tests/ main.py web.py

mypy:
	poetry run mypy src/ main.py web.py --check-untyped-defs

lint:
	poetry run ruff check src/ main.py web.py

isort:
	poetry run isort src/ tests/ main.py web.py