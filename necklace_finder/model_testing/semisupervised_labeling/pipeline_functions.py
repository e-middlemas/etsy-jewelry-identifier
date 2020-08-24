# Basics
import shutil
import numpy as np
import time
import pickle
import os
import matplotlib.pyplot as plt

# Image preprocessing stuff
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input

# Model stuff
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K

# LSH stuff
from lshash_2 import LSHash
from tqdm import notebook
from PIL import Image


#------------------------------------------------------
# Load in model, define image path
#------------------------------------------------------

# Load in the model.
modelpath = "$USER-DEFINED"

def load_trained_model():
    #modelpath = os.path.join(os.getcwd(),"./")
    modelfile = modelpath+"VGG_binaryclassifier_v1_updated_4layers_even.smallerLR.h5"
    return load_model(modelfile)
    


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
    try:
        img = image.load_img(img_path, target_size=(150,150))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

    except:
        x = 0
 
    return x


def make_prediction(img_array, model):
    """
    Makes a prediction of the category using the model
    uploaded above on an inputted image array.
    
    Output is a string indicating the label of the 
    category.
    """
    prediction = model.predict(img_array)
    prediction = prediction.flatten()
    
    categories = np.array(['keep', 'throwaway'])

    return categories[prediction==max(prediction)][0]



def calc_feature_vectors(imgpath_list):
    # If feature_dict is passed into the function, this code
    # will automatically append to it.
    
    model = load_trained_model()

    # decided on the third layer after looking at 
    # model.summary(). It's the last layer that produces
    # features before categorizing.
    
    layerno = 3 # the second-to-last layer is indexed 3
    get_intlayer_output = K.function([model.input],[model.layers[layerno].output])     
    # Convert images to arrays via "preprocess_img"
    # then, get_intlayer_output returns the feature vector
    # for the image. Playing with the output of get_intlayer_output
    # helped me decide to add the "[0].flatten()" to convert it
    # from a 3D array with zero dimensions to a 1D array.

    start_time = time.time()
    feature_dict = {f: get_intlayer_output([preprocess_img(f)])[0].flatten() for f in imgpath_list} 
    end_time = time.time()
    print("Total Time: "+str(end_time - start_time)+" seconds.")
    
    return feature_dict

    
def move_to_new_folder(img_path,prediction,origpath,destpath):
    """
    Moves an image to a new path based on its model-
    predicted category. Image paths are user-provided.
    Returns nothing.
    """
    source = origpath+img_path
    dest = destpath+prediction+"/"+img_path
    shutil.move(source,dest)
#    shutil.copy(source,dest)
    
    
def calc_LSH(feature_dict):
    # Locality Sensitive Hashing: this calculates the hashings for 
    # every feature vector in the feature_dict dictionary
    
    # if an lsh object is passed to the function, it skips creating the
    # the hash object.
    
    # params
    k = 5 # hash size
    L = 7  # number of tables
    d = len(feature_dict[next(iter(feature_dict))]) # Dimension of Feature vector
    
    # initialize hash object
    lsh = LSHash(hash_size=k, input_dim=d, num_hashtables=L)
    
    # Save hash on all the images
    for img_path, vec in notebook.tqdm(feature_dict.items()):
        lsh.index(vec, extra_data=img_path)
        
    return lsh
    
    
def get_similar_item(idx, feature_dict, lsh_variable, n_items,func):
    response = lsh_variable.query(feature_dict[list(feature_dict.keys())[idx]].flatten(), num_results=n_items+1, distance_func=func)    
    return response


def plot_similar_items(idx, feature_dict, lsh, n_items, func):
    response = get_similar_item(idx, feature_dict, lsh, n_items,func)
    
    columns = 3
    rows = int(np.ceil(n_items+1/columns))
    fig=plt.figure(figsize=(2*rows, 3*rows))
    for i in range(1, columns*rows +1):
        if i<n_items+2:
    #        print(response[i-1][0][1]) # uncomment to print filename in addition to images.
            img = Image.open(response[i-1][0][1])
            fig.add_subplot(rows, columns, i)
            plt.imshow(img)
            plt.axis('off')
    plt.show()
