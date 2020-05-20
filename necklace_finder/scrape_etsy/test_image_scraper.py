""" 
Testing Image Scraper code located in image_scraper.py
Written by Eleanor Middlemas
Originally written January 20, 2020

This code is simply to test the image scraper functions. If a user wants to utilize this code,
they must insert paths to their own folders containing scraped images, path to the csv file, and the path to the text file containing their API key (i.e., those indicated with outputfolder, savedimagefolder, and path2listingscsv)
"""

from image_scraper import run_scraper


outputfolder = "./scraped_images/"
savedimagefolder = "./all_images/"

path2listingscsv =" "

path = " "
file_object  = open(path+"etsy_api_key.txt","r")
myapikey = file_object.read()

ct = run_scraper(myapikey, path2listingscsv, outputfolder, savedimagefolder)
print("Stopped at count: "+str(ct))
