from __future__ import absolute_import
from celery import Celery
import sys

sys.dont_write_bytecode = True



app = Celery(
    'crawler'
    #,broker='redis://localhost'
    ,broker='amqp://es-processor.inl.io'
    ,include=['crawler.tasks'])

#app.config_from_object('celeryconfig')

if __name__ == '__main__':
    app.start()
