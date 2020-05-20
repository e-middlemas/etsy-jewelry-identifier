"""
Driver for scraping Etsy listings of necklaces and associated images on listings, to eventually be used for the webapp Neck-Less Searching. This webapp uses a CNN to locate the necklaces from the scraped listings that most closely resembles that of a user-provided image. 

Written by Eleanor Middlemas
January 20, 2020

Please see README_Etsy_Scraper for more information. 

*** User must: ***
- Define output_image_path - the path to a folder where the user would like to store newly-scraped images.
- Define prev_saved_image_folder - the path to a folder containing images that have already been scraped. This folder and the output_image_path folder may be the same. 
- Define output_csv_path - the path where the user would like to save a csv of the text from each listing, i.e., potential labels for the necklaces, but more importantly, the listing ids, which are used to scrape the associated necklace images
- Ensure that they have applied for an Etsy Developer account, which provides an Etsy API key. This API key should be stored in a text file titled "etsy_api_key.txt" in the same directory as this driver.
- Define "nolistings" & "mxlistings" below. 
    - "nolistings" is the total number of listings the users wishes to scrape at once. I think the typical limit of API pings for new Etsy developers is 10,000. Please take this into account as we must ping the API twice for each listing: once for the text & to obtain the listing ID, and once more to obtain the associated image. 
    - "mxlistings" - this is the number of listings to scrape at once. I think the limit is 100.
"""

from image_scraper import run_scraper
from datetime import datetime
from text_scraper import run_text_scraper


output_image_path = "$USER-DEFINED"
prev_saved_image_folder = "$USER-DEFINED"

now = datetime.now() # current date and time
d = now.strftime("%m/%d/%Y")
h = now.strftime("%I%p")

# USER: Ensure the following path is desired
output_csv_path = os.getcwd()+"./$USER-DEFINED"
csv_name = "raw_textlistings_"+d+"."+h+".csv"

file_object  = open(os.getcwd()+"etsy_api_key.txt","r")
myapikey = file_object.read()

nolistings = 1
mxlistings = 1

run_text_scraper(apikey, nolistings, maxlistings, output_csv_path, csv_name)

ct = run_scraper(myapikey, output_csv_path+csv_name, 
                 output_image_path, prev_saved_image_folder)

print("Stopped at count: "+str(ct))
