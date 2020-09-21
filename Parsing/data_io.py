"""
__author__: Lauren Cole, Chinmay Kale
script containing functions for reading and writing data from files
"""

import bs4
from inkml_data import InkMLData
from inkml_data import TraceGroup
import os
import re
import shutil


def parse_inkml_list(inkml_file_list):
    """
    creates a dictionary of inkmldata objects mapped to their uis
    :param inkml_file_list: text file containing a list of inkml file paths to process. one inkml file per line
    :return:
    """
    inkml_dict = {}
    i = 0
    with open(inkml_file_list) as inkml_file_list_obj:
        for line in inkml_file_list_obj:
            print("processing", i, "=", line)
            inkml = parse_inkml(line.strip())
            if inkml is not None:
                inkml_dict[inkml.ui] = inkml
                i += 1
    return inkml_dict

def parse_inkml(filepath):
    """
    parses one inkml file into inkmldata object
    :param filepath: file path of the inkml file
    :return: inkmldata object
    """
    inkml_data = InkMLData()
    with open(filepath, 'rb') as inkml_file:
        xml_data = bs4.BeautifulSoup(inkml_file, "lxml")
        ink = xml_data.ink
        if (ink == None):
            return None
        category = ''
        expression = ''
        ui = ''
        gt = ''
        writer = ''
        if (ink.find('annotation', {'type': 'category'})):
            category = ink.find('annotation', {'type': 'category'}).get_text()
            inkml_data.category = category
        if (ink.find('annotation', {'type': 'expression'})):
            expression = ink.find('annotation', {'type': 'expression'}).get_text()
            inkml_data.expression = expression
        if (ink.find('annotation', {'type': 'ui', 'type': 'UI'})):
            ui = ink.find('annotation', {'type': 'ui', 'type': 'UI'}).get_text()
            inkml_data.ui = ui.strip()
        if (ink.find('annotation', {'type': 'writer'})):
            writer = ink.find('annotation', {'type': 'writer'}).get_text()
            inkml_data.writer = writer
        if (ink.find('annotation', {'type': 'truth'})):
            gt = ink.find('annotation', {'type': 'truth'}).get_text()
            inkml_data.gt = gt
        inkml_data.path = filepath
        expression_trace = get_expression_trace(ink)
        inkml_data.expression_trace = expression_trace
        file_name = os.path.basename(inkml_file.name)
        inkml_data.filename = file_name.split('.')[0]
    return inkml_data


def get_expression_trace(ink_xml_object):
    expression_trace = None
    # outer xml
    expression_trace_xml = ink_xml_object.find('tracegroup')
    # inner xml
    trace_group_list = expression_trace_xml.findAll('tracegroup')
    trace_group_obj_dict = {}

    for symbol_trace_group in trace_group_list:
        trace_group_obj = TraceGroup()
        trace_group_id = symbol_trace_group.get('xml:id')
        truth_label = symbol_trace_group.find('annotation', {'type': 'truth'}).get_text()
        traceviews = symbol_trace_group.findAll('traceview')
        truth_instance = None
        if (symbol_trace_group.find('annotationxml')):
            truth_instance = symbol_trace_group.find('annotationxml')['href']
        else:
            if (len(traceviews) <= 1):
                break
            trace_id = traceviews[1]['tracedataref']
            truth_instance = truth_label + "_xkey_id" + trace_id
        traces = []
        trace_dict = {}
        for traceview in traceviews:
            trace_reference = traceview['tracedataref']
            symbol_traces_xml = ink_xml_object.find(id=trace_reference)
            symbol_trace = symbol_traces_xml.get_text()
            strokes = process_traces(symbol_trace)
            # traces.append(symbol_trace)
            traces.append(strokes)
            trace_dict[trace_reference] = strokes
        trace_group_obj.trace_group_id = trace_group_id
        trace_group_obj.truth_label = truth_label
        trace_group_obj.truth_instance = truth_instance
        trace_group_obj.traces = traces
        trace_group_obj.trace_dict = trace_dict
        trace_group_obj_dict[truth_instance] = trace_group_obj
    return trace_group_obj_dict

def process_traces(symbol_trace):
    """
    processes traces from one string to a list of lists,
    where the inner lists represent points and the outer list represents a list of points in a stroke
    :param symbol_trace:
    :return: a list of lists, see above for description
    """
    strokes = symbol_trace.split(',')
    stroke_list = []
    for point_string in strokes:
        point_string = point_string.strip()
        point_x_y = point_string.split(' ')
        point_x_y_int = []
        for axis in point_x_y:
            point_x_y_int.append(float(axis.strip()))
            # point_x_y_int.append(axis.strip())
        stroke_list.append(point_x_y_int)
    return stroke_list




#def write_to_lg_files(inkml, inkml_key, graph, data_dir):
def write_to_lg_files(inkml, nodes, edges, lg_path):
    print('Write to lg file')
    nodes_num = len(nodes)
    text = '# IUD, '+inkml.filename+'\n'
    text += '# Objects('+str(nodes_num)+'):\n'
    for node in nodes:
        # text += '# Object: '+str(node.label_id)+' .\n'
        # text += 'N, '+str(node.id)+', '+str(node.predicted)+', 1.0\n'
        stroke_id_string = ', '.join([str(ids) for ids in node.stroke_ids])
        node_gt = node.gt
        node_label_id = node.label_id
        if node.gt == ',':
            node_gt = '\\comma'
        elif len(node.gt)>1:
            node_gt = '\\'+node.gt
        if  ',' in node.label_id: 
            node_label_id = node.label_id.replace(',','comma')
        text += 'O, ' +str(node_label_id)+ ", " +str(node_gt)+', 1.0, ' + stroke_id_string + '\n'


    text += '\n'
    text += '# Relationships from SRT:\n'
    for edge in edges:
        node1_label_id = edge.node1.label_id
        node2_label_id = edge.node2.label_id
        if  ',' in edge.node1.label_id: 
            node1_label_id = edge.node1.label_id.replace(',','comma')
        if  ',' in edge.node2.label_id: 
            node2_label_id = edge.node2.label_id.replace(',','comma')
        text += 'R, '+node1_label_id+', '+node2_label_id+', '+edge.rel+', 1.0\n'
    print('inkml.filename : ',inkml.filename)
    with open(lg_path+inkml.filename+'.lg','w') as f:
        f.write(text)


def write_to_lpga_file(location, file_list):
    with open(location, 'w') as write_file:
        for file in file_list:
            write_file.write(file+'\n')



def prepare_inkml_folder(file_list_location, target_location):
    file_list = []
    with open(file_list_location, 'r') as file_obj:
        file_list = file_obj.readlines()
    for filename in file_list:
        filename = filename.strip().replace('"','')
        shutil.copyfile('./lpga_release-master/Data/Expressions/inkml/all_inkmls/'+filename+'.inkml',target_location+'/'+filename+'.inkml')


