import numpy as np

BOUNDARY_DIM = (2.0/5.0)
NUM_LINES = 9

def get_trace_num(data_obj):
    """
    returns the number of traces in a character inkml
    :param tracelist: a list of traces
    :return: the length of tracelist
    """
    return len(data_obj.traces)

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
    xdata = data_obj.traces[0][:,0]
    for i in range(1, len(data_obj.traces)):
        xdata = np.append(xdata, data_obj.traces[i][:,0])
    return np.mean(xdata)

def get_y_mean(data_obj):
    """
    returns the mean of all x coordinates in the points in a character object
    :param data_obj:
    :return:
    """
    ydata = data_obj.traces[0][:, 1]
    for i in range(1, len(data_obj.traces)):
        ydata = np.appendy(ydata, data_obj.traces[i][:, 1])
    return np.mean(ydata)

def get_covariance(data_obj):
    xdata = data_obj.traces[0][:,0]
    ydata = data_obj.traces[0][:, 1]
    for i in range(1, len(data_obj.traces)):
        xdata = np.append(xdata, data_obj.traces[i][:,0])
        ydata = np.appendy(ydata, data_obj.traces[i][:, 1])
    cov_mat = np.cov(np.stack(xdata, ydata))
    return cov_mat[0, 1]

def get_aspect_ratio(data_obj):
    """
    returns aspect ratio of the character
    :param data_obj:
    :return:
    """
    return data_obj.xmax/data_obj.ymax

def is_hcrossing(p1, p2, y):
    """
    method to see if a horizontal line with a y value of y crosses between 2 points
    :param p1: 2x1 np array in form [x,y]
    :param p2: 2x1 np array in form [x,y]
    :param y: y value
    :return:
    """
    if p1[0, 1] <= y and p2[0, 1] >=y:
        return True
    elif p1[0, 1] >= y and p2[0, 1] <=y:
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
    if p1[0, 0] <= x and p2[0, 0] >=x:
        return True
    elif p1[0, 0] >= x and p2[0, 0] <=x:
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
    data = data_obj.traces[0]
    for i in range(1, len(data_obj.traces)):
        data = np.stack(data, data_obj.traces[i])
    num_points = np.shape(data)[0]

    #tally these and take averages at the end
    cross_avgs = []
    first_points_avgs = []
    last_points_avgs = []
    ymin = iter * BOUNDARY_DIM
    line_gap = BOUNDARY_DIM/9

    for i in range(9):
        y = ymin + (i * line_gap)
        for j in range(1, num_points - 1):
            line_crossings = []
            p2 = data_obj[j]
            p1 = data_obj[j-1]
            if is_hcrossing(p1, p2, y):
                #get x value of crossing, append
                x_intersect = -1 * ((p2[1] - y) / ((p2[1] - p1[1])/(p2[0] - p1[0])) - p2[0])
                line_crossings.append[x_intersect]

        cross_avgs.append(len(line_crossings))
        first_points_avgs.append(0) if len(line_crossings) == 0 else first_points_avgs.append(line_crossings[0])
        last_points_avgs.append(0) if len(line_crossings) == 0 else last_points_avgs.append([line_crossings[-1]])

    #get averages
    return sum(cross_avgs)/len(cross_avgs), sum(first_points_avgs)/len(first_points_avgs), sum(last_points_avgs)/len(last_points_avgs)


def get_vertical_crossings(iter, data_obj):
    """

    :param iter:
    :param data_obj:
    :return:
    """
    # flatten all points in traces into 1 np array
    data = data_obj.traces[0]
    for i in range(1, len(data_obj.traces)):
        data = np.stack(data, data_obj.traces[i])
    num_points = np.shape(data)[0]

    # tally these and take averages at the end
    cross_avgs = []
    first_points_avgs = []
    last_points_avgs = []
    xmin = iter * BOUNDARY_DIM
    line_gap = BOUNDARY_DIM / 9

    for i in range(9):
        x = xmin + (i * line_gap)
        for j in range(1, num_points - 1):
            line_crossings = []
            p2 = data_obj[j]
            p1 = data_obj[j - 1]
            if is_vcrossing(p1, p2, x):
                # get y value of crossing, append
                y_intersect = -1 * (((p2[0] - x) * (p2[1] - p1[1])/(p2[0] - p1[0])) - p2[1])
                line_crossings.append[y_intersect]

        cross_avgs.append(len(line_crossings))
        first_points_avgs.append(0) if len(line_crossings) == 0 else first_points_avgs.append(line_crossings[0])
        last_points_avgs.append(0) if len(line_crossings) == 0 else last_points_avgs.append([line_crossings[-1]])

    # get averages
    return sum(cross_avgs) / len(cross_avgs), sum(first_points_avgs) / len(first_points_avgs), sum(
        last_points_avgs) / len(last_points_avgs)


global_feature_map = {
    get_trace_num : 0,
    get_x_mean: 1,
    get_y_mean: 2,
    get_covariance : 3,
    get_aspect_ratio : 4
}

crossings_feature_map = {
    get_horizontal_crossings : (5, 6, 7),
    get_vertical_crossings: (20, 21, 22)
}

def extract_all_features(data_obj):

    for key in global_feature_map():
        data_obj.features[global_feature_map[key]] = key(data_obj)


    for i in range(5):
        for key in crossings_feature_map:
            inds = crossings_feature_map[key]
            f1, f2, f3 = key(i, data_obj)
            data_obj.features[inds[0] + 3 * iter], \
            data_obj.features[inds[1] + 3 * iter], \
            data_obj.features[inds[2]] = \
                f1, f2, f3
    # for key in crossings_feature_map:
    #     inds = crossings_feature_map[key]
    #     f1, f2, f3 = key(data_obj)
    #     data_obj.features[inds[0] + 3 * iter] , \
    #     data_obj.features[inds[1] + 3 * iter], \
    #     data_obj.features[inds[2]] = \
    #         f1, f2, f3
    #     iter += 1
