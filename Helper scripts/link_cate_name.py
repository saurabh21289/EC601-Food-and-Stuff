#link categories with restaurant names
#will be stored as json file
import pandas as pd
import json

def read_files(f):
	df=pd.read_csv(f)
	df = df.loc[:,['categories','name','stars']]
	df = df.dropna()
	#loc first and then drop. Or it drops all data
	return df

f = 'business2.csv'
#change to whatever the file's name is
df = read_files(f)
print(df.head())
#The input of the dunction is df and the output should be a dictionary whose
#key is the category and the value is a list consists of name and stars of the
#restaurant
def link_categories_name(df):
	result = {}
	for index, data in df.iterrows():
		for category in eval(data[0]):
			#I used eval because the original data is like '['asdasd','asdad']', 
			#It's a string of list, eval helps give the list instead of string
			if category in result:
				result[category].append([data[1],data[2]])
				#As there are three elements in data, the first is categories
				#and the second and third is name and stars relatively
			else:
				result[category]=[[data[1],data[2]]]
	return result

name_cate=link_categories_name(df)

def sort_dict_by_stars(nc):
	for key in nc:
		nc[key]=sorted(nc[key],key=lambda star:star[1],reverse=True)
	return nc
#As we want to get the several restautant with highest stars, so I sort the 
#lists in the dictinary and let them in decending order

#Write to json file
new_dict=sort_dict_by_stars(name_cate)
with open('linked_cate_name.json','w') as outfile:
	for key in new_dict:
		json.dump({key:new_dict[key]},outfile)
		outfile.write('\n')
		#As we want to write to file line by line, so used this method
