#!/usr/local/bin/python

import ez_setup
ez_setup.use_setuptools()

from pkg_resources import require
require("simplejson==1.4")

import simplejson
from urllib2 import urlopen
from urllib import urlencode

NESTORIA_API_URL = "http://api.nestoria.co.uk/api"

############################################################################################################

#===========================================================================================================
def echo():
    """
    simply echos back the request. Intended to be used in testing and debugging.

    """

    harcoded_parameters = {'action': 'echo', 'version': '1.1', 'encoding': 'json'}
    req_url  = NESTORIA_API_URL + "?" + urlencode(harcoded_parameters)
    json_results = urlopen(req_url).read()

    try:
      python_results = simplejson.loads(json_results)
      return python_results['response']['status_text']
    except:
      print req_url
      print json_results
      return ""

#===========================================================================================================
def search_listings(place_name=None, 
                    south_west=None, north_east=None, 
                    centre_point=None,
                    radius=None,
                    number_of_results=None, listing_type=None, property_type=None,
                    price_max=None, price_min=None,
                    bedroom_max=None,bedroom_min=None,
                    size_max=None,size_min=None,
                    sort=None,
                    keywords=None,keywords_exclude=None):
    """
    search the database for listing based on location and filter the results.

    # where to search: EITHER
    place_name: 'Chelsea'     a place name, post code, tube station, etc.
    
    # OR
    south_west: 'lat,lng'     the SW point of a bounding box
    north_east: 'lat,lng'     the NE point of a bounding box

    # OR
    centre_point: 'lat,lng'   the centre point for a search 
                              (with default radius of 2km)

    # OR
    radius: 'lat,lng,num[km|mi]'   centre point with specific radius 
                                   in km (kilometres) or mi (miles)
                                   note that the 'km' or 'mi' is not optional
    
    # options:
    number_of_results:  10                    defaults to 20, capped at 50

    # filters to narrow the results:
    listing_type:  'rent' or 'buy' or 'share'  defaults to 'buy'
    property_type: 'all', 'house' or 'flat'    defaults to 'all'
    
    price_max:   'max' or number               defaults to 'max'  
    price_min:   'min' or number               defaults to 'min'
    
    bedroom_max: 'max' or number               defaults to 'max'  
    bedroom_min: 'min' or number               defaults to 'min'
    
    # for api.nestoria.es requests you may also filter 
    # by size in square metres

    size_max: 'max' or number               defaults to 'max'  
    size_min: 'min' or number               defaults to 'min'

    # sorting the results 
    # if no sort parameter is requested results are sorted by 
    # "Nestoria Rank" our propriatary relevance agorithm.

    sort: 'bedroom_lowhigh'  or 'bedroom_highlow' # by number of bedrooms
          'price_lowhigh'    or 'price_highlow'   # by price 
          'newest'           or 'oldest'   # by date
        
    keywords: 'garden'                         comma seperated list of valid keywords 
    keywords_exclude: 'lower_ground_floor'     comma seperated list of valid keywords 

    # valid keywords and keywords_exclude vary depending on the country
    # the list of valid keywords can be requested using the keywords method (see below)
    # keywords should always be submitted as shown here; 
    # lowercased and with _ in place of space

    ES: adosado, amueblado, atico, balcon, buhardilla, bungalow, calefac_central, chimenea, doble_garaje, ex_vpo, garaje, garaje_particular, gimnasio, invernadero, jacuzzi, jardin, jardin_comunitario, lavavajillas, loft, obra_nueva, piscina, piscina_comunitaria, piscina_individual, pista_de_deportes, planta_baja, playa_cercana, plaza_de_aparcamiento, portero, portero_automatico, sauna, semi_amueblado, sin_ambueblar, sin_ascensor, sotano, suelo_de_madera, terraza, trastero, villa

    UK: attic, auction, balcony, basement, bungalow, cellar, conservatory, conversion, cottage, detached, detached_garage, dishwasher, double_garage, excouncil, fireplace, freehold, furnished, garage, garden, grade_ii, gym, high_ceilings, hot_tub, leasehold, lift, loft, lower_ground_floor, maisonette, mews, new_build, off_street_parking, parking, patio, penthouse, porter, purpose_built, refurbished, sauna, sealed_bid, semi_detached, share_freehold, shared_garden, swimming_pool, terrace, unfurnished, victorian, wood_floor

    """
    
    """
    harcoded API parameters:

    action:   The name of the API methods, eg 'echo'
    version:  The API version - allows for backward compatability. Optional
    encoding: How you would like the results encoded, 'xml' or 'json'
    pretty:   If set the JSON response will be pretty printed
    callback: name of function to wrap the JSON in (see below)

    """
    parameters = {}

    if place_name != None:
       parameters['place_name']=place_name
    elif south_west != None and north_east != None:
       parameters['south_west']=south_west
       parameters['north_east']=north_east
    elif centre_point!=None:
       parameters['centre_point']=centre_point
    elif radius!=None:
       parameters['radius']=radius

    if number_of_results!=None:
       parameters['number_of_results']=number_of_results
    if listing_type!=None:
       parameters['listing_type']=listing_type
    if property_type!=None:
       parameters['property_type']=property_type
    if price_max!=None:
       parameters['price_max']=price_max
    if price_min!=None:
       parameters['price_min']=price_min
    if bedroom_max!=None:
       parameters['bedroom_max']=bedroom_max
    if bedroom_min!=None:
       parameters['bedroom_min']=bedroom_min
    if size_max!=None:
       parameters['size_max']=size_max
    if size_min!=None:
       parameters['size_min']=size_min
    if sort!=None:
       parameters['sort']=sort
    if keywords!=None:
       parameters['keywords']=keywords
    if keywords_exclude!=None:
       parameters['keywords_exclude']=keywords_exclude
    
    harcoded_parameters = {'action': 'search_listings', 'version': '1.1', 'encoding': 'json'}
    req_url  = NESTORIA_API_URL + "?" + urlencode(harcoded_parameters) + '&' + urlencode(parameters)
    json_results = urlopen(req_url).read()
    try:
      python_results = simplejson.loads(json_results)
      return python_results['response']['listings']
    except:
      print req_url
      print json_results
      return []
    

#===========================================================================================================
def keywords():
    """
    This is a simple API method that returns a sorted list of valid keywords.    
    """

    harcoded_parameters = {'action': 'keywords', 'version': '1.1', 'encoding': 'json'}
    req_url  = NESTORIA_API_URL + "?" + urlencode(harcoded_parameters)
    json_results = urlopen(req_url).read()

    try:
      python_results = simplejson.loads(json_results)
      return python_results['response']['keywords']
    except:
      print req_url
      print json_results
      return ""


############################################################################################################


#===========================================================================================================
def main():

    print echo()

    result_list =  search_listings(place_name='Chelsea')
    for r in result_list:
        print r
        print "--" 

    print keywords()

    return ""

if __name__ == "__main__":
   print main()
