"""
__author__ = Lauren Cole, Chinmay Kale

this programs takes in a text file pointing
command line arugment options:
    -path to textfile that points to inkml files to process, 1 inkml file per line
    -select baseline versus sophisticated processor
"""

import argparse
import os
from parser_project import ParserProject
import data_io
import baseline_parser
import pickle


def arg_setup():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("location", help="add location of inkml list as argument")
    argument_parser.add_argument("--parser_type", help="type of parser: baseline or sophisticated")
    argument_parser.add_argument("--train", help="train or not: y or n")
    #argument_parser.add_argument("--zanibbi", help="Location of dprl project(Graph Based)")
    arglist = argument_parser.parse_args()
    project = ParserProject(arglist.location, arglist.parser_type, arglist.train)
    return project


def main():
    project = arg_setup()

    print(project.location)
    if(not os.path.exists('inkml_pickle.txt')):
        
        project.inkml_dict = data_io.parse_inkml_list(project.location+'/inkml_list.txt')
        for key in project.inkml_dict:
            print(project.inkml_dict[key])
        with open('inkml_pickle.txt', 'wb') as pickle_file:
            pickle.dump(project.inkml_dict,pickle_file)
        print('Dumping data')

    inkml_data = None
    with open('inkml_pickle.txt','rb') as pickle_read_file:
        inkml_data = pickle.load(pickle_read_file)
    i=0




    if(project.parser_type == 'baseline'):
        for key in inkml_data.keys():
            inkml = inkml_data[key]
            i+=1
            print('Progress : '+str(i))
            project.baseline_parser(inkml)
    elif(project.parser_type == 'los'):
        if project.train == 'yes':
            #project.split_LPGA_dataset(inkml_data)
            #sub_folder_list = ['expressmatch','extension','HAMEX','KAIST', 'MATHBrush', 'MfrDB']
            #sub_folder_list = ['expressmatch','extension','HAMEX1','HAMEX2','KAIST', 'MathBrush1','MathBrush2', 'MfrDB1', 'MfrDB2']
        
            print('Starting train test split: ')
            print('Inkml data : ',len(inkml_data))
            result = project.split_LPGA_dataset(inkml_data)
            train, test = result
            print(len(train))
            print(len(test))
            data_io.write_to_lpga_file(project.train_file_list_location,train)
            data_io.write_to_lpga_file(project.test_file_list_location,test)
            train_files_location = project.dprl_project_location+'../Data/Expressions/Train'
            test_files_location = project.dprl_project_location+'../Data/Expressions/Test'
            data_io.prepare_inkml_folder(project.train_file_list_location, train_files_location)
            data_io.prepare_inkml_folder(project.test_file_list_location, test_files_location)

        
            #sub_folder_list = ['dummy']
            #for subfolder in sub_folder_list:
                #project.edit_config(subfolder)
            #subfolder = None
            project.sophisticated_parser()
        
        

if __name__ == "__main__":
    main()
