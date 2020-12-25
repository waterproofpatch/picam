# LAN IP
PI_ADDRESS=192.168.1.189
# WAN IP
PI_ADDRESS=71.244.171.63
PI_SSH_PORT=59219
PI_USER=pi
PI_DIR=~/workspace
PI_FILES=deploy.sh \
		 requirements.txt \
		 nginx.site.conf \
		 wsgi.ini \
		 start.sh \
		 stop.sh \
		 frontend/dist/ \
		 backend/

.PHONY: test

# Build frontend files for deployment
build:
	(cd frontend && npm run build)

# Deploy to Pi
deploy: build
	scp -r -P $(PI_SSH_PORT) $(PI_FILES) $(PI_USER)@$(PI_ADDRESS):$(PI_DIR)
	ssh -t -p $(PI_SSH_PORT) $(PI_USER)@$(PI_ADDRESS) '(cd workspace && source venv/bin/activate && ./deploy.sh && ./start.sh)'

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
	rm -rf htmlcov .coverage images
