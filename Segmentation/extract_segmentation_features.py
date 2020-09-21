import numpy as np
import losgraph
import scipy.stats as stats
import pickle
import math

#HISTOGRAM BIN CONSTANTS
NUM_ANGLE_BINS = 6
NUM_RADIUS_BINS = 5
NOISE_EPSILON = 0.000001


def handle_size_one(point, radius):
    #find the right bin to put this point in
    features = np.zeros(NUM_ANGLE_BINS * NUM_RADIUS_BINS)
    x_max = 0
    index = 0
    radius_gap = radius / NUM_RADIUS_BINS
    angle_gap = (2 * math.pi) / (NUM_ANGLE_BINS)
    for i in range(1, NUM_RADIUS_BINS + 1):
        # print(index)
        x_min = x_max
        x_max = x_min + radius_gap
        theta_min = 0
        if point[0] < x_max and point[0] >= x_min:
            for j in range(NUM_ANGLE_BINS):
                theta_max = theta_min + angle_gap
                if point[1] < theta_max and point[1] >= theta_min:
                    features[index] = 1.0
                    return features
                theta_min = theta_min + angle_gap

            index += 1
    return features

def noise_introduction(points):
    seen = set()
    for i in range(len(points)):
        if points[i] not in seen:
            seen.add(points[i])
        else:
            place = True
            while place:
                points[i] = points[i] + NOISE_EPSILON
                if points[i] not in seen:
                    seen.add(points[i])
                    place = False
    return points

def convert_points_to_log_polar(center, points):
    new_points = []

    h = np.array([1, 0])

    for point in points:
        w = np.array([point[0] - center[0], point[1] - center[1]])
        if point[0] == center[0] and point[1] == center[1]:
            theta = 0
        elif point[1] >= center[1]:
            theta = np.arccos(np.dot(w, h) / (np.linalg.norm(w) * np.linalg.norm(h)))
        else:
            theta = (2 * math.pi) - (np.arccos(np.dot(w, h) / (np.linalg.norm(w) * np.linalg.norm(h))))

        distance = np.linalg.norm(center - point)
        # print(distance, theta)
        new_points.append(np.array([distance, theta]))

    return new_points

def get_parzen_radius(node1, node2, center):
    max = 0
    for point in node1.points:
        distance = np.linalg.norm(point - center)
        if distance > max:
            max = distance
    for point in node2.points:
        distance = np.linalg.norm(point - center)
        if distance > max:
            max = distance
    return max * 1.5

def get_parzen_features(points, radius):
    """
    returns feature vector for 1 of the 3 parzen window shape contexts
    :param points:
    :param bbc:
    :param radius:
    :return:
    """
    # print(points)
    # gkde = stats.gaussian_kde(points)

    features = np.zeros(NUM_ANGLE_BINS * NUM_RADIUS_BINS)

    if len(points) == 0:
        return features
    if len(points) == 1:
        return handle_size_one(points[0], radius)
    # print("num points = ", len(points))
    radius_gap = radius / NUM_RADIUS_BINS
    angle_gap = (2 * math.pi) / (NUM_ANGLE_BINS)
    points = np.array(points)
    rad_points = points[:, 0]
    theta_points = points[:, 1]
    while True:
        try:
            gkde_rad = stats.gaussian_kde(rad_points)
            break
        except np.linalg.LinAlgError:
            print("singular covariance matrix. introducting noise")
            rad_points = noise_introduction(rad_points)
        except:
            print(len)
    while True:
        try:
            gkde_theta = stats.gaussian_kde(theta_points)
            break
        except np.linalg.LinAlgError:
            print("singular covariance matrix. introducting noise")
            theta_points = noise_introduction(theta_points)

    x_max = 0
    index = 0

    for i in range(1, NUM_RADIUS_BINS + 1):
        # print(index)
        x_min = x_max
        x_max = x_min + radius_gap
        theta_min = 0
        for j in range(NUM_ANGLE_BINS):
            # if j != NUM_ANGLE_BINS - 1:
            theta_max = theta_min + angle_gap
            # else:
            #     theta_max = 0
            # print("rads/thetas", np.array([x_min, x_max]), np.array([theta_min, theta_max]))
            # features[index] = gkde.integrate_box(np.array(x_min, x_max), np.array(theta_min, theta_max))
            rad_pd = gkde_rad.integrate_box_1d(x_min, x_max)
            angle_pd = gkde_theta.integrate_box_1d(theta_min, theta_max)
            # print(rad_pd, angle_pd)
            features[index] = rad_pd * angle_pd

            theta_min = theta_min + angle_gap

            index += 1
    # print(features)
    return features

def get_average_bbc(node1, node2):
    """
    returns the midpoint of the bounding box centers of 2 nodes
    :param node1:
    :param node2:
    :return:
    """
    return np.array([(node1.boundingbox_center[0] + node2.boundingbox_center[0]) / 2,
                     (node1.boundingbox_center[1] + node2.boundingbox_center[1]) / 2])

def get_other_window_points(graph, radius, center, node1, node2):
    #test to see if any bounding box points are in the window
    to_test = []
    for id in graph.nodes:
        if id != node1.id and id != node2.id:
            node = graph.nodes[id]
            ul = np.array(node.get_x_min(), node.get_y_max())
            ll = np.array(node.get_x_min(), node.get_y_min())
            ur = np.array(node.get_x_max(), node.get_y_max())
            lr = np.array(node.get_x_min(), node.get_y_max())

            if np.linalg.norm(ul - center) <= radius:
                to_test.append(id)
                continue;
            if np.linalg.norm(ll - center) <= radius:
                to_test.append(id)
                continue;
            if np.linalg.norm(ur - center) <= radius:
                to_test.append(id)
                continue;
            if np.linalg.norm(lr - center) <= radius:
                to_test.append(id)

    other_points = []
    for id in to_test:
        points = graph.nodes[id].points
        for point in points:
            if np.linalg.norm(point - center) <= radius:
                other_points.append(point)
    return other_points

def get_all_parzen(graph, node1, node2):
    center = get_average_bbc(node1, node2)
    radius = get_parzen_radius(node1, node2, center)
    context1_points = node1.points
    context2_points = node2.points
    context_other_points = get_other_window_points(graph, radius, center, node1, node2)
    context1_points = convert_points_to_log_polar(center, context1_points)
    context2_points = convert_points_to_log_polar(center, context2_points)
    context_other_points = convert_points_to_log_polar(center, context_other_points)

    features = get_parzen_features(context1_points, radius)

    features = np.concatenate((features, get_parzen_features(context2_points, radius)))

    features = np.concatenate((features, get_parzen_features(context_other_points, radius)))

    return features


def get_mean_x(node):
    """
    returns the mean x value of all points in a node
    :param node:
    :return:
    """
    ret =  np.mean(node.points[:, 0])
    return ret

def get_mean_y(node):
    """
    returns the mean x value of all points in a node
    """
    ret = np.mean(node.points[:, 1])
    return ret

def get_bbc_distance(node1, node2):
    """
    calculates the distance between bounding box centers
    :param node1:
    :param node2:
    :return:
    """
    ret = np.linalg.norm(node1.boundingbox_center - node2.boundingbox_center)
    return ret

def get_size_difference(node1, node2):
    """
    calculates the difference in area between the 2 node bounding boxes
    :return:
    """
    area1 = (node1.get_x_max() - node1.get_x_min()) * (node1.get_y_max() - node1.get_y_min())
    area2 = (node2.get_x_max() - node2.get_x_min()) * (node2.get_y_max() - node2.get_y_min())
    return abs(area1 - area2)

def get_horizontal_distance(node1, node2):
    """
    returns mean horizontal distance between 2 nodes
    :param node1:
    :param node2:
    :return:
    """
    ret =  (get_mean_x(node1) + get_mean_x(node2)) / 2
    return ret

def get_vertical_offset(node1, node2):
    """
    returns mean vertical distance between 2 nodes
    :param node1:
    :param node2:
    :return:
    """
    return (get_mean_y(node1) + get_mean_y(node2)) / 2

def get_min_max_point_distance(node1, node2):
    """
    returns the distance between the closest point pair with one point from stroke a and 1 point from stroke b
    :param node1:
    :param node2:
    :return:
    """
    min = 100000000
    max = 0
    for point1 in node1.points:
        for point2 in node2.points:
            dist = np.linalg.norm(point1 - point2)
            if dist < min:
                min = dist
            if dist > max:
                max = dist

    return min, max

def get_boundingbox_overlaps(node1, node2):
    """
    returns area of overlap between 2 bounding boxes
    :return:
    """
    x_overlap = max(0, min(node1.get_x_max(), node2.get_x_max()) - max(node1.get_x_min(), node2.get_x_min()))
    y_overlap = max(0, min(node2.get_y_min(), node1.get_y_min()) - min(node1.get_y_max(), node2.get_y_max()))
    return x_overlap, x_overlap * y_overlap

def get_starting_differences(node1, node2):
    """
    returns euclidean distance between start point of each stroke, horizontal displacement between starting points of each stroke
    :param node1:
    :param node2:
    :return:
    """

    point1 = node1.points[0]
    point2 = node2.points[0]

    return np.linalg.norm(point1 - point2), abs(point1[0] - point2[0])

def get_ending_differences(node1, node2):
    """
    returns euclidean distance between start point of each stroke, horizontal displacement between ending points of each stroke
    :param node1:
    :param node2:
    :return:
    """
    point1 = node1.points[-1]
    point2 = node2.points[-1]

    return np.linalg.norm(point1 - point2), abs(point1[0] - point2[0])


def calculate_parallelity(node1, node2):
    """
    calculates parallelity between 2 nodes and returns
    :param node1:
    :param node2:
    :return:
    """

    node1vec = node1.points[-1] - node1.points[0]
    node1vec = node1vec / np.linalg.norm(node1vec)
    node2vec = node2.points[-1] - node2.points[0]
    node2vec = node2vec / np.linalg.norm(node2vec)
    ret = np.arccos(np.dot(node1vec, node2vec))
    return ret

def calculate_writing_curvature(node1, node2):
    """

    :param node1:
    :param node2:
    :return:
    """

def get_time_gap(node1, node2):
    """

    :param node1:
    :param node2:
    :return:
    """
    return abs(int(node1.id) - int(node2.id))

#FEATURES SIZE
FEATURES_SIZE = 15
#map feature vector inidices to functions that calculate them, 1 return value
geometric_features_map_r1 = {
    get_size_difference : 0,
    get_bbc_distance : 1,
    get_horizontal_distance : 2,
    get_vertical_offset : 3,
    calculate_parallelity : 4,
    # 5: calculate_writing_curvature,
    get_time_gap : 6
}
#map feature vector inidices to functions that calculate them, 2 return values
geometric_features_map_r2 = {
    get_min_max_point_distance : 7,
    get_boundingbox_overlaps : 9,
    get_starting_differences : 11,
    get_ending_differences : 13


}

def add_ground_truth(graph, edge):
    """
    2 edges should have a value of 1 for merge and 0 for split. we merge 2 edges if they belong to the same tracegroup
    :return:
    """
    if graph.nodes[edge[0]].tracegroup == graph.nodes[edge[1]].tracegroup:
        return np.array([1])
    else:
        return np.array([0])

def extract_features(graph):
    # print(graph)
    feature_vectors = {}
    for edge in graph.edges:
        edge_id = edge[0] + "_" + edge[1]
        node1 = graph.nodes[edge[0]]
        node2 = graph.nodes[edge[1]]
        features = np.zeros(FEATURES_SIZE)

        for key in geometric_features_map_r1.keys():
            features[geometric_features_map_r1[key]] = key(node1, node2)

        for key in geometric_features_map_r2.keys():
            features[geometric_features_map_r2[key]], features[geometric_features_map_r2[key] + 1] = key(node1, node2)

        features = np.concatenate((features, get_all_parzen(graph, node1, node2)))
        features = np.concatenate((features, add_ground_truth(graph, edge)))
        # print(features.size)
        feature_vectors[edge_id] = features
    return feature_vectors

def test_feature_extraction():
    with open('inkml_with_graphs.obj', 'rb') as file:
        inkml_data_list = pickle.load(file)

    i = 0
    for key in inkml_data_list:
        inkml_data_list[key].feature_vectors = extract_features(inkml_data_list[key].graph)
        inkml_data_list[key].graph.plot_expression()
        # print(inkml_data_list[key].feature_vectors)
        i += 1
        if i == 5:
            break

#test_feature_extraction()

