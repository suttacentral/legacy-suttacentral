# SuttaCentral

# Setup

## Dependencies

- Python 3.3+
- Python virtualenv (i.e., `python` and `pip` pointing to a Python 3.3+ environment)
- MySQL 5.5+
- Apache + PHP (if developing on the PHP version)

## Repository

    cd path/to/working/directory
    git clone git@git.suttacentral.net:suttacentral.git
    cd suttacentral
    git clone git@git.suttacentral.net:suttacentral-text.git text

## Requirements

    pip install -r requirements.txt

## Configuration

Copy `local.conf-example` to `local.conf` and edit accordingly. If you're
starting from scratch, you probably don't need edit anything as the
defaults are suitable.

## Database

Create a database user:

    make create-db-user

Set its authorization:

    make setup-db-auth

Fetch a copy of the latest database dump:

    make fetch-db-export

Create the database:

    make create-db

Load the database dump into the database:

    make load-db

# Developing

## Running the Server

    make server

Then visit <http://localhost:8800/>.

## Making Changes

**TODO: git stuff in here?**

## Deployment

    make deploy-staging

Then visit <http://staging.suttacentral.net/>.

# PHP Setup

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

## Deployment

    make deploy-production

Then visit <http://php.suttacentral.net/>.
