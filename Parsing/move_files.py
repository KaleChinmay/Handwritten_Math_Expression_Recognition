from os import listdir
from os.path import isfile, join

import os
import shutil

# Move a file by renaming it's path

#MfrDB3088.lg

def main():
    path = '/home/chinmay/Desktop/Parsing/Parsing/Data'
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    other_path = '/home/chinmay/Desktop/Parsing/Parsing/lpga_release-master/output/GtLGs'
    onlyfilesBad = [f for f in listdir(other_path) if isfile(join(other_path, f))]
    print(onlyfiles)
    print(onlyfilesBad)

    onlyfiles = set(onlyfiles)
    for file in onlyfilesBad:
        if file not in onlyfiles:
            #os.rename(other_path+'/'+file, '/home/chinmay/Desktop/Parsing/Parsing/lpga_release-master/output/qwerty/'+file)
            print(file)
main()