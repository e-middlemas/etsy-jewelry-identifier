"""
Sort images into folders labeling them as necklaces & non-necklaces.
Eleanor Middlemas
January 2020

This code sorts images based on the predictions made by the binary model: i.e., whether or not the image contains a necklace.
"""

# Basics
import os
import shutil
import numpy as np

from pipeline_functions import *

# Define source & destination image folders (without categories)

# source
imgpathorig = '$USER-DEFINED'
allimages = [f for f in os.listdir(imgpathorig) if f.endswith(".jpg")]
noimages = len(allimages)

# destination
outimgpath = os.path.join(os.getcwd(),'../data/binary_labeled/')

#------------------------------------------------------
# Execute functions in a loop across all images.
#------------------------------------------------------

model = load_trained_model()

for i,img in enumerate(allimages):
    if not (img.startswith('.')):
        img_path = imgpathorig+img
        preprocessed_image = preprocess_img(img_path)
        if preprocessed_image.all()==0:
            prediction = 'throwaway'
        else:
            prediction = make_prediction(preprocessed_image,model)
        if prediction=='throwaway':
            move_to_new_folder(img,prediction,imgpathorig,outimgpath)
            print('Moved '+img+' to '+prediction+', '+str(noimages-i)+' left')
        else:
            move_to_new_folder(img,prediction,imgpathorig,imgpathorig)
            print("Image kept.")
        
