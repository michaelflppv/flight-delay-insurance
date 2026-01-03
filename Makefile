.PHONY: help install setup download-data train test run clean docker-build docker-up docker-down logs health check lint format

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Flight Delay Insurance - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  1. make install        # Install dependencies"
	@echo "  2. make setup          # Set up environment"
	@echo "  3. make download-data  # Download dataset from Kaggle"
	@echo "  4. make train          # Train ML models"
	@echo "  5. make run            # Start API server"
	@echo ""
	@echo "$(YELLOW)Or use Docker:$(NC)"
	@echo "  make docker-up         # Build and start everything"

install: ## Install dependencies using Poetry
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@command -v poetry >/dev/null 2>&1 || { echo "$(RED)Error: Poetry not found. Install from https://python-poetry.org$(NC)"; exit 1; }
	poetry install
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

setup: ## Set up environment files and directories
	@echo "$(BLUE)Setting up environment...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓ Created .env from .env.example$(NC)"; \
		echo "$(YELLOW)  Please review .env and add your Kaggle credentials if needed$(NC)"; \
	else \
		echo "$(YELLOW)  .env already exists, skipping$(NC)"; \
	fi
	@mkdir -p data models logs
	@echo "$(GREEN)✓ Created data/, models/, logs/ directories$(NC)"
	@echo "$(GREEN)✓ Setup complete!$(NC)"

download-data: ## Download flight dataset from Kaggle
	@echo "$(BLUE)Downloading dataset from Kaggle...$(NC)"
	@echo "$(YELLOW)Note: This requires Kaggle API credentials in ~/.kaggle/kaggle.json$(NC)"
	@echo "$(YELLOW)Get your API token from: https://www.kaggle.com/settings/account$(NC)"
	@echo ""
	poetry run python scripts/download_data.py
	@if [ $$? -eq 0 ]; then \
		echo "$(GREEN)✓ Dataset downloaded successfully$(NC)"; \
	else \
		echo "$(RED)✗ Dataset download failed$(NC)"; \
		exit 1; \
	fi

train: ## Train ML models (requires dataset)
	@echo "$(BLUE)Training ML models...$(NC)"
	@if [ ! -d "data" ] || [ -z "$$(ls -A data/*.csv 2>/dev/null)" ]; then \
		echo "$(RED)✗ No data found. Run 'make download-data' first$(NC)"; \
		exit 1; \
	fi
	@echo "MODE=train" > .env.tmp
	@grep -v "^MODE=" .env >> .env.tmp 2>/dev/null || true
	@mv .env.tmp .env
	poetry run python scripts/train.py
	@echo "MODE=test" > .env.tmp
	@grep -v "^MODE=" .env >> .env.tmp 2>/dev/null || true
	@mv .env.tmp .env
	@echo "$(GREEN)✓ Models trained successfully$(NC)"
	@echo "$(GREEN)  Models saved in models/$(NC)"

test: ## Run tests (placeholder - add tests first)
	@echo "$(BLUE)Running tests...$(NC)"
	@if poetry run pytest --version >/dev/null 2>&1; then \
		poetry run pytest tests/ -v; \
	else \
		echo "$(YELLOW)No tests configured yet. Add tests in tests/ directory$(NC)"; \
	fi

run: ## Run the Flask API server
	@echo "$(BLUE)Starting Flask API server...$(NC)"
	@if [ ! -f "models/flight_delay_classifier_v1.pkl" ]; then \
		echo "$(RED)✗ Models not found. Run 'make train' first$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Starting server at http://localhost:5000$(NC)"
	@echo "$(YELLOW)  Press Ctrl+C to stop$(NC)"
	@echo ""
	poetry run python scripts/serve.py

dev: ## Run server in development mode with auto-reload
	@echo "$(BLUE)Starting development server...$(NC)"
	@echo "FLASK_DEBUG=True" > .env.tmp
	@grep -v "^FLASK_DEBUG=" .env >> .env.tmp 2>/dev/null || true
	@mv .env.tmp .env
	poetry run python scripts/serve.py

clean: ## Clean generated files (models, logs, cache)
	@echo "$(BLUE)Cleaning generated files...$(NC)"
	@rm -rf models/*.pkl
	@rm -rf logs/*.log
	@rm -rf __pycache__ **/__pycache__
	@rm -rf .pytest_cache
	@rm -rf .coverage htmlcov
	@echo "$(GREEN)✓ Cleaned models, logs, and cache$(NC)"

clean-all: clean ## Clean everything including data and Docker volumes
	@echo "$(BLUE)Cleaning all files including data...$(NC)"
	@rm -rf data/*.csv
	@docker-compose down -v 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned all files$(NC)"

health: ## Check API health status
	@echo "$(BLUE)Checking API health...$(NC)"
	@curl -s http://localhost:5000/health | python -m json.tool 2>/dev/null || \
		echo "$(RED)✗ API not responding. Is the server running?$(NC)"

check: ## Quick health and status check
	@echo "$(BLUE)System Status Check$(NC)"
	@echo ""
	@echo "$(YELLOW)Dependencies:$(NC)"
	@command -v poetry >/dev/null 2>&1 && echo "$(GREEN)✓ Poetry installed$(NC)" || echo "$(RED)✗ Poetry not found$(NC)"
	@command -v docker >/dev/null 2>&1 && echo "$(GREEN)✓ Docker installed$(NC)" || echo "$(YELLOW)  Docker not found (optional)$(NC)"
	@echo ""
	@echo "$(YELLOW)Files:$(NC)"
	@[ -f .env ] && echo "$(GREEN)✓ .env exists$(NC)" || echo "$(RED)✗ .env not found (run 'make setup')$(NC)"
	@[ -d data ] && echo "$(GREEN)✓ data/ directory exists$(NC)" || echo "$(RED)✗ data/ not found$(NC)"
	@[ -d models ] && echo "$(GREEN)✓ models/ directory exists$(NC)" || echo "$(RED)✗ models/ not found$(NC)"
	@echo ""
	@echo "$(YELLOW)Data & Models:$(NC)"
	@[ -n "$$(ls -A data/*.csv 2>/dev/null)" ] && echo "$(GREEN)✓ Dataset downloaded$(NC)" || echo "$(YELLOW)  No data found (run 'make download-data')$(NC)"
	@[ -f models/flight_delay_classifier_v1.pkl ] && echo "$(GREEN)✓ Models trained$(NC)" || echo "$(YELLOW)  Models not found (run 'make train')$(NC)"
	@echo ""
	@echo "$(YELLOW)API:$(NC)"
	@curl -s http://localhost:5000/health >/dev/null 2>&1 && echo "$(GREEN)✓ API running$(NC)" || echo "$(YELLOW)  API not running (run 'make run')$(NC)"

predict: ## Test prediction with example data
	@echo "$(BLUE)Testing prediction...$(NC)"
	poetry run python scripts/predict.py

# Docker commands
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Docker image built$(NC)"

docker-up: ## Start services with Docker Compose
	@echo "$(BLUE)Starting Docker services...$(NC)"
	@if [ ! -f models/flight_delay_classifier_v1.pkl ]; then \
		echo "$(YELLOW)Warning: Models not found. Training first...$(NC)"; \
		$(MAKE) train; \
	fi
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "$(GREEN)  API available at http://localhost:5000$(NC)"
	@echo "  View logs: make logs"
	@echo "  Check health: make health"

docker-down: ## Stop Docker services
	@echo "$(BLUE)Stopping Docker services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

docker-restart: ## Restart Docker services
	@$(MAKE) docker-down
	@$(MAKE) docker-up

logs: ## View Docker logs
	docker-compose logs -f

# Code quality
lint: ## Run linting (flake8)
	@echo "$(BLUE)Running linter...$(NC)"
	poetry run flake8 src/ scripts/ --max-line-length=120 --exclude=venv,__pycache__

format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(NC)"
	poetry run black src/ scripts/ tests/ --line-length=120

# Full workflow shortcuts
first-run: install setup download-data train ## Complete first-time setup
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)✓ First-time setup complete!$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Run the API:  $(BLUE)make run$(NC)"
	@echo "  2. Test it:      $(BLUE)make predict$(NC)"
	@echo ""

all: first-run ## Alias for first-run

# Development workflow
dev-setup: install setup ## Quick setup for development (without data download)
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo "$(YELLOW)Note: You still need to run 'make download-data' and 'make train'$(NC)"

# Production shortcuts
prod-start: ## Start production server with Docker
	@echo "$(BLUE)Starting production server...$(NC)"
	@$(MAKE) docker-up

prod-stop: ## Stop production server
	@$(MAKE) docker-down

prod-restart: ## Restart production server
	@$(MAKE) docker-restart

# Utility commands
shell: ## Open Poetry shell
	poetry shell

jupyter: ## Start Jupyter notebook (if installed)
	poetry run jupyter notebook

info: ## Show project information
	@echo "$(BLUE)Project Information$(NC)"
	@echo ""
	@echo "Name:    Flight Delay Insurance API"
	@echo "Version: 0.1.0"
	@echo "Python:  $(shell poetry run python --version)"
	@echo ""
	@echo "Dependencies:"
	@poetry show --tree --only main | head -10

update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	poetry update
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

# One-command demo
demo: ## Quick demo (install, setup, run with sample - requires manual data)
	@echo "$(BLUE)Starting demo...$(NC)"
	@$(MAKE) install
	@$(MAKE) setup
	@echo ""
	@echo "$(YELLOW)========================================$(NC)"
	@echo "$(YELLOW)Demo Setup Complete$(NC)"
	@echo "$(YELLOW)========================================$(NC)"
	@echo ""
	@echo "To complete the demo:"
	@echo "  1. $(BLUE)make download-data$(NC)  - Download dataset"
	@echo "  2. $(BLUE)make train$(NC)         - Train models"
	@echo "  3. $(BLUE)make run$(NC)           - Start API"
	@echo ""
