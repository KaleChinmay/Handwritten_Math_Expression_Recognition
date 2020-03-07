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

	print('Main Program Begins : ')
	write_csv.generate_file_list()
	write_csv.generate_junk_file_list()
	print('File list Generated')
	if path.exists(classification_driver.data_type_map[sys.argv[1]]+'ser_objs.txt'):
		with open(classification_driver.data_type_map[sys.argv[1]]+'ser_objs.txt','rb') as pickle_file:
			data_object_list = pickle.load(pickle_file)
	else:
		data_object_list = parse_data.parse_data()
		with open(classification_driver.data_type_map[sys.argv[1]]+'ser_objs.txt','wb') as pickle_file:
			pickle.dump(data_object_list,pickle_file)
	print('object created')
	#Normalize
	if not path.exists('.\\Data\\feature_list_'+classification_driver.data_type_map[sys.argv[1]]+'.csv'):
		count = len(data_object_list)
		i=0
		for data_object in data_object_list:
			i+=1
			#Code for Feature Extraction here:
			print(i,' of ',count,'.')
			data_object.translate_scale()
			feature_extraction.extract_all_features(data_object)
		write_csv.generate_features_table(data_object_list)
		print('data_normalized')

	classification_driver.classify()
	#Feature Extraction follows

	#After this we can save all features in one csv as a table with final column as output(GT)
	#This will also save time for parsing ISO files again and again.







if __name__=='__main__':
	main()