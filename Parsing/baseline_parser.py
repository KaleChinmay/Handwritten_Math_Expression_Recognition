"""
__author__ = Lauren Cole, Chinmay Kale


"""

#one expression contains multiple nodes
#for each symbol there is one node object.
#take in a list of nodes in the order they were written. in the case where symbols were strated, but only partially completed before moving on to another symbol, we go in the order they were started (so id of first stroke)
#for each successive pair of nodes, we will create an edge object, defining the relationship to be "node2" is right of "node1"
#write this data to lg file, passing in node list, and edge list. these lists can exist inside the inkml data class, accessible through project instance
#write to lg will be in data_io, need to add lines for processing edges
import inkml_data
import graph
import data_io

def baseline_parser(inkml):
	#print(inkml.expression_trace)
	print(inkml.filename)
	keys = list(inkml.expression_trace.keys())
	#print(keys)
	#keys.sort(key = lambda x: min(list(inkml.expression_trace[x].trace_group_id))) 
	#print(keys)
	i=1
	graph_nodes = []
	for key in inkml.expression_trace.keys():
		truth_instance = inkml.expression_trace[key].truth_instance
		node = graph.Node(i,'Node'+str(i),truth_instance, truth_instance.split('_')[0])
		print('---------------------------')
		print(inkml.expression_trace[key].trace_group_id)
		print(inkml.expression_trace[key])
		graph_nodes.append(node)
		i+=1
	graph_nodes.sort(key = lambda x: x.min_x_point)
	edges = add_edges(graph_nodes)
	print("rdngsuigb;enoslkfcnse",path)
	raise e
	data_io.write_to_lg_files(inkml, nodes, edges, path)


def add_edges(graph_nodes):
	edges = []
	for i in range(len(graph_nodes)-1):
		current_node_id = graph_nodes[i].id
		edge = graph.Edge(graph_nodes[i],graph_nodes[i+1],'Right')
		edges.append(edge)

	for edge in edges:
		print('----Edge----')
		print(edge)
		print(edge.node1.gt+' - '+edge.rel+' - '+edge.node2.gt)


	return edges


