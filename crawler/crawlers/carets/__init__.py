# crawler.crawlers.carets.__init__.py
from ... import rets
from .. import download, Listing
import sys

def crawl (context, config, indexCallback):
    crawler = rets.Rets()

    crawler.url = config['url']
    crawler.username = config['username']
    crawler.password = config['password']
    crawler.useragent = config['useragent']

    if crawler.login():
        if context['verbose']:
            print "Logged in!"
        crawler.download(context=context, config=config, limit=500, toListingCallback=toListing, indexCallback=indexCallback)

        crawler.logout()
    else:
        if context['verbose']:
            print "Login failed."

def toListing(context, data):
    l = Listing()

    ###############################################
    # Map CARETS fields to our internal structure #
    ###############################################

    # TODO: We need to map a lot more -- waiting on Coy to discuss field requirements.

    l['MlsNumber'] = data['ListingID']
    l['LeadRoutingEmail'] = data['ListAgentEmail']


    # l['AdNumber'] = data['AdNumber']
    # l['BuildersModelCode'] = data['BuildersModelCode']
    # l['BuildersTractCode'] = data['BuildersTractCode']
    # l['BuildersTractName'] = data['BuildersTractName']
    # l['BuildersTractNameOther'] = data['BuildersTractNameOther']
    l['CancelledDate'] = data['CancelledDate']
    # l['CARETSListingStatus'] = data['CARETSListingStatus']
    # l['CDOM'] = data['CDOM']
    # l['CDOMCalculatedDate'] = data['CDOMCalculatedDate']
    # l['CDOMModificationTimestamp'] = data['CDOMModificationTimestamp']
    # l['CDOMUpdateYN'] = data['CDOMUpdateYN']
    l['ClosePrice'] = data['ClosePrice']
    l['ClosingDate'] = data['ClosingDate']
    # l['ContactOrder1'] = data['ContactOrder1']
    # l['ContactOrder2'] = data['ContactOrder2']
    # l['ContactOrder3'] = data['ContactOrder3']
    # l['ContactOrder4'] = data['ContactOrder4']
    # l['ContactOrder5'] = data['ContactOrder5']
    # l['ContactOrder6'] = data['ContactOrder6']
    l['DOM'] = data['DOM']
    l['DOMUpdateYN'] = data['DOMUpdateYN']
    # l['GateCode'] = data['GateCode']
    # l['GeocodeOverrideYN'] = data['GeocodeOverrideYN']
    # l['HOAYN'] = data['HOAYN']
    # l['ICDOM'] = data['ICDOM']
    # l['LandLeaseAmountPerYear'] = data['LandLeaseAmountPerYear']
    # l['LandLeaseExpirationYear'] = data['LandLeaseExpirationYear']
    # l['LandLeasePurchaseYN'] = data['LandLeasePurchaseYN']
    # l['LastMediaDate'] = data['LastMediaDate']
    # l['LastModifiedBy'] = data['LastModifiedBy']
    # l['LastPhotoDate'] = data['LastPhotoDate']
    # l['ListBrokerLicenseNumber'] = data['ListBrokerLicenseNumber']
    # l['ListingAgreement'] = data['ListingAgreement']
    l['ListingDate'] = data['ListingDate']
    l['ListingEntryDate'] = data['ListingEntryDate']
    l['ListingID'] = data['ListingID']
    l['ListingKey'] = data['ListingKey']
    l['ListingModificationDate'] = data['ListingModificationDate']
    l['ListingStatus'] = data['ListingStatus']
    # l['ListingSubscriptionClassList'] = data['ListingSubscriptionClassList']
    # l['ListingSubscriptionList'] = data['ListingSubscriptionList']
    l['ListingTerms'] = data['ListingTerms']
    l['ListPrice'] = data['ListPrice']
    l['ListPriceLow'] = data['ListPriceLow']
    l['LotLocation'] = data['LotLocation']
    l['ManagementCompanyName'] = data['ManagementCompanyName']
    l['ManagementCompanyName2'] = data['ManagementCompanyName2']
    l['ManagementCompanyPhone2'] = data['ManagementCompanyPhone2']
    l['ManagementCompanyPhone2Ext'] = data['ManagementCompanyPhone2Ext']
    l['ManagementCompanyPhone'] = data['ManagementCompanyPhone']
    l['ManagementCompanyPhoneExt'] = data['ManagementCompanyPhoneExt']

    l['MatchCode'] = data['MatchCode']
    l['ModificationTimestamp'] = data['ModificationTimestamp']
    l['OffMarketDate'] = data['OffMarketDate']
    l['OriginalListPrice'] = data['OriginalListPrice']
    # l['OwnersName'] = data['OwnersName']
    #l['PendingDate'] = data['PendingDate']
    l['PricePerAcre'] = data['PricePerAcre']
    l['PricePerSqft'] = data['PricePerSqft']
    l['PrimaryObjectModificationTimestamp'] = data['PrimaryObjectModificationTimestamp']
    l['RawCDOM'] = data['RawCDOM']
    l['RawDOM'] = data['RawDOM']
    l['ReciprocalListingYN'] = data['ReciprocalListingYN']
    l['ReciprocalMemberAreaCode'] = data['ReciprocalMemberAreaCode']
    l['ReciprocalMemberName'] = data['ReciprocalMemberName']
    l['ReciprocalMemberOfficeName'] = data['ReciprocalMemberOfficeName']
    l['ReciprocalMemberPhoneExt'] = data['ReciprocalMemberPhoneExt']
    l['ReciprocalMemberPhone'] = data['ReciprocalMemberPhone']
    l['SoldPricePerSqft'] = data['SoldPricePerSqft']
    l['SoldTerms'] = data['SoldTerms']
    #l['Source'] = data['Source']
    # l['SquareFootageSource'] = data['SquareFootageSource']
    l['StatusChangeDate'] = data['StatusChangeDate']
    # l['SubSystemLocale'] = data['SubSystemLocale']
    # l['SystemLocale'] = data['SystemLocale']
    l['TaxLegalLotNumber'] = data['TaxLegalLotNumber']
    l['TaxMelloRoos'] = data['TaxMelloRoos']
    l['TaxParcelNumber'] = data['TaxParcelNumber']
    l['TotalPhotoCount'] = data['TotalPhotoCount']
    l['UID'] = data['UniqueID']
    # l['VOWAutomatedValuationDisplay'] = data['VOWAutomatedValuationDisplay']
    # l['VOWConsumerComment'] = data['VOWConsumerComment']

    l['PropertyType'] = data['PropertyType']
    l['PropertySubType'] = data['PropertySubType']

    ####################
    # Property Address #
    ####################
    l['PropertyAddress'] = {
        'Address': data['FullStreetAddress']
        , 'UnitNumber': data['UnitNumber']
        , 'StreetDirPrefix': data['StreetDirPrefix']
        , 'StreetDirSuffix': data['StreetDirSuffix']
        , 'StreetName': data['StreetName']
        , 'StreetNumber': data['StreetNumber']
        , 'StreetNumberModifier': data['StreetNumberModifier']
        , 'StreetSuffix': data['StreetSuffix']
        , 'StreetSuffixModifier': data['StreetSuffixModifier']
        , 'City': data['City']
        , 'CityOther': data['CityOther']
        , 'State': data['State']
        , 'zipCode': data['ZipCode']
        , 'ZipCodePlus4': data['ZipCodePlus4']
        , 'Country': data['Country']
        , 'County': data['County']
        , 'Longitude': data['Longitude']
        , 'Latitude': data['Latitude']
        , 'ThomasGuideFullMapString': data['ThomasGuideFullMapString']
        , 'ThomasGuideMapPage': data['ThomasGuideMapPage']
        , 'ThomasMapXLetter': data['ThomasMapXLetter']
        , 'ThomasMapYNumber': data['ThomasMapYNumber']
    }

    ###############
    # Association #
    ###############
    l['Association'] = {
        'Name': data['AssociationName']
        ,'Phone': data['AssociationPhoneNumber']
        ,'PhoneExt': data['AssociationPhoneNumberExt']
    }

    ###########
    # Offices #
    ###########
    l['Offices'] = [
        {
            'Priority': 1
            , 'ID': data['ListOfficeId']
            , 'Name': data['ListOfficeName']
            , 'Phone': data['ListOfficePhone']
            , 'PhoneExt': data['ListOfficePhoneExt']
            , 'Fax': data['ListOfficeFax']
        }
        ,{
            'Priority': 2
            , 'ID': data['AltOfficeID']
            , 'Name': data['AltOfficeName']
            , 'Phone': data['AltOfficePhone']
            , 'PhoneExt': data['AltOfficePhoneExt']
            , 'Fax': data['AltOfficeFax']
        }
        ,{
            'Priority': 3
            , 'ID': data['SaleOfficeID']
            , 'Name': data['SaleOfficeName']
            , 'Phone': data['SaleOfficePhone']
            , 'PhoneExt': data['SaleOfficePhoneExt']
            , 'Fax': data['SaleOfficeFax']
        }
        ,{
            'Priority': 4
            , 'ID': data['AltSaleOfficeID']
            , 'Name': data['AltSaleOfficeName']
            , 'Phone': data['AltSaleOfficePhone']
            , 'PhoneExt': data['AltSaleOfficePhoneExt']
            , 'Fax': data['AltSaleOfficeFax']
        }
    ]

    ##########
    # Agents #
    ##########
    # Primary Agent
    agent = {
        'Priority': 1
        ,'CellPhone': data['ListAgentCellPhone']
        ,'DirectPhone': data['ListAgentDirectPhone']
        ,'DirectPhoneExt': data['ListAgentDirectPhoneExt']
        ,'Email': data['ListAgentEmail']
        ,'Fax': data['ListAgentFax']
        ,'FirstName': data['ListAgentFirstName']
        ,'HomePhone': data['ListAgentHomePhone']
        ,'HomePhoneExt': data['ListAgentHomePhoneExt']
        ,'Key': data['ListAgentKey']
        ,'Languages': data['ListAgentLanguages']
        ,'LastName': data['ListAgentLastName']
        ,'LicenseNumber': data['ListAgentLicenseNumber']
        ,'OfficeKey': data['ListAgentOfficeKey']
        ,'Pager': data['ListAgentPager']
        ,'PreferredFax': data['ListAgentPreferredFax']
        ,'PreferredPhone': data['ListAgentPreferredPhone']
        ,'PreferredPhoneExt': data['ListAgentPreferredPhoneExt']
        ,'TollFreePhone': data['ListAgentTollFreePhone']
        ,'TollFreePhoneExt': data['ListAgentTollFreePhoneExt']
        ,'VoiceMailExt': data['ListAgentVoiceMailExt']
        ,'VoiceMailPhone': data['ListAgentVoiceMailPhone']
        ,'BrokerLicenseNumber': data['ListBrokerLicenseNumber']
    }

    l['Agents'].append(agent)

    agent = {
        'Priority': 2
        ,'CellPhone': data['AltAgentCellPhone']
        ,'DirectPhone': data['AltAgentDirectPhone']
        ,'DirectPhoneExt': data['AltAgentDirectPhoneExt']
        ,'Email': data['AltAgentEmail']
        ,'Fax': data['AltAgentFax']
        ,'FirstName': data['AltAgentFirstName']
        ,'HomePhone': data['AltAgentHomePhone']
        ,'HomePhoneExt': data['AltAgentHomePhoneExt']
        ,'Key': data['AltAgentKey']
        ,'Languages': data['AltAgentLanguages']
        ,'LastName': data['AltAgentLastName']
        ,'LicenseNumber': data['AltAgentLicenseNumber']
        ,'OfficeKey': data['AltAgentOfficeKey']
        ,'Pager': data['AltAgentPager']
        ,'PreferredFax': data['AltAgentPreferredFax']
        ,'PreferredPhone': data['AltAgentPreferredPhone']
        ,'PreferredPhoneExt': data['AltAgentPreferredPhoneExt']
        ,'TollFreePhone': data['AltAgentTollFreePhone']
        ,'TollFreePhoneExt': data['AltAgentTollFreePhoneExt']
        ,'VoiceMailExt': data['AltAgentVoiceMailExt']
        ,'VoiceMailPhone': data['AltAgentVoiceMailPhone']
        ,'BrokerLicenseNumber': data['AltBrokerLicenseNumber']
    }

    l['Agents'].append(agent)

    agent = {
        'Priority': 3
        ,'CellPhone': data['SaleAgentCellPhone']
        ,'DirectPhone': data['SaleAgentDirectPhone']
        ,'DirectPhoneExt': data['SaleAgentDirectPhoneExt']
        ,'Email': data['SaleAgentEmail']
        ,'Fax': data['SaleAgentFax']
        ,'FirstName': data['SaleAgentFirstName']
        ,'HomePhone': data['SaleAgentHomePhone']
        ,'HomePhoneExt': data['SaleAgentHomePhoneExt']
        ,'Key': data['SaleAgentKey']
        ,'Languages': data['SaleAgentLanguages']
        ,'LastName': data['SaleAgentLastName']
        ,'LicenseNumber': data['SaleAgentLicenseNumber']
        ,'OfficeKey': data['SaleAgentOfficeKey']
        ,'Pager': data['SaleAgentPager']
        ,'PreferredFax': data['SaleAgentPreferredFax']
        ,'PreferredPhone': data['SaleAgentPreferredPhone']
        ,'PreferredPhoneExt': data['SaleAgentPreferredPhoneExt']
        ,'TollFreePhone': data['SaleAgentTollFreePhone']
        ,'TollFreePhoneExt': data['SaleAgentTollFreePhoneExt']
        ,'VoiceMailExt': data['SaleAgentVoiceMailExt']
        ,'VoiceMailPhone': data['SaleAgentVoiceMailPhone']
        ,'BrokerLicenseNumber': data['SaleBrokerLicenseNumber']
    }

    l['Agents'].append(agent)

    agent = {
        'Priority': 4
        ,'CellPhone': data['AltSaleAgentCellPhone']
        ,'DirectPhone': data['AltSaleAgentDirectPhone']
        ,'DirectPhoneExt': data['AltSaleAgentDirectPhoneExt']
        ,'Email': data['AltSaleAgentEmail']
        ,'Fax': data['AltSaleAgentFax']
        ,'FirstName': data['AltSaleAgentFirstName']
        ,'HomePhone': data['AltSaleAgentHomePhone']
        ,'HomePhoneExt': data['AltSaleAgentHomePhoneExt']
        ,'Key': data['AltSaleAgentKey']
        ,'Languages': data['AltSaleAgentLanguages']
        ,'LastName': data['AltSaleAgentLastName']
        ,'LicenseNumber': data['AltSaleAgentLicenseNumber']
        ,'OfficeKey': data['AltSaleAgentOfficeKey']
        ,'Pager': data['AltSaleAgentPager']
        ,'PreferredFax': data['AltSaleAgentPreferredFax']
        ,'PreferredPhone': data['AltSaleAgentPreferredPhone']
        ,'PreferredPhoneExt': data['AltSaleAgentPreferredPhoneExt']
        ,'TollFreePhone': data['AltSaleAgentTollFreePhone']
        ,'TollFreePhoneExt': data['AltSaleAgentTollFreePhoneExt']
        ,'VoiceMailExt': data['AltSaleAgentVoiceMailExt']
        ,'VoiceMailPhone': data['AltSaleAgentVoiceMailPhone']
        ,'BrokerLicenseNumber': data['AltSaleBrokerLicenseNumber']
    }

    l['Agents'].append(agent)

    # General stats
    l['YearBuilt'] = data['YearBuilt']
    l['Description'] = data['PublicRemarks']
    l['SqFeet'] = data['BuildingSize']
    l['LotSize'] = data['LotSizeSQFT']

    # Grab all the available ammenities
    l['Amenities'] = {}

    l['Amenities']['Roofing'] = data['Roofing']
    l['Amenities']['RVAccessDimensions'] = data['RVAccessDimensions']
    l['Amenities']['NumberOfRemoteControls'] = data['NumberOfRemoteControls']
    l['Amenities']['FloorMaterial'] = data['FloorMaterial']
    l['Amenities']['DisabilityAccess'] = data['DisabilityAccess']
    l['Amenities']['Fence'] = data['Fence']
    l['Amenities']['ElementarySchool'] = data['ElementarySchool']
    l['Amenities']['CarportSpacesTotal'] = data['CarportSpacesTotal']
    l['Amenities']['PatioFeatures'] = data['PatioFeatures']
    l['Amenities']['BathroomFeatures'] = data['BathroomFeatures']
    l['Amenities']['ParkingSpacesTotal'] = data['ParkingSpacesTotal']
    l['Amenities']['AssociationRules'] = data['AssociationRules']
    l['Amenities']['CoolingType'] = data['CoolingType']
    l['Amenities']['SpaConstruction'] = data['SpaConstruction']
    l['Amenities']['FireplaceRooms'] = data['FireplaceRooms']
    l['Amenities']['Levels'] = data['Levels']
    l['Amenities']['FireplaceYN'] = data['FireplaceYN']
    l['Amenities']['Appliances'] = data['Appliances']
    l['Amenities']['LotDescription'] = data['LotDescription']
    l['Amenities']['GarageSpacesTotal'] = data['GarageSpacesTotal']
    l['Amenities']['TVServices'] = data['TVServices']
    l['Amenities']['View'] = data['View']
    l['Amenities']['BathFull'] = data['BathFull']
    l['Amenities']['EntryFloorNumber'] = data['EntryFloorNumber']
    l['Amenities']['CoveredSpacesTotal'] = data['CoveredSpacesTotal']
    l['Amenities']['BedroomsTotal'] = data['BedroomsTotal']
    l['Amenities']['OtherAssociationFees'] = data['OtherAssociationFees']
    l['Amenities']['HOAFee1'] = data['HOAFee1']
    l['Amenities']['HOAFee2'] = data['HOAFee2']
    l['Amenities']['OpenOtherSpacesTotal'] = data['OpenOtherSpacesTotal']
    l['Amenities']['PoolYN'] = data['PoolYN']
    l['Amenities']['DrivingDirections'] = data['DrivingDirections']
    l['Amenities']['HeatingType'] = data['HeatingType']
    l['Amenities']['BuildingSize'] = data['BuildingSize']
    l['Amenities']['GreenLocation'] = data['GreenLocation']
    l['Amenities']['GreenCertifyingBody'] = data['GreenCertifyingBody']
    l['Amenities']['GreenIndoorAirQuality'] = data['GreenIndoorAirQuality']
    l['Amenities']['GreenCertificationRating'] = data['GreenCertificationRating']
    l['Amenities']['GreenHTAindex'] = data['GreenHTAindex']
    l['Amenities']['GreenSustainability'] = data['GreenSustainability']
    l['Amenities']['GreenWalkScore'] = data['GreenWalkScore']
    l['Amenities']['GreenBuildingCertification'] = data['GreenBuildingCertification']
    l['Amenities']['GreenWaterConservation'] = data['GreenWaterConservation']
    l['Amenities']['GreenEnergyEfficient'] = data['GreenEnergyEfficient']
    l['Amenities']['GreenEnergyGeneration'] = data['GreenEnergyGeneration']
    l['Amenities']['GreenYearCertified'] = data['GreenYearCertified']
    l['Amenities']['GreenWaterConservation'] = data['GreenWaterConservation']
    l['Amenities']['CookingAppliances'] = data['CookingAppliances']
    l['Amenities']['PublicRemarks'] = data['PublicRemarks']
    l['Amenities']['HOAFeeFrequency1'] = data['HOAFeeFrequency1']
    l['Amenities']['HOAFeeFrequency2'] = data['HOAFeeFrequency2']
    l['Amenities']['LegalDisclosures'] = data['LegalDisclosures']
    l['Amenities']['BuildersModelName'] = data['BuildersModelName']
    l['Amenities']['FirePlaceFuel'] = data['FirePlaceFuel']
    l['Amenities']['JuniorMiddleSchool'] = data['JuniorMiddleSchool']
    l['Amenities']['LaundryLocations'] = data['LaundryLocations']
    l['Amenities']['Sprinklers'] = data['Sprinklers']
    l['Amenities']['BathHalf'] = data['BathHalf']
    l['Amenities']['InteriorFeatures'] = data['InteriorFeatures']
    l['Amenities']['PoolDescriptions'] = data['PoolDescriptions']
    l['Amenities']['DwellingStories'] = data['DwellingStories']
    l['Amenities']['OtherStructures'] = data['OtherStructures']
    l['Amenities']['PoolAccessories'] = data['PoolAccessories']
    l['Amenities']['FoundationDetails'] = data['FoundationDetails']
    l['Amenities']['CommunityFeatures'] = data['CommunityFeatures']
    l['Amenities']['LotSizeDimensionDescription'] = data['LotSizeDimensionDescription']
    l['Amenities']['Rooms'] = data['Rooms']
    l['Amenities']['ParkingType'] = data['ParkingType']
    l['Amenities']['BuildingStructureStyle'] = data['BuildingStructureStyle']
    l['Amenities']['AssociationFeesInclude'] = data['AssociationFeesInclude']
    l['Amenities']['LotSizeAcres'] = data['LotSizeAcres']
    l['Amenities']['LotSizeSource'] = data['LotSizeSource']
    l['Amenities']['Area'] = data['Area']
    l['Amenities']['PropertyCondition'] = data['PropertyCondition']
    l['Amenities']['Water'] = data['Water']
    l['Amenities']['BuildersName'] = data['BuildersName']
    l['Amenities']['BathOneQuarter'] = data['BathOneQuarter']
    l['Amenities']['Sewer'] = data['Sewer']
    l['Amenities']['EntryLocation'] = data['EntryLocation']
    l['Amenities']['AssociationAmenities'] = data['AssociationAmenities']
    l['Amenities']['HighMidRiseAmenities'] = data['HighMidRiseAmenities']
    l['Amenities']['BuyerFinancing'] = data['BuyerFinancing']
    l['Amenities']['HighSchool'] = data['HighSchool']
    l['Amenities']['WaterHeaterFeatures'] = data['WaterHeaterFeatures']
    l['Amenities']['TaxLegalTractNumber'] = data['TaxLegalTractNumber']
    l['Amenities']['SpecialConditions'] = data['SpecialConditions']
    l['Amenities']['DistanceToBeachInMiles'] = data['DistanceToBeachInMiles']
    l['Amenities']['WaterDistrict'] = data['WaterDistrict']
    l['Amenities']['BathThreeQuarter'] = data['BathThreeQuarter']
    l['Amenities']['OtherStructuralFeatures'] = data['OtherStructuralFeatures']
    l['Amenities']['BedroomFeatures'] = data['BedroomFeatures']
    l['Amenities']['ExteriorConstruction'] = data['ExteriorConstruction']
    l['Amenities']['Inclusions'] = data['Inclusions']
    l['Amenities']['CommonWalls'] = data['CommonWalls']
    l['Amenities']['TaxLegalBlockNumber'] = data['TaxLegalBlockNumber']
    l['Amenities']['SecuritySafety'] = data['SecuritySafety']
    l['Amenities']['Volt220Location'] = data['Volt220Location']
    l['Amenities']['Exclusions'] = data['Exclusions']
    l['Amenities']['LandLeaseType'] = data['LandLeaseType']
    l['Amenities']['ParkingFeatures'] = data['ParkingFeatures']
    l['Amenities']['Possession'] = data['Possession']
    l['Amenities']['SpaDescriptions'] = data['SpaDescriptions']
    l['Amenities']['Zoning'] = data['Zoning']
    l['Amenities']['SpaYN'] = data['SpaYN']
    l['Amenities']['BathsTotal'] = data['BathsTotal']
    l['Amenities']['SchoolDistrict'] = data['SchoolDistrict']
    l['Amenities']['HeatingFuel'] = data['HeatingFuel']
    l['Amenities']['UnitLocation'] = data['UnitLocation']
    l['Amenities']['UnitsTotalInComplex'] = data['UnitsTotalInComplex']
    l['Amenities']['PropertySubType'] = data['PropertySubType']
    l['Amenities']['YearBuiltSource'] = data['YearBuiltSource']
    l['Amenities']['UnitFloorInBuilding'] = data['UnitFloorInBuilding']
    l['Amenities']['TotalFloors'] = data['TotalFloors']
    l['Amenities']['DirectionFaces'] = data['DirectionFaces']
    l['Amenities']['Doors'] = data['Doors']
    l['Amenities']['PoolConstruction'] = data['PoolConstruction']
    l['Amenities']['EatingAreas'] = data['EatingAreas']
    l['Amenities']['PlayingCourts'] = data['PlayingCourts']
    l['Amenities']['Windows'] = data['Windows']
    l['Amenities']['FireplaceFeatures'] = data['FireplaceFeatures']
    l['Amenities']['KitchenFeatures'] = data['KitchenFeatures']
    l['Amenities']['AreaOther'] = data['AreaOther']
    l['Amenities']['WillConsiderLeaseYN'] = data['WillConsiderLeaseYN']
    l['Amenities']['ViewYN'] = data['ViewYN']
    l['Amenities']['PoolYN'] = data['PoolYN']

    #########
    # Media #
    #########
    for media in data['media']:
        # WTH are they including urls to open houses in here?
        if int(media['PropMediaBytes']) > 0:
            url = media['PropMediaURL']
            #print "%s (%s bytes)" % (url, media['PropMediaBytes'])
            timestamp = media['PropMediaModificationTimestamp']

            #s3url = save_to_s3(context=context, url=url)
            s3url = None
            l['Photos'].append({'URL': url, 'S3URL': s3url, 'Timestamp': timestamp})

    return l
