import os



def main():
	#Assuming code is running from Data folder
	inkml_location = './lpga_release-master/Data/Expressions/inkml/'
	lg_location = './lpga_release-master/Data/Expressions/lg_output/'


	sub_folder_list = ['expressmatch','extension','HAMEX1','HAMEX2','KAIST', 'MathBrush1','MathBrush2', 'MfrDB1','MfrDB2']
	#sub_folder_list = ['dummy']
	for folder in sub_folder_list:
		inkml_subfolder = inkml_location+folder
		inkml_file_list = os.listdir(inkml_subfolder)
		lg_subfolder = lg_location+folder+'_lg'
		for inkml_file in inkml_file_list:
			abs_inkml_file = inkml_subfolder+'/'+inkml_file
			lg_file = inkml_file.split('.')[0]+'.lg'
			abs_lg_file = lg_subfolder+'/'+lg_file
			command = 'crohme2lg.pl '+abs_inkml_file+' '+abs_lg_file
			os.system(command)
			print('Generated lg for : ',inkml_file)
		
		
		





if __name__=='__main__':
	main()