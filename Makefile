.PHONY: test

# Build docker image. Docker hub account username is 'waterproofpatch'
docker:
	docker build . -t waterproofpatch/pi-cam

# Run the docker container locally
run_docker: 
	docker run -p 8080:80 waterproofpatch/pi-cam

# Push docker image to docker hub. Assumes logged in using 'docker login'.
push_docker:
	docker push waterproofpatch/pi-cam:latest

# Deploy to AWS beanstock. Assumes logged into AWS.
deploy: docker push_docker
	eb deploy VuePythonTemplate-env

# Start the wsgi server locally. Useful to verify the uwsgi config is working
run_uwsgi:
	uwsgi --ini wsgi.ini 

# Start the backend
run_backend:
	python -m backend.app 

# Start the frontend
run_frontend:
	(cd frontend && npm run serve)

# Run the tests and generate coverage
test:
	coverage run -m pytest backend/test -s && coverage html

# remove artifacts
clean:
	rm -rf htmlcov .coverage uploads