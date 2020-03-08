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
from sklearn.model_selection import train_test_split
import preprocessing
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import accuracy_score
import joblib
import csv
import sys




data_folder = '.\\Data\\'

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



def classify(data, classifier_param, junk_param):
	classifier = None
	classifier_file = ''

	if classifier_param == '0':
		print('Using KDTree')
		classifier = KNeighborsClassifier(n_neighbors=1,algorithm='kd_tree')
	elif(classifier_param == '1'):
		print('Using RandomForest')
		classifier = RandomForestClassifier(n_estimators=100, random_state=42)
	else:
		print('Invalid input, returning')
		return

	data = data.fillna(0)
	data = data.replace([np.inf, -np.inf], 0)

	features = data.drop(columns=['Class label'], axis=1)
	labels = np.array(data['Class label'])
	le = pp.LabelEncoder()
	encoded_labels = le.fit_transform(data['Class label'])

	train_features, test_features, train_labels, test_labels = train_test_split(features, encoded_labels,
		test_size = 0.3, random_state = 42, stratify=encoded_labels)



	model = classifier.fit(train_features, train_labels)

	
	classifier_file = 'model_'+classifier_type_map[classifier_param]+"_"+data_type_map[junk_param]+'.txt'
	with open(classifier_file,'wb') as f:
		joblib.dump(model, f, compress=3)
	predictions = model.predict(test_features)
	accuracy = accuracy_score(predictions, test_labels)
	predictions = le.inverse_transform(predictions)
	test_features['predictions'] = predictions
	ouput_data = test_features['predictions']
	ouput_data.to_csv(data_folder+'prediction_output.csv', index=True, header=None,quoting=csv.QUOTE_NONE)


def classification(junk_param, classifier_param):


	if(junk_param=='0'):
		print('Classifying Valid Symbols only')
		data = pd.read_csv(data_folder+'symbol_feature_list.csv', header=None,  index_col='ID',
			usecols=features_dict.keys() , names = [features_dict[key] for key in features_dict.keys()])
		classify(data, classifier_param, junk_param)
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
		classify(data, classifier_param, junk_param)
	else:
		print('Invalid input, returning')


#def split_data(data, labels):
