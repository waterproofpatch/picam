# PiCam

Template for setting up a simple RESTful API with authentication and backend models using Python's Flask microframework and VueJS for the frontend.

## Requirements

- eb `brew install eb`
- docker
- nginx
- uwsgi

## Development

Start the app in debug mode for testing

### Start the backend

```bash
source venv/bin/activate
python -m backend.app
```

### Start the frontend

```bash
(cd frontend && npm run serve)
```

## Production

Deploy to production using AWS Beanstalk and Docker Hub.

### Build docker container

```bash
docker build . -t waterproofpatch/vue-python-template
# test docker instance
docker run -p 8080:80 waterproofpatch/vue-python-template
# deploy to docker hub
docker push waterproofpatch/vue-python-template
```

### Deploy to AWS

```bash
make deploy
```

Then visit http://vuepythontemplate-env.ynepgp3pkf.us-west-2.elasticbeanstalk.com/#/

### Test UWSGI

```bash
uwsgi --socket 0.0.0.0:5000 --protocol=http --wsgi-file backend/app.py --callable app --virtualenv ./venv
# or using wsgi ini file
uwsgi --ini wsgi.ini
```

### EB Test

```bash
eb init -p docker vue-python-template
eb local run --port 5000
eb open
# then to deploy:
eb deploy VuePythonTemplate-env
```

## Pi Connection

IP: 192.168.1.189 

To discover:

```bash
sudo nmap -sn 192.168.1.0/24 > first.txt
```

Then look for a device with "Raspberry pi foundation"

```bash
ssh pi@192.168.1.189
```

