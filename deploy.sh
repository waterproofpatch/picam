#!/bin/bash

sudo mkdir -p /var/www/wsgi
sudo cp -r dist/* /var/www/html
sudo cp -r nginx.site.conf /etc/nginx/sites-enabled/
sudo chown -R www-data:www-data /var/www/html
sudo chown -R www-data:www-data /var/www/wsgi
