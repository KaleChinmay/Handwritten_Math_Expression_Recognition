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


data_folder = '.\\Data\\'
SYMBOL_INKML_LIST_FILE = 'file_list_no_junk.csv'
JUNK_INKML_LIST_FILE = 'file_list_junk.csv'

def generate_dummy_data():
    gt_file = open("trainingSymbols/iso_GT.txt")
    with open("dummy_data.csv", "w") as dummy:
        for line in gt_file:
            gts = line.split(",")
            dummy.write(gts[0] + ", -, +, n, 9, 8, 7, =, (, ), 5\n")
    gt_file.close()




#Generate csv containing inkml files list for both junk and valid symbols
def generate_inkml_file_list():
    symbol_files_count = 85801
    junk_files_count = 74283
    generate_file_list('trainingSymbols',SYMBOL_INKML_LIST_FILE, 'iso', symbol_files_count)
    generate_file_list('trainingJunk',JUNK_INKML_LIST_FILE, 'junk',junk_files_count)


#Generate csv for given file list
def generate_file_list(location, filename, ink_filename, file_count):
    with open(data_folder+filename,'w',newline='') as file_list:
        file_writer = csv.writer(file_list, delimiter=',')
        for i in range(file_count):
            file_name = data_folder+location+'\\' + ink_filename + str(i) + '.inkml'
            file_writer.writerow([file_name])



def generate_features_table(data_object_list,feature_file_name):
    with open(data_folder+feature_file_name,'w',newline='') as feature_list:
        file_writer = csv.writer(feature_list, delimiter=',')
        for i in range(len(data_object_list)):
            row_list = []
            for key in sorted(data_object_list[i].features.keys()):
                row_list.append(data_object_list[i].features[key])
            row_list.append(data_object_list[i].id)
            row_list.append(data_object_list[i].gt)
            file_writer.writerow(row_list)



def write_output_csv_files(data):

    #temp_data = copy.deepcopy(data)
    #with junk
    train_data_junk, test_data_junk = train_test_split(data,
        test_size = 0.3)
    train_data_junk.to_csv(data_folder+'train_junk.csv', index=False)
    test_data_junk.to_csv(data_folder+'test_junk.csv', index=False)

    #without junk
    data_without_junk = data[data['Class label']!='junk']
    train_data_w_junk, test_data_w_junk = train_test_split(data_without_junk,
        test_size = 0.3)
    train_data_w_junk.to_csv(data_folder+'train_w_junk.csv', index=False)
    test_data_w_junk.to_csv(data_folder+'test_w_junk.csv', index=False)
