import re
import sys, traceback, inspect

# Use relative imports from within a module, for reasons.
# http://axialcorps.com/2013/08/29/5-simple-rules-for-building-great-python-packages/
from .. import datatypes

from xml.dom.minidom import parseString


# Compiling the regex saves a few cycles
listing_regex = re.compile('<Listing>(.*?)</Listing>')


def parse_chunk (chunk):
    # parse out elements of the xml we're looking for, returning the part of the chunk we're keeping
    
    # Grab everything between <Listing></Listing>. If there's no matches, it's an incomplete chunk; return it
    match = listing_regex.search(chunk)
    if match:
        listing_xml = match.group(0)
        
        l = parse_listing_xml(listing_xml)

        # Return the unused portion of the chunk
        return (chunk[len(listing_xml):], l)
    else:
        return (chunk, None)

def parse_listing_xml (fragment):
    # Pros and cons of using a xml parser vs. regex:
    #   parser's may be faster, using underlying libraries written in C
    #   parser's try to build a tree, which consumes more resources
    #   parser's don't work so well against fragments

    # Parse the xml fragment
    try:
        dom = parseString('<?xml version="1.0"?><Listings xmlns:commons="http://rets.org/xsd/RETSCommons" xmlns="http://rets.org/xsd/Syndication/2012-03" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:schemaLocation="http://rets.org/xsd/Syndication/2012-03/Syndication.xsd" xml:lang="en-us" version="0.96">' + fragment + '</Listings>')
        
        listing = datatypes.listing.Listing()
    
        el_listing = get_element(dom, 'Listing')
        if el_listing:
            ###################
            # Brokerage block #
            ###################
            el_brokerage = get_element(el_listing, 'Brokerage')
            if el_brokerage:
                brokerage = {}
                if el_brokerage.getElementsByTagName('Address'):
                    brokerage['address'] = parse_address( el_brokerage.getElementsByTagName('Address')[0] )
            
                brokerage['email'] = get_element_value(el_brokerage, 'Email')
                brokerage['fax'] = get_element_value(el_brokerage, 'Fax')
                brokerage['logo_url'] = get_element_value(el_brokerage, 'LogoURL')
                brokerage['name'] = get_element_value(el_brokerage, 'Name')
                brokerage['phone'] = get_element_value(el_brokerage, 'Phone')
                brokerage['url'] = get_element_value(el_brokerage, 'WebsiteURL')
                
                listing['brokerage'] = brokerage
            
            #################
            # Address block #
            #################
            el_address = get_element(el_listing, 'Address')
            if el_address:
                listing['property_address'] = parse_address( el_address )
            
                # TODO: geo data may be provided but is hand-typed. If it's present, 
                # we should use it, otherwise we'll need to calculate/look up the info
                    
            #################
            # Offices block #
            #################
            listing['offices'] = []
            el_offices = get_element(el_listing, 'Office')
            if el_offices:
                for el in el_offices.childNodes:
                    office = {}
                    if el.getElementsByTagName('Address'):
                        office['address'] = parse_address( el.getElementsByTagName('Address')[0] )
                    
                    office['broker_id'] = get_element_value(el, 'BrokerId')
                    office['corporate_name'] = get_element_value(el, 'CorporateName')
                    office['fax'] = get_element_value(el, 'Fax')
                    office['main_office_id'] = get_element_value(el, 'MainOfficeId')
                    office['name'] = get_element_value(el, 'Name')
            
                    # TODO: OfficeCode
                    office['code'] = []
                
                    office['email'] = get_element_value(el, 'OfficeEmail')
                    office['id'] = get_element_value(el, 'OfficeId')
                    office['key'] = get_element_value(el, 'OfficeKey')
                    office['phone'] = get_element_value(el, 'PhoneNumber')
                    office['url'] = get_element_value(el, 'Website')
                    
                    listing['offices'].append(office)
            
                    
            ######################
            # Participants block #
            ######################
            listing['participants'] = []
                    
            el_participants = get_element(el_listing, 'Office')
            if el_participants:
                for el in el_participants.childNodes:
                    participant = {}
            
                    if el.getElementsByTagName('Address'):
                        participant['address'] = parse_address( el.getElementsByTagName('Address')[0] )
            
                    participant['email'] = get_element_value(el, 'Email')
                    participant['fax'] = get_element_value(el, 'Fax')
                    participant['first_name'] = get_element_value(el, 'FirstName')
                    participant['last_name'] = get_element_value(el, 'LastName')
            
                    # TODO: Licenses
            
                    participant['id'] = get_element_value(el, 'ParticipantId')
                    participant['key'] = get_element_value(el, 'ParticipantKey')
                    participant['phone'] = get_element_value(el, 'PrimaryContactPhone')            
                    participant['role'] = get_element_value(el, 'Role')
                    participant['url'] = get_element_value(el, 'WebsiteURL')
            
                    listing['participants'].append(participant)
            
            
            ################
            # Photos block #
            ################
            el_photo = get_element(el_listing, 'Photos')
            if el_photo:
                listing['photos'] = []
                for el in el_photo.childNodes:
                    url = get_element_value(el, 'MediaURL')
                    timestamp = get_element_value(el, 'MediaModificationTimestamp')
                    listing['photos'].append({'url': url, 'timestamp': timestamp})
            
            
                    
            ########################
            # All other attributes #
            ########################
            listing['listing_source_id'] = 1
            listing['price'] = get_element_value (el_listing, 'ListPrice')
            listing['mlsnumber'] = get_element_value(el_listing, 'MlsNumber')
            listing['url'] = get_element_value(el_listing, 'ListingURL')
            listing['provider_name'] = get_element_value(el_listing, 'ProviderName')
            listing['provider_url'] = get_element_value(el_listing, 'ProviderURL')
            listing['provider_category'] = get_element_value(el_listing, 'ProviderCategory')
            listing['lead_routing_email'] = get_element_value(el_listing, 'LeadRoutingEmail')
            listing['bedrooms'] = get_element_value(el_listing, 'Bedrooms')
            listing['bathrooms'] = get_element_value(el_listing, 'Bathrooms')
            listing['property_type'] = get_element_value(el_listing, 'PropertyType')
            listing['property_subtype'] = get_element_value(el_listing, 'PropertySubType')
        #print listing
        
        if listing.valid():
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
def get_element (dom, tag):
    element = dom.getElementsByTagName(tag)
    if (element):
        return element[0]
    return None
    
# Parses a parent level Address element
# See http://app.listhub.com/syndication-docs/rets2012.html#elements_/Listings/Listing/Address
def parse_address (el):
    address = {}
    address['address'] = get_element_value(el, 'commons:FullStreetAddress')
    address['unit_number'] = get_element_value(el, 'commons:UnitNumber')
    address['city'] = get_element_value(el, 'commons:City')
    address['state'] = get_element_value(el, 'commons:StateOrProvince')
    address['postal_code'] = get_element_value(el, 'commons:PostalCode')
    address['country'] = get_element_value(el, 'commons:Country')
    return address
    
def get_element_value (el, tag):
    if el:
        if el.getElementsByTagName(tag) and el.getElementsByTagName(tag)[0].firstChild:
            return el.getElementsByTagName(tag)[0].firstChild.nodeValue
    return None