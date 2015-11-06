Listhub and RETS crawler.
=====

## Introduction
This was written last year for a project that never really got off of the ground.  Since it was sitting in my source code directory, and I never really got paid for the project (that's another story altogether, I'm afraid), I decided to open source the code of the crawler and other components that were mine.

## Setting up the runtime

  ./install_requirements.sh
  ./create_runtime.sh
  ./run_crawler.sh

## Running the tests

  ./run_tests.sh

I make no claims that the tests actually work, but, it's honestly a great start, right?

## Reference Docs

* python : https://docs.python.org/2/
* elasticsearch : http://www.elasticsearch.org/guide/en/elasticsearch/client/python-api/current/
* celery : http://www.celeryproject.org/
* boto : https://github.com/boto/boto

