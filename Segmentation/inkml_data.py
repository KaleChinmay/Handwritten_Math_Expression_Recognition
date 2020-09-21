

class InkMLData:
	filename = ''
	category = ''
	expression = ''
	ui = ''
	writer = ''
	gt = ''

	truth_dict= {}
	expression_trace = None
	predicted_trace = []
	predicted_groups =[]
	path = ''
	los_graph = None
	features_vectors = {}
	def __init__(self):
		pass

	def __str__(self):
		return "Object :-" \
			+"\ncategory = "+self.category \
			+"\nexpression = "+self.expression \
			+"\nui = "+self.ui \
			+"\nwriter = "+self.writer \
			+"\nexpression_trace = "+self.expression_trace.__str__()\
			+"\npath = " + self.path




class TraceGroup:
	#Example : tan, cos
	truth_label = ''
	#Example : tan_1, tan_2, cos_1
	truth_instance = ''
	traces = []
	trace_dict = {}
	norm_trace_dict = {}
	def __init__(self):
		pass

	def __str__(self):
		return "Object :- " \
			+"\ntruth_label"+self.truth_label \
			+"\ntruth_instance"+self.truth_instance \
			+"\ntraces"+str(self.traces)


'''
class Stroke:

    def __init__(self):
        self.points = []


    def addPoints(self):



class Points:
	x = 0
	y = 0
	def __init__(self,x,y):
		self.x = x
		self.y = y

'''


