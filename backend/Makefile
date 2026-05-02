# ITMS Backend Makefile
# Convenient commands for development

.PHONY: help install run test lint format clean migrate migration seed docker-up docker-down

help:
	@echo "ITMS Backend - Available Commands"
	@echo "=================================="
	@echo "make install      - Install dependencies"
	@echo "make run          - Run development server"
	@echo "make test         - Run tests"
	@echo "make lint         - Run linters"
	@echo "make format       - Format code"
	@echo "make migrate      - Run database migrations"
	@echo "make migration    - Create new migration"
	@echo "make seed         - Seed database with test data"
	@echo "make clean        - Clean cache files"
	@echo "make docker-up    - Start Docker containers"
	@echo "make docker-down  - Stop Docker containers"
	@echo "make docker-logs  - View Docker logs"
	@echo "make db-shell     - Open PostgreSQL shell"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v --cov=app --cov-report=html

lint:
	flake8 app/
	mypy app/

format:
	black app/
	isort app/

migrate:
	alembic upgrade head

migration:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

seed:
	python scripts/seed_data.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f backend

db-shell:
	docker-compose exec postgres psql -U itms_user -d itms_db
