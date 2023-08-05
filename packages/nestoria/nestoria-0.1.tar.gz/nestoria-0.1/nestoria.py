#!/usr/bin/python

import urllib2
import simplejson

HOSTNAME = ''
REALM = ''
USER = ""
PASS = ""

API_VERSION = '1.0'
ENCODING = 'json'

NESTORIA_API_URL = "http://api.nestoria.co.uk/api"

############################################################################################################

#===========================================================================================================
def req(url):

    authinfo = urllib2.HTTPBasicAuthHandler()
    authinfo.add_password(REALM, HOSTNAME, USER, PASS)
    opener = urllib2.build_opener(authinfo, urllib2.HTTPDefaultErrorHandler())

    request = urllib2.Request(url)
    response = opener.open(request).read()

    return response


#===========================================================================================================
def echo():
    """
    simply echos back the request. Intended to be used in testing and debugging.

    """

    url = NESTORIA_API_URL +'?action=echo'
    url += '&version='+API_VERSION
    url += '&encoding='+ENCODING

    json_results = req(url=url)
    python_results = simplejson.loads(json_results)

    return python_results['response']['status_text']


#===========================================================================================================
def search_listings(place_name='Soho', south_west='lat,lng', north_east='lat,lng', centre_point='lat,lng',
                    number_of_results='20', listing_type='buy', property_type='all',
                    price_max='', price_min='',
                    bedroom_max='',bedroom_min=''):
    """
    search the database for listing based on location and filter the results.

    params:
            (   place_name: 'Soho'     a place name, post code, tube station, etc.
            or  south_west: 'lat,lng'     the SW point of a bounding box
            or  north_east: 'lat,lng'     the NE point of a bounding box
            or  centre_point: 'lat,lng'   the centre point for a search )

            number_of_results:  10                    defaults to 20

            listing_type: 'let' or 'buy'              defaults to 'buy'
            property_type: 'all', 'house' or 'flat'   defaults to 'all'
    
            price_max:   'max' or number              defaults to 'max'  
            price_min:   'min' or number              defaults to 'min'
    
            bedroom_max: 'max' or number              defaults to 'max'  
            bedroom_min: 'min' or number              defaults to 'min'
    """

    url = NESTORIA_API_URL +'?action=search_listings'
    url += '&version='+API_VERSION
    url += '&encoding='+ENCODING

    if south_west != 'lat,lng':
       url += '&south_west='+south_west
    elif north_east != 'lat,lng':
       url += '&north_east='+north_east
    elif centre_point != 'lat,lng':
       url += '&centre_point='+centre_point
    else:
       url += '&place_name='+place_name

    url += '&number_of_results='
    url += '&listing_type='+listing_type
    url += '&property_type='+property_type
    url += '&price_max='+price_max
    url += '&price_min='+price_min
    url += '&bedroom_max='+bedroom_max
    url += '&bedroom_min='+bedroom_min

    json_results = req(url=url)
    python_results = simplejson.loads(json_results)

    return python_results['response']['listings']


############################################################################################################


#===========================================================================================================
def main():

    result_list =  search_listings(place_name='Soho', number_of_results='20', listing_type='buy', property_type='all',
                                   price_max='', price_min='', bedroom_max='',bedroom_min='')
    for r in result_list:
        print r
        print "--" 


if __name__ == "__main__":
   print main()