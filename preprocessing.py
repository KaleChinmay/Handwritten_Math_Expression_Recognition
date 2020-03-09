import csv
import bs4
import ast
import scipy.spatial.distance as distance
import sklearn
import numpy as np
from character_data import Character_Data
import write_csv



def interpolate_trace(old_trace):
    """
    interpolates a long a trace, doubling the total amount of points
    :param old_trace: a list of points representing the trace to be interpolated
    :return: the new trace with added points
    """
    # get d
    n = len(old_trace)
    sumdist = 0
    for i in range(n - 1):
        sumdist += distance.euclidean(old_trace[i], old_trace[i + 1])
    dist = sumdist / n

    skip = False
    previous = 0

    # interpolate points
    new_trace = []
    for i in range(1, n):
        if i != 0 and distance.euclidean(old_trace[previous], old_trace[i] < dist):
            skip = True
            i += 1
            continue

        if skip:
            # calculate ldiff
            l = 0
            for j in range(previous, i):
                l += distance.euclidean(old_trace[j], old_trace[j + 1])
            ldiff = l - dist

            skip = False
            previous = i

        else:
            new_trace.append(old_trace[i - 1])
            if old_trace[i - 1][0] == old_trace[i][0]:
                continue
            # calculate and append new point
            slope = (old_trace[i][1] - old_trace[i - 1][1]) / (old_trace[i][0] - old_trace[i - 1][0])
            new_point = []
            # get new x
            if old_trace[i][0] > old_trace[i - 1][0]:
                new_point.append(old_trace[i - 1][0] + np.sqrt(pow(dist, 2) / (pow(slope, 2) + 1)))
            else:
                new_point.append(old_trace[i - 1][0] - np.sqrt(pow(dist, 2) / (pow(slope, 2) + 1)))
            # get new y
            if (old_trace[i - 1][1] < old_trace[i][1]):
                new_point.append(old_trace[i - 1][1] + distance)
            elif old_trace[i][1] == old_trace[i + 1][1]:
                new_point.append(slope * new_point[0] + old_trace[i][1] - slope * old_trace[i][0])
            else:
                new_point.append(old_trace[i - 1][1] - dist)

            new_trace.append(new_point)

            previous += 1


def get_gt():
    gt_dict = {}
    with open('./Data/trainingSymbols/iso_GT.txt', 'r') as iso_gt:
        for line in iso_gt:
            temp_list = line.split(',')
            gt_dict[temp_list[0]] = temp_list[1]
    return gt_dict



def create_objs(file, gt_dict):
    """
    returns a dictionary of Character_Data objects. key = id, and value is the object
    :param file:
    :param gt_dict:
    :return:
    """
    objects = {}
    location = './Data/trainingSymbols/'
    with open('./Data/meta_data.csv', 'w+') as meta_file:
        for i in range(171, 85801):
            # with open('./Data/meta_data.csv','w+'):
            file_name = location + 'iso' + str(i) + '.inkml'
            with open(file_name) as file:
                xml_data = bs4.BeautifulSoup(file, 'lxml')
                data_obj = Character_Data()
                ink = xml_data.ink
                name = ink.find_all('annotation')[1].get_text()
                data_obj.id = name
                data_obj.gt = gt_dict[name].strip()
                trace = ink.trace
                temp_content = [[content.strip() for content in trace.contents] for trace in ink.find_all('trace')]
                x = [[a.split(',') for a in trace][0] for trace in temp_content]
                data_obj.trace = x
                objects[name] = data_obj
        return objects


def preprocess_objects(data_obj):
    """
    makes preprocessing calls on the object
    :param data:
    :return:
    """


def preprocess_data(csv_file):
    gt_dict = get_gt()
    filename = write_csv.generate_meta_file()
    data = create_objs(filename, gt_dict)
    for key in data:
        preprocess_objects(data[key])