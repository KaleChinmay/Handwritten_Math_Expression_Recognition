"""

"""

import argparse
import inkml_data
import graph
import data_io
from configuration.configuration import Configuration
import os
import warnings
import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn import preprocessing as pp


warnings.filterwarnings("ignore", category=DeprecationWarning) 

class ParserProject:

	inkml_dict = None
	def __init__(self, location, parser, train='no'):
		self.location = location
		self.dprl_project_location = './lpga_release-master/src/'
		self.train_file_list_location = self.dprl_project_location+'../Data/Expressions/Training.txt'
		self.test_file_list_location = self.dprl_project_location+'../Data/Expressions/Testing.txt'
		if parser is None:
			self.parser_type = 'baseline'
		else:
			self.parser_type = parser
		self.train = train
		if(train=='yes'):
			self.parser_type = 'los'

	def __str__(self):
		return self.location + "\ntype="+self.parser_type+"\ndprl project location="+self.dprl_project_location


	def baseline_parser(self, inkml):
		keys = list(inkml.expression_trace.keys())
		i=1
		graph_nodes = []
		for key in inkml.expression_trace.keys():
			truth_instance = inkml.expression_trace[key].truth_instance
			node = graph.Node(i,'Node'+str(i),truth_instance, truth_instance.split('_')[0])
			node.trace = inkml.expression_trace[key].traces
			node.stroke_ids = inkml.expression_trace[key].trace_dict.keys()
			node.get_limits()
			graph_nodes.append(node)

			i+=1
		graph_nodes.sort(key = lambda x: x.min_x_point)
		edges = self.add_edges(graph_nodes)
		data_io.write_to_lg_files(inkml, graph_nodes, edges, self.location+'../LGs/')


	def add_edges(self, graph_nodes):
		edges = []
		for i in range(len(graph_nodes)-1):
			current_node_id = graph_nodes[i].id
			edge = graph.Edge(graph_nodes[i],graph_nodes[i+1],'Right')
			edges.append(edge)
		return edges


	def edit_config(self,subfolder):
		relative_dataset_lg_location = '../Data/Expressions/lg_output/'
		relative_dataset_location = '../Data/Expressions/inkml/'
		config_location = self.dprl_project_location+'configs/full_system_infty.conf'
		config = Configuration.from_file(config_location)

		#inkml
		inkml_path = config.get_str('TESTING_DATASET_PATH')
		config.set('TESTING_DATASET_PATH', relative_dataset_location+subfolder)
		inkml_path = config.get_str('TESTING_DATASET_PATH')
		config.write_to_file(config_location, 'TESTING_DATASET_PATH', inkml_path)

		#lg 
		lg_path = config.get_str('TESTING_DATASET_LG_PATH')
		config.set('TESTING_DATASET_LG_PATH', relative_dataset_lg_location+subfolder+'_lg')
		lg_path = config.get_str('TESTING_DATASET_LG_PATH')
		config.write_to_file(config_location, 'TESTING_DATASET_LG_PATH', lg_path)


	def sophisticated_parser(self):
		config_location = 'configs/full_system_infty.conf'
		print('Calling LPGA')
		print(config_location)
		if(self.train=='yes'):
			command = 'sudo python3 symbol_parse_script.py '+config_location+' 0'
		elif(self.train=='no'):
			command = 'sudo python3 symbol_parse_script.py '+config_location+' 1'
		current_project_context = os.path.abspath('.')
		dprl_project_context = os.path.abspath(self.dprl_project_location)
		os.chdir(dprl_project_context)
		os.system(command)
		os.chdir(current_project_context)



	def split_LPGA_dataset1(self, inkml_data):
	    uis_to_symbols = create_ui_symbol_map(inkml_data)
	    symbol_index_map, size = create_symbol_index_map(uis_to_symbols)
	    array = np.zeros(size)
	    uis = []
	    for ui in uis_to_symbols:
	        indices = np.zeros(size)
	        uis.append(ui)
	        for symbol in uis_to_symbols[ui]:
	            indices[symbol_index_map[symbol]] = uis_to_symbols[ui][symbol]
	        array = np.vstack((array, indices))
	    array = np.delete(array, (0), axis=0)
	    le = pp.LabelEncoder()
	    encoded_uis = le.fit_transform(uis)
	    x1 = np.zeros(len(encoded_uis))
	    x = np.column_stack((np.array(encoded_uis), x1))
	    x_train, y_train, x_test, y_test = train_test_split(x, array, test_size=(1 / 3))

	    x_train = x_train[:, 0].astype(int)
	    x_test = x_test[:, 0].astype(int)

	    training_ids = le.inverse_transform(x_train)
	    testing_ids = le.inverse_transform(x_test)

	    return set(training_ids.tolist()), set(testing_ids.tolist())

	def split_LPGA_dataset(self, inkml_data):
		file_names = []
		for key in inkml_data.keys():
			file_names.append(inkml_data[key].filename)
		train, test, _, _ = train_test_split(file_names, file_names, test_size=(1 / 3))
		return train, test



def create_symbol_index_map(ui_symbol_map):
    symbol_index_map = {}
    index = 0
    for ui in ui_symbol_map:
        for symbol in ui_symbol_map[ui]:
            if symbol not in symbol_index_map:
                symbol_index_map[symbol] = index
                index += 1
    return symbol_index_map, index

def create_ui_symbol_map(inkml_data):
    ui_symbol_map = {}
    for key in inkml_data:
        expression = inkml_data[key]
        ui_symbol_map[expression.ui] = {}
        for symbol in expression.expression_trace:
            character = symbol[:-2].strip('\\')
            if character in ui_symbol_map[expression.ui]:
                ui_symbol_map[expression.ui][character] = ui_symbol_map[expression.ui][character] + 1
            else:
                ui_symbol_map[expression.ui][character] = 1
    return ui_symbol_map



def create_ui_symbol_labels(inkml_data):
    ui_symbol_map = []
    for key in inkml_data:
        expression = inkml_data[key]
        row = [expression.ui]
        for symbol in expression.expression_trace:
            row.append(symbol)
        ui_symbol_map.append(row)
    return ui_symbol_map


