import numpy as np
import pandas as pd
import re
from etsy_py.api import EtsyAPI

"""
Written by Eleanor Middlemas
Insight Project: Neck-Less Searching
Allowing users to bypass Etsy searching to find their ideal necklace according to
an image the user provides.
January 18, 2020

These functions scrape text from listings on Etsy and saves the following attributes
to a python dictionary that is returned to the user:
- listing_id
- url to listing
- price of item
- materials that item uses
- "taxonomy_path", or a list of categories/keywords that describe the item.

The user provides:
- their Etsy-provided API key
- the number of listings they would like to query at once (the maximum is 100)
- the maximum number of listings they would like to scrape. 

"""

def save_dictionary(savedict,r,nolistings):
    """
    This function takes in the dictionary object that the API returns, looks 
    for the listings that are still active and saves only the attributes listed 
    above in the dictionary.
    """
    # Features I want to save to the csv. Can edit this later
    dictlist = ['listing_id','url','price','materials','taxonomy_path']
    for x in np.arange(0,nolistings):
        if r.json()['results'][x]['state']=='active':
            savedict.append({a: r.json()['results'][x][a] for a in dictlist})
        else:
            continue
    
    return savedict

def scrape_listings(myapikey, nolistings, maxlistings):
    """
    This function actually queries the Etsy API, which returns the listings in dictionary
    format. The returned dictionary is then passed to the "save_dictionary" function. 
    
    The user indicates how many listings they would like to return at once (the maximum
    is 100), as well as the maxium total number of listings returned (maximum is 100k per 
    day).
    """
    import time
    t0 = time.time()

    api = EtsyAPI(api_key=myapikey)

    # dont' want this statement to re-run bc limited number of API queries
    if 'savedict' in locals() and len(savedict)>0:
            print("savedict already defined. ")
    else:
        offset= 0 
        savedict = [] # initialize list that will eventually contain dictionaries of listing items
        while offset<maxlistings:
            print(('Fetching listings from /listings/active?limit='+str(nolistings)+'&offset='+str(offset)+'&category=Jewelry&keywords=necklace'))
            r = api.get('/listings/active?limit='+str(nolistings)+'&offset='+str(offset)+'&category=Jewelry&keywords=necklace')
            time.sleep(0.3)  # wait 0.3 seconds before we make the next request
            offset+=nolistings

            save_dictionary(savedict,r,nolistings)

    elapsedtime = time.time() - t0
    print("Successfully scraped "+str(maxlistings)+". Elapsed time: "+str(elapsedtime)+" seconds.")
    
    return savedict
