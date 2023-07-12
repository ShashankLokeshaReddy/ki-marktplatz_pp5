#!/bin/bash

pip install -e /code
./django_prototype/wait-for-it.sh db:5432 -- python django_prototype/manage.py runserver 0.0.0.0:8000
