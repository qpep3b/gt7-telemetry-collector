start:
	poetry run python main.py

graphs:
	poetry run python graphs.py

format:
	poetry run ruff format src/ tests/ main.py web.py

mypy:
	poetry run mypy src/ main.py web.py --check-untyped-defs

lint:
	poetry run ruff check src/ main.py web.py

isort:
	poetry run isort src/ tests/ main.py web.py