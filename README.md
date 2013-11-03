# SuttaCentral

[![Build Status](https://travis-ci.org/suttacentral/suttacentral.png?branch=master)](https://travis-ci.org/suttacentral/suttacentral)

Source code to [suttacentral.net](http://suttacentral.net/): early Buddhist texts, translations, and parallels.

## Setup

See the [wiki page](https://github.com/suttacentral/suttacentral/wiki/SuttaCentral-Dev-Setup).

## Running the Server

    make server

Then visit <http://localhost:8800/>.

## Deployment

To deploy changes to [staging](http://staging.suttacentral.net/):

    make deploy-staging

To deploy changes to [production](http://suttacentral.net/):

    make deploy-production
