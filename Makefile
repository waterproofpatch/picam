PI_ADDRESS=192.168.1.189

.PHONY: test

# Build docker image. Docker hub account username is 'waterproofpatch'
docker:
	docker build . -t waterproofpatch/pi-cam

# Run the docker container locally
run_docker: 
	docker run -p 8080:80 waterproofpatch/pi-cam

# Deploy to AWS beanstock. Assumes logged into AWS.
deploy: 
	docker save waterproofpatch/pi-cam:latest > pi-cam.docker.tar

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

# update NPM libraries
update:
	# update NPM
	npm install -g npm
	(cd frontend && npm update --dev)

# remove artifacts
clean:
	rm -rf htmlcov .coverage uploads