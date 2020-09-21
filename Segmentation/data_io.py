import bs4
import os
from inkml_data import InkMLData
from inkml_data import TraceGroup
import pickle
import scipy.interpolate as interpolate
import csv
import copy
import numpy as np

#interpolation length


def get_inkml_data(inkml_path):
	dirs = os.listdir(inkml_path)
	dirs = [os.path.join(inkml_path, folder,"") for folder in dirs]
	inkml_data_list = {}
	for expression_folder in dirs:
		inkml_files = os.listdir(expression_folder)
		inkml_files = [os.path.join(expression_folder, files) for files in inkml_files]
		#print('-------------------------------------------------------------------------------')
		#print(inkml_files)
		i = 0
		inkml_files_len = len(inkml_files)
		for inkml in inkml_files:
			i+=1
			print('Progress : ',i,' of ',inkml_files_len)
			inkml_data = get_inkml(inkml)
			if(inkml_data):
				inkml_data_list[inkml_data.ui] = inkml_data



	with open('inkml_binary.obj','wb') as ink_obj:
		pickle.dump(inkml_data_list, ink_obj)



def get_inkml(inkml_file_path):
	inkml_data = InkMLData()
	with open(inkml_file_path,'rb') as inkml_file:
		#print('<><><><><>')
		#print('File Name : ', inkml_file_path)
		xml_data = bs4.BeautifulSoup(inkml_file, "lxml")
		ink = xml_data.ink
		if(ink==None):
			return None
		category = ''
		expression = ''
		ui = ''
		gt = ''
		writer = ''
		if(ink.find('annotation',{'type':'category'})):
			category = ink.find('annotation',{'type':'category'}).get_text()
			inkml_data.category = category
		if(ink.find('annotation',{'type':'expression'})):
			expression = ink.find('annotation',{'type':'expression'}).get_text()
			inkml_data.expression = expression
		if(ink.find('annotation',{'type':'ui','type':'UI'})):
			ui = ink.find('annotation',{'type':'ui','type':'UI'}).get_text()
			inkml_data.ui = ui.strip()
		else:
			print("NOO")
		if(ink.find('annotation',{'type':'writer'})):
			writer = ink.find('annotation',{'type':'writer'}).get_text()
			inkml_data.writer = writer
		if(ink.find('annotation',{'type':'truth'})):
			gt= ink.find('annotation',{'type':'truth'}).get_text()
			inkml_data.gt = gt
		inkml_data.path = inkml_file_path
		expression_trace = get_expression_trace(ink)
		inkml_data.expression_trace = expression_trace
		file_name = os.path.basename(inkml_file.name)
		inkml_data.filename = file_name.split('.')[0]
	return inkml_data




def get_expression_trace(ink_xml_object):
	expression_trace = None
	#outer xml
	expression_trace_xml = ink_xml_object.find('tracegroup')
	#inner xml
	trace_group_list = expression_trace_xml.findAll('tracegroup')
	trace_group_obj_dict = {}

	for symbol_trace_group in trace_group_list:
		trace_group_obj = TraceGroup()
		truth_label = symbol_trace_group.find('annotation',{'type':'truth'}).get_text()
		traceviews = symbol_trace_group.findAll('traceview')
		truth_instance = None
		if(symbol_trace_group.find('annotationxml')):
			truth_instance = symbol_trace_group.find('annotationxml')['href']
		else:
			if(len(traceviews)<=1):
				break
			trace_id = traceviews[1]['tracedataref']
			truth_instance = truth_label+"_xkey_id"+trace_id
		
		traces = []
		trace_dict = {}
		for traceview in traceviews:
			#print('================================')
			trace_reference = traceview['tracedataref']
			symbol_traces_xml = ink_xml_object.find(id=trace_reference)
			symbol_trace = symbol_traces_xml.get_text()
			strokes = process_traces(symbol_trace)
			#print(symbol_trace)
			#traces.append(symbol_trace)
			traces.append(strokes)
			trace_dict[trace_reference] = strokes
		trace_group_obj.truth_label = truth_label
		trace_group_obj.truth_instance = truth_instance
		trace_group_obj.traces = traces
		trace_group_obj.trace_dict = trace_dict
		trace_group_obj_dict[truth_instance] = trace_group_obj
		# print(trace_dict)
	# print('Before')

	# print('<><><><><><><><><><><><><><>')
	normalize_expression(trace_group_obj_dict)
	# interpolate_expression(trace_group_obj_dict)
	return trace_group_obj_dict


def get_average_distance(stroke):
	size = len(stroke)
	avg_distance = 0
	for i in range(1, size):
		avg_distance += np.linalg.norm(np.array(stroke[i]) - np.array(stroke[i-1]))
	avg_distance = avg_distance/size

	return avg_distance

def interpolate_expression(trace_group_obj_dict):
	"""
	step must occur after duplicate point removal

	:param trace_group_obj_dict:
	:return:
	"""
	# print(trace_group_obj_dict)
	for group_key in trace_group_obj_dict:
		trace_dict = trace_group_obj_dict[group_key].norm_trace_dict
		for trace_key in trace_dict:
			new_stroke = []
			stroke = trace_dict[trace_key]
			distance = get_average_distance(stroke)/2
			size = len(stroke)
			for i in range (1, size):
				if stroke[i][0] <= stroke[i-1][0]:
					backwards = True
				else:
					backwards = False
				#determine how many points to add
				n = int(((np.linalg.norm(np.array(stroke[i]) - np.array(stroke[i-1]))) // distance) - 1)
				# print(n)
				new_stroke.append(stroke[i - 1])

				if n > 0:
					x_change = (stroke[i][0] - stroke[i-1][0]) / (n + 1)
					x = []
					for j in range(1, n+1):
						x.append(stroke[i-1][0] + j * x_change)
					if not backwards:
						y = np.interp(x, [stroke[i-1][0], stroke[i][0]], [stroke[i-1][1], stroke[i][1]])
					else:
						x.reverse()
						y = list(np.interp(x, [stroke[i][0], stroke[i-1][0]], [stroke[i][1], stroke[i-1][1]]))
						x.reverse()
						y.reverse()
					for j in range(n):
						new_stroke.append([x[j], y[j]])

					print(stroke[i-1], stroke[i])
					print("Xs", x, "Ys", y)
			new_stroke.append(stroke[size-1])

			# print(len(new_stroke), len()
			trace_dict[trace_key] = new_stroke
			# print("STROKE:", stroke)
			# print("INTERP:", new_stroke)


def normalize_expression(trace_group_obj_dict):
	print(trace_group_obj_dict)
	max_x_point = None
	min_x_point = None
	max_y_point = None
	min_y_point = None
	width = 0
	height = 0
	min_x = 99999999
	max_x = 0
	min_y = 99999999
	max_y = 0
	for group_key in trace_group_obj_dict.keys():
		trace_dict = trace_group_obj_dict[group_key].trace_dict
		for key1 in trace_dict.keys():
			stroke = trace_dict[key1]
			for point in stroke:
				if point[0] > max_x:
					max_x = point[0]
					max_x_point = point
				if point[0] < min_x:
					min_x = point[0]
					min_x_point = point
				if point[1] > max_y:
					max_y = point[1]
					max_y_point = point
				if point[1] < min_y:
					min_y = point[1]
					min_y_point = point
	width = max_x-min_x
	height = max_y-min_y
	if(height==0):
		height = 1
	aspect_ratio = width/height

	for group_key in trace_group_obj_dict.keys():
		trace_dict = trace_group_obj_dict[group_key].trace_dict
		t_stroke_dict = None
		t_stroke_dict = copy.deepcopy(trace_dict)
		for key2 in t_stroke_dict.keys():
			stroke = t_stroke_dict[key2]
			for point in stroke:
				if(min_x >= 0):
					point[0] = point[0]-min_x
				else:
					point[0] = point[0]+min_x
				if(min_y >= 0):
					point[1] = point[1]-min_y
				else:
					point[1] = point[1]+min_y

		s_t_stroke_dict = None
		s_t_stroke_dict = copy.deepcopy(trace_dict)
		for key3 in s_t_stroke_dict.keys():
			stroke = s_t_stroke_dict[key3]
			for point in stroke:
				if(height >= width):
					point[1] = (2*point[1]/height)
					point[0] = (2*point[0]/height)
				else:
					point[0] = (2*point[0]/width)
					point[1] = (2*point[1]/width)


		trace_group_obj_dict[group_key].norm_trace_dict = s_t_stroke_dict
		# print(s_t_stroke_dict)





def remove_duplicates(stroke_list):
	new_list = []
	seen = set()
	for stroke in stroke_list:
		if (stroke[0], stroke[1]) not in seen:
			seen.add((stroke[0], stroke[1]))
			l = []
			for s in stroke:
				l.append(float(s))
			new_list.append(l)
	return new_list



def process_traces(symbol_trace):
	strokes = symbol_trace.split(',')
	stroke_list = []
	for point_string in strokes:
		point_string = point_string.strip()
		point_x_y = point_string.split(' ')
		point_x_y_int = []
		for axis in point_x_y:
			# point_x_y_int.append(float(axis.strip()))
			point_x_y_int.append(axis.strip())
		stroke_list.append(point_x_y_int)
	stroke_list = remove_duplicates(stroke_list)
	return stroke_list



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


def write_to_lg_files(inkml, inkml_key, graph, data_dir):
	models_directory =  data_dir+'/LGs/'
	nodes_num = len(graph)
	text = '# IUD, '+inkml.filename+'\n'
	text += '# Objects('+str(nodes_num)+'):\n'
	for node in graph:
		# text += '# Object: '+str(node.label_id)+' .\n'
		# text += 'N, '+str(node.id)+', '+str(node.predicted)+', 1.0\n'
		stroke_id_string = ', '.join([str(ids) for ids in node.stroke_ids])
		text += 'O, ' +str(node.label_id)+ ", " +str(node.predicted)+', 1.0, ' + stroke_id_string + "\n"
	print('inkml.filename : ',inkml.filename)
	with open(inkml.filename+'.lg','w') as f:
		f.write(text)	
