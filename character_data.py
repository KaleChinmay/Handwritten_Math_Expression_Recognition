import copy
import numpy as np


class Character_Data:
    def __init__(self):
        self.gt = ''
        self.id = 1
        self.trace = []
        self.location = '.\\Data\\trainingSymbols\\'
        self.filename = ''
        self.name = ''
        self.max_x_point = None
        self.min_x_point = None
        self.max_y_point = None
        self.min_y_point = None
        self.height = 0
        self.width = 0
        self.aspect_ratio = 0
        self.norm_traces = None
        self.features = {}

    def __str__(self):
        return self.gt+'\n'+self.id+'\n'+self.filename

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
                    #print(point)
                    self.min_x_point = point
                if point[1] > max_y:
                    max_y = point[1]
                    self.max_y_point = point
                if point[1] < min_y:
                    min_y = point[1]
                    self.min_y_point = point


    def translate_scale(self):
        #translate
        self.get_limits()
        max_x = self.max_x_point[0]
        min_x = self.min_x_point[0]
        min_y = self.min_y_point[1]
        max_y = self.max_y_point[1]
        self.width = max_x-min_x
        self.height = max_y-min_y
        if(self.height==0):
            self.height = 1
        self.aspect_ratio = self.width/self.height
        strokes = self.trace
        t_strokes = None
        t_strokes = copy.deepcopy(strokes)
        strokes_len = len(strokes)
        for i in range(strokes_len):
            strokes_i_len = len(strokes[i])
            for j in range(strokes_i_len):
                if(min_x >= 0):
                    t_strokes[i][j][0] = strokes[i][j][0]-min_x
                else:
                    t_strokes[i][j][0] = strokes[i][j][0]+min_x
                if(min_y >- 0):
                    t_strokes[i][j][1] = strokes[i][j][1]-min_y
                else:
                    t_strokes[i][j][1] = strokes[i][j][1]+min_y
        #print(strokes)
        #print(t_strokes)        # Scale depending on the bigger dimension
        # if x (width) is higher, scale with x while preserving aspect ratio
        # if y (height) is higher, scale with y while preserving aspect ratio        s_t_strokes = None
        s_t_strokes = copy.deepcopy(strokes)
        st_strokes_len = len(s_t_strokes)
        for i in range(st_strokes_len):
            st_strokes_i_len = len(s_t_strokes[i])
            for j in range(st_strokes_i_len):
                if(self.height >= self.width):
                    s_t_strokes[i][j][1] = (2*t_strokes[i][j][1]/self.height)
                    s_t_strokes[i][j][0] = (2*t_strokes[i][j][0]/self.height)
                else:
                    s_t_strokes[i][j][0] = (2*t_strokes[i][j][0]/self.width)
                    s_t_strokes[i][j][1] = (2*t_strokes[i][j][1]/self.width)

        st_strokes_len = len(s_t_strokes)
        for i in range(st_strokes_len):
            s_t_strokes[i] = np.array(s_t_strokes[i])
        #print(s_t_strokes[i] )

        
        self.norm_traces = s_t_strokes
        #print(self.norm_traces)