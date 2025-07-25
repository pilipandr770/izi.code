# Makefile for SaaS Shop Flask Application

.PHONY: help install dev test clean lint format migrate upgrade downgrade reset-db create-admin run-dev run-prod

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Setup development environment"
	@echo "  test        - Run tests"
	@echo "  clean       - Clean up temporary files"
	@echo "  lint        - Run code linting"
	@echo "  format      - Format code"
	@echo "  migrate     - Create database migration"
	@echo "  upgrade     - Apply database migrations"
	@echo "  downgrade   - Rollback database migration"
	@echo "  reset-db    - Reset database (WARNING: deletes all data)"
	@echo "  create-admin - Create admin user"
	@echo "  run-dev     - Run development server"
	@echo "  run-prod    - Run production server"

# Install dependencies
install:
	pip install -r requirements.txt

# Setup development environment
dev: install
	@echo "Setting up development environment..."
	@if not exist .env copy .env.example .env
	flask db init
	flask db migrate -m "Initial migration"
	flask db upgrade
	flask init-db
	@echo "Development environment ready!"

# Run tests
test:
	python -m pytest tests.py -v

# Clean up
clean:
	del /q /s __pycache__ 2>nul || true
	del /q /s *.pyc 2>nul || true
	del /q /s *.pyo 2>nul || true
	del /q /s .pytest_cache 2>nul || true
	del /q /s .coverage 2>nul || true

# Code linting
lint:
	flake8 app/ --max-line-length=120 --exclude=migrations

# Code formatting
format:
	black app/ tests.py run.py config.py

# Database migrations
migrate:
	flask db migrate

upgrade:
	flask db upgrade

downgrade:
	flask db downgrade

# Reset database (dangerous!)
reset-db:
	@echo "WARNING: This will delete all data!"
	@echo "Press Ctrl+C to cancel or Enter to continue..."
	@pause
	flask reset-db

# Create admin user
create-admin:
	flask create-admin

# Run development server
run-dev:
	set FLASK_ENV=development && python run.py

# Run production server
run-prod:
	set FLASK_ENV=production && gunicorn -w 4 -b 0.0.0.0:5000 run:app

# Extract translatable strings
extract-messages:
	pybabel extract -F babel.cfg -k _l -o messages.pot .

# Initialize translations
init-translation:
	pybabel init -i messages.pot -d app/translations -l $(LANG)

# Update translations
update-translations:
	pybabel update -i messages.pot -d app/translations

# Compile translations
compile-translations:
	pybabel compile -d app/translations

# Docker commands
docker-build:
	docker build -t saas-shop .

docker-run:
	docker run -p 5000:5000 saas-shop

# Deployment
deploy-render:
	@echo "Deploying to Render.com..."
	@echo "Make sure render.yaml is configured properly"
	git add .
	git commit -m "Deploy to Render"
	git push origin main

# Security check
security-check:
	pip install safety bandit
	safety check
	bandit -r app/

# Generate requirements
freeze:
	pip freeze > requirements.txt

# Setup virtual environment
venv:
	python -m venv venv
	@echo "Virtual environment created. Activate with: venv\Scripts\activate"
