# SuttaCentral

## Dependencies

- MySQL
- Python 3.2+ and `virtualenv` (e.g., `python` and `pip` pointing to a Python 3 environment) (if developing the Python version)
- Apache + PHP (if developing the PHP version)

## Getting the repository

    cd path/to/working/directory
    git clone git@git.suttacentral.net:suttacentral.git
    cd suttacentral
    git clone git@git.suttacentral.net:suttacentral-text.git text

## Database Setup

Create the database as MySQL `root` (i.e., `mysql -u root`):

    CREATE DATABASE sc CHARACTER SET utf8;
    CREATE USER sc@localhost IDENTIFIED BY '...';
    GRANT ALL PRIVILEGES ON sc.* TO sc@localhost;
    FLUSH PRIVILEGES;

Then preload a database dump with:

    mysql -u sc -psc sc < sc.sql

Ask somebody on the project if you don't have a copy of the database.

**TODO: Auto-dump database and make available by URL.**

## Python SuttaCentral

### Setup

Install the required python packages:

    pip install -r requirements.txt

Copy `local.conf-example` to `local.conf` and update the `mysql` database settings.

### Start

    python server.py

## Deploy

    make deploy-staging

Then visit <http://staging.suttacentral.net/>.

## PHP SuttaCentral

### Setup

Create an Apache config for your local environment:

    <VirtualHost *:80>
      ServerName suttacentral.local
      DocumentRoot /path/to/suttacentral/php
      <Directory /path/to/suttacentral/php>
        AllowOverride all
        Order allow,deny
        Allow from all
      </Directory>
    </VirtualHost>

Copy `php/includes/db.inc.php-example` to `php/includes/db.inc.php` and update it accordingly.

## Restart Apache

    sudo apachectl restart

## Deploy

    make deploy-production

Then visit <http://php.suttacentral.net/>.
