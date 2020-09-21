import os 



ROOT = ""
TRAINING_DATA_PATH = ""


class Location:
	def __init__(self, data_path):
		#self.proj_root = root
		self.training_data_path = self.set_up_variables(data_path)
		self.inkml_path = self.training_data_path+'/inkml/'


	def set_up_variables(self, path_string):
		TRAINING_DATA_PATH = os.path.abspath(path_string)
		print('----------------------------')
		print(TRAINING_DATA_PATH)
		return TRAINING_DATA_PATH












