"""
script to generate a csv file that lists all inkml files needed for classifier
"""
import csv
import pandas as pd
import numpy as np
import copy
from sklearn.model_selection import train_test_split
from classification_driver import data_type_map
import sys


data_folder = './Data/'
SYMBOL_INKML_LIST_FILE = 'file_list_no_junk.csv'
JUNK_INKML_LIST_FILE = 'file_list_junk.csv'
TEST_INKML_LIST_FILE = 'test_file_list.csv'

def generate_dummy_data():
    """
    depracated. used to create fake data to test pipeline
    :return:
    """
    gt_file = open("trainingSymbols/iso_GT.txt")
    with open("dummy_data.csv", "w") as dummy:
        for line in gt_file:
            gts = line.split(",")
            dummy.write(gts[0] + ", -, +, n, 9, 8, 7, =, (, ), 5\n")
    gt_file.close()




#Generate csv containing inkml files list for both junk and valid symbols
def generate_inkml_file_list():
    """
    genreates list of inkml files to be used in pipeline
    :return:
    """
    symbol_files_count = 85801
    junk_files_count = 74283
    test_files_count = 18434
    generate_file_list('trainingSymbols',SYMBOL_INKML_LIST_FILE, 'iso', symbol_files_count)
    generate_file_list('trainingJunk',JUNK_INKML_LIST_FILE, 'junk',junk_files_count)
    generate_file_list('testSymbols',TEST_INKML_LIST_FILE,'iso',test_files_count)


#Generate csv for given file list
def generate_file_list(location, filename, ink_filename, file_count):
    """
    generates list of files
    :param location:
    :param filename:
    :param ink_filename:
    :param file_count: 
    :return:
    """
    with open(data_folder+filename,'w',newline='') as file_list:
        file_writer = csv.writer(file_list, delimiter=',')
        for i in range(file_count):
            file_name = data_folder+location+'/' + ink_filename + str(i) + '.inkml'
            file_writer.writerow([file_name])



def generate_features_table(data_object_list,feature_file_name):
    """
    generates csv containing feature vectors
    :param data_object_list:
    :param feature_file_name:
    :return:
    """
    with open(data_folder+feature_file_name,'w',newline='') as feature_list:
        file_writer = csv.writer(feature_list, delimiter=',')
        for i in range(len(data_object_list)):
            row_list = []
            for key in sorted(data_object_list[i].features.keys()):
                row_list.append(data_object_list[i].features[key])
            row_list.append(data_object_list[i].id)
            row_list.append(data_object_list[i].gt)
            file_writer.writerow(row_list)


def write_output_files(data, filename):
    data.to_csv(data_folder+filename, index=True, header=None,quoting=csv.QUOTE_NONE)