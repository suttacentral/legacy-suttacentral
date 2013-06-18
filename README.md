# Python SuttaCentral

## Setup

Assumes a Python 3 `virtualenv` (e.g., `python` and `pip` pointing to a Python 3 environment)...

    pip install -r requirements.txt

## Start the server

    python app.py

## Deploy code to staging

    make deploy-staging

Then visit <http://staging.suttacentral.net/>.

# PHP SuttaCentral

## Deploy code to production

    make deploy-production

Then visit <http://php.suttacentral.net/>.

## Local development setup

**Assumes Apache, MySQL, and PHP are installed.**

### Create and load the database

    CREATE DATABASE suttacentral CHARACTER SET utf8;
    CREATE USER suttacentral@localhost IDENTIFIED BY '...';
    GRANT ALL PRIVILEGES ON suttacentral.* TO suttacentral@localhost;
    FLUSH PRIVILEGES;

### Clone the repository

    cd path/to/working/directory
    git clone git@git.suttacentral.net:suttacentral.git
    cd suttacentral
    git clone git@git.suttacentral.net:suttacentral-text.git text

### Setup the PHP-Database Connectivity

    cp php/includes/db.inc.php-example php/includes/db.inc.php

Then edit `php/includes/db.inc.php`.

### Setup the Apache config

    <VirtualHost *:80>
      ServerName suttacentral.local
      DocumentRoot /path/to/suttacentral/php
      <Directory /path/to/suttacentral/php>
        AllowOverride all
        Order allow,deny
        Allow from all
      </Directory>
    </VirtualHost>

### Restart Apache

    sudo apachectl restart
