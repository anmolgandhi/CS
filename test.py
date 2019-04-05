

import Data_Sources
import json


class test:
	
	def __init__(self):
		self.mapping = {"Anmol Gandhi": "1245"}
		self.a = Data_Sources.Data_Sources()
		self.twitter_obj = self.a.Twitter(["WSJ","FinancialTimes"])
		self.salesfore_obj = self.a.salesforce()
		with open('client.json') as json_file:  
		    self.personal_info_obj = json.load(json_file)

		self.main_obj = {"1245": {"Personal" :self.personal_info_obj,"Twitter": self.twitter_obj,"salesforce": self.salesfore_obj}}

	def to_json(self,name):
		self.id = self.mapping[name]
		self.main_obj = self.main_obj[self.id]
		with open("final_data.json", "w") as final:
			json.dump(self.main_obj, final, indent=4,ensure_ascii=False)
		print("Success!!!")
