#!/bin/sh

POOLS=3
WORKERS=15

celery multi stop $POOLS -c $WORKERS

sleep 10

# HACK: DIE DIE DIE
ps auxww | grep 'crawler worker' |grep -v grep| awk '{print $2}'| xargs kill -9
ps auxww | grep 'celery worker' |grep -v grep| awk '{print $2}'| xargs kill -9
