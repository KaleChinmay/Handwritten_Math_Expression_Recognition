import write_csv
import parse_data
import feature_extraction
from character_data import Character_Data

def main():
	print('Main Program Begins : ')
	write_csv.generate_file_list()
	print('File list Generated')
	data_object_list = parse_data.parse_data()
	print('object created')
	#Normalize
	count = len(data_object_list)
	i=0
	for data_object in data_object_list:
		i+=1
		#Code for Feature Extraction here:
		print(i,' of ',count,'.')
		print('Object \n',data_object)
		data_object.translate_scale()
		feature_extraction.extract_all_features(data_object)
	print('data_normalized')
	#Feature Extraction follows

	#After this we can save all features in one csv as a table with final column as output(GT)
	#This will also save time for parsing ISO files again and again.







if __name__=='__main__':
	main()