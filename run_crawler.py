#!/usr/bin/env python2.7
#
#   Crawl the various MLS sources, sending the listings to be parsed to the Celery worker(s)
#

import os
if not os.environ.has_key('VIRTUAL_ENV'):
    raise EnvironmentError('Virtual environment not found. did you forget to source runtime/bin/activate?')

import sys
sys.path.append("./crawler")
sys.dont_write_bytecode = True


import sys, time, getopt

from crawler.celery import app
from crawler.config import Config
import importlib
#import crawler.crawlers
# TODO: Make getCrawler dynamically import crawler by name
from crawler.crawlers import listhub, carets

from crawler import tasks


def usage():
    print "Usage: %s --verbose --debug" % (sys.argv[0])

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:vd", ["help", 'debug', 'verbose'])
    except getopt.GetoptError as err:
        # print help information and exit:
        usage()
        #print str(err) # will print something like "option -a not recognized"
        sys.exit(2)

    context = {
        'verbose': False
        ,'debug': False
    }

    for o, a in opts:
        if o in ('-v', '--verbose'):
            context['verbose'] = True
        elif o in ('--debug'):
            context['debug'] = True
        else:
            usage()
            sys.exit(2)


    # esHost = Config.ELASTICSEARCH_HOST
    # esPort = Config.ELASTICSEARCH_PORT
    #
    # if os.environ.has_key('ELASTICSEARCH_HOST'):
    #     esHost = os.environ['ELASTICSEARCH_HOST']
    #
    # if os.environ.has_key('ELASTICSEARCH_PORT'):
    #     esPort = os.environ['ELASTICSEARCH_PORT']
    #
    # # Connect to ElasticSearch
    # es = Elasticsearch( [{"host": esHost, "port": esPort}] )

    #
    # # Index management:
    # # The main index, idx, is an alias to multiple seperate indexes. Do not explicitly attempt to create it as an index.
    # # One index per source, timestamped so that deleted/expired listings are removed automatically.
    # #
    # # alias: idx
    # #           \
    # #           |-- listhub_20140520
    # #           |-- carets_20140519
    # #           |-- iresret_20140520
    # #           |-- nwmls_20140518
    # #           |-- rmls_20140520
    # #           |-- raprets_20140520
    #
    # # 1) Create an index, for today, for each source
    # # 2) After crawling has finished, update the alias for each source to point
    #

    # Get the active sources (Listhub, CARETS, etc)
    def getCrawler(name):
        # TODO: dynamically import crawler
        #importlib.import_module("crawler.crawlers.%s" % name)
        #print globals()
        return globals()[name]

    # TODO: Allow the crawler to be specified from the command line
    # TODO: pull this from an as of now non-existent db table
    crawlers = []
    crawler = {
        'id': 1
        ,'name': 'listhub'
        ,'url': 'https://feeds.listhub.com/pickup/'
        #,'url': 'http://localhost/~stone/'
        ,'filename': 'myfeed.xml.gz'
        ,'username': ''
        ,'password': ''
        ,'last_crawled': ''
    }
    crawlers.append(crawler)

    crawler = {
        'id': 2
        ,'name': 'carets'
        ,'url': 'http://carets.retscure.com:6103/platinum/login'
        ,'filename': None
        ,'username': 'carets1234'
        ,'password': 'carets1234'
        ,'useragent': 'CARETS-General/1.0'
        ,'last_crawled': ''
    }
    crawlers.append(crawler)

    # crawler = {
    #     'id': 3
    #     ,'name': 'rmls'
    #     ,'url': 'http://rets.rmlsweb.com:6103/rets/login'
    #     ,'filename': None
    #     ,'username': 'DS44IN50'
    #     ,'password': 'DS1001IN123'
    #     ,'useragent': 'CARETS-General/1.0'
    #     ,'last_crawled': ''
    # }
    # crawlers.append(crawler)

    for crawler in crawlers:

        # TODO: Run each crawler in parallel to speed things up

        # Prep the information needed by each crawler:
        #   ElasticSearch Index Name, i.e., Listhub or carets

        crawler['idxname'] = '%s' % crawler['name']
        # es.indices.create(index=idxname, ignore=400)

        obj = getCrawler(crawler['name'])

        obj.crawl(context, crawler, tasks.index_listing)

        # Update crawler stats

        # Add new index to idx alias
        # es.indices.put_alias(name='idx', index=idxname)
        #
        # # Update the master idx alias to use this index, and remove any other indexes for this crawler
        # aliases = es.indices.get_alias(name='idx', index='%s_*' % (crawler['name']))
        # for idx in aliases:
        #     if idx != idxname:
        #         # Remove the old index
        #         es.indices.delete(index=idx, ignore=[400, 404])
        #         if context['verbose']:
        #             print 'Removing index %s' % (idx)
        #     else:
        #         if context['verbose']:
        #             print 'Leaving index %s' % (idx)
        #
        # None


if __name__ == "__main__":
    main()

