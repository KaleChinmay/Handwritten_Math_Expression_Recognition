from pattern_recognition import PatternRec
import data_io
import location
import sys
import pickle
import joblib
import losgraph
import math
import portion as P
import concurrent.futures
import numpy as np
from datetime import datetime
import extract_segmentation_features
import matplotlib.pyplot as plt
from skmultilearn.model_selection import iterative_train_test_split
from sklearn.model_selection import train_test_split as tts
from scipy.stats import entropy as kullback_liebler
from skmultilearn.model_selection import IterativeStratification
import copy
import random
from sklearn import preprocessing as pp
import segmentation_classifier
import argparse


def read_inkml(project):
    data_io.get_inkml_data(project.location.inkml_path)


def get_inkml_data():
    with open('inkml_binary.obj', 'rb') as ink_obj:
        inkml_data_list = pickle.load(ink_obj)
        return inkml_data_list


def make_graphs(inkml_data_list):
    test = []
    for key in inkml_data_list:
        test.append(inkml_data_list[key])
    print(datetime.now())
    print("MAKING GRAPHS")
    with concurrent.futures.ProcessPoolExecutor(max_workers=15) as executor:
        for obj, graph in zip(test, executor.map(processor_task1, test)):
            inkml_data_list[graph.name].los_graph = graph
            print("making graph:", graph.name, ".", inkml_data_list[graph.name].los_graph.name)
    with open('inkml_with_graphs.obj', 'wb') as file:
        pickle.dump(inkml_data_list, file)


def get_inkml_graphs():
    with open('inkml_with_graphs.obj', 'rb') as file:
        inkml_data_list = pickle.load(file)
    return inkml_data_list


def extract_seg_features(inkml_data_list):
    test = []
    for key in inkml_data_list:
        test.append(inkml_data_list[key])
    features_dt = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=15) as executor:
        for obj, vectors in zip(test, executor.map(processor_task2, test)):
            features_dt[obj.ui] = vectors
            print("extracting features:", obj.ui)
    with open('features.txt', 'wb') as file:
        joblib.dump(features_dt, file)
    print("serialized")


def get_features_dict():
    with open('features.txt', 'rb') as file:
        features_data = joblib.load(file)
    return features_data


def get_strokes_as_list(expression_trace):
    traces = []
    for symbol in expression_trace:
        for trace in expression_trace[symbol].traces:
            points = []
            for point in trace:
                points.append([point[0], point[1]])
            points = np.array(points)
            traces.append(points)
    return traces


def processor_task1(inkml):
    return losgraph.make_LOS_graph(inkml.ui, inkml.expression_trace)


def processor_task2(inkml):
    return extract_segmentation_features.extract_features(inkml.los_graph)


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


def create_symbol_index_map(ui_symbol_map):
    symbol_index_map = {}
    index = 0
    for ui in ui_symbol_map:
        for symbol in ui_symbol_map[ui]:
            if symbol not in symbol_index_map:
                symbol_index_map[symbol] = index
                index += 1
    return symbol_index_map, index


def set_swap(set1, set2, item1, item2):
    """
    puts item1 from set 1 into set 2. puts item2 from set 2 into set 1
    :param set1:
    :param set2:
    :param item1:
    :param item2:
    :return:
    """
    set1.remove(item1)
    set2.add(item1)
    set2.remove(item2)
    set1.add(item1)


#
# def update_pds(uis_to_symbols, symbol_index_map, ui1, ui2, train_pd, test_pd):
#
#     for symbol in uis_to_symbols[ui1]:
#         number = uis_to_symbols[ui1][symbol]
#         train_pd[symbol_index_map[symbol]] += number
#         test_pd[symbol_index_map[symbol]] -= number
#
#     for symbol in uis_to_symbols[ui2]:
#         number = uis_to_symbols[ui2][symbol]
#         test_pd[symbol_index_map[symbol]] += number
#         train_pd[symbol_index_map[symbol]] -= number
#
#     return train_pd, test_pd
#
# def get_swap_kl(uis_to_symbols, symbol_index_map, ui1, ui2, train_pd, test_pd):
#     """
#     gets the kl of making a certain swap
#     :param uis_to_symbols:
#     :param symbol_indeX_map:
#     :param item1:
#     :param item2:
#     :param train_pd:
#     :param test_pd:
#     :return:
#     """
#     train_pd = train_pd.copy()
#     test_pd = test_pd.copy()
#     train_pd, test_pd = update_pds(uis_to_symbols, symbol_index_map, ui1, ui2, train_pd, test_pd)
#     kl = kullback_liebler(train_pd, test_pd)
#
#     return kl
#
# def get_best_successor(ui_train, ui_test, train_pd, test_pd, uis_to_symbols, symbol_index_map):
#
#     i = 0
#     best_kl = 1000000
#     to_swap = ["", ""]
#     for train_sample in ui_train:
#         for test_sample in ui_test:
#             new_kl = get_swap_kl(uis_to_symbols, symbol_index_map, train_sample, test_sample, train_pd, test_pd)
#             print(i)
#             if new_kl < best_kl:
#                 best_kl = new_kl
#                 to_swap[0] = train_sample
#                 to_swap[1] = test_sample
#             i += 1
#     return best_kl, to_swap
#
# def train_test_split(inkml_data):
#     uis_to_symbols = create_ui_symbol_map(inkml_data)
#     symbol_index_map, size = create_symbol_index_map(uis_to_symbols) #map a symbol to its index in pdf
#
#     #CREATE INITIAL RANDOM SPLIT
#     print(uis_to_symbols)
#     gts = []
#     uis = []
#     for key in inkml_data:
#         uis.append(inkml_data[key].ui)
#         gts.append(inkml_data[key].gt)
#     data = np.column_stack((np.array(uis), np.array(gts)))
#
#     #initial random split
#     ui_train, ui_test, labels_train, labels_test = tts(data[:, 0], data[:, 1], test_size=(1 / 3))
#
#
#     #create probabilities for test sets
#     train_pd = np.zeros(size)
#     test_pd = np.zeros(size)
#
#     ui_train = set(ui_train.flatten())
#     ui_test = set(ui_test.flatten())
#
#     for ui in ui_train:
#         symbols = uis_to_symbols[ui]
#         for symbol in symbols:
#             train_pd[symbols[symbol]] += symbols[symbol]
#     for ui in ui_test:
#         symbols = uis_to_symbols[ui]
#         for symbol in symbols:
#             test_pd[symbols[symbol]] += symbols[symbol]
#     kl = kullback_liebler(train_pd, test_pd)
#
#     climbing = True
#
#     while (climbing):
#         print("climbing loop")
#         best_kl, to_swap = get_best_successor(ui_train, ui_test, train_pd, test_pd, uis_to_symbols, symbol_index_map)
#         if best_kl < kl:
#             kl = best_kl
#             set_swap(ui_train, ui_test, to_swap[0], to_swap[1])
#             update_pds(uis_to_symbols, symbol_index_map,to_swap[0], to_swap[1], train_pd, test_pd)
#         else:
#             climbing = False
#     return ui_train, ui_test

def create_ui_symbol_labels(inkml_data):
    ui_symbol_map = []
    for key in inkml_data:
        expression = inkml_data[key]
        row = [expression.ui]
        for symbol in expression.expression_trace:
            row.append(symbol)
        ui_symbol_map.append(row)
    return ui_symbol_map


def split_data(inkml_data):
    print("split data")
    uis_to_symbols = create_ui_symbol_map(inkml_data)
    symbol_index_map, size = create_symbol_index_map(uis_to_symbols)
    print("size:", size)
    array = np.zeros(size)
    uis = []
    for ui in uis_to_symbols:
        print(ui)
        indices = np.zeros(size)
        uis.append(ui)
        for symbol in uis_to_symbols[ui]:
            indices[symbol_index_map[symbol]] = uis_to_symbols[ui][symbol]
        array = np.vstack((array, indices))
    array = np.delete(array, (0), axis=0)
    le = pp.LabelEncoder()
    encoded_uis = le.fit_transform(uis)
    x1 = np.zeros(len(encoded_uis))
    print(len(encoded_uis))
    x = np.column_stack((np.array(encoded_uis), x1))
    print(array.shape)
    x_train, y_train, x_test, y_test = iterative_train_test_split(x, array, test_size=(1 / 3))

    x_train = x_train[:, 0].astype(int)
    x_test = x_test[:, 0].astype(int)

    training_ids = le.inverse_transform(x_train)
    testing_ids = le.inverse_transform(x_test)
    print(type(training_ids), type(testing_ids))
    return set(training_ids.tolist()), set(testing_ids.tolist())


def main():
    argument_parser = argparse.ArgumentParser()
    #argument_parser.add_argument("segmentor", help="Name of the Segmentor Options :- 'Baseline' or 'LosSegmentor'")
    argument_parser.add_argument("data_location", help="Location of data Directory")
    argument_parser.add_argument("--segmentor", help="Options : baseline or los")
    argument_parser.add_argument("--dataset", help="Options : 'train'  - For Split into train and test) or \
        'bonus' Train on all dataset")
    args = argument_parser.parse_args()

    project = PatternRec(args.data_location, args.segmentor, args.dataset)
    # MAKE INITIAL INKML DATA OBJS*************************************
    # location.set_up_variables()
    # data_io.get_inkml_data(project.location.inkml_path)
    # *********************************************************

    # MAKE GRAPHS AND ADD TO INKML DATA OBJECTS. USES MULTIPROCESSING
    # 	with open('inkml_binary.obj','rb') as ink_obj:
    #  		inkml_data_list = pickle.load(ink_obj)

    # i =0
    # for key in inkml_data_list:
    # 	plt.figure()
    # 	expression_trace = inkml_data_list[key].expression_trace
    # 	for tracegroup_key in expression_trace:
    # 		normal_traces = expression_trace[tracegroup_key].norm_trace_dict
    # 		for trace in normal_traces:
    # 			stroke = normal_traces[trace]
    # 			plt.scatter(np.array(stroke)[:,0], np.array(stroke)[:,1], s=10)
    #
    # 	plt.show()
    # 	i += 1
    # 	if i == 10:
    # 		break

    # test = []
    # for key in inkml_data_list:
    #  	test.append(inkml_data_list[key])
    # print(datetime.now())
    # print("MAKING GRAPHS")
    # with concurrent.futures.ProcessPoolExecutor(max_workers=15) as executor:
    #  	for obj, graph in zip(test, executor.map(processor_task1, test)):
    #  		inkml_data_list[graph.name].los_graph = graph
    #  		print("making graph:", graph.name, ".", inkml_data_list[graph.name].los_graph.name)
    # print(datetime.now())
    #
    #
    # with open('inkml_with_graphs.obj', 'wb') as file:
    # 	pickle.dump(inkml_data_list, file)

    # with open('inkml_with_graphs.obj', 'rb') as file:
    # 	inkml_data_list = pickle.load(file)
    #
    # i =0
    # for key in inkml_data_list:
    #
    # 	graph = inkml_data_list[key].los_graph
    # 	graph.plot_expression()
    #
    #
    # 	i += 1
    # 	if i == 10:
    # 		break

    #	**************************************************************

    # LOAD 	SERIALIZED FILE WITH GRAPHS AND EXTRACT FEATURES
    # with open('inkml_with_graphs.obj', 'rb') as file:
    # 	inkml_data_list = pickle.load(file)
    #
    # test = []
    # for key in inkml_data_list:
    # 	test.append(inkml_data_list[key])
    #
    # features_dt = {}
    #
    # with concurrent.futures.ProcessPoolExecutor(max_workers=15) as executor:
    # 	for obj, vectors in zip(test, executor.map(processor_task2, test)):
    # 		features_dt[obj.ui] = vectors
    # 		print("extracting features:", obj.ui)
    #
    # with open('features.txt', 'wb') as file:
    # 	joblib.dump(features_dt, file)
    # print("serialized")
    #
    # with open('features.txt', 'rb') as file:
    # 	features_data = joblib.load(file)

    # PatternRec.expression_recognizer(inkml_data)
    #
    # xp = [1, 3, 7, 5, 4, 3]
    # fp = [1, 3, 7, 8, 9, 12]
    # new_x = []
    # new_y = []
    # for i in range(1, len(xp))
    #
    # y = np.interp(x, xp, fp, period=2.5)
    # plt.scatter(xp, fp, color = "green")
    # plt.scatter(x, y, color="blue")
    # plt.show()

    # read_inkml(project)
    # inkml_data = get_inkml_data()
    # make_graphs(inkml_data)
    # get_inkml_graphs()
    inkml_data = get_inkml_graphs()
    # extract_seg_features(inkml_data)
    features_data = get_features_dict()
    test_ids = None
    if (project.dataset == 'train'): 
        train_ids, test_ids = split_data(inkml_data)
        predicted_data = None
        if(project.segmentor=='los'):
            predicted_data = segmentation_classifier.segment_driver(train_ids, test_ids, features_data)
        project.expression_recognizer(inkml_data, test_ids,project.segmentor, predicted_data)
    else:
        train_ids = inkml_data
        if(project.segmentor == 'los'):
            segmentation_classifier.segment_driver(train_ids, None, features_data)
        project.expression_recognizer(inkml_data, test_ids,project.segmentor, inkml_data)




if __name__ == '__main__':
    main()

# this line is a test
