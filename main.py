import write_csv
import parse_data


def main():
	print('Main Program Begins : ')
	write_csv.generate_file_list()
	print('File list Generated')
	data = parse_data.parse_data()
	print('object created')
	#Normalize
	data.translate_scale()
	print(data_normalized)






if __name__=='__main__':
	main()