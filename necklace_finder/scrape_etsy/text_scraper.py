import os
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


These functions also act to clean up the text listings from Etsy by removing duplicate
entries and removing listings that are not necklaces at all. The goal is that, then
the user may take the final list of listing ID's to then scrape the associated images
off of Etsy.

The listings are saved as a .csv file somewhere. The user must run these functions by
loading the data from the csv as a dataframe, and then passing that dataframe "df" into
the functions below. The functions will return a cleaned dataframe that can then be 
outputted once more as a .csv file.

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


def rename_categories(df):
    """
    Renames the text in "taxonomy_path" column by replacing the text with the last 
    part of the string. I.e., the first part of the string will read "JewelryNecklace"
    if the item is categorized as a Necklace and "Jewelry" if it's not a necklace. This
    function removes the "JewelryNecklace" part, and replaces it with what's left. 
    
    Etsy uses a number of categories that are listed in under "strcategories" below. 
    There are a few not listed there, but are categorized as "Other". If the listing
    has a taxonomy_path that does not contain the word "Necklace", it is labeled
    "NotANecklace".
    
    Last, this function renames the "taxonomy_path" column "category".
    """
    df = df.fillna('')
    categories = df.taxonomy_path.values
    # if values are saved as lists then convert to a string.
    if type(categories[0])==list:
        categories = [str(i) for i in categories]
    pattern = re.compile('[\W_]+')
    categories = [pattern.sub('',i) for i in categories]
    
    # Replace taxonomy_path lists with the associated string
    strcategories = ['Pendants', 'BeadedNecklaces', 'Charm',\
                     'Crystal','MonogramNameNecklaces','Chokers',\
                     'Other','NotNecklaces']


    for x in np.arange(0,len(categories)):
        mode = 0
        for s in strcategories:
            if s in categories[x]:
                categories[x]=s
                mode=1
        if (mode==0) and ('Necklaces' in categories[x]):
            categories[x]="Other"
            mode=1
        elif mode==0:
            categories[x]="NotANecklace"
            mode=1

    df.taxonomy_path = categories
    df = df.rename(columns={"taxonomy_path": "category"})
    
    return df


def delete_duplicates_notnecklaces(df):
    """
    This function does two things:
    (1) Removes duplicate listings.
    (2) Removes listings that are not categorized as Necklaces on Etsy.
    
    Returns a dataframe with these things removed as well as a dataframe containing
    the duplicate listings.
    
    ***NOTE: When this function is executed, it automatically removes the duplicate
    listings from the original dataframe IN ADDITION TO the returned dataframe. This
    is because the "dataFrame.drop_duplicates()" function acts on the dataframe.***
    """
    
    duplicates = df[df.duplicated()] # see what they look like
    print("Number of duplicates: ")
    print(len(duplicates))
    print(duplicates['category'].value_counts()) # apparently there were no duplicates!
    print(" ")

    df.drop_duplicates(keep = "first", inplace = True)
    print("Sum after dropping duplicates: ")
    print(len(df)) # drop_duplicates acts on dataframe directly
    print(" ")

    print("Number of not necklaces")
    print(sum(df['category']=='NotANecklace')) 
    print(" ")
    cleaneddf = df[df.category != 'NotANecklace']

    print("Final cleaned dataframe:")
    print(cleaneddf['category'].value_counts())
    print(" ")
    print("Final number of listings: ")
    print(len(cleaneddf))
    return cleaneddf, duplicates



def run_text_scraper(apikey, nolistings, maxlistings, outputpath, csvname):

    # nolistings: number of listings to scrape at a time (max 100)
    # maxlistings: maximum number of listings to scrape (max 100k)
    listdict = scrape_listings(myapikey,nolistings,maxlistings) # returns newest listings first
    
    df = pd.DataFrame(listdict)
    df.to_csv(outputpath+"/"+csvname,index=False)
    
    # Clean listings by renaming categories & deleting those that are not necklaces
    cleaneddf = rename_categories(df)
    cleaneddf, dups = delete_duplicates_notnecklaces(cleaneddf)
    cleaneddf.to_csv(outputpath+"/cleaned_"+csvname,index=False)

