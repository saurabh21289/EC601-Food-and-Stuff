"""Use the output from the CategoryPredictor MRJob to predict the
category of text. This uses a simple naive-bayes model - see
http://en.wikipedia.org/wiki/Naive_Bayes_classifier for more details.
"""

from __future__ import with_statement

from flask import Flask, render_template, flash, request, Markup
from flask import jsonify

from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask_googlemaps import Map
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons

from random import randint

import json
import re
import os
import folium
import pandas as pd

import numpy as np

import math
import sys
import requests
import json
import category_predictor

# App config.
# DEBUG = True
app = Flask(__name__, template_folder="templates")
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
# you can set key as config
app.config['GOOGLEMAPS_KEY'] = "AIzaSyAXozhGr5tKlXS4l8FRri4CX36aTviOzXk"

# you can also pass key here
GoogleMaps(app, key="AIzaSyAXozhGr5tKlXS4l8FRri4CX36aTviOzXk")

class ReusableForm(Form):
    food = TextField('Food:', validators=[validators.required()])



class ReviewCategoryClassifier(object):
	"""Predict categories for text using a simple naive-bayes classifier."""

	@classmethod
	def load_data(cls, input_file):
		"""Read the output of the CategoryPredictor mrjob, returning
		total category counts (count of # of reviews for each
		category), and counts of words for each category.
		"""

		job = category_predictor.CategoryPredictor()

		category_counts = None
		word_counts = {}

		with open(input_file) as src:
			for line in src:
				category, counts = job.parse_output_line(line)

				if category == 'all':
					category_counts = counts
				else:
					word_counts[category] = counts

		return category_counts, word_counts

	@classmethod
	def normalize_counts(cls, counts):
		"""Convert a dictionary of counts into a log-probability
		distribution.
		"""
		total = sum(counts.itervalues())
		lg_total = math.log(total)

		return dict((key, math.log(cnt) - lg_total) for key, cnt in counts.iteritems())

	def __init__(self, input_file):
		"""input_file: the output of the CategoryPredictor job."""
		category_counts, word_counts = self.load_data(input_file)

		self.word_given_cat_prob = {}
		for cat, counts in word_counts.iteritems():
			self.word_given_cat_prob[cat] = self.normalize_counts(counts)

		# filter out categories which have no words
		seen_categories = set(word_counts)
		seen_category_counts = dict((cat, count) for cat, count in category_counts.iteritems() \
										if cat in seen_categories)
		self.category_prob = self.normalize_counts(seen_category_counts)

	def classify(self, text):
		"""Classify some text using the result of the
		CategoryPredictor MRJob. We use a basic naive-bayes model,
		eg, argmax_category p(category) * p(words | category) ==
		p(category) * pi_{i \in words} p(word_i | category).

		p(category) is stored in self.category_prob, p(word | category
		is in self.word_given_cat_prob.
		"""
		# start with prob(category)
		lg_scores = self.category_prob.copy()

		# then multiply in the individual word probabilities
		# NOTE: we're actually adding here, but that's because our
		# distributions are made up of log probabilities, which are
		# more accurate for small probabilities. See
		# http://en.wikipedia.org/wiki/Log_probability for more
		# details.
		for word in category_predictor.words(text):
			for cat in lg_scores:
				cat_probs = self.word_given_cat_prob[cat]

				if word in cat_probs:
					lg_scores[cat] += cat_probs[word]
				else:
					lg_scores[cat] += cat_probs['UNK']

		# convert scores to a non-log value
		scores = dict((cat, math.exp(score)) for cat, score in lg_scores.iteritems())

		# normalize the scores again - this isnt' strictly necessary,
		# but it's nice to report probabilities with our guesses
		total = sum(scores.itervalues())
		return dict((cat, prob / total) for cat, prob in scores.iteritems())

list1 = []
values1 =[]
lats = []
lons = []
stars = []
address = []
names = []
user_data = []

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    get_my_ip()
    input_file = 'category_predictor_merged_without_restaurants.json'
    form = ReusableForm(request.form)
    print form.errors
    if request.method == 'POST':
        food=request.form['food']
        print food

        result={}
	with open('../../dataset/linked_cate_name.json','r') as infile:
		for lines in infile.readlines():
			temp = json.loads(lines)
			result[temp[0]]=temp[1]
        
        text = food
        guesses = ReviewCategoryClassifier(input_file).classify(text)
        best_guesses = sorted(guesses.iteritems(), key=lambda (_, prob): prob, reverse=True)[0:5]
        #locations(best_guesses)
        print "Best guess = " + best_guesses[0][0]       
        if form.validate():
            del list1[:]
            del values1[:]
            del lons[:]
            del stars[:]
            del address[:]
            del names[:]      
            for guess, prob in best_guesses:
                #result[guess][0][2]=(result[guess][0][2]).encode('utf-8')
                result[guess][0][2]=(result[guess][0][2]).encode('ascii', 'ignore')
                #temp = ', '.join(str(item) for item in result[guess][0])
                temp = []
                for item in result[guess][0]:
                    temp.append(item)
                
                print "Latitude= ", temp[3]
                print "Longitude = ", temp[4]
                names.append(temp[0])
                stars.append(temp[1])
                address.append(temp[2])
                lats.append(temp[3])
                lons.append(temp[4])
		#temp = re.sub(r'\n','',temp)
		print str(temp[0]), round(prob*100,2),'%'
                #data = 'Category: "%s" - %.2f%% chance' % (guess, prob * 100)
                #print str(data)
		data = []
		#i = 0
		#for i in temp[0:30]:
                #    if i != ',':
                #        data.append(i)
                #list1.append(str(temp[0:15]))
                #data = ''.join(data)
		#stars = temp[1]
                list1.append(str(temp[0]))
                value = round(prob * 100,2)
                values1.append(value) #round(prob*100,2), '%'
                               
                flash('Suggested Restaurant is "' + str(temp[0]) + '" with a Rating of ' + str(temp[1]) + ' stars.' + ' It is located at '+ '"' + str(temp[2]) + '"', str(best_guesses[0][0]) + ' Food')
        else:
                flash('All the form fields are required.', 'Error')

    #map_locations(lats, lons, names, stars, address)
                #fullmap(lats, lons, names, stars, address)
    return render_template('index.html', form=form)

@app.route("/chart")
def chart():
    labels = ["January","February","March","April","May","June","July","August"]
    values = [10,9,8,7,6,4,7,8]
    colors = [ "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC"  ]
    return render_template('chart.html', set=zip(values1, list1, colors))

#@app.route("/ip", methods=["GET"])
def get_my_ip():
    # print "IP Address = " + request.remote_addr
    # return "Hi there!"
    ip_address = request.remote_addr
    # print "ip = " + ip_address
    r = requests.get('http://freegeoip.net/json/' + str(ip_address))
    #print r.text

    user_info = json.loads(r.text)
    for key, value in user_info.items():
        user_data.append(value)
    #print 'Zip = ', user_data["zip_code"]
    #print 'Lat = ', user_data["latitude"]
    #print 'Lon = ', user_data["longitude"]
    #return jsonify({'ip': request.remote_addr}), 200
    #return r.text, r.status_code, r.headers.items()

@app.route("/map")
#def map():
#    return render_template('fullmap.html')
def fullmap():
    #lats, lons, names, stars, address
    #print "Lat_test= " + str(lats[0])
    #for i in user_data:
    #    print i
    #print "Lat_user =" + str(user_data['latitude'])
    print "User Lat= ", str(user_data[7])
    print "Usre Lon= ", str(user_data[5])
    fullmap = Map(
        identifier="fullmap",
        varname="fullmap",
        style=(
            "height:100%;"
            "width:100%;"
            "top:0;"
            "left:0;"
            "position:absolute;"
            "z-index:200;"
        ),
        lat=np.mean(lats),
        lng=np.mean(lons),
        markers=[
            {
                'icon': '//maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat': str(lats[0]),
                'lng': str(lons[0]),
                #'infobox': "Hello I am <b style='color:green;'>GREEN</b>!"
                'infobox': str(names[0]) + ', ' + str(stars[0]) + ', ' + str(address[0])
            },
            {
                'icon': '//maps.google.com/mapfiles/ms/icons/blue-dot.png',
                'lat': str(lats[1]),
                'lng': str(lons[1]),
                'infobox': str(names[1]) + ', ' + str(stars[1]) + ', ' + str(address[1])
            },
            {
                'icon': icons.dots.blue,
                'title': 'Click Here',
                'lat': str(lats[2]),
                'lng': str(lons[2]),
                'infobox': str(names[2]) + ', ' + str(stars[2]) + ', ' + str(address[2])
##                'infobox': (
##                    "Hello I am <b style='color:#ffcc00;'>YELLOW</b>!"
##                    "<h2>It is HTML title</h2>"
##                    "<img src='//placehold.it/50'>"
##                    "<br>Images allowed!"
##                )
            },
            {
                'icon': '//maps.google.com/mapfiles/ms/icons/blue-dot.png',
                'lat': str(lats[3]),
                'lng': str(lons[3]),
                'infobox': str(names[3]) + ', ' + str(stars[4]) + ', ' + str(address[4])
            },
            {
                'icon': '//maps.google.com/mapfiles/ms/icons/blue-dot.png',
                'lat': str(lats[4]),
                'lng': str(lons[4]),
                'infobox': str(names[4]) + ', ' + str(stars[4]) + ', ' + str(address[4])
            },
            {
                'icon': '//maps.google.com/mapfiles/ms/icons/yellow-dot.png',
                'lat': str(user_data[7]),
                'lng': str(user_data[5]),
                'infobox': ("<b>You are here! </b>" + str(user_data[0]) + ', ' + str(user_data[1]) + ', ' + str(user_data[8]) + ', ' + str(user_data[10]))
            },
            
        ],
        cluster = True,
        cluster_gridsize = 10,
        # maptype = "TERRAIN",
        zoom="2"
    )
    return render_template('example_fullmap.html', fullmap=fullmap)


##def mapview():
##    mymap = Map(
##        identifier="cluster-map",
##        lat=37.4419,
##        lng=-122.1419,
##        markers=[{'lat': 37.4419, 'lng': -122.1419}, {'lat': 37.4500, 'lng': -122.1419}, {'lat': 36.4419, 'lng': -120.1419}],
##        cluster = True,
##        cluster_gridsize=10
##    )
##    return render_template('clustermap.html', clustermap=clustermap)

def map_locations(lats, lons, names, stars, full_address):

    locations = list(zip(lons, lats))
    popups = ['{},\n {},\n Rating = {}'.format(name, full_address, stars) for name, full_address, stars in zip(names, full_address, stars)]

    for i in locations:
        print i
    
    from folium.plugins import MarkerCluster

    m = folium.Map(location=[np.mean(lons), np.mean(lats)],
                      tiles='Cartodb Positron', zoom_start=2)

    m.add_child(MarkerCluster(locations=locations, popups=popups))

    m.save('templates/map.html')
    print "Done."

##def locations(best_guesses):
##    df = pd.read_csv('../../dataset/business.csv',  low_memory=False)
##    df_test = df[df['stars'] > 3.0]
##    df2 = df_test[['latitude', 'longitude', 'name', 'stars', 'full_address']]
##    lons = df2.head(10).longitude.tolist()
##    lats = df2.head(10).latitude.tolist()
##    names = df2.head(10).name.tolist()
##    stars = df2.head(10).stars.tolist()
##    full_address = df2.head(10).full_address.tolist()
##    print "Best guess = " + best_guesses[0][0]
##    map_locations(lons, lats, names, stars, full_address)

app.run(host='0.0.0.0', port=5000, use_reloader=True)
