#!/bin/bash

# directory dependencies
sudo mkdir -p /var/www/wsgi
sudo mkdir -p /var/www/html/cam
sudo mkdir -p /var/run/wsgi
sudo mkdir -p /var/log/wsgi

# copy frontend files
sudo cp -r dist/* /var/www/html

# copy site config for nginx
sudo cp -r nginx.site.conf /etc/nginx/sites-enabled/

# make these writable for wsgi
sudo chown -R pi:pi /var/log/wsgi
sudo chown -R pi:pi /var/run/wsgi

# correct permissions for nginx to serve
sudo chown -R www-data:www-data /var/www/html
sudo chown -R www-data:www-data /var/www/html/cam
sudo chown -R www-data:www-data /var/www/wsgi

# make cam writable so pi can write images to it
sudo chmod -R 770 /var/www/html/cam

source venv/bin/activate && pip install -r requirements.txt

