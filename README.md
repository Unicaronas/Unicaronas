[![Build Status](https://travis-ci.com/Unicaronas/my.svg?branch=master)](https://travis-ci.com/Unicaronas/Unicaronas)

[![forthebadge](https://forthebadge.com/images/badges/contains-technical-debt.svg)](https://forthebadge.com)

# Unicaronas

This website serves 5 purposes:
- Allow users to sign up to the service
- Allow users to edit their preferences
- Allow users to create and edit applications
- Serve as an oauth2 authorization server for applications created by the users
- Serve as the resource server for the API used by said applications

## Requirements
- Python 3.x
- Django 2.x
- Postgres >= 9
- [PostGIS](https://postgis.net/)
- Redis

## Preparations
You'll need an API key for the [Geocoding API](https://developers.google.com/maps/documentation/geocoding/intro) from Google

You'll also need API keys and/or secrets from the following APIs:
- [Google reCaptcha](https://www.google.com/recaptcha/intro/v3beta.html)
- [BlaBlaCar](https://dev.blablacar.com/docs/versions/1.0)
- [AWS access key, Secret and a bucket](https://aws.amazon.com/)

Finally, if you want to enable social sign-in, get OAuth2 credentials from Google, Facebook or Github

## Installation
Clone the repo, set up your [virtualenv](https://virtualenv.pypa.io/en/stable/) and run `pip install -r requirements.txt`.

Then run `python initialize.py` and answer the questions.

## Usage
After everything is set up, configure your superuser by running `python manage.py createsuperuser`.

Then run the app with `./run.sh` and go to `localhost:8000/admin/`.

There you can configure your site at the `Sites` model and your social logins as social accounts model.

Done!

# Deploying to Heroku
You can also deploy to Heroku


[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
