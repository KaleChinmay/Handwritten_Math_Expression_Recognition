import write_csv
import parse_data
import feature_extraction	
from character_data import Character_Data
import classification_driver
import pickle
from os import path
import sys

"""
COMMAND LINE ARGS GUIDE
sys.argv[1] = junk, no junk or bonus. 0 = no junk, 1 = with junk, 2 = all for  bonus, 3 = junk only
sys.argv[2] = classifier type. 0 = kd tree, 1 = random forest
"""

def main():


	junk_param = sys.argv[1]
	classifier_param = sys.argv[2]
	print('Main Program Begins : ')
	write_csv.generate_inkml_file_list()
	symbol_data_obj_list , junk_data_obj_list = parse_data.parse_data()
	print(len(symbol_data_obj_list))
	print(len(junk_data_obj_list))

	print('object created')
	symbol_data_obj_list = feature_extraction.get_features(symbol_data_obj_list,'symbol_feature_list.csv')
	junk_data_obj_list = feature_extraction.get_features(junk_data_obj_list,'junk_feature_list.csv')
	print('Features extracted')

	classification_driver.classification(junk_param, classifier_param)
	#Feature Extraction follows

	#After this we can save all features in one csv as a table with final column as output(GT)
	#This will also save time for parsing ISO files again and again.
	print('Done!')






if __name__=='__main__':
	main()