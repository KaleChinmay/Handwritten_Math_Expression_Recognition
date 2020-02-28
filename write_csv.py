"""
script to generate a csv file that lists all inkml files needed for classifier
"""
import csv
import bs4




def get_gt():
    gt_dict = {}
    with open('.\\Data\\trainingSymbols\\iso_GT.txt','r') as iso_gt:
        for line in iso_gt:
            temp_list = line.split(',')
            gt_dict[temp_list[0]] = temp_list[1]
    return gt_dict


def generate_dummy_data():
    gt_file = open("trainingSymbols/iso_GT.txt")
    with open("dummy_data.csv", "w") as dummy:
        for line in gt_file:
            gts = line.split(",")
            dummy.write(gts[0] + ", -, +, n, 9, 8, 7, =, (, ), 5\n")
    gt_file.close()


def generate_file_list():
    location = '.\\Data\\trainingSymbols\\'
    with open('.\\Data\\file_list.csv','w',newline='') as file_list:
        file_writer = csv.writer(file_list, delimiter=',')
        for i in range(85801):
            file_name = location + 'iso' + str(i) + '.inkml'
            file_writer.writerow([file_name])


def generate_meta_data():
    print('Hello')
    '''
    with open('.\\Data\\file_list.csv','r') as trace_file_list:
        with open('.\\Data\\file_list.csv','w') as meta_data:
            file_writer = csv.writer(meta_file, delimiter=',')
            data = csv.reader(csv_file,delimiter=',')
            gt_dict = get_gt()
            for row in data:
                file_name = row[0]
                with open(file_name,'r') as inkml_file:
                    xml_data = bs4.BeautifulSoup(inkml_file,'lxml')
                    ink = xml_data.ink
                    #Meta data for the inkml files
                    name = ink.find_all('annotation')[1].get_text()
                    ground_truth = gt_dict[name].strip()
                    trace = ink.trace
                    file_writer.writerow([file_name,name,ground_truth,trace])
    '''



