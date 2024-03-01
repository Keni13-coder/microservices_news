#!/bin/bash

if [[ "${1}" == "celery" ]]; then
    celery -A background_celery.app_celery:celery worker --loglevel=INFO --logfile=./logs/celery.log --pool=solo
elif [[ "${1}" == "flower" ]]; then
    celery -A background_celery.app_celery:celery flower
    fi