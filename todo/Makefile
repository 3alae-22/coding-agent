.PHONY: install migrate run

install:
	uv sync --dev

migrate:
	uv run python manage.py migrate

run:
	uv run python manage.py runserver