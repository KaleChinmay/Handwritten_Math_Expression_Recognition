"""
not part of parsing pipeline. generates list of inkml files on computer

"""
import sys
import os

def gen_file_list(inkml_path):
    dirs = os.listdir(inkml_path+"/inkml")
    dirs = [os.path.join(inkml_path+"/inkml", folder) for folder in dirs]
    with open(inkml_path+"/inkml_list.txt", "w") as inkml_list:
        for expression_folder in dirs:
            inkml_files = os.listdir(expression_folder)
            inkml_files = [os.path.join(expression_folder, files) for files in inkml_files]
            i = 0
            inkml_files_len = len(inkml_files)
            for inkml in inkml_files:
                i += 1
                print('Progress : ', i, ' of ', inkml_files_len)
                inkml_list.write(inkml+"\n")
def main():
    #file path should lead to the Train folder
    #so still need to add /inkml to file path
    filepath = sys.argv[1]
    gen_file_list(filepath)
if __name__ == "__main__":
    main()