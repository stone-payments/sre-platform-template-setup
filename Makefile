build:
	python -m pip install -r requirements.txt

test:
	python -m unittest

lint:
	pylint setup.py