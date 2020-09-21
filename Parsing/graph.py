import copy
import numpy as np
import data_io
from dataclasses import dataclass

class Node():
    name = ''
    trace = None
    def __init__(self, id_, name, truth_instance, gt):
        self.id = id_
        self.label_id = truth_instance
        self.name = name
        self.trace = None
        self.max_x_point = None
        self.min_x_point = None
        self.max_y_point = None
        self.min_y_point = None
        self.height = 0
        self.width = 0
        self.aspect_ratio = 0
        self.norm_traces = None
        self.features = {}
        self.gt = gt
        self.predicted = ''
        self.stroke_ids = ''

    def __str__(self):
        return 'Node : '+self.name



    def get_limits(self):
        strokes = self.trace
        max_x_point = None
        min_x_point = None
        max_y_point = None
        min_y_point = None
        min_x = 99999999
        max_x = 0
        min_y = 99999999
        max_y = 0
        for stroke in strokes:
            for point in stroke:
                if point[0] > max_x:
                    max_x = point[0]
                    self.max_x_point = point
                if point[0] < min_x:
                    min_x = point[0]
                    self.min_x_point = point
                if point[1] > max_y:
                    max_y = point[1]
                    self.max_y_point = point
                if point[1] < min_y:
                    min_y = point[1]
                    self.min_y_point = point


"""
simple class to represent an edge between 2 nodes. 
contains a reference to the nodes, and a string representing their relationship
"""
@dataclass
class Edge:
    node1: Node
    node2: Node
    rel: str


    def __str__(self):
        return "node1 : "+self.node1.gt+" -"+self.rel+"- node2 : "+self.node2.gt