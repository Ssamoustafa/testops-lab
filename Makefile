install:
	python -m pip install -e ".[dev]"

quality:
	ruff check .
	mypy src

unit:
	pytest tests/unit

test:
	pytest --cov=testops --cov-report=term-missing

demo:
	testops examples/results.json --max-p95-ms 2000
