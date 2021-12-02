#!/bin/bash
set -e
  

cd $1

echo 'Creating Migration'
python manage.py makemigrations

echo 'Applying Migration'
python manage.py migrate

echo 'Running server'
python manage.py runserver 0.0.0.0:8000