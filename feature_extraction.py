import numpy as np
import scipy.spatial.distance as distance
from os import path
import write_csv

BOUNDARY_DIM = (2.0/5.0)
NUM_LINES = 9
DATA_FOLDER = './Data/'
#TODO: change get_line_length from average length per trace to average length across all traces
#TODO: calculate sum and average of all angles in a new function
#TODO: calculate the number of sharp points - maybe this can happen inside the function above . its in reference 22 of zannibis
def get_trace_num(data_obj):
    """
    returns the number of traces in a character inkml
    :param tracelist: a list of traces
    :return: the length of tracelist
    """
    return len(data_obj.norm_traces)

# def get_x_range(data_obj):
#     """
#     returns range of x values in data_objs traces
#     :param data_obj: an instance of Character_Data
#     :return:
#     """
#     return data_obj.xmax - data_obj.xmin
#
# def get_y_range(data_obj):
#     """
#     returns range of y values in data_objs traces
#     :param data_obj:  an instance of Character_Data
#     :return:
#     """
#     return data_obj.ymax - data_obj.ymin

def get_x_mean(data_obj):
    """
    returns the mean of all x coordinates in the points in a character object
    :param data_obj:
    :return:
    """
    #print('---------------------')
    #print(data_obj.norm_traces)
    #print(type(data_obj.norm_traces))

    xdata = data_obj.norm_traces[0][:,0]
    norm_traces_len = len(data_obj.norm_traces)
    for i in range(1, norm_traces_len):
        xdata = np.concatenate([xdata, data_obj.norm_traces[i][:,0]])
    return np.mean(xdata)

def get_y_mean(data_obj):
    """
    returns the mean of all x coordinates in the points in a character object
    :param data_obj:
    :return:
    """
    ydata = data_obj.norm_traces[0][:, 1]
    norm_traces_len = len(data_obj.norm_traces)
    for i in range(1, norm_traces_len):
        ydata = np.concatenate([ydata, data_obj.norm_traces[i][:, 1]])
    return np.mean(ydata)

def get_covariance(data_obj):
    xdata = data_obj.norm_traces[0][:,0]
    ydata = data_obj.norm_traces[0][:, 1]
    norm_traces_len = len(data_obj.norm_traces)
    for i in range(1, norm_traces_len):
        xdata = np.concatenate([xdata, data_obj.norm_traces[i][:,0]])
        ydata = np.concatenate([ydata, data_obj.norm_traces[i][:, 1]])
    cov_mat = np.cov(np.stack((xdata, ydata),axis=0))
    return cov_mat[0, 1]

def get_aspect_ratio(data_obj):
    """
    returns aspect ratio of the character
    :param data_obj:
    :return:
    """
    return data_obj.aspect_ratio

def get_line_length(data_obj):
    """
    sums the euclidean distance of all the points in each trace
    :param data_obj:
    :return:
    """
    total_sum = 0
    for trace in data_obj.norm_traces:
        trace_sum = 0
        trace_len = len(trace)
        for i in range(1, trace_len):
            trace_sum += distance.euclidean(trace[i-1], trace[i])
        total_sum += trace_sum
    return total_sum, total_sum/len(data_obj.norm_traces)

def getAngle(p1, p2, p3):
    """
    returns the angle between 3 points
    :param p1:
    :param p2:
    :param p3:
    :return:
    """
    l12 = distance.euclidean(p1, p2)
    l23 = distance.euclidean(p2, p3)
    l13 = distance.euclidean(p1, p3)
    term = (pow(l12, 2) + pow(l23, 2) - pow(l13, 2)) / 2 * l12 * l23
    angle = np.arccos(term)
    #print('Angle : ',angle)
    return angle

def get_theta(i, angles):
    theta = angles[i] - angles[i-1]

def get_num_sharp_points(data_obj):
    #list of sharp points
    angles = []
    for trace in data_obj.norm_traces:
        trace_angles = []
        for i in range(1, np.size(trace, axis = 1) - 1):
            trace_angles.append(getAngle(trace[i-1], trace[i], trace[i+1]))
        angles.append(trace_angles)


    #each trace has 2 sharp points by default, so initialize to this
    V = len(data_obj.norm_traces) * 2
    angle_len = len(angles)
    #print(angle_len)
    for i in range(angle_len):
        angle_i_len = len(angles[i])
        for j in range(1, angle_i_len):
            thetas = []
            #print('j: ',j)
            theta = get_theta(j, angles)
            thetas.append(theta)
            if theta == 0:
                continue
        delta =theta * thetas[j-1]
        if theta < 0:
            V += 1
    return V

def get_angle_data(data_obj):
    angles = []
    for trace in data_obj.norm_traces:
        for i in range(1, np.size(trace, axis=0) - 1):
            angles.append(getAngle(trace[i - 1], trace[i], trace[i + 1]))
    total = sum(angles)
    return total, total/len(data_obj.norm_traces)

    #loop through and compute sum of euclidean distances between each
def is_hcrossing(p1, p2, y):
    """
    method to see if a horizontal line with a y value of y crosses between 2 points
    :param p1: 2x1 np array in form [x,y]
    :param p2: 2x1 np array in form [x,y]
    :param y: y value
    :return:
    """
    #print('y: ',y)
    #print('y1: ',p1[1])
    #print('y2: ',p2[1])

    if p1[1] <= y and p2[1] >=y:
        return True
    elif p1[1] >= y and p2[1] <=y:
        return True
    else:
        return False

def is_vcrossing(p1, p2, x):
    """
    method to see if a vertical line with a x value of x crosses between 2 points
    :param p1: 2x1 np array in form [x,y]
    :param p2: 2x1 np array in form [x,y]
    :param x: x value
    :return:
    """
    if p1[0] <= x and p2[0] >=x:
        return True
    elif p1[0] >= x and p2[0] <=x:
        return True
    else:
        return False



def get_horizontal_crossings(iter, data_obj):
    """
    computes number of crossings in a horizontal line in bottom-most box
    returns number of crossings, x coordinate of first intersection, x coordinate of last intersection
    :param box:
    :param data_obj:
    :return:
    """

    #flatten all points in traces into 1 np array
    '''
    data = data_obj.norm_traces[0]
    for i in range(1, len(data_obj.norm_traces)):
        data = np.stack((data, data_obj.norm_traces[i]),axis=0)
    num_points = np.shape(data)[0]
    '''
    #tally these and take averages at the end
    cross_avgs = []
    first_points_avgs = []
    last_points_avgs = []
    ymin = iter * BOUNDARY_DIM
    line_gap = BOUNDARY_DIM/9

    for i in range(9):
        y = ymin + (i * line_gap)
        line_crossings = []
        norm_traces_len  = len(data_obj.norm_traces)
        for k in range(norm_traces_len):
            data = data_obj.norm_traces[k]
            data_len  = len(data)
            for j in range(1, data_len):
                p2 = data[j]
                p1 = data[j-1]
                if is_hcrossing(p1, p2, y):
                    #get x value of crossing, append
                    #x_intersect = -1 * ((p2[1] - y) / ((p2[1] - p1[1])/(p2[0] - p1[0])) - p2[0])
                    if ( p2[1]==p1[1]):
                        line_crossings.extend([p1[0],p2[0]])
                    else:
                        x_intersect = -1*((((p2[0]-p1[0])*(p2[1]-y))/p2[1]-p1[1])-p2[0])
                        line_crossings.append(x_intersect)

        cross_avgs.append(len(line_crossings))
        first_points_avgs.append(0) if len(line_crossings) == 0 else first_points_avgs.append(line_crossings[0])
        last_points_avgs.append(0) if len(line_crossings) == 0 else last_points_avgs.append(line_crossings[-1])

    #get averages
    return sum(cross_avgs)/len(cross_avgs), sum(first_points_avgs)/len(first_points_avgs), sum(last_points_avgs)/len(last_points_avgs)


def get_vertical_crossings(iter, data_obj):
    """
    :param iter:
    :param data_obj:
    :return:
    """
    # flatten all points in norm_traces into 1 np array
  #  data = data_obj.norm_traces[0]
   # for i in range(1, len(data_obj.norm_traces)):
        #data = np.stack((data, data_obj.norm_traces[i]),axis = 0)
    #num_points = np.shape(data)[0]

    # tally these and take averages at the end
    cross_avgs = []
    first_points_avgs = []
    last_points_avgs = []
    xmin = iter * BOUNDARY_DIM
    line_gap = BOUNDARY_DIM / 9

    for i in range(9):
        x = xmin + (i * line_gap)
        line_crossings = []
        norm_traces_len  = len(data_obj.norm_traces)
        for k in range(norm_traces_len):
            data = data_obj.norm_traces[k]
            data_len = len(data)
            for j in range(1, data_len):
                p2 = data[j]
                p1 = data[j - 1]
                if is_vcrossing(p1, p2, x):
                    # get y value of crossing, append
                    #y_intersect = -1 * (((p2[0] - x) * (p2[1] - p1[1])/(p2[0] - p1[0])) - p2[1])```
                    if(p2[0]==p1[0]):
                        line_crossings.extend([p1[1],p2[1]])
                    else:
                        y_intersect = -1*((((p2[1]-p2[1])*(p2[0]-x))/(p2[0]-p1[0]))*p2[1])
                        line_crossings.append(y_intersect)

        cross_avgs.append(len(line_crossings))
        first_points_avgs.append(0) if len(line_crossings) == 0 else first_points_avgs.append(line_crossings[0])
        last_points_avgs.append(0) if len(line_crossings) == 0 else last_points_avgs.append(line_crossings[-1])

    # get averages
    return sum(cross_avgs) / len(cross_avgs), sum(first_points_avgs) / len(first_points_avgs), sum(
        last_points_avgs) / len(last_points_avgs)


#holds features 0 through 4, 35
global_feature_map = {
    get_trace_num : 0,
    get_x_mean: 1,
    get_y_mean: 2,
    get_covariance : 3,
    get_aspect_ratio : 4
    #get_num_sharp_points : 39
}
#global features map for 2 return value functions
global_double_feature_map = {
    get_line_length : (35, 36),
    get_angle_data : (37, 38)
}

#holds features number 5 through 34
crossings_feature_map = {
    get_horizontal_crossings : (5, 6, 7),
    get_vertical_crossings: (20, 21, 22)
}

def extract_all_features(data_obj):

    for key in global_feature_map.keys():
        data_obj.features[global_feature_map[key]] = key(data_obj)

    for key in global_double_feature_map.keys():
        data_obj.features[global_double_feature_map[key][0]], data_obj.features[global_double_feature_map[key][1]] = key(data_obj)

    for i in range(5):
        for key in crossings_feature_map.keys():
            inds = crossings_feature_map[key]
            f1, f2, f3 = key(i, data_obj)
            data_obj.features[inds[0] + 3 * i], \
            data_obj.features[inds[1] + 3 * i], \
            data_obj.features[inds[2] + 3 * i] = \
                f1, f2, f3
    # for key in crossings_feature_map:
    #     inds = crossings_feature_map[key]
    #     f1, f2, f3 = key(data_obj)
    #     data_obj.features[inds[0] + 3 * iter] , \
    #     data_obj.features[inds[1] + 3 * iter], \
    #     data_obj.features[inds[2]] = \
    #         f1, f2, f3
    #     iter += 1


def get_features(data_object_list, feature_file_name):
    #Normalize
    if not path.exists(DATA_FOLDER+feature_file_name):
        count = len(data_object_list)
        i=0
        for data_object in data_object_list:
            i+=1
            #Code for Feature Extraction here:
            print(i,' of ',count,'.')
            data_object.translate_scale()
            extract_all_features(data_object)
        write_csv.generate_features_table(data_object_list, feature_file_name)
        print('data_normalized')
    else:
        print('Feature list already created.')
    return data_object_list
