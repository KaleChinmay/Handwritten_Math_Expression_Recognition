"""
the driver file for the classification project
calls functions to preprocess, extract features, classify and evaluation
"""
import feature_extraction
import write_csv
from sklearn import preprocessing as pp
#from sklearn.neighbors import NearestNeighbors as knn
from sklearn.neighbors import KNeighborsClassifier
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPClassifier
import preprocessing
import pandas as pd
import matplotlib.pyplot as plt
from os import path
import numpy as np
from sklearn.metrics import accuracy_score
import joblib
import csv
import sys
from sklearn import svm




data_folder = './Data/'

data_type_map = {
	"0" : "no_junk",
	"1" : "with_junk",
	"2" : "bonus",
	"3" : "junk_only"
}
classifier_type_map = {
	"0" : "kd",
	"1" : "rfc"
}

features_dict = {
	0 : 'No of Traces',
	1 : 'Mean X',
	2 : 'Mean Y',
	3 : 'Covariance',
	4 : 'Aspect Ratio,',
	5 : 'HC1',
	6 : 'HC2',
	7 : 'HC3',
	8 : 'HC4',
	9 : 'HC5',
	10 : 'HC6',
	11 : 'HC7',
	12 : 'HC8',
	13 : 'HC9',
	14 : 'HC10',
	15 : 'HC11',
	16 : 'HC12',
	17 : 'HC13',
	18 : 'HC14',
	19 : 'HC15',
	20 : 'VC1',
	21 : 'VC2',
	23 : 'VC3',
	24 : 'VC4',
	25 : 'VC5',
	26 : 'VC6',
	27 : 'VC7',
	28 : 'VC8',
	29 : 'VC9',
	30 : 'VC10',
	31 : 'VC11',
	32 : 'VC12',
	33 : 'VC13',
	34 : 'VC14',
	#35 : 'Sum of line length',
	#36 : 'Avg line length per trace',
	#37 : 'Sum of angular change',
	#38 : 'Average angular change',
	#40 : 'Sharp points',
	#39 is id
	39 : 'ID',
	40 : 'Class label'

}

class_label_dict = {}
THRESHOLD = 10



def preprocess(data, train_labels):
	elements, count = np.unique(train_labels, return_counts =True)
	for key, value in zip(elements, count):
		class_label_dict[key] = value

	below_threshold_labels = []
	for key in class_label_dict.keys():
		if(class_label_dict[key]<THRESHOLD):
			below_threshold_labels.append(key)
	data = data[~data['Class label'].isin(below_threshold_labels)]

	return data




def classify(data, classifier_param, junk_param, train_param, testing_data=None):
	if(junk_param=='2'):
		classifier_file = 'model_'+classifier_type_map[classifier_param]+'_final_prediction.txt'
		model = None
		le = None

		testing_data = testing_data.fillna(0)
		testing_data = testing_data.replace([np.inf, -np.inf], 0)
		testing_data = testing_data.drop(columns=['Class label'], axis=1)
		data = data.fillna(0)
		data = data.replace([np.inf, -np.inf], 0)
		data = preprocess(data, data['Class label'])
		le = pp.LabelEncoder()
		train_labels = le.fit_transform(data['Class label'])
		features = data.drop(columns=['Class label'], axis=1)
		if(train_param=='1'):
			#labels = np.array(data['Class label'])
			if classifier_param == '0':
				print('Using KDTree')
				classifier = KNeighborsClassifier(n_neighbors=1,algorithm='kd_tree')
			elif(classifier_param == '1'):
				print('Using Ensemble')
				classifier = RandomForestClassifier(n_estimators=150, random_state=42, max_depth=35)
				#classifier = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(100, 5), random_state=42)
				#model1 = LogisticRegression(random_state=1)
				#model2 = tree.DecisionTreeClassifier(random_state=1)
				

				#classifier = VotingClassifier(estimators=[('lr', model1), ('rf', model3)], voting='hard')
				#classifier = RandomForestClassifier(n_estimators=100, random_state=42)
				#classifier = AdaBoostClassifier(n_estimators=100, random_state=42)

			else:
				print('Invalid input, returning')
				return None, None
			model = classifier.fit(features, train_labels)
			print('Model created')
			model_info = [model,le]
			with open(classifier_file,'wb') as f:
				joblib.dump(model_info, f, compress=3)
		elif(train_param=='0'):
			if(path.exists(classifier_file)):
				print('Found existing model :',classifier_file)
				model_info = joblib.load(classifier_file)
				model = model_info[0]
				le = model_info[1]
				print('Using model ',classifier_file)
			else:
				print('Model '+classifier_file+' not found. Returning')
				return None, None
		predictions = model.predict(testing_data)
		predictions = le.inverse_transform(predictions)
		testing_data['predictions'] = predictions
		ouput_data = testing_data['predictions']
		prediction_file = classifier_type_map[classifier_param]+'_final_prediction.csv'
		write_csv.write_output_files(ouput_data, prediction_file)
		print('Created file : '+prediction_file)
		print('Generated Ground Truth and Output files')
		return prediction_file, None
	else:
		classifier = None
		classifier_file = 'model_'+classifier_type_map[classifier_param]+"_"+data_type_map[junk_param]+'.txt'
		model = None
		data = data.fillna(0)
		data = data.replace([np.inf, -np.inf], 0)
		features = data.drop(columns=['Class label'], axis=1)
		labels = np.array(data['Class label'])
		le = pp.LabelEncoder()
		encoded_labels = le.fit_transform(data['Class label'])

		train_features, test_features, train_labels, test_labels = train_test_split(features, encoded_labels,
			test_size = 0.3, random_state = 42, stratify=encoded_labels)
		print(train_param)
		
		if(train_param == '0'):
			if(path.exists(classifier_file)):
				print('Found existing model :',classifier_file)
				model = joblib.load(classifier_file)
				print('Using model ',classifier_file)
			else:
				print('Model '+classifier_file+' not found. Returning')
				return None, None
		else:
			if classifier_param == '0':
				print('Using KDTree')
				classifier = KNeighborsClassifier(n_neighbors=1,algorithm='kd_tree')
			elif(classifier_param == '1'):
				print('Using RandomForest')
				classifier = RandomForestClassifier(n_estimators=100, random_state=42)
			else:
				print('Invalid input, returning')
				return None, None
			model = classifier.fit(train_features, train_labels)
			classifier_file = 'model_'+classifier_type_map[classifier_param]+"_"+data_type_map[junk_param]+'.txt'
			with open(classifier_file,'wb') as f:
				joblib.dump(model, f, compress=3)
			print('Using model ',classifier_file)

		predictions = model.predict(test_features)
		GT_file = None
		accuracy = accuracy_score(predictions, test_labels)
		test_labels = le.inverse_transform(test_labels)
		print(accuracy)
		#Write GT (input file)
		test_features['Class label'] = test_labels
		gt_data = test_features['Class label']
		GT_file = classifier_type_map[classifier_param]+'_'+data_type_map[junk_param]+'_GT.csv'
		write_csv.write_output_files(gt_data, GT_file)
		print('Created file : '+GT_file)
		predictions = le.inverse_transform(predictions)
		test_features['predictions'] = predictions
		ouput_data = test_features['predictions']
		prediction_file = classifier_type_map[classifier_param]+'_'+data_type_map[junk_param]+'_prediction.csv'
		write_csv.write_output_files(ouput_data, prediction_file)
		print('Created file : '+prediction_file)
		print('Generated Ground Truth and Output files')
		return prediction_file, GT_file



def classification(junk_param, classifier_param, train_param):


	if(junk_param=='0'):
		print('Classifying Valid Symbols only')
		data = pd.read_csv(data_folder+'symbol_feature_list.csv', header=None,  index_col='ID',
			usecols=features_dict.keys() , names = [features_dict[key] for key in features_dict.keys()])
		prediction_file, GT_file = classify(data, classifier_param, junk_param, train_param)
	elif(junk_param=='1'):
		print('Classifying Valid+Junk Symbols.')
		data = None
		valid_symbol_data = pd.read_csv(data_folder+'symbol_feature_list.csv', header=None,  index_col='ID',
			usecols=features_dict.keys() , names = [features_dict[key] for key in features_dict.keys()])
		junk_symbol_data = pd.read_csv(data_folder+'junk_feature_list.csv', header=None,  index_col='ID',
			usecols=features_dict.keys() , names = [features_dict[key] for key in features_dict.keys()])
		#Merge 2 dataframes
		frames = [valid_symbol_data, junk_symbol_data]
		data = pd.concat(frames)
		prediction_file, GT_file = classify(data, classifier_param, junk_param, train_param)
	elif(junk_param=='2'):
		test_symbol_data = pd.read_csv(data_folder+'test_feature_list.csv', header=None,  index_col='ID',
			usecols=features_dict.keys() , names = [features_dict[key] for key in features_dict.keys()])
		valid_symbol_data = pd.read_csv(data_folder+'symbol_feature_list.csv', header=None,  index_col='ID',
			usecols=features_dict.keys() , names = [features_dict[key] for key in features_dict.keys()])
		junk_symbol_data = pd.read_csv(data_folder+'junk_feature_list.csv', header=None,  index_col='ID',
			usecols=features_dict.keys() , names = [features_dict[key] for key in features_dict.keys()])
		#Merge 2 dataframes
		frames = [valid_symbol_data, junk_symbol_data]
		data = pd.concat(frames)
		prediction_file, GT_file = classify(data, classifier_param, junk_param, train_param, test_symbol_data)
	else:
		print('Invalid input, returning')
	return prediction_file, GT_file




