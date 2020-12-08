#!/bin/bash

sudo mkdir -p /var/www/wsgi
sudo mkdir -p /var/run/wsgi
sudo mkdir -p /var/log/wsgi

sudo cp -r dist/* /var/www/html
sudo cp -r nginx.site.conf /etc/nginx/sites-enabled/

sudo chown -R pi:pi /var/log/wsgi
sudo chown -R pi:pi /var/run/wsgi

sudo chown -R www-data:www-data /var/www/html
sudo chown -R www-data:www-data /var/www/wsgi

