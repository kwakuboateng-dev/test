.PHONY: run install superuser migrate clean docker-build docker-run help

# Default target
all: help

# Run the development server
run:
	./venv/bin/python3 -m uvicorn main:app --reload --port 8000

# Install dependencies
install:
	pip install -r requirements.txt

# Create a superuser for the admin panel
superuser:
	python3 create_superuser.py

# Run database migrations
migrate:
	python3 migrate_db.py

# Create the database (run this first if database doesn't exist)
createdb:
	createdb odoyewu || echo "Database may already exist"

# Run premium features migration
migrate-premium:
	python3 migrate_premium.py

# Seed database with sample data
seed:
	python3 seed_data.py

# Clean up pycache and other artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build Docker image
docker-build:
	docker build -t odoyewu-backend .

# Run Docker container
docker-run:
	docker run -p 8000:8000 odoyewu-backend

# Show help
help:
	@echo "Available commands:"
	@echo "  make run              - Run the development server"
	@echo "  make install          - Install dependencies"
	@echo "  make superuser        - Create a superuser for the admin panel"
	@echo "  make createdb         - Create the odoyewu database"
	@echo "  make migrate          - Run database migrations"
	@echo "  make migrate-premium  - Run premium features migration"
	@echo "  make seed             - Seed database with sample data"
	@echo "  make clean            - Clean up pycache and artifacts"
	@echo "  make docker-build     - Build Docker image"
	@echo "  make docker-run       - Run Docker container"
