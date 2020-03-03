"""
script to generate a csv file that lists all inkml files needed for classifier
"""
import csv


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



def generate_features_table(data_object_list):
    location = '.\\Data\\'
    with open('.\\Data\\feature_list.csv','w',newline='') as feature_list:
        file_writer = csv.writer(feature_list, delimiter=',')
        for i in range(len(data_object_list)):
            row_list = []
            for key in sorted(data_object_list[i].features.keys()):
                row_list.append(data_object_list[i].features[key])
            row_list.append(data_object_list[i].gt)
            file_writer.writerow(row_list)


    


