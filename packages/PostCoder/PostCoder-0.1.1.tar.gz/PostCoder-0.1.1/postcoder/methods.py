"""Implements the various search methods provided by postcoder as
easy to use methods

USAGE:
======
from postcoder.methods import SearchMethods

SERVICE = SearchMethods(
                       API_USERNAME,
                       API_PASSWORD,
                       'Example File'   #Optional
                       ) 

print SERVICE.get_thrfare_addresses(POST_CODE)
print SERVICE.get_premise_list(POST_CODE)
print SERVICE.get_match_address(ADDRESS_LINE)
print SERVICE.get_grids(POST_CODE)
print SERVICE.get_postzon(POST_CODE)
print SERVICE.get_distance(POST_CODE, POST_CODE_2)
"""
# methods.py
# Copyright (C) 2010 Sharoon Thomas sharoon.thomas@openlabs.co.in
#
# This module is part of postcoder module by Openlabs
#(Visit http://openlabs.co.in)
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import logging
from math import sqrt
#Set logging level
logging.basicConfig(level=logging.ERROR)

try:
    from suds.client import Client
except ImportError, suds_import_err:
    logging.critical("Module SUDS is not installed.\
        Install SUDS from https://fedorahosted.org/suds/")
    raise suds_import_err

from postcoder.exceptions import IPAddressException, \
                                CredentialsException, \
                                SuspensionException, \
                                CreditsException, \
                                LicenseTException, \
                                LicensePException, \
                                LicensePGException, \
                                PostCoderException

#This is the default postcoder WSDL URL when this was written on 
#Monday, 15 February 2010
WSDL = "http://www.postcoderwebsoap.co.uk/websoap/websoap.php?wsdl"
POSTCODE_VALID = {
        '0':'Full Postcode found',
        '1':'Part Postcode found',
        '-3':'No Postcode or Part Postcode found',
}
RET_CODES = {
        '0':'Postcode and premise found OK',
        '1':'Postcode found, premise not Matched',
        '2':'Postcode found, premise not present in address',
        '3':'Invalid Postcode',
        '4':'No Postcode, or incomplete Postcode, in address'
}

def find_exception(code):
    """
    Returns a postcoder exception depending on the error code
    @param code: Code of error
    :return Returns the correct exception for a code
    """
    exceptions = {
        '1004':IPAddressException,
        '1008':CredentialsException,
        '1010':SuspensionException,
        '1015':CreditsException,
        '2001':LicenseTException,
        '2002':LicensePException,
        '2003':LicensePGException
    }
    return exceptions.get(code, PostCoderException)


class SearchMethods(object):
    """
    The Search methods outlined by postcoder are implemented
    here.
    """
    def __init__(self,
                    username,
                    password,
                    identifier="Undefined",
                    wsdl_url=WSDL,
                    ):
        """Create an instance of postcoder for a set of 
        credentials, identifier is 
        
        @param username: the user name of your Postcoder Web account
        @param password: the user name of your Postcoder Web account
        @param identifier: an optional item which identifies the page that the 
            search request came from, allowing the statistics for Web SOAP usage 
            to be broken down into more detail.See the statistics section for 
            information on how this is used.
        @param wsdl_url: Web Services Description Language document location
            defaults to the URL when this program was coded
        """
        self._username = username
        self._password = password
        self._identifier = identifier
        self._wsdl_url = wsdl_url
        self._client = Client(self._wsdl_url)
        
    def _get_username(self):
        """Get the user name of your Postcoder Web account"""
        return self._username
    
    def _set_username(self, value):
        """Set the user name of your Postcoder Web account"""
        self._username = value
    
    username = property(_get_username, _set_username)
    
    def _get_password(self):
        """Get the user name of your Postcoder Web account"""
        return self._password
    
    def _set_password(self, value):
        """Set the user name of your Postcoder Web account"""
        self._password = value
    
    password = property(_get_password, _set_password)
    
    def _get_identifier(self):
        """Get optional identifier for statistics"""
        return self._identifier
    
    def _set_identifier(self, value):
        """Set optional identifier for statistics"""
        self._identifier = value
    
    identifier = property(_get_identifier, _set_identifier)
    
    def _get_soap_client(self):
        """The initialised SOAP Client object if you want to \
        perform some other method""" 
        return self._client
    
    soap_client = property(_get_soap_client)
    
    def get_thrfare_addresses(self, postcode):
        """The getThrfareAddresses method accepts a Postcode \
and returns a street level address.
        @param postcode: UK postcode as string
        """
        result = self._client.service.getThrfareAddresses(
                                        postcode,
                                        self._identifier,
                                        self._username,
                                        self._password
                                             )
        if result.error_code != '0':
            raise find_exception(result.error_code)(result.error_message)
        else:
            return {
                'addresses':[
                             {
                    'po_box':each.po_box,
                    'dependent_street':each.dependent_street,
                    'street':each.street,
                    'double_dependent_locality':each.double_dependent_locality,
                    'dependent_locality':each.dependent_locality,
                    'post_town':each.post_town,
                    'county':each.county,
                    'postcode':each.postcode,
                              }
                            for each in result.addresses
                            ],
                'postcode_valid':POSTCODE_VALID.get(result.postcode_valid),
                'retcode':RET_CODES.get(result.retcode),
                'search_string':result.search_string,
                'time_taken':result.time_taken,
            }
    
    def get_premise_list(self, postcode):
        """The getPremiseList method accepts a Postcode and returns \
the full address with a list of all organisations and premises \
that exist at the given Postcode.
        @param postcode: UK postcode as string
        """
        result = self._client.service.getPremiseList(
                                        postcode,
                                        self._identifier,
                                        self._username,
                                        self._password
                                             )
        if result.error_code != '0':
            raise find_exception(result.error_code)(result.error_message)
        else:
            return {
                'addresses':[
                             {
                    'premise':[
                               {
                            'organisation':premise.organisation,
                            'premise':premise.premise
                                } for premise in each.premise
                               ],
                    'dependent_street':each.dependent_street,
                    'street':each.street,
                    'double_dependent_locality':each.double_dependent_locality,
                    'dependent_locality':each.dependent_locality,
                    'post_town':each.post_town,
                    'county':each.county,
                    'postcode':each.postcode,
                              }
                            for each in result.addresses
                            ],
                'postcode_valid':POSTCODE_VALID.get(result.postcode_valid),
                'retcode':RET_CODES.get(result.retcode),
                'search_string':result.search_string,
                'time_taken':result.time_taken,
            }      

    def get_match_address(self, input_string):
        """Accepts an input string that should contain known elements of an \
address separated by commas.find a match for the address by searching \
all PAF records
        @param input_string: Known elements of an address separated by comma
        """
        result = self._client.service.getMatchAddress(
                                input_string,
                                self._identifier,
                                self._username,
                                self._password
                                     )
        if result.error_code != '0':
            raise find_exception(result.error_code)(result.error_message)
        else:
            return {
                'addresses':[
                             {
                    'premise':[
                               {
                            'organisation':premise.organisation,
                            'premise':premise.premise
                                } for premise in each.premise
                               ],
                    'dependent_street':each.dependent_street,
                    'street':each.street,
                    'double_dependent_locality':each.double_dependent_locality,
                    'dependent_locality':each.dependent_locality,
                    'post_town':each.post_town,
                    'county':each.county,
                    'postcode':each.postcode,
                              }
                            for each in result.addresses
                            ],
                'postcode_valid':POSTCODE_VALID.get(result.postcode_valid),
                'retcode':RET_CODES.get(result.retcode),
                'search_string':result.search_string,
                'time_taken':result.time_taken,
            } 
    
    def get_grids(self, postcode):
        """The getGrids method accepts a Postcode and returns Ordnance Survey \
100m Easting and Northing measurements that refer to the distance East \
and North from a fixed point just South West of the Isles of Scilly.
        @param postcode: UK postcode as string
        """
        result = self._client.service.getGrids(
                                        postcode,
                                        self._identifier,
                                        self._username,
                                        self._password
                                             )
        if result.error_code != '0':
            raise find_exception(result.error_code)(result.error_message)
        else:
            return {
                'grideast':result.grideast,
                'gridnorth':result.gridnorth,
                'latitude_osgb36':result.latitude_osgb36,
                'longitude_osgb36':result.longitude_osgb36,
                'latitude_etrs89':result.latitude_etrs89,
                'longitude_etrs89':result.longitude_etrs89,
                'postcode_valid':POSTCODE_VALID.get(result.postcode_valid),
                'retcode':RET_CODES.get(result.retcode),
                'search_string':result.search_string,
                'time_taken':result.time_taken,
                    }
    
    def get_postzon(self, postcode):     
        """The getPostzon method accepts a Postcode and returns demographic \
and geographical information about a Postcode record. Data available \
includes the Ordnance Survey Grid References, Local Authority and NHS \
Health Authority information.
        
        @param postcode: UK postcode as string
        """
        result = self._client.service.getPostzon(
                                        postcode,
                                        self._identifier,
                                        self._username,
                                        self._password
                                             )
        if result.error_code != '0':
            raise find_exception(result.error_code)(result.error_message)
        else:
            return {
                'grideasting':result.grideasting,
                'gridnorthing':result.gridnorthing,
                'grideastingstatus':result.grideastingstatus,
                'gridnorthingstatus':result.gridnorthingstatus,
                'localauthoritywardcode':result.localauthoritywardcode,
                'localauthoritywardname':result.localauthoritywardname,
                'localunitaryauthorityname':result.localunitaryauthorityname,
                'nhshealthauthoritycode':result.nhshealthauthoritycode,
                'nhshealthauthorityname':result.nhshealthauthorityname,
                'primarycaretrustcode':result.primarycaretrustcode,
                'primarycaretrustname':result.primarycaretrustname,
                'primarycaretrustha':result.primarycaretrustha,
                'postcode_valid':POSTCODE_VALID.get(result.postcode_valid),
                'retcode':RET_CODES.get(result.retcode),
                'search_string':result.search_string,
                'time_taken':result.time_taken,
                    }

    def get_distance(self, post_code_1, post_code_2, unit="km"):
        """
        Finds the straight line difference between two postcodes
        @param post_code_1: First Post Code
        @param post_code_2: Second Post Code
        @param unit: km=kilometer, m=miles
        """
        factor = {'km':0.01, 'm':0.006213}.get(unit, 1)
        grid_1 = self.get_grids(post_code_1)
        grid_2 = self.get_grids(post_code_2)
        if grid_1 and grid_2:
            return sqrt(
                    (
     (int(grid_2.get('gridnorth', 0)) - int(grid_1.get('gridnorth', 0))) ** 2
                    ) 
                    + 
                    (
     (int(grid_2.get('grideast', 0)) - int(grid_1.get('grideast', 0))) ** 2
                    )
                    ) * factor
