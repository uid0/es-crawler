#!/bin/sh

POOLS=5
WORKERS=10
#ELASTICSEARCH_HOST=localhost celery multi start w1 w2 w3 --loglevel=DEBUG --pidfile=%n.pid --logfile=%n.log --quiet
LOGLEVEL=DEBUG

celery multi start $POOLS -c $WORKERS --quiet
celery -A crawler worker -l $LOGLEVEL -n %n.log --quiet
celery -A crawler worker -l $LOGLEVEL -n %n.log --quiet
celery -A crawler worker -l $LOGLEVEL -n %n.log --quiet
celery -A crawler worker -l $LOGLEVEL -n %n.log --quiet
celery -A crawler worker -l $LOGLEVEL -n %n.log --quiet
