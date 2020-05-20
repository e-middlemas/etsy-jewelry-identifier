import numpy as np
import time
import pickle
import matplotlib.pyplot as plt

# LSH stuff
from lshash_2 import LSHash
from tqdm import notebook
from PIL import Image


def calc_LSH(feature_dict,modeltype):
    # Locality Sensitive Hashing: this calculates the hashings for every feature vector 
    # in the feature_dict dictionary
    # params
    k = 32 # hash size
    L = 10  # number of tables
    d = len(feature_dict[next(iter(feature_dict))]) # Dimension of Feature vector
    # ^^ "next(iter(feature_dict))" - returns the first key of the dictionary. 

    lsh = LSHash(hash_size=k, input_dim=d, num_hashtables=L)

    # LSH on all the images
    start_time = time.time()
    for img_path, vec in notebook.tqdm(feature_dict.items()):
        lsh.index(vec, extra_data=img_path)

    end_time = time.time()

    print("Calculating feature vectors for 11k images took around 13-14 minutes.")
    print("Calculating hashes on 11k feature vectors took "+str(end_time-start_time)+" seconds. Pickling... ")

    # Exporting as pickle
    pickle.dump(lsh, open('./lsh_feature_'+modeltype+'classification.p', "wb"))

    
def get_similar_item(idx, feature_dict, lsh_variable, n_items,func):
    response = lsh_variable.query(feature_dict[list(feature_dict.keys())[idx]].flatten(), 
                     num_results=n_items+1, distance_func=func)    
    return response


def plot_similar_items(idx, n_items, feature_dict, lsh,func):
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