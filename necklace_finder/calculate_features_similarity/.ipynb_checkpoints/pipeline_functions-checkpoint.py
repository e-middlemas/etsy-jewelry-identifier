# Basics
import shutil
import numpy as np
import time
import pickle
import os

# Image preprocessing stuff
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input

# Model stuff
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K

#------------------------------------------------------
# Load in model, define image path
#------------------------------------------------------

# Load in the model.
# modelpath = "/Users/eleanor/Dropbox/Documents/Career.NewJob/insightproject/repo/labeling/"

def load_trained_model(modeltype):
    modelpath = os.path.join(os.getcwd(),"./")
    if modeltype=='binary':
        modelfile = modelpath+"VGG_binaryclassifier_v1.h5"
    else:
        modelfile = modelpath+"VGG_categorical_classifier_round1.h5"
    model = load_model(modelfile)
    return model
    


#------------------------------------------------------
# Define functions
#------------------------------------------------------

def preprocess_img(img_path):
    """
    Converts an image to an array. Takes in a string
    with the whole image path (path + filename) and 
    outputs an array of numbers corresponding to the 
    image.
    """
    img = image.load_img(img_path, target_size=(150,150))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)

    return x


def make_prediction(img_array, model, modeltype):
    """
    Makes a prediction of the category using the model
    uploaded above on an inputted image array.
    
    Output is a string indicating the label of the 
    category.
    """
    prediction = model.predict(img_array)
    prediction = prediction.flatten()
    
    if modeltype=='binary':
        categories = np.array(['keep', 'throwaway'])
    else:
        # from label_map = (train_generator.class_indices) in code:
        # {'beadedpearl': 0, 'choker': 1, 'largependant': 2, 'longnecklaces': 3, 'smallpendant': 4, 'throwaway': 5}
        categories = np.array(['beadedpearl', 'choker', 'largependant', \
         'longnecklaces', 'smallpendant', 'throwaway'])


    return categories[prediction==max(prediction)][0]



def calc_feature_vectors(imgpath_list,modeltype):
    # decided on the third layer after looking at 
    # model.summary(). It's the last layer that produces
    # features before categorizing.
    
    model = load_trained_model(modeltype)
    
    if modeltype=='binary':
        layerno = 3 # the second-to-last layer is indexed 3
    else:
        layerno = 7 # the second-to-last layer is indexed 7

    get_intlayer_output = K.function([model.input],[model.layers[layerno].output])     
    
    # Convert images to arrays via "preprocess_img"
    # then, get_intlayer_output returns the feature vector
    # for the image. Playing with the output of get_intlayer_output
    # helped me decide to add the "[0].flatten()" to convert it
    # from a 3D array with zero dimensions to a 1D array.

    start_time = time.time()
    feature_dict = {f: get_intlayer_output([preprocess_img(f)])[0].flatten() for f in imgpath_list} 
    end_time = time.time()
    print("Total Time: "+str(end_time - start_time)+" seconds. Pickling..")
    
    pname = "./VGG_feature_"+modeltype+"_classification_necklaces.p"
    pickle.dump(feature_dict, open(pname, "wb"))

    
def move_to_new_folder(img_path,prediction,origpath,destpath):
    """
    Moves an image to a new path based on its model-
    predicted category. Image paths are hard-coded above.
    Takes in the image filename only - no paths to 
    filename should be included. Returns nothing.
    """
    source = origpath+img_path
    dest = destpath+prediction+"/"+img_path
#    shutil.move(source,dest)
    shutil.copy(source,dest)
    
