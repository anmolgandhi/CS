
#import test
import json
import re
from pandas.io.json import json_normalize
import pandas as pd
#a = test.test()
#final = a.to_json("Anmol Gandhi")
def getdata(name):
	with open(name) as f:
	    data = json.load(f)
	return(data)

