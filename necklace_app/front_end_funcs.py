#-------------------------------------------------------------------------------
# basic functions & analytics
import os
import numpy as np
import pandas as pd
import time

# making predictions & extracting features with model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K

# pinging SQL
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2

# loading classified image features
import pickle

#-------------------------------------------------------------------------------

noitems = 4
#mainpath = os.getcwd()+"/static/data/"
mainpath = os.getcwd()+"/necklace_app/static/data/"

def read_in_image(imgpath):
    tstart = time.time()
    img = image.load_img(imgpath,target_size=(150,150))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    processedimage = preprocess_input(x)
    
    tend = time.time()
    print("Reading in image took: "+str(tend-tstart)+" seconds.")
    
    return processedimage


def load_model_classify_input(processedimage):
    tstart = time.time()
    modelfile = mainpath+"VGG_binaryclassifier_v1_updated_4layers_even.smallerLR.h5"
    model = load_model(modelfile)
    prediction = model.predict(processedimage)

    categories = np.array(['keep', 'throwaway'])
    
    tend = time.time()
    print("Reading in model & making prediction took: "+str(tend-tstart)+" seconds.")
    
    return model, categories[prediction[0]==max(prediction[0])][0]


def extract_img_features(model,imgpath,processedimage):
    tstart = time.time()
    feature_dict = pickle.load(open(mainpath+"VGG_feature_binary_classification_necklaces.p","rb"))
    get_intlayer_output = K.function([model.input],
                                  [model.layers[3].output])
    newimgfeature = get_intlayer_output([processedimage])[0].flatten()
    feature_dict[imgpath] = newimgfeature

    tend = time.time()
    print("Extracting features & adding them to dictionary took: "+str(tend-tstart)+" seconds.")

    return feature_dict


def cosine_dist(x, y):
        return 1 - np.dot(x, y) / ((np.dot(x, x) * np.dot(y, y)) ** 0.5)
    
def euclidean_dist(x, y):
    """ This is a hot function, hence some optimizations are made. """
    diff = np.array(x) - y
    return np.sqrt(np.dot(diff, diff))


def calc_distances(feature_dict, imgpath):
    tstart = time.time()
    origkeys = list(feature_dict.keys())
    
    distances = {}
    keyno = list(feature_dict.keys()).index(imgpath)
    for key in feature_dict.keys():
    #    d = euclidean_dist(feature_dict[origkeys[keyno]],feature_dict[key])
        d = cosine_dist(feature_dict[origkeys[keyno]],feature_dict[key])
        distances[d] = key
    tend = time.time()
    print("Calculating distances manually took: "+str(tend-tstart)+" seconds.")
    
    tstart = time.time()
    sorted_distance = {k: v for k, v in sorted(distances.items(), key=lambda item: item[0],reverse=False)}
    keys = list(sorted_distance.keys())

    similar_listings = []
    distances = []
    for i in range(0,noitems+1):
        distances.append(1-keys[i])
        tmp = sorted_distance[keys[i]].split("/")
        tmp = tmp[-1].split(".")
        similar_listings.append(tmp[0])

    tend = time.time()
    print("Finding similar items took: "+str(tend-tstart)+" seconds.")
    
    return similar_listings, distances

def find_price_url(similar_listings):

    dbname = 'listing_text'
    username = 'ubuntu' # change this to your username
#    username = 'postgres' # change this to your username
    pw = '' # insert your password here

    engine = create_engine('postgres://%s:%s@localhost/%s'%(username,pw,dbname))
    print(engine.url)
    con = None
    con = psycopg2.connect(database = dbname, user = username, password = pw)
    
    listing = []
    for i in range(1,noitems+1):
        listingid = similar_listings[i]

        sql_query = """
        SELECT category, price, url, listing_id
        FROM """+dbname+"""
        WHERE listing_id="""+listingid+"""
        ;
        """
        listing.append(pd.read_sql_query(sql_query,con))

    listing = pd.concat(listing)

    if len(listing['listing_id'])>noitems:
        listing = listing.drop([1])

    print("Extracted from database successfully!")
        
    return listing

def return_similar_necklaces(imgpath):
    x = read_in_image(imgpath)
    model, prediction = load_model_classify_input(x)
    print(prediction)
    if prediction!='throwaway':
        features = extract_img_features(model,imgpath, x)
        similar_listings, distances = calc_distances(features, imgpath)
        listing_info = find_price_url(similar_listings)
        
        return prediction, listing_info, distances
    else:
        return prediction, None, None
            
    
        
