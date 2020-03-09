import write_csv
import parse_data
import feature_extraction
from character_data import Character_Data
import classification_driver
import pickle
from os import path
import sys
import os

"""
__author__ = Laurne Cole, Chinmay Kale
driver file for classification pipeline
"""
"""
COMMAND LINE ARGS GUIDE
sys.argv[1] = junk, no junk or bonus. 0 = no junk, 1 = with junk,  2 = train all dataset, (Test on new dataset)
sys.argv[2] = classifier type. 0 = kd tree, 1 = random forest
sys.argv[3] = Train Flag,  0 = test with existing model, 1 = Train again
"""

data_folder = './Data/'

def main():


	junk_param = sys.argv[1]
	classifier_param = sys.argv[2]
	train_param = sys.argv[3]
	#split_param = sys.argv[4]

	print('Main Program Begins : ')
	write_csv.generate_inkml_file_list()
	symbol_data_obj_list , junk_data_obj_list, test_data_obj_list = parse_data.parse_data(junk_param)
	print(len(symbol_data_obj_list))
	print(len(junk_data_obj_list))
	print(len(test_data_obj_list))

	print('object created')
	symbol_data_obj_list = feature_extraction.get_features(symbol_data_obj_list,'symbol_feature_list.csv')
	junk_data_obj_list = feature_extraction.get_features(junk_data_obj_list,'junk_feature_list.csv')
	test_data_obj_list = feature_extraction.get_features(test_data_obj_list,'test_feature_list.csv')
	print('Features extracted')

	prediction_file, GT_file = classification_driver.classification(junk_param, classifier_param, train_param)
	#Feature Extraction follows
	if(prediction_file is not None and GT_file is not None):
		command = 'python evalSymbIsole.py '+data_folder+GT_file+' '+data_folder+prediction_file+' HTML > output.html'
		#After this we can save all features in one csv as a table with final column as output(GT)
		#This will also save time for parsing ISO files again and again.
		os.system(command)
	print('Done!')






if __name__=='__main__':
	main()

