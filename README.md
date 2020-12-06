# PiCam

Template for setting up a simple RESTful API with authentication and backend models using Python's Flask microframework and VueJS for the frontend.

## Requirements

- a raspberry pi
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

### Build docker container

```bash
docker build . -t waterproofpatch/pi-cam
# test docker instance
docker run -p 8080:80 waterproofpatch/pi-cam
# save to tarball
docker save waterproofpatch/pi-cam:latest > pi-cam.docker.tar
```

### Deploy to Pi

```bash
make deploy
```

### Test UWSGI

```bash
uwsgi --socket 0.0.0.0:5000 --protocol=http --wsgi-file backend/app.py --callable app --virtualenv ./venv
# or using wsgi ini file
uwsgi --ini wsgi.ini
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
