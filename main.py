import write_csv
import parse_data
import feature_extraction
from character_data import Character_Data
import pickle
from os import path


def main():
	print('Main Program Begins : ')
	write_csv.generate_file_list()
	print('File list Generated')
	if path.exists('intermediate.txt'):
		with open('intermediate.txt','rb') as pickle_file:
			data_object_list = pickle.load(pickle_file)
	else:
		data_object_list = parse_data.parse_data()
		with open('intermediate.txt','wb') as pickle_file:
			pickle.dump(data_object_list,pickle_file)
	print('object created')
	#Normalize
	count = len(data_object_list)
	i=0
	for data_object in data_object_list:
		i+=1
		#Code for Feature Extraction here:
		print(i,' of ',count,'.')
		#if(i !=65397):
		#	continue
		#print(data_object.norm_traces[0])
		#print('filename :',data_object.filename)
		data_object.translate_scale()
		feature_extraction.extract_all_features(data_object)
		#break
	write_csv.generate_features_table(data_object_list)
	print('data_normalized')
	#Feature Extraction follows

	#After this we can save all features in one csv as a table with final column as output(GT)
	#This will also save time for parsing ISO files again and again.







if __name__=='__main__':
	main()