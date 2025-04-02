.PHONY: setup start-local start-prod collect-static create-admin lint
export PYTHONPATH := src

setup-local:
	@echo "🔧 Installing Poetry (if not already installed)..."
	@export PATH="$$HOME/.local/bin:$$PATH"; \
	if ! command -v poetry &> /dev/null; then pip install --user poetry; fi; \
	echo "📂 Setting up poetry to create a venv inside a project..."; \
	poetry config virtualenvs.in-project true; \
	echo "📦 Installing dependencies..."; \
	poetry install; \
	echo "✅ Setup complete!"; \
	poetry env info



start-local:
	poetry run python -m manage migrate users
	poetry run python -m manage migrate
	poetry run python -m manage collectstatic --noinput
	poetry run uvicorn server.asgi:app --port 8201 --reload --host 0.0.0.0

start-prod:
	@echo "🔄 Performing migrations..."
	poetry run python -m manage migrate users
	poetry run python -m manage migrate
	poetry run python -m manage collectstatic --noinput
	bash -c 'poetry run uvicorn server.asgi:app --port ${TCP_PORT} --workers 1 --host 0.0.0.0 $$( [ -n "$$ROOT_PATH" ] && echo "--root-path $$ROOT_PATH" )'

collect-static:
	@echo "🗂️ Collecting static files..."
	poetry run python -m manage collectstatic --noinput

create-admin:
	poetry run python -m manage createsuperuser

test:
	echo "Running tests... #TODO"

lint:
	poetry run black ./
	poetry run isort ./
	poetry run ruff check ./ --fix
	poetry run mypy .