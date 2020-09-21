import numpy as np
import scipy.spatial as spatial
import math
import matplotlib.pyplot as plt
import portion as P
import concurrent.futures

def get_min_max(stroke):
    x = stroke[:,0]
    y = stroke[:,1]
    return np.amin(x), np.amax(x), np.amin(y), np.amax(y)

def get_average_distance(stroke):
    size = len(stroke)
    avg_distance = 0
    for i in range(1, size):
        avg_distance += np.linalg.norm(np.array(stroke[i]) - np.array(stroke[i-1]))
    avg_distance = avg_distance/size

    return avg_distance

def interpolate_stroke(stroke):
    new_stroke = []
    distance = get_average_distance(stroke) / 2
    size = len(stroke)
    for i in range(1, size):
        if stroke[i][0] <= stroke[i - 1][0]:
            backwards = True
        else:
            backwards = False
        # determine how many points to add
        n = int(((np.linalg.norm(np.array(stroke[i]) - np.array(stroke[i - 1]))) // distance) - 1)
        # print(n)
        new_stroke.append(stroke[i - 1])

        if n > 0:
            x_change = (stroke[i][0] - stroke[i - 1][0]) / (n + 1)
            x = []
            for j in range(1, n + 1):
                x.append(stroke[i - 1][0] + j * x_change)
            if not backwards:
                y = np.interp(x, [stroke[i - 1][0], stroke[i][0]], [stroke[i - 1][1], stroke[i][1]])
            else:
                x.reverse()
                y = list(np.interp(x, [stroke[i][0], stroke[i - 1][0]], [stroke[i][1], stroke[i - 1][1]]))
                x.reverse()
                y.reverse()
            for j in range(n):
                new_stroke.append(np.array([x[j], y[j]]))
    new_stroke.append(stroke[size - 1])
    return new_stroke

class Node:
    """
    a class to represent a "node" in a line of sight graph. most calculations are done upon initialization including the bounding box of the strokes, and the convex hull
    stroke should be an numpy 2 x n array. all x points in one column, all y points in another
    """
    def __init__(self, id, trace_group, stroke):
        self.id = id
        self.tracegroup = trace_group
        self.points = stroke
        self.edges = list()
        self.boundingbox = ""
        self.boundingbox_center = ""
        self.calculate_bounding_box()
        # print("node =", self.id, "bbc=", self.boundingbox_center)
        # print(self.points)
        # print(np.size(self.points, axis=0))
        if np.size(self.points, 0) < 4 or self.get_y_max() == self.get_y_min() or self.get_x_min() == self.get_x_max(): #if stroke has < 4 points convex hull impossible, if striaght line, convex hull impossible
            self.hull = self.points
        else:
            conv = spatial.ConvexHull(self.points, qhull_options='QbB')
            self.hull = []
            for index in conv.vertices:
                self.hull.append(self.points[index])
            self.hull = np.array(self.hull)
        self.points = np.array(interpolate_stroke(self.points))
       # self.plot_hull_and_show()


    def get_y_max(self):
        """
        returns maximum y value in the stroke
        """
        return self.boundingbox[3]

    def get_x_max(self):
        """
        returns maximum x value in the stroke
        :return:
        """
        return self.boundingbox[1]

    def get_y_min(self):
        """
        returns minimum y value in the stroke
        :return:
        """
        return self.boundingbox[2]

    def get_x_min(self):
        """
        returns minimum x value in the stroke
        :return:
        """
        return self.boundingbox[0]

    def calculate_bounding_box(self):
        """
            calculates bounding box and bounding box center for a stroke
        :return:
        """
        xmin, xmax, ymin, ymax = get_min_max(self.points)
        self.boundingbox = [xmin, xmax, ymin, ymax]
        self.boundingbox_center = np.array([(xmin+xmax)/2, (ymin+ymax)/2])


    def get_convex_hull(self):
        """
        returns points on a convex hull
        :return:
        """
        return self.hull

    def add_edge(self, edge):
        """
        adds an edge between 2 nodes
        :param edge:
        :return:
        """
        self.edges.append(edge)

    def plot_hull_and_show(self):
        """
        method for testing purposes
        plots points in this stroke, including the convex hull and the bounding box center. shows graph
        :return:
        """
        plt.figure()
        plt.plot(self.points[:, 0], self.points[:, 1], 'o')
        plt.plot(self.hull[:, 0], self.hull[:, 1], 'k-')
        plt.title("Node ID: " + str(self.id))
        plt.scatter(self.boundingbox_center[0], self.boundingbox_center[1], color='m')
        plt.show()

    def plot_hull(self):
        """
        method for testing purposes. plots the convex hull and bounding box center but doesn't show. can be called on many nodes
        to plot them in the same plot
        :return:
        """

        plt.scatter(self.points[:,0], self.points[:,1],  s=4)
        plt.plot(self.hull[:,0], self.hull[:,1], 'k-')
        plt.scatter(self.boundingbox_center[0], self.boundingbox_center[1], color='m')

class Edge:
    """
    class to represent edges.
    """
    label = ''
    node1 = ''
    node2 = ''

    def __init__(self, node1, node2):
        if node1.id < node2.id:
            self.node1 = node1
            self.node2 = node2
        else:
            self.node1 = node2
            self.node2 = node1

    def __eq__(self, other):
        if self.node1 == other.node1:
            if self.node2 == other.node2:
                return True
        return False

class LOSGraph:
    """
    a class to represent a line of sight graph. contains a list of nodes and functionality to edit
    argument tracegroup should be a list of strokes. a stroke should be a list of points
    """
    def __init__(self, name):
        """
        constructor for LOSGraph class. nodes will be stored as a dictionary of nodes, mapping the node id number to the node itself
        """
        self.name = name
        self.nodes = dict()
        self.edges = set()


    def add_node(self, node):
        """
        adds a node to the graph
        :param node: node to be added
        :return:
        """
        self.nodes[node.id] = node

    def add_undirected_edge(self, node1, node2):
        """
        adds an undirected edge between two nodes by adding 2 directed edges
        :param node1:
        :param node2:
        :return:
        """
        # node1.add_edge(node2.id)
        # node2.add_edge(node1.id)
        edge = (min(node1.id, node2.id), max(node1.id, node2.id))
        if edge not in self.edges:
            self.edges.add(edge)

    def los(self, uas, interval):
        """
        tests to see if there is overlap between an unblocked angle interval set, and the set of intervals blocked by a stroke
        :param: uas - unblocked angle set, member of Portion.closed() class
        :param interval: interval, member of Portion.closed() class
        :return:
        """
        intersect = uas & interval
        if not intersect.empty:
            return True
        return False


    def remove_blocked_region(self, uas, interval):
        """
        returns set difference of unblocked angle intervals and the intervals blocked off by a node
        :param uas:
        :param interval:
        :return:
        """
        return uas - interval

    def invert_interval(self, theta_min, theta_max):
        """
        "inverts" an interval. used when an angle rnage crosses 0 degrees.
        example: turns the angle range: 10 degrees to 350 degrees,  to 0 to 10 degrees union 350 to 360 degrees
        note: calculations are done in radians but degrees are easier to visualize, so above example was in degrees
        :param theta_min:
        :param theta_max:
        :return:
        """
        return P.closed(0, theta_min) | P.closed(theta_max, 2*math.pi)

    def cross_positive_x(self, bbc, point1, point2):
        if (point2[1] - point1[1] == 0):
            return False
        if (point1[1] >= bbc[1] and point2[1] <= bbc[1]) or (point1[1] <= bbc[1] and point2[1] >= bbc[1]): #the point crosses the x axis so we need to learn where
            x = ((bbc[1] - point1[1]) * (point2[0] - point1[0])) / (point2[1] - point1[1]) + point1[0]
            if x > bbc[0]:
                return True
        return False

    #TODO currently not possible to draw an edge to a node with only one point
    #prune based on covered ranges
    def construct_edges(self):
        """
        implementation to construct edges in a line of sight graph. see writeup for references.
        :return:
        """
        # figure = plt.figure()
        # plt.title("edge debugging")
        for key in self.nodes:
            node = self.nodes[key]
            #print("node:", node.id)
            unblocked_angle_set = P.closed(0, 2*math.pi)
            others = set(self.nodes.keys())
            others.remove(node.id)
            others = list(others)
            others.sort(key=lambda x: np.linalg.norm(node.boundingbox_center - self.nodes[x].boundingbox_center))
            # print(others)
            for otherkey in others:
              #  print("other:", otherkey)
                other = self.nodes[otherkey]
                hull = other.get_convex_hull()
                size = len(hull)
                angle_range = P.closed(2, 1) #creates an empty angle range. using 2 and 1 is arbitary
                for i in range(size):
                    point = hull[i]
                    w = np.array([point[0] - node.boundingbox_center[0], point[1] - node.boundingbox_center[1]])
                    h = np.array([1, 0])
                    # print("hull point:", point)
                    # print("bbc:", node.boundingbox_center)
                    if point[0] == node.boundingbox_center[0] and point[1] == node.boundingbox_center[1]:
                        theta = 0
                    elif point[1] >= node.boundingbox_center[1]:
                        theta = np.arccos(np.dot(w, h) / (np.linalg.norm(w) * np.linalg.norm(h)))
                    else:
                        theta = (2 * math.pi) - (np.arccos(np.dot(w, h) / (np.linalg.norm(w) * np.linalg.norm(h))))
                    # print(theta)
                    if i > 0:
                        if self.cross_positive_x(node.boundingbox_center, hull[i], hull[i-1]):
                            angle_range = angle_range | self.invert_interval(min(theta, prev_theta), max(theta, prev_theta))
                        else:
                            angle_range = angle_range | P.closed(theta, prev_theta) | P.closed(prev_theta, theta)
                #     print(theta)
                #     print(point)
                #     theta_min = min(theta_min, theta)
                #     theta_max= max(theta, theta_max)
                #     print("thetas:", theta_min, theta_max)
                # # if other.get_y_max() > node.boundingbox_center[1] and other.get_y_min() < node.boundingbox_center[1] and other.get_x_min() > node.boundingbox_center[0]:
                #     print("INVERT")
                #     print(node.boundingbox_center)
                #     print("    "+str(other.get_x_min()))
                #     hull_interval = self.invert_interval(theta_min, theta_max)
                    prev_theta = theta
                # if invert:
                #     print("INVERT")
                #     print(node.boundingbox_center)
                #     print("    "+str(other.get_x_min()))
                #     hull_interval = self.invert_interval(theta_min, theta_max)
                # else:
                #     hull_interval = P.closed(theta_min, theta_max)
                if self.los(unblocked_angle_set, angle_range):
                    # print("True")
                    # print("adding edge:", str(node.id), "can see", str(other.id))
                    self.add_undirected_edge(node, other)
                # print("hull interval going into remove method:", angle_range)
                unblocked_angle_set = self.remove_blocked_region(unblocked_angle_set, angle_range)
                # print("unblocked angle set:", unblocked_angle_set)
        # for pt in self.nodes[0].hull:
        #     print(pt, self.nodes[1].boundingbox_center)
        #     plt.plot([pt[0],self.nodes[1].boundingbox_center[0]] , [pt[1], self.nodes[1].boundingbox_center[1]], 'k-')
        #plt.show()


    def print_graph(self):
        """
        prints representation of the graph to the console
        :return:
        """
        for node in self.nodes:
            print("Node: " + str(node))
            print("    neighbors:")
            for edge in self.nodes[node].edges:
                print("        "+str(edge))

    def plot_expression(self):
        plt.figure()
        plt.title("Expression Graph")
        for node in self.nodes:
            self.nodes[node].plot_hull()
        # for edge in self.edges:
        #     plt.plot([self.nodes[edge[0]].boundingbox_center[0], self.nodes[edge[1]].boundingbox_center[0]],
        #              [self.nodes[edge[0]].boundingbox_center[1], self.nodes[edge[1]].boundingbox_center[1]],
        #              'k-', color='green')
        plt.show()


# def  make_LOS_graph(name, strokes):
#     """
#         constructs a line of sight graph
#     :param strokes: a list of 2D np arrays of 2 columns. column 0 should be all x values, and column 1 should be corresponding y values
#     :return: the finished graph with complete with edges and ready to move on to feature extraction stage
#     """
#     id = 0
#
#     graph = LOSGraph(name)
#     for stroke in strokes:
#         graph.add_node(Node(id, stroke))
#         id += 1
#     graph.construct_edges()
#     for node in graph.nodes:
#         graph.nodes[node].plot_hull()
#     return graph
    # see = 1
    # hull = 3
    # for pt in graph.nodes[hull].hull:
    #     print(pt, graph.nodes[see].boundingbox_center)
    #     plt.plot([pt[0],graph.nodes[see].boundingbox_center[0]] , [pt[1], graph.nodes[see].boundingbox_center[1]], 'k-')
    # plt.show()

def make_LOS_graph(name, expression_trace):
    graph = LOSGraph(name)
    for symbol in expression_trace:
        # print(symbol)
        dct = expression_trace[symbol].norm_trace_dict
        for trace_id in dct:
            points = []
            for point in dct[trace_id]:
                points.append([point[0], point[1]])
            points = np.array(points)
            graph.add_node(Node(trace_id, symbol, points))
    graph.construct_edges()
    return graph
