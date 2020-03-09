from character_data import Character_Data
import bs4
import csv
import sys
import write_csv
from os import path
import pickle

"""
__author__ = Laurne Cole, Chinmay Kale
functions for retrieving script from inkml files
"""
data_folder = './Data/'


def get_gt(gt_location):
	"""
	parse a ground truth file into a dictionary mapping ground truths to ids
	:param gt_location:
	:return:
	"""
	#gt_location = 'trainingSymbols/iso_GT.txt'
	gt_dict = {}
	with open(data_folder+gt_location,'r') as gt:
		for line in gt:
			temp_list = line.split(',')
			gt_dict[temp_list[0]] = temp_list[1]
	return gt_dict


def remove_dups(data):
	"""
	remove duplicate points from traces and convert to float
	:param data:
	:return:
	"""
	data_trace_len = len(data.trace)
	for i in range(data_trace_len):
		data_trace_i_len = len(data.trace[i])

		for j in range(data_trace_i_len):

			point = data.trace[i][j].strip()
			point = point.split(' ')
			point_dimensions = len(point)

			for k in range(point_dimensions):
				point[k] = float(point[k])
			data.trace[i][j] = point
	return data


def parse_inkml(listfile_name, gt_location, junk_param):
	"""
	read inkml file and create character data objects
	:param listfile_name:
	:param gt_location:
	:param junk_param:
	:return:
	"""
	gt_dict = {}
	with open(data_folder+listfile_name,'r') as trace_file_list:
		data = csv.reader(trace_file_list,delimiter=',')
		gt_dict = get_gt(gt_location)
		data_obj_list = []
		i = 0
		data_len = len(gt_dict.keys())
		for row in data:
			file_name = row[0]
			with open(file_name,'r') as inkml_file:
				i+=1
				print(i,' of ',data_len)
				xml_data = bs4.BeautifulSoup(inkml_file, 'lxml')
				ink = xml_data.ink
				#Meta data for the inkml files
				name = ink.find_all('annotation')[1].get_text()
				trace = ink.trace
				data_obj = Character_Data()
				data_obj.filename = file_name
				data_obj.id = name
				if(junk_param!='2'):
					data_obj.gt = gt_dict[name].strip()
				else:
					data_obj.gt = 'NA'
				temp_content = [[content.strip() for content in trace.contents] for trace in ink.find_all('trace')]
				x = [[a.split(',') for a in trace][0] for trace in temp_content]
				data_obj.trace = x
				data_obj = remove_dups(data_obj)
				data_obj_list.append(data_obj)
	return data_obj_list



def serializa_data_obj_list(serialized_filename, input_inkml_list_file, gt_file_location, junk_param):
	"""
	serialize a list of data objects to a binary pickle file
	:param serialized_filename:
	:param input_inkml_list_file:
	:param gt_file_location:
	:param junk_param:
	:return:
	"""
	data_obj_list = []
	if path.exists(data_folder+serialized_filename):
		with open(data_folder+serialized_filename,'rb') as pickle_file:
			data_obj_list = pickle.load(pickle_file)
	else:
		data_obj_list = parse_inkml(input_inkml_list_file,gt_file_location, junk_param)
		with open(data_folder+serialized_filename,'wb') as pickle_file:
			pickle.dump(data_obj_list,pickle_file)
	return data_obj_list



def parse_data(junk_param):
	"""
	write data to files
	:param junk_param:
	:return:
	"""
	symbol_data_obj_list = []
	junk_data_obj_list = []

	symbol_data_obj_list = serializa_data_obj_list('symbols_objs.txt',
		write_csv.SYMBOL_INKML_LIST_FILE,'trainingSymbols/iso_GT.txt', junk_param)

	junk_data_obj_list= serializa_data_obj_list('junk_objs.txt',
		write_csv.JUNK_INKML_LIST_FILE,'trainingJunk/junk_GT_v3.txt', junk_param)

	test_data_obj_list = serializa_data_obj_list('test_objs.txt',
		write_csv.TEST_INKML_LIST_FILE,'testSymbols/symbols_with_junk_GT.txt' , 2)
	return symbol_data_obj_list , junk_data_obj_list, test_data_obj_list