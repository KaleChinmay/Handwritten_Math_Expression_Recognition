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


def classify():
	print(features_dict)
	data = pd.read_csv('.\\Data\\feature_list.csv', header=None,  index_col='ID',
		usecols=features_dict.keys() , names = [features_dict[key] for key in features_dict.keys()])




	#rite_output_csv(data)
	data = data.fillna(0)
	data = data.replace([np.inf, -np.inf], 0)
	write_csv.write_output_csv_files(data)
	print(data.head(15))
	#print(data.describe())

	features = data.drop(columns=['Class label'], axis=1) 
	labels = np.array(data['Class label'])

	le = pp.LabelEncoder()
	encoded_labels = le.fit_transform(data['Class label'])
	print('Labels : ',np.unique(encoded_labels))
	print(type(encoded_labels))

	train_features, test_features, train_labels, test_labels = train_test_split(features, encoded_labels, 
		test_size = 0.3, random_state = 42, stratify=encoded_labels)
	print(type(test_labels))






	
	'''
	train_labels_count = train_labels.size
	test_labels_count = test_labels.size
	#train_labels/train_labels_count
	unique_train_labels, unique_train_labels_count  = np.unique(train_labels, return_counts=True)
	print('train_labels: ',unique_train_labels)
	print('Count : ',unique_train_labels_count)
	#print('Priors : ', unique_train_labels_count/train_labels_count)

	unique_test_labels, unique_test_labels_count = np.unique(test_labels, return_counts=True)

	print('test_labels : ',unique_test_labels)
	print('Count : ',unique_test_labels_count)
	#print('Priors : ', unique_test_labels_count/test_labels_count)
	'''

	#split_data(data)

	#row_count = data[0].count()
	#column_count = 37
	#classifier = RandomForestClassifier(n_estimators = 100, random_state = 42)
	classifier = KNeighborsClassifier(n_neighbors=1,algorithm='kd_tree')
	model = classifier.fit(train_features, train_labels)
	with open('rfc_model_no_junk.txt','wb') as f:
		joblib.dump(model, f, compress=3)
	predictions = model.predict(test_features)
	accuracy = accuracy_score(predictions, test_labels)
	#print(predictions)

	predictions = le.inverse_transform(predictions)

	#print(accuracy)
	#print(train_labels)
	test_features['predictions'] = predictions

	ouput_data = test_features['predictions']
	#print(ouput_data)
	ouput_data.to_csv('.\\Data\\prediction_output.csv', index=True, header=None,quoting=csv.QUOTE_NONE)



#def split_data(data, labels):


