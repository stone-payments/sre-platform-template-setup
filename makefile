test:
	docker build -f ./Dockerfile.test -t setup-test .
	docker run --rm -it setup-test