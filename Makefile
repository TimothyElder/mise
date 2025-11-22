editable:
	python -m venv .venv-test
	source .venv-test/bin/activate

	pip install -e ".[dev]"
	mise

start:
	python -m src/mise