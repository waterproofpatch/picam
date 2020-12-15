# PiCam

Template for setting up a simple RESTful API with authentication and backend models using Python's Flask microframework and VueJS for the frontend.

## Requirements

- a raspberry pi
- nginx
- uwsgi

## Development

Install dependencies on Pi:

```bash
ssh pi@<pi_ip_address>
cd ~/workspace
sudo apt-get install libatlas-base-dev
source venv/bin/activate
pip install -r requirements.txt
```

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

### Deploy to Pi (also restarts web services)

```bash
make deploy
```

### Deploy and Start on Pi

```bash
# first time
ssh pi@192.168.1.189:~/workspace
source venv/bin/activate
pip install picamera
sudo adduser pi www-data

# every time
./deploy.sh
./start.sh
```

Configure crontab to execute the job on reboot:

```bash
@reboot /home/pi/workspace/deploy.sh && start.sh
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

## AWS Beanstalk

See 'picam'.

Following https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html
