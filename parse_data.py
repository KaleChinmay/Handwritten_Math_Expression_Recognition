from character_data import Character_Data
import bs4
import csv



def get_gt():
    gt_dict = {}
    with open('.\\Data\\trainingSymbols\\iso_GT.txt','r') as iso_gt:
        for line in iso_gt:
            temp_list = line.split(',')
            gt_dict[temp_list[0]] = temp_list[1]
    return gt_dict



def remove_dups(data):
    for i in range(len(data.trace)):
        for j in range(len(data.trace[i])):
            point = data.trace[i][j].strip()
            point = point.split(' ')
            for k in range(2):
                point[k] = int(point[k])
            data.trace[i][j] = point
    return data



def parse_data():
	with open('.\\Data\\file_list.csv','r') as trace_file_list:
		data = csv.reader(trace_file_list,delimiter=',')
		gt_dict = get_gt()
		data_obj_list = []
		for row in data:
			file_name = row[0]
			with open(file_name,'r') as inkml_file:
				xml_data = bs4.BeautifulSoup(inkml_file, 'lxml')
				ink = xml_data.ink
                #Meta data for the inkml files
				name = ink.find_all('annotation')[1].get_text()
				ground_truth = gt_dict[name].strip()
				trace = ink.trace
				data_obj = Character_Data()
				data_obj.id = name
				data_obj.gt = gt_dict[name].strip()
				temp_content = [[content.strip() for content in trace.contents] for trace in ink.find_all('trace')]
				x = [[a.split(',') for a in trace][0] for trace in temp_content]
				data_obj.trace = x
				data_obj = remove_dups(data_obj)
				data_obj_list.append(data_obj)
			print(data_obj)
			break
	return data_obj_list
