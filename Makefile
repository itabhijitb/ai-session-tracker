.PHONY: install dev test lint build publish clean

install:
	pip install .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/

build: clean
	pip install build
	python -m build

publish-test: build
	pip install twine
	twine upload --repository testpypi dist/*

publish: build
	pip install twine
	twine upload dist/*

clean:
	rm -rf dist/ build/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
