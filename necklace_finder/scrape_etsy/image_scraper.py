from etsy_py.api import EtsyAPI
import pandas as pd
import numpy as np
import requests
import shutil
import os

"""
Written by Eleanor Middlemas
Insight Project: Neck-Less Searching
Allowing users to bypass Etsy searching to find their ideal necklace according to
an image the user provides.
January 18, 2020

Inputs: 
1. An API key (called "KEYSTRING") provided by the Etsy developers site after signing up.
2. A string that indicates the path to a csv that includes text of Etsy listing 
    information - most importantly - the listing ID number.
3. A string that indicates the path to an output folder where the images scraped will
    be saved. **NOTE: PLEASE ENSURE THERE IS A TRAILING slash ("/" on a mac) within 
    this string!!!**

These set of functions are paired with the scrape-and-clean listing text functions
to subsequently scrape Etsy. Those functions produce a .csv file that includes important
information about the listings that will be used in later analysis. These functions below
use the listing ID numbers from that .csv file to locate the listing images online. 

Then the functions below automatically save the images to a user-specified local 
directory.

"""

def read_listing_ids(df):
    """
    Takes in a dataframe (which comes from the csv file) and then outputs a list of strings 
    containing the listing ID numbers.    
    """
    listingids = df['listing_id'].values
    liststring = [str(x) for x in listingids]
    return liststring
    
    
def saveimage(api,listid,outputfolder):
    """
    This function scrapes the image online and saves it to the user-defined directory path.
    
    Takes in the etsy API, a single listing ID string, and the output folder string
    in which the images will be saved. 
    """
    rimage = api.get('/listings/'+listid+'/images')
     # Open the url image, set stream to True, this will return the stream content.
    if (np.array(rimage.json()['results']).size==0) or (rimage.json()['results'][0])==False:
        print("Listing has no image!")
    else:
        image_url = rimage.json()['results'][0]['url_570xN']
        resp = requests.get(image_url, stream=True)

        # Open a local file with wb ( write binary ) permission.
        imagename = outputfolder+listid+".jpg"
        local_file = open(imagename, 'wb')

        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        resp.raw.decode_content = True

        # Copy the response stream raw data to local image file.
        shutil.copyfileobj(resp.raw, local_file)

        # Remove the image url response object to finish saving.
        del resp
        
    
    
def loop_scrape(api,liststrings,outputfolder,savedimagefolder):
    """
    This function loops through the list of ID strings to be fed into the "saveimage" function. 
    
    Takes in etsy API object, the list of listing-ID-strings, and the output
    folder string indicating where the images will be saved. The API object and output 
    folder are simply fed to the "saveimage" function. This function loops through the list
    of ID strings to be fed into the "saveimage" function. 
    
    This function returns "ct" - which tells the user how many images were scraped. 
    This is important if the API limits are reached before all the images can be scraped.
    """
    import time
    t0 = time.time()

    ct = 0
    for listid in liststrings:
        print("Ct: "+str(ct)+"; no. "+listid)
        # here, I want to check to see if the listid already exists in folder
        if os.path.exists(outputfolder+listid+".jpg")==True or os.path.exists(savedimagefolder+listid+".jpg"):
            print("Image already scraped.")
            ct+=1
            continue
        else:
            ct += 1
            saveimage(api,listid,outputfolder)
            time.sleep(0.3)

    elapsedtime = time.time() - t0
    print("Elapsed time: "+str(elapsedtime)+" seconds.")
    
    return ct


def run_scraper(myapikey, path2listingscsv, outputfolder, savedimagefolder):
    """
    Main driver.
    
    First create a list of ID strings with "read_listing_ids",
    then it creates the Etsy API object with the user-provided Etsy API key, 
    and then runs the "loop_scrape" function to scrape the images!
    
    Returns the "ct" variable provided in "loop_scrape" so the user can keep track of 
    how many images are scraped.
    """
    df = pd.read_csv(path2listingscsv)
    liststring = read_listing_ids(df)
    api = EtsyAPI(api_key=myapikey)
    ct = loop_scrape(api,liststring,outputfolder,savedimagefolder)
    
    return ct
