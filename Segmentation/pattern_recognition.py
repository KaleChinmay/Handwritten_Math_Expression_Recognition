from location import Location
import data_io
import graph
import feature_extraction
import joblib
import pickle
import numpy as np
import pandas as pd


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
    #39 : 'ID',
    #40 : 'Class label'
}



class PatternRec():

    location = None
    segmentor = ''
    dataset = None

    def __init__(self, location_string, segmentor='baseline', dataset='train'):
        self.segmentor = segmentor
        self.location = Location(location_string)
        self.dataset = dataset
        print(self.location.training_data_path)
        print(self.segmentor)
        print(self.dataset)


    def expression_recognizer(self, inkml_data, test_ids, segmentor, predicted_data):
        #Use LOS Segment if predicted data exist 
        if(predicted_data):
            expression_dict = {}
            for index, row in predicted_data.iterrows():
                #print(index, row['predicted'])
                index_list = index.split('***')
                index = index_list[0]
                nodes = index_list[1].split("_")
                node_1 = nodes[0]
                node_2 = nodes[1]
                # index_part_list = index_list[:-2]
                # node_1 = index_list[-2]
                # node_2 = index_list[-1]
                # index = "_".join(index_part_list)
                if(row['predicted']==1.0):
                    if(index in expression_dict.keys()):
                        expression_dict[index].append((node_1,node_2))
                    else:
                        print("adding", index)
                        expression_dict[index] = [(node_1, node_2)]
                else:
                    if index not in expression_dict.keys():
                        print("adding as empty", index)
                        expression_dict[index] = []

            print("expression dict lenth:", len(expression_dict))
            print("test id length:,", len(test_ids))
            no_edges = set(test_ids).difference(set(expression_dict.keys()))
            for key in no_edges:
                expression_dict[key] = []
            for inkml_key in test_ids:
                inkml = inkml_data[inkml_key]
                print('Name : ',inkml_key)
                print('Starting Segmentation')
                segments = self.los_segmenter(expression_dict[inkml_key], inkml)



                #segments = self.segmentor(inkml)
                print('Total Segments: ',len(segments))
                for segment in segments:
                    #print(segment.trace)
                    segment.translate_scale()
                    segment.interpolate_strokes()
                    feature_extraction.extract_all_features(segment)
                self.classify(segments)
                data_io.write_to_lg_files(inkml, inkml_key, segments,self.location.training_data_path)
                break
        else:
            for inkml_key in inkml_data:
                inkml = inkml_data[inkml_key]
                print('Starting Segmentation')
                segments = self.segmentor(inkml)
                print('Total Segments: ',len(segments))
                for segment in segments:
                    #print(segment.trace)
                    segment.translate_scale()
                    segment.interpolate_strokes()
                    feature_extraction.extract_all_features(segment)
                self.classify(segments)
                data_io.write_to_lg_files(inkml, inkml_key, segments,self.location.training_data_path)
                break


    def get_strokes_as_list(self,expression_trace):
        traces = []
        for symbol in expression_trace:
            for trace in expression_trace[symbol].traces:
                traces.append([trace])
        return traces

    def los_segmenter(self, node_tuple_list, inkml):
        # print("***************************")
        # print(node_tuple_list)
        # #should inkml have another data field called segments?
        group_sets = []
        stroke_groups = []

        id_to_points = {}
        for key in inkml.expression_trace:
            trace_group = inkml.expression_trace[key]
            for node_id in trace_group.trace_dict.keys():
                id_to_points[int(node_id)] = trace_group.trace_dict[node_id]
        #id_to_points now maps node ID to unpreprocessed strokes
        # print(id_to_points)
        for node_tuple in node_tuple_list:
            if len(group_sets) == 0:
                group_sets.append(set(node_tuple))
                # stroke_groups.append([id_to_points[int(node_tuple[0])], id_to_points[int(node_tuple[1])]])
            else:
                for i in range(len(group_sets)):
                    found = False
                    if set(node_tuple).intersection(group_sets[i]):
                        group_sets[i] = set(node_tuple).union(group_sets[i])
                        found = True

                if not found:
                    group_sets.append(set(node_tuple))


        all = set()
        for i in range(len(group_sets)):
            all = all.union(group_sets[i])
            group_sets[i] = list(group_sets[i])
            strokes = []
            for node in group_sets[i]:
                strokes.append(id_to_points[int(node)])
            stroke_groups.append(strokes)
        # print("ALL")
        # print(all)
        for id in id_to_points.keys():
            if str(id) not in all:
                print()
                soloset = [id]
                group_sets.append(soloset)
                stroke_groups.append([id_to_points[int(id)]])

        inkml.predicted_traces = stroke_groups
        inkml.predicted_groups = group_sets
        # print(group_sets)
        # print(stroke_groups)
            #
            # for key in inkml.expression_trace.trace_dict.keys():
            # 	trace_dict = inkml.expression_trace.trace_dict
            # 	if key in node_tuple:
            # 		inkml.predicted_trace



        index = inkml.ui
        segments = []
        i=0

        for i in range(len(stroke_groups)):
            segment = graph.Node(i, 'Node' + str(i), stroke_groups[i])
            segment.stroke_ids = group_sets[i]
            segments.append(segment)
            i+=1

        # for stroke_group in stroke_groups:
        #     segment = graph.Node(i,'Node'+str(i),stroke_group)
        #     segments.append(segment)
        #     i+=1
        print('Stroke Group length:',len(stroke_groups))
        return segments


    def baseline_segmentor(self,inkml):
        strokes = self.get_strokes_as_list(inkml.expression_trace)
        segments = []
        for i in range(len(strokes)):
            segment = graph.Node(i,'Node'+str(i),strokes[i])
            segments.append(segment)
        return segments

    def classify(self,segments):
        label_id_dict = {}
        model_info = joblib.load(self.location.training_data_path+'/model_kd_final_prediction.txt')
        model = model_info[0]
        le = model_info[1]
        for segment in segments:
            features = segment.features
            feature_list = []
            for key in sorted(features.keys()):
                if (key in features_dict.keys()):
                    feature_list.append(features[key])
            df = pd.DataFrame([feature_list], columns=[features_dict[key] for key in features_dict.keys()])
            df = df.fillna(0)
            df = df.replace([np.inf, -np.inf], 0)
            prediction = model.predict(df)
            prediction = le.inverse_transform(prediction)
            #Label (Predicted class)
            prediction = prediction[0]
            # print('----------------------------------------------------')
            # print('Predicted value : ',prediction)
            # print('Trace : ',segment.trace)
            # print('id : ',segment.id)
            segment.predicted = prediction
            if prediction in label_id_dict.keys():
                label_id_dict[prediction] += 1
            else:
                label_id_dict[prediction] = 1
            # Label id (Example : b_1)
            segment.label_id = str(segment.predicted)+'_'+str(label_id_dict[prediction])
        return None


