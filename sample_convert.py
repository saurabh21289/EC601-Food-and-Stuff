#Sample and convert the json file to csv
#for the bussiness file, get 1 quater of all
#for the larger review file, get 1/10 samples
#combine the business_id, stars and text review together.
import json
import csv


f=open('yelp_academic_dataset_review.json','r')
a=f.readlines()
b=[]
for i in a[::10]:
	b.append(json.loads(i))
f.close()
f=open('yelp_academic_dataset_business.json','r')
c=f.readlines()
d=[]
for i in c[::4]:
	d.append(json.loads(i))
f.close()
result = [['business_id','stars','reviews']]#add header to the file
for i in d:
	#int(i['stars'])#convert star 1.5,2.5,3.5,4.5 to 1, 2, 3, 4
	result.append([i['business_id'],int(i['stars']),''])
for i in result:
	for j in b:
		if i[0]==j['business_id']:
			i[2]+=j['text']
with open('id_stars_text.csv','w') as f:
	datawriter = csv.writer(f)
	for row in result:
		if (row[2] !=''):
			datawriter.writerow(row)
#from the result, most restaurant has one review while part of restaurant
#doesn't have. Some restaurant has several reviews.
