__all__ = ["listhub", "carets"]
import urllib2
import os.path
import json
import md5
import urllib2
import tempfile
import os
import mimetypes

READ_BLOCK_SIZE = 1024*16


# TODO: Remove this class and refer to the app/isNowListed/Listing module, so crawler and inlv2 use the same object
class Listing(dict):

    def __init__(self, *args, **kw):

        # Define structure and set default values
        self['Price'] = None
        self['MlsNumber'] = None
        self['URL'] = None
        self['ProviderName'] = None
        self['ProviderURL'] = None
        self['ProviderCategory'] = None
        self['LeadRoutingEmail'] = None
        # self['Bedrooms'] = None
        # self['Bathrooms'] = None
        self['PropertyType'] = None
        self['PropertySubType'] = None


        self['PropertyAddress'] = {
            'Address': None
            , 'StreetNumber': None
            , 'StreetNumberModifier': None
            , 'StreetDirPrefix': None
            , 'StreetDirSuffix': None
            , 'StreetName': None
            , 'StreetSuffix': None
            , 'UnitNumber': None
            , 'City': None
            , 'State': None
            , 'ZipCode': None
            , 'ZipCodePlus4': None
            , 'County': None
            , 'Country': None
            , 'Latitude': 0.0
            , 'Longitude': 0.0
            , 'CrossStreets': None
            , 'LotLocation': None
        }

        self['Offices'] = []
        self['Brokerage'] = []

        self['Agents'] = []

        self['Photos'] = []
        self['Ammenities'] = {}

        super(Listing, self).__init__(*args, **kw)

    def __setitem__(self, key, value):
        # Throw an exception if the key isn't in the pre-defined list of valid keys

        super(Listing, self).__setitem__(key, value)

    def valid(self):
        # TODO: verify the data as much as possible
        if 'UID' not in self or self['UID'] is None:
            return 0

        # if 'mlsnumber' not in self or self['mlsnumber'] is None:
        #     return 0
        # if 'property_address' not in self:
        #     return 0
        # if 'zipCode' not in self['property_address'] or self['property_address']['zipCode'] is None:
        #     return 0
        # if 'price' in self and self['price'] > 0:
        #     return 1
        return 1

    def to_json(self):
        return json.dumps(self)


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
