# Basics
import os
import shutil
import numpy as np

from pipeline_functions import *

# Define source & destination image folders (without categories)

# source
imgpathorig = '/Users/eleanor/Dropbox/Documents/Career.NewJob/insightproject/repo/data/scraped_images/'
allimages = os.listdir(imgpathorig)
noimages = len(allimages)

# destination
outimgpath = os.path.join(os.getcwd(),'../data/binary_labeled/')

#------------------------------------------------------
# Execute functions in a loop across all images.
#------------------------------------------------------
    
for i,img in enumerate(allimages):
    if not (img.startswith('.')):
        img_path = imgpathorig+img
        preprocessed_image = preprocess_img(img_path)
        prediction = make_prediction(preprocessed_image)
        move_to_new_folder(img,prediction)

        print('Moved '+img+' to '+prediction+', '+str(noimages-i)+' left')    
        