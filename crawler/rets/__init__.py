# app/crawler/rets/__init__.py

import os, os.path
import requests
from requests.auth import HTTPDigestAuth
from xml.dom.minidom import parseString


class RetsResponse(dict):
    replyCode = False
    dom = None

    def __init__(self, data):
        if data:
            self.dom = parseString(data)

            # Get the reply code, to see if the request was successful
            self.replyCode = self._get_reply_code(self.dom.getElementsByTagName('RETS'))

    # Parse the xml.dom.nodelist
    def _get_reply_code(self, nodelist):
        if nodelist.length == 1:
            node = nodelist[0]
            return int(node.attributes['ReplyCode'].value)
        return False

    def _get_attribute_value(self, node, attr):
        if node:
            return node.attributes[attr].value
        else:
            return None

class RetsSearchResponse(RetsResponse):

    total_records = None
    delimiter = None
    rows = []

    def __init__(self, data):
        super(RetsSearchResponse, self).__init__(data)

        self.rows = []
        if self.dom:
            if self.replyCode == 0:

                # Parse the document to find out what kind of response it is.
                nodes = self.dom.getElementsByTagName('COUNT')
                if nodes.length == 1:
                    node = nodes[0]
                    self.records = int(self._get_attribute_value(node, 'Records'))

                # Get the delimiter
                nodes = self.dom.getElementsByTagName('DELIMITER')
                if nodes.length == 1:
                    node = nodes[0]
                    self.delimiter = chr(int(self._get_attribute_value(node, 'value')))

                # Get the columns
                columns = []
                nodes = self.dom.getElementsByTagName('COLUMNS')
                if nodes.length == 1:
                    node = nodes[0]
                    if node.hasChildNodes:
                        for col in node.firstChild.nodeValue.split(self.delimiter):
                            columns.append(col)

                # Parse the rows
                nodes = self.dom.getElementsByTagName('DATA')
                for node in nodes:
                    row = []
                    for field in node.firstChild.nodeValue.split(self.delimiter):
                        row.append(field)

                    # Build a dict of column -> value
                    self.rows.append(dict(zip(columns, row)))


class RetsLoginResponse(RetsResponse):
    # <RETS ReplyCode="0" ReplyText="V2.7.0 2964: Success">
    # <RETS-RESPONSE>
    # MemberName=CARETS TEST ACCOUNT
    # User=CARETSTEST, CARETS-ALLOW NO QUERIES:Login:System-CARETS:MDS Application Login:MDS Access Common, 90, CARETSTEST
    # Broker=CARETSTEST
    # MetadataVersion=1.12.33
    # MinMetadataVersion=1.1.1
    # OfficeList=CARETSTEST
    # TimeoutSeconds=1800
    # Action=http://ptest.mris.com:6103/cornerstone/get?Command=Message
    # Search=http://ptest.mris.com:6103/cornerstone/search
    # GetMetadata=http://ptest.mris.com:6103/cornerstone/getmetadata
    # Logout=http://ptest.mris.com:6103/cornerstone/logout
    # GetObject=http://ptest.mris.com:6103/cornerstone/getobject
    # Login=http://ptest.mris.com:6103/cornerstone/login
    # Get=http://ptest.mris.com:6103/cornerstone/get
    # </RETS-RESPONSE>
    # </RETS>

    def __init__(self, data):
        super(RetsLoginResponse, self).__init__(data)

        if self.dom:

            if self.replyCode == 0:
                # Parse the document to find out what kind of response it is.
                nodes = self.dom.getElementsByTagName('RETS-RESPONSE')
                if nodes.length >= 1:
                    node = nodes[0]
                    if node.hasChildNodes:
                        for line in node.firstChild.nodeValue.split("\n"):
                            pos = line.find('=')
                            key = line[0:pos]
                            val = line[pos+1:]
                            if len(key) > 0 and len(val) > 0:
                                self[key] = val

        None


class Rets():

    url = ''
    username = ''
    password = ''
    useragent = ''
    retsversion = 'RETS/1.7.2'

    session = None
    capabilities = None

    def login(self):

        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(self.username, self.password)
        self.session.headers.update({'User-Agent': self.useragent ,'RETS-Version': self.retsversion})

        request = self.session.get(self.url)
        self.capabilities = RetsLoginResponse(request.text)
        return True

    def download(self, context=None, config=None, offset=1, limit=500, toListingCallback=None, indexCallback=None):
        if self.session and self.capabilities:
            url = self.capabilities['Search']

            # Required: SearchType, Class

            # &Select= In this section of the query string enter the columns to display, separated by commas, with no spaces.
            # Offset=1 -- first query set to 1, use the count and Limit to retrieve data in batches

            # First request: Only get the count of records available (Count=2)
            query = '?Offset=%d&Limit=%d&QueryType=DMQL2&StandardNames=0&Count=2&Format=COMPACT-DECODED&SearchType=Property&Class=RES&Query=(ListingStatus=|ACTIVE)' % (offset, limit)
            r = self.session.get(url + query)
            resp = RetsSearchResponse(r.text)

            if context['verbose']:
                print "%d records found" % (resp.records)

            # Subsequent request(s): Fetch the next (n) properties, until we've reached the end
            for offset in xrange(1, resp.records, limit):
                query = '?Offset=%d&Limit=%d&QueryType=DMQL2&StandardNames=0&Count=1&Format=COMPACT-DECODED&SearchType=Property&Class=RES&Query=(ListingStatus=|ACTIVE)' % (offset, limit)

                r = self.session.get(url + query)

                resp = RetsSearchResponse(r.text)
                if indexCallback and toListingCallback:
                    for row in resp.rows:
                        # Get media records for the listing
                        # http://ptest.mris.com:6103/ptest/search?QueryType=DMQL2&StandardNames=0&Count=0&Format=COMP ACT-DECODED&SearchType=Media&Class=PROP_MEDIA&Query=(PropObjectKey=50005497282)
                        row['media'] = self.getMediaRecords(row['ListingKey'])
                        indexCallback.delay(context, config, toListingCallback(context, row))

                # HACK: Explicit teardown needed for some reason; rows doesn't seem to clear without it.
                resp.rows = []
                resp = None
                r = None

        return

    def getMediaRecords(self, key):
        if self.session and self.capabilities:
            url = self.capabilities['Search']

            query = '?QueryType=DMQL2&StandardNames=0&Count=0&Format=COMPACT-DECODED&SearchType=Media&Class=PROP_MEDIA&Query=(PropObjectKey=%s)' % key
            r = self.session.get(url + query)
            resp = RetsSearchResponse(r.text)
            return resp.rows

        return []

    def logout(self):
        if self.session and self.capabilities:
            logoutUrl = self.capabilities['Logout']
            r = self.session.get(logoutUrl)
        return True