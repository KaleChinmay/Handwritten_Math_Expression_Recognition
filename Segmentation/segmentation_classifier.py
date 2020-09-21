from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import BaggingClassifier

from sklearn import preprocessing as pp
from sklearn.metrics import accuracy_score

import joblib
import pandas as pd
import numpy as np


# the parameter contains data with gt
def train(train_data):
    le = pp.LabelEncoder()
    encoded_labels = le.fit_transform(train_data['gt'])
    train_features = train_data.drop(columns=['gt'], axis=1)

    rfc = AdaBoostClassifier(n_estimators=10)
    rfc_model = rfc.fit(train_features, encoded_labels)
    model_info = [rfc_model, le]
    with open('segmentation_classifier.txt', 'wb') as f:
        joblib.dump(model_info, f, compress=3)
    #rfc_prediction = rfc_model.predict(test_features)
    #accuracy = accuracy_score(tree_prediction, test_labels)
    #print('Training Accuracy: ', accuracy)


# This parameter doesnt contain gt
def classify(test_data):
    model_info = joblib.load('segmentation_classifier.txt')
    model = model_info[0]
    le = model_info[1]
    gt = test_data['gt']
    test_data = test_data.drop(columns=['gt'], axis = 1)
    prediction = model.predict(test_data)
    prediction = le.inverse_transform(prediction)
    accuracy = accuracy_score(prediction, gt)
    test_data['predicted'] = prediction
    print(accuracy)
    #test_data['gt'] = prediction
    return test_data


def segment_driver(train_ids, test_ids, features_dict):
    # get data formatted
    training_features_list = []
    training_ids = []
    for ui in train_ids:
        for edge in features_dict[ui]:
            training_features_list.append(features_dict[ui][edge])
            training_ids.append(ui + "***" + edge)
    testing_features_list = []
    testing_ids = []
    for ui in test_ids:
        for edge in features_dict[ui]:
            testing_features_list.append(features_dict[ui][edge])
            testing_ids.append(ui + "***" + edge)

    train_df = pd.DataFrame(training_features_list)
    test_df = pd.DataFrame(testing_features_list)
    train_df = train_df.fillna(0)
    test_df = test_df.fillna(0)
    train_df['Index'] = np.array(training_ids)
    df_train = train_df.set_index('Index')
    test_df['Index'] = np.array(testing_ids)
    df_test = test_df.set_index('Index')

    # df = pd.DataFrame(features_list)
    # df['Index'] = np.array(ids)
    # df = df.set_index('Index')
    # print(df)
    # df_test = df[df.index.str.contains(test_ids)]
    # df_train = df[df.index.str.contains(train_ids)]
    print(df_train)
    print(df_test)
    df_train = df_train.rename(columns = {105:'gt'})

    if(df_test):
        df_test = df_test.rename(columns = {105: 'gt'})
        #train(df_train)
        df_test = classify(df_test)


# print(df_train)
    return df_test
