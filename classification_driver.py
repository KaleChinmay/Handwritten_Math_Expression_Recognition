"""

the driver file for the classification project
calls functions to preprocess, extract features, classify and evaluation


"""

import preprocessing
import feature_extraction

from sklearn.neighbors import NearestNeighbors as knn
from sklearn import tree
import preprocessing



def main():
    data = preprocessing.preprocess()

main()