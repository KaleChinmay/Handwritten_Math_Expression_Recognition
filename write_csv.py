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

def generate_meta_file(file):
    location = '.\\Data\\trainingSymbols\\'
    meta_file = open(location+file)
    file_writer = csv.writer(meta_file, delimiter=',')
    for i in range(171, 85801):
        file_name = location + 'iso' + str(i) + '.inkml'
        file_writer.writerow(location+file_name)