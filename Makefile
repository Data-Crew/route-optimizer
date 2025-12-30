# Route Optimizer - Makefile
# ============================
# Modular route optimization: CPP, TSP, and more

.PHONY: help build run shell clean test example verify

# Default target
help:
	@echo "🚗 Route Optimizer - Available Commands"
	@echo "   Supports: CPP (Chinese Postman), TSP (Traveling Salesman)"
	@echo "========================================"
	@echo ""
	@echo "Docker - Option A (Development, interactive shell):"
	@echo "  make build      Build Docker image"
	@echo "  make shell      Enter container bash (then run scripts manually)"
	@echo ""
	@echo "Docker - Option B (Quick execution):"
	@echo "  make build      Build Docker image"
	@echo "  docker compose run --rm app python <script.py>"
	@echo ""
	@echo "Docker - Other:"
	@echo "  make run        Show available examples"
	@echo "  make clean      Remove Docker containers and images"
	@echo ""
	@echo "Local (requires virtualenv):"
	@echo "  make venv       Create virtual environment"
	@echo "  make install    Install dependencies in venv"
	@echo "  make verify     Verify installation"
	@echo "  make example    Run CPP example (parking enforcement)"
	@echo "  make example-tsp Run TSP example (delivery route)"
	@echo "  make test       Run module tests"
	@echo ""

# ===================
# Docker Commands
# ===================

build:
	@echo "🔨 Building Docker image..."
	docker compose build

run:
	@echo "🚀 Running route optimizer..."
	docker compose up

shell:
	@echo "🐚 Opening shell in container..."
	docker compose run --rm app bash

clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker compose down --rmi local --volumes --remove-orphans
	@echo "✅ Cleanup complete"

# ===================
# Local Commands
# ===================

VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip

venv:
	@echo "🐍 Creating virtual environment..."
	python3 -m venv $(VENV_DIR)
	@echo "✅ Virtual environment created at $(VENV_DIR)"
	@echo ""
	@echo "To activate, run:"
	@echo "  source $(VENV_DIR)/bin/activate"

install: venv
	@echo "📦 Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencies installed"

verify:
	@echo "🔍 Verifying installation..."
	$(PYTHON) verify_install.py

example:
	@echo "🚀 Running parking enforcement example (CPP)..."
	$(PYTHON) parking_enforcement.py

example-tsp:
	@echo "🚀 Running delivery route example (TSP)..."
	$(PYTHON) delivery_route.py

test:
	@echo "🧪 Running tests..."
	$(PYTHON) -c "from route_optimizer import Zone, RouteOptimizer; print('✅ Module imports OK')"

