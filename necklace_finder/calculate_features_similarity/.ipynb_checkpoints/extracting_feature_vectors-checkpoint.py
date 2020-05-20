
from pipeline_functions import calc_feature_vectors
import os

#------------------------------------------------------
# Define string of image paths
#------------------------------------------------------

# Hard code image path to prevent errors when reading from 
# feature vector later.
imgpath = '/Users/eleanor/Dropbox/Documents/Career.NewJob/insightproject/repo/data/binary_labeled/keep/'
images = os.listdir(imgpath)

# Produce a vector of full paths to filenames
filenames = [imgpath+img for img in images if not (img.startswith('.'))]
noimages = len(filenames)

#------------------------------------------------------
# Calculate feature vectors for files
#------------------------------------------------------

# requires a full pathname to file
calc_feature_vectors(filenames,'categorical_v1')
