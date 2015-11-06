# crawler.crawlers.listhub.__init__.py
import zlib
import sys
import traceback
import re
import os, os.path
from .. import download, Listing
import resource
import md5

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

READ_BLOCK_SIZE = 1024*16
d = zlib.decompressobj(16 + zlib.MAX_WBITS) # this magic number can be inferred from the structure of a gzip file

# Compiling the regex saves a few cycles
listing_regex = re.compile('<Listing>(.*?)</Listing>')

def read_chunk (fh, size=READ_BLOCK_SIZE):
    """ Lazy function (generator) to read a file in chunks. Default chunk size is 1k."""
    while True:
        data = d.decompress(fh.read(size))
        #data = fh.read(size)
        if not data:
            break
        yield data

def crawl (context, config, callback):
    tmpfile = '/tmp/govlisted.xml.gz'

    if not context['debug']:
        if os.path.isfile(tmpfile):
            os.remove(tmpfile)

    if download(context=context, url=config['url'] + config['filename'], file=tmpfile, username=config['username'], password=config['password']):

        fh = open(tmpfile, 'r')
        buffer = ''

        count = 0
        for chunk in read_chunk(fh):
            buffer += chunk

            # Keep parsing the chunk until we've parsed out all the listings
            while True:

                (buffer, listing) = parse_chunk(context, buffer)
                if listing:
                    count += 1

                    if context['verbose']:
                        if count % 1000 == 0:
                            print count
                            # sys.stdout.write('.')
                            # sys.stdout.flush()

                    callback.delay(context, config, listing)
                    None
                else:
                    break

            # if context['verbose']:
            #     print 'Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        fh.close()
        #os.remove(tmpfile)
    else:
        print "Unable to download %s" % (tmpfile)
    None

def parse_chunk (context, chunk):
    # parse out elements of the xml we're looking for, returning the part of the chunk we're keeping

    # Grab everything between <Listing></Listing>. If there's no matches, it's an incomplete chunk; return it
    match = listing_regex.search(chunk)
    if match:
        listing_xml = match.group(0)
        #print "listing xml length: %d" % (len(listing_xml))

        l = parse_listing_xml(context, listing_xml)

        # Return the unused portion of the chunk
        return (chunk[len(listing_xml):], l)
    else:
        return (chunk, None)

def parse_listing_xml (context, fragment):
    # Pros and cons of using a xml parser vs. regex:
    #   parser's may be faster, using underlying libraries written in C
    #   parser's try to build a tree, which consumes more resources
    #   parser's don't work so well against fragments

    # Parse the xml fragment
    try:
        # HACK: ET handles namespaces clumbsily, but it's fast
        # HACK: so we'll work around the namespacing for now
        # TODO: See if there's a better way to handle namespacing
        # TODO: using register_namespace and namespace:tag
        ns = 'http://rets.org/xsd/Syndication/2012-03'
        ns_commons = 'http://rets.org/xsd/RETSCommons'

        # Parse the xml fragment
        xml = '<?xml version="1.0"?><Listings xmlns:commons="http://rets.org/xsd/RETSCommons" xmlns="http://rets.org/xsd/Syndication/2012-03" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:schemaLocation="http://rets.org/xsd/Syndication/2012-03/Syndication.xsd" xml:lang="en-us" version="0.96">' + fragment + '</Listings>'
        root = ET.fromstring(xml)

        listing = Listing()

        el_listing = root[0]
        if el_listing:
            ###################
            # Brokerage block #
            ###################
            el_brokerage = get_ns_element(el_listing, ns, 'Brokerage')
            if el_brokerage:
                brokerage = {}

                el_brokerage_address = get_ns_element(el_brokerage, ns, 'Address')
                if el_brokerage_address is not None:
                    brokerage['Address'] = parse_address( el_brokerage_address, ns_commons )

                brokerage['Email'] = get_ns_element_value(el_brokerage, ns, 'Email')
                brokerage['Fax'] = get_ns_element_value(el_brokerage, ns, 'Fax')
                brokerage['LogoUrl'] = get_ns_element_value(el_brokerage, ns, 'LogoURL')
                brokerage['Name'] = get_ns_element_value(el_brokerage, ns, 'Name')
                brokerage['Phone'] = get_ns_element_value(el_brokerage, ns, 'Phone')
                brokerage['Url'] = get_ns_element_value(el_brokerage, ns, 'WebsiteURL')

                listing['Brokerage'] = brokerage

            #################
            # Address block #
            #################
            el_address = get_ns_element(el_listing, ns, 'Address')
            if el_address:
                listing['PropertyAddress'] = parse_address( el_address, ns_commons )

                el_location = get_ns_element(el_listing, ns, 'Location')
                if el_location is not None:
                    listing['PropertyAddress']['Latitude'] =  get_ns_element_value(el_location, ns, 'Latitude')
                    listing['PropertyAddress']['Longitude'] =  get_ns_element_value(el_location, ns, 'Longitude')
                    listing['PropertyAddress']['County'] =  get_ns_element_value(el_location, ns, 'County')

                # TODO: geo data may be provided but is hand-typed. If it's present,
                # we should use it, otherwise we'll need to calculate/look up the info

            #################
            # Offices block #
            #################
            listing['Offices'] = []
            el_offices = get_ns_element(el_listing, ns, 'Offices')
            if el_offices is not None:
                for el in el_offices:
                    office = {}

                    el_address = get_ns_element(el, ns, 'Address')
                    if el_address is not None:
                        office['Address'] = parse_address( el_address, ns_commons )

                    # if el.getElementsByTagName('Address'):
                    #     office['Address'] = parse_address( el.getElementsByTagName('Address')[0] )

                    office['ID'] = get_ns_element_value(el, ns, 'OfficeId')
                    office['BrokerID'] = get_ns_element_value(el, ns, 'BrokerId')
                    office['MainOfficeID'] = get_ns_element_value(el, ns, 'MainOfficeId')

                    office['Key'] = get_ns_element_value(el, ns, 'OfficeKey')

                    office['CorporateName'] = get_ns_element_value(el, ns, 'CorporateName')
                    office['Name'] = get_ns_element_value(el, ns, 'Name')

                    office['Email'] = get_ns_element_value(el, ns, 'OfficeEmail')
                    office['Phone'] = get_ns_element_value(el, ns, 'PhoneNumber')
                    office['Fax'] = get_ns_element_value(el, ns, 'Fax')
                    office['URL'] = get_ns_element_value(el, ns, 'Website')

                    # TODO: OfficeCode
                    office['Code'] = []


                    listing['Offices'].append(office)


            ######################
            # Participants block #
            ######################
            listing['Agents'] = []

            el_participants = get_ns_element(el_listing, ns, 'ListingParticipants')
            if el_participants is not None:
                for el in el_participants:
                    participant = {}

                    el_address = get_ns_element(el, ns, 'Address')
                    if el_address is not None:
                        participant['Address'] = parse_address( el_address, ns_commons )

                    participant['Email'] = get_ns_element_value(el, ns, 'Email')

                    participant['Fax'] = get_ns_element_value(el, ns, 'Fax')
                    participant['PreferredFax'] = participant['Fax']

                    participant['FirstName'] = get_ns_element_value(el, ns, 'FirstName')
                    participant['LastName'] = get_ns_element_value(el, ns, 'LastName')

                    # TODO: Licenses

                    participant['ID'] = get_ns_element_value(el, ns, 'ParticipantId')
                    participant['Key'] = get_ns_element_value(el, ns, 'ParticipantKey')
                    participant['PreferredPhone'] = get_ns_element_value(el, ns, 'PrimaryContactPhone')
                    participant['Role'] = get_ns_element_value(el, ns, 'Role')
                    participant['URL'] = get_ns_element_value(el, ns, 'WebsiteURL')

                    listing['Agents'].append(participant)


            ################
            # Photos block #
            ################
            el_photo = get_ns_element(el_listing, ns, 'Photos')
            if el_photo is not None:
                listing['Photos'] = []
                for el in el_photo:
                    url = get_ns_element_value(el, ns, 'MediaURL')

                    # TODO: Add multi-download to speed this up
                    #s3url = save_to_s3(context=context, url=url)
                    s3url = None

                    timestamp = get_ns_element_value(el, ns, 'MediaModificationTimestamp')

                    listing['Photos'].append({'URL': url, 'S3URL': s3url, 'Timestamp': timestamp})

            ########################
            # All other attributes #
            ########################
            # listing['listing_source_id'] = 1

            # Not all listings will have MlsNumber (FSBO, for example). IfFSBO
            listing['MlsNumber'] = get_ns_element_value(el_listing, ns, 'MlsNumber')

            listing['ListPrice'] = get_ns_element_value(el_listing, ns, 'ListPrice')

            # Generate a unique id for this listing, based on mls number + zip, or ListingKey.
            # This will be used for indexing the Listing in ElasticSearch
            listing['UID'] = get_ns_element_value(el_listing, ns, 'ListingKey')

            listing['ListingURL'] = get_ns_element_value(el_listing, ns, 'ListingURL')
            listing['ListingStatus'] = get_ns_element_value(el_listing, ns, 'ListingStatus')

            listing['ProviderName'] = get_ns_element_value(el_listing, ns, 'ProviderName')
            listing['ProviderURL'] = get_ns_element_value(el_listing, ns, 'ProviderURL')
            listing['ProviderCategory'] = get_ns_element_value(el_listing, ns, 'ProviderCategory')

            listing['LeadRoutingEmail'] = get_ns_element_value(el_listing, ns, 'LeadRoutingEmail')
            listing['PropertyType'] = get_ns_element_value(el_listing, ns, 'PropertyType')
            listing['PropertySubType'] = get_ns_element_value(el_listing, ns, 'PropertySubType')

            listing['YearBuilt'] = get_ns_element_value(el_listing, ns, 'YearBuilt')
            listing['LotSize'] = get_ns_element_value(el_listing, ns, 'LotSize')
            listing['Description'] = get_ns_element_value(el_listing, ns, 'ListingDescription')
            listing['SqFeet'] = get_ns_element_value(el_listing, ns, 'LivingArea')


            # Add as many of the attributes as possible.
            listing['Amenities'] = {}
            el_attributes = get_ns_element(el_listing, ns, 'DetailedCharacteristics')
            if el_attributes is not None:

                listing['Amenities']['BuildingUnitCount'] =  get_ns_element_value(el_attributes, ns, 'BuildingUnitCount')
                listing['Amenities']['CondoFloorNum'] =  get_ns_element_value(el_attributes, ns, 'CondoFloorNum')
                listing['Amenities']['HasAttic'] =  get_ns_element_value(el_attributes, ns, 'HasAttic')
                listing['Amenities']['HasBarbecueArea'] =  get_ns_element_value(el_attributes, ns, 'HasBarbecueArea')
                listing['Amenities']['HasBasement'] =  get_ns_element_value(el_attributes, ns, 'HasBasement')
                listing['Amenities']['HasCeilingFan'] =  get_ns_element_value(el_attributes, ns, 'HasCeilingFan')
                listing['Amenities']['HasDeck'] =  get_ns_element_value(el_attributes, ns, 'HasDeck')
                listing['Amenities']['HasDisabledAccess'] =  get_ns_element_value(el_attributes, ns, 'HasDisabledAccess')
                listing['Amenities']['HasDock'] =  get_ns_element_value(el_attributes, ns, 'HasDock')
                listing['Amenities']['HasDoorman'] =  get_ns_element_value(el_attributes, ns, 'HasDoorman')
                listing['Amenities']['HasDoublePaneWindows'] =  get_ns_element_value(el_attributes, ns, 'HasDoublePaneWindows')
                listing['Amenities']['HasElevator'] =  get_ns_element_value(el_attributes, ns, 'HasElevator')
                listing['Amenities']['HasFireplace'] =  get_ns_element_value(el_attributes, ns, 'HasFireplace')
                listing['Amenities']['HasGarden'] =  get_ns_element_value(el_attributes, ns, 'HasGarden')
                listing['Amenities']['HasGatedEntry'] =  get_ns_element_value(el_attributes, ns, 'HasGatedEntry')
                listing['Amenities']['HasGreenhouse'] =  get_ns_element_value(el_attributes, ns, 'HasGreenhouse')
                listing['Amenities']['HasHotTubSpa'] =  get_ns_element_value(el_attributes, ns, 'HasHotTubSpa')
                listing['Amenities']['HasJettedBathTub'] =  get_ns_element_value(el_attributes, ns, 'HasJettedBathTub')
                listing['Amenities']['HasLawn'] =  get_ns_element_value(el_attributes, ns, 'HasLawn')
                listing['Amenities']['HasMotherInLaw'] =  get_ns_element_value(el_attributes, ns, 'HasMotherInLaw')
                listing['Amenities']['HasPatio'] =  get_ns_element_value(el_attributes, ns, 'HasPatio')
                listing['Amenities']['HasPond'] =  get_ns_element_value(el_attributes, ns, 'HasPond')
                listing['Amenities']['HasPool'] =  get_ns_element_value(el_attributes, ns, 'HasPool')
                listing['Amenities']['HasPorch'] =  get_ns_element_value(el_attributes, ns, 'HasPorch')
                listing['Amenities']['HasRVParking'] =  get_ns_element_value(el_attributes, ns, 'HasRVParking')
                listing['Amenities']['HasSauna'] =  get_ns_element_value(el_attributes, ns, 'HasSauna')
                listing['Amenities']['HasSecuritySystem'] =  get_ns_element_value(el_attributes, ns, 'HasSecuritySystem')
                listing['Amenities']['HasSkylight'] =  get_ns_element_value(el_attributes, ns, 'HasSkylight')
                listing['Amenities']['HasSportsCourt'] =  get_ns_element_value(el_attributes, ns, 'HasSportsCourt')
                listing['Amenities']['HasSprinklerSystem'] =  get_ns_element_value(el_attributes, ns, 'HasSprinklerSystem')
                listing['Amenities']['HasVaultedCeiling'] =  get_ns_element_value(el_attributes, ns, 'HasVaultedCeiling')
                listing['Amenities']['HasWetBar'] =  get_ns_element_value(el_attributes, ns, 'HasWetBar')
                listing['Amenities']['Intercom'] =  get_ns_element_value(el_attributes, ns, 'Intercom')
                listing['Amenities']['IsCableReady'] =  get_ns_element_value(el_attributes, ns, 'IsCableReady')
                listing['Amenities']['IsNewConstruction'] =  get_ns_element_value(el_attributes, ns, 'IsNewConstruction')
                listing['Amenities']['IsWaterfront'] =  get_ns_element_value(el_attributes, ns, 'IsWaterfront')
                listing['Amenities']['IsWired'] =  get_ns_element_value(el_attributes, ns, 'IsWired')
                listing['Amenities']['LegalDescription'] =  get_ns_element_value(el_attributes, ns, 'LegalDescription')
                listing['Amenities']['NumFloors'] =  get_ns_element_value(el_attributes, ns, 'NumFloors')
                listing['Amenities']['NumParkingSpaces'] =  get_ns_element_value(el_attributes, ns, 'NumParkingSpaces')
                listing['Amenities']['RoomCount'] =  get_ns_element_value(el_attributes, ns, 'RoomCount')
                listing['Amenities']['YearUpdated'] =  get_ns_element_value(el_attributes, ns, 'YearUpdated')

                ########################################################
                # Get the attributes that contain a list of attributes #
                ########################################################
                def get_attributes(el, parentName):
                    attribs = []
                    elem = get_ns_element(el, ns, parentName)
                    if elem is not None:
                        for child in elem:
                            attribs.append(child.text)
                    return attribs

                listing['Amenities']['Appliances'] = get_attributes(el_attributes, 'Appliances')
                listing['Amenities']['ArchitectureStyle'] = get_attributes(el_attributes, 'ArchitectureStyle')
                listing['Amenities']['CoolingSystems'] = get_attributes(el_attributes, 'CoolingSystems')
                listing['Amenities']['ExteriorTypes'] = get_attributes(el_attributes, 'ExteriorTypes')
                listing['Amenities']['FloorCoverings'] = get_attributes(el_attributes, 'FloorCoverings')
                listing['Amenities']['HeatingFuels'] = get_attributes(el_attributes, 'HeatingFuels')
                listing['Amenities']['HeatingSystems'] = get_attributes(el_attributes, 'HeatingSystems')
                listing['Amenities']['ParkingTypes'] = get_attributes(el_attributes, 'ParkingTypes')
                listing['Amenities']['RoofTypes'] = get_attributes(el_attributes, 'RoofTypes')
                listing['Amenities']['Rooms'] = get_attributes(el_attributes, 'Rooms')
                listing['Amenities']['ViewTypes'] = get_attributes(el_attributes, 'ViewTypes')


            listing['Amenities']['BedroomsTotal'] = get_ns_element_value(el_listing, ns, 'Bedrooms')
            listing['Amenities']['BathsTotal'] = get_ns_element_value(el_listing, ns, 'Bathrooms')

        #print listing

        #if listing.valid():
        return listing
    except Exception, e:
        #print "Unable to parse XML data from string: %" % e
        print e
        #print fragment
        traceback.print_stack()
        sys.exit()

    return None


# It seems stupid to have to do this, but if we only need an element that, by
# schema, only exists "zeroOrOne", this is cleaner.
def get_ns_element(el, ns, name):
    nsname = '{%s}%s' % (ns, name)
    return el.find(nsname)

# Parses a parent level Address element
# See http://app.listhub.com/syndication-docs/rets2012.html#elements_/Listings/Listing/Address
def parse_address (el, ns):
    address = {}
    address['Address'] = get_ns_element_value(el, ns, 'FullStreetAddress')
    address['UnitNumber'] = get_ns_element_value(el, ns, 'UnitNumber')
    address['City'] = get_ns_element_value(el, ns, 'City')
    address['State'] = get_ns_element_value(el, ns, 'StateOrProvince')
    address['ZipCode'] = get_ns_element_value(el, ns, 'PostalCode')
    address['Country'] = get_ns_element_value(el, ns, 'Country')
    return address

def get_ns_element_value (el, ns, name):
    nsname = '{%s}%s' % (ns, name)
    element = el.find(nsname)
    if element is not None:
        return element.text
    return None
