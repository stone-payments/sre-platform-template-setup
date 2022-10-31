test:
	docker build -f ./Dockerfile.test -t setup-test .
	docker run --rm -it setup-test

lint:
	python -m pip install -r requirements.txt
	pylint setup.py