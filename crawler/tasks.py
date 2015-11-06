from __future__ import absolute_import
import sys
sys.dont_write_bytecode = True

from crawler.celery import app

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.exception import S3CreateError
import md5
import tempfile
import mimetypes
import urllib2
import os.path
import json
import os


import logging
from elasticsearch import Elasticsearch
from crawler.config import Config

esHost = Config.ELASTICSEARCH_HOST
esPort = Config.ELASTICSEARCH_PORT

if os.environ.has_key('ELASTICSEARCH_HOST'):
    esHost = os.environ['ELASTICSEARCH_HOST']

if os.environ.has_key('ELASTICSEARCH_PORT'):
    esPort = os.environ['ELASTICSEARCH_PORT']

tracer = logging.getLogger('elasticsearch.trace')
tracer.setLevel(logging.DEBUG)
tracer.addHandler(logging.FileHandler('/tmp/elasticsearch-%d-py.sh' % os.getpid()))

READ_BLOCK_SIZE = 1024*16

s3conn = None
s3bucket = None

@app.task(name='crawler.tasks.index_listing')
def index_listing (context, crawler, listing):
    # sys.stdout.write('index_listing called!')
    # return

    if listing and listing.valid():
        doc = listing.to_json()

        # id -- Based on mlsid + zip code, so we replace listings instead of creating duplicates
        # m = md5.new(listing['mlsnumber'] + listing['property_address']['zipCode'])
        #
        # docid = m.hexdigest()
        #
        # Each parser will generate a listing-specific ID to be used for indexing
        docid = listing['UID']

        # Cache the images from this listing
        try:
            for photo in listing['Photos']:

                s3url = save_to_s3(context=context, url=photo['URL'])
                #s3url = None
                # TODO: Index dimensions and size of image and add to photo dict
                photo['S3URL'] = s3url

        # Connect to ElasticSearch
            global esHost, esPort
            es = Elasticsearch( [{"host": esHost, "port": esPort}] )

            res = es.index(index=crawler['idxname'], doc_type='listing', body=doc, id=docid)
            if res['created']:
                print "Document %s indexed." % docid
            else:
                print "Document %s updated." % docid
        except:
            e = sys.exc_info()[0]
            # TODO: Add a timestamp
            f = open('exceptions.log')
            f.write(e)
            f.close()
            print "Error: %s" % e
            #sys.exit(1)
        # If the document is already indexed, the old one will be deleted and the new indexed in its place
        # if context['verbose']:
        #     if res['created']:
        #         sys.stdout.write('.')
        #     else:
        #         sys.stdout.write('|')

    else:
        None
        # if context['verbose']:
        #     sys.stdout.write('x')
        #     print listing
            #sys.exit(1)
        # TODO: Add some kind of logging for invalid listings, so they can be investigated (bad data or bad parser?)

    # if context['verbose']:
    #     sys.stdout.flush()
    None

def connect_to_s3(bucketName):
    conn = S3Connection(Config.AMAZON_ACCESS_KEY, Config.AMAZON_SECRET_KEY)
    bucket = conn.get_bucket(bucketName)
    return (conn, bucket)

def get_s3_url(bucketName=None, key=None):
    if bucketName and hash:
        conn = S3Connection(Config.AMAZON_ACCESS_KEY, Config.AMAZON_SECRET_KEY)
        bucket = conn.get_bucket(bucketName)
        k = Key(bucket)
        k.key = key
        return k.generate_url(expires_in=0, query_auth=False, force_http=True)

def get_s3_key(url=None):
    if url:
        return md5.new(url).hexdigest()



def save_to_s3(context=None, bucketName=None, hash=None, url=None, file=None, metadata={}):

    global s3conn, s3bucket

    # Connect if this is the first time
    if s3conn is None or s3bucket is None:
        # (s3conn, s3bucket) = connect_to_s3 (bucketName)
        s3conn = S3Connection(Config.AMAZON_ACCESS_KEY, Config.AMAZON_SECRET_KEY)
        if bucketName:
            s3bucket = s3conn.get_bucket(bucketName)
        else:
            s3bucket = s3conn.get_bucket(Config.AMAZON_S3_BUCKET)

    tries = 3
    retries = 0
    while True:
        try:

            s3url = None

            if s3conn and s3bucket:
                # Unique key -- probably a hash of source id, Listing id, and media key
                if not hash and url:
                    # Calculate the hash based on the url
                    hash = md5.new(url).hexdigest()
                else:
                    None

                # Don't upload if this hash already exists
                if s3bucket.get_key(hash):
                    return True

                ####################################
                # Create and store a new S3 object #
                ####################################
                k = Key(s3bucket)

                k.key = hash

                # Add metadata, if any.
                if metadata:
                    for key in metadata:
                        k.set_metadata(key, metadata[key])

                # TODO: Set permissions, so all can open/download
                default_policy = 'public-read'

                if file:
                    # Attempt to guess the mimetype
                    mime = mimetypes.guess_type(url, strict=True)
                    if (mime[0]):
                        k.set_metadata('Content-Type', mime[0])

                    k.set_contents_from_filename(file, policy=default_policy)
                elif url:
                    tmpFile = tempfile.NamedTemporaryFile(delete=False)
                    # Get the mime type of the downloaded file, since we may not be able to guess from the file name
                    d = download(context, url, tmpFile.name)
                    if d['success']:
                        k.set_metadata('Content-Type', d['mimeType'][0])
                        bytesWritten = k.set_contents_from_filename(tmpFile.name, policy=default_policy)
                        os.unlink(tmpFile.name)
                else:
                    k.set_contents_from_string('')

                return k.generate_url(expires_in=0, query_auth=False, force_http=True)
            else:
                # Reconnect and retry
                print "Not connected; retrying"
        except S3CreateError:
            # S3CreateError: 409 Conflict
            # <?xml version="1.0" encoding="UTF-8"?>
            # <Error><Code>OperationAborted</Code><Message>A conflicting conditional operation is currently in progress against this resource. Please try again.</Message><RequestId>CB641156214B1D46</RequestId><HostId>JV/2q+uV3uFhdXomsnZt+B8yak5/g7MuL2725PnqcipLAZFfU4nhkU3Pq2p7c/z+</HostId></Error>
            # Retry the operation, but abort if it keeps failing
            if retries > tries:
                if context['verbose']:
                    print "S3CreateError: 409 Conflict (aborting)"
                break
            else:
                if context['verbose']:
                    print "S3CreateError: 409 Conflict (retrying)"
                retries += 1
                continue
        break

def download(context, url, file, username=None, password=None):

    retval = {
        'success': False
        ,'mimeType': None
    }

    # Dev hack: don't redownload the file
    if os.path.isfile(file):
        # Verify the file has size
        statinfo = os.stat(file)
        if statinfo.st_size > 0:
            retval['success'] = True
            return retval

    if context['verbose']:
        print "Opening url %s" % url

    if username and password:
        authmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        authmgr.add_password(
            realm = None
            ,uri = url
            ,user = username
            ,passwd = password
        )

        authhandler = urllib2.HTTPBasicAuthHandler(authmgr)
        opener = urllib2.build_opener(authhandler)

        urllib2.install_opener(opener)

    req = urllib2.urlopen(url)
    meta = req.info()
    # print meta
    # file_size = int(meta.getheaders("Content-Length")[0])

    retval['mimeType'] = meta.getheaders("Content-Type")

    file_size_dl = 0
    if file:
        fh = open(file, 'wb')
        buffer = ''
        while True:
            buffer = req.read(READ_BLOCK_SIZE)
            file_size_dl += len(buffer)
            if not buffer:
                break
            fh.write(buffer)

            # if context and context['debug']:
            #     status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            #     status = status + chr(8)*(len(status)+1)
            #     print status,

        fh.close()
        retval['success'] = True
        return retval
    return retval