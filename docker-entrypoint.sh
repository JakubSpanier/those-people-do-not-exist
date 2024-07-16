#!/bin/bash

echo "Apply database migrations"
python manage.py migrate

echo "Downloading the human images"
python manage.py downloadhumanimages 21

echo "Starting server"
python manage.py runserver 0.0.0.0:8000