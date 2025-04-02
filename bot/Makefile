.PHONY: setup-local start-local start-prod collect-static create-admin lint
export PYTHONPATH := src

setup-local:
	@echo "🔧 Installing Poetry (if not already installed)..."
	@if ! command -v poetry &> /dev/null; then pip install --user poetry; fi
	@echo "📂 Setting up poetry to create a venv inside a project..."
	poetry config virtualenvs.in-project true
	@echo "📦 Installing dependencies..."
	poetry install
	@echo "✅ Setup complete!"
	poetry env info



start:
	poetry run python -m main

lint:
	poetry run black ./
	poetry run isort ./
	poetry run ruff check ./ --fix
	poetry run mypy .