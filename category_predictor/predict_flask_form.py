"""Use the output from the CategoryPredictor MRJob to predict the
category of text. This uses a simple naive-bayes model - see
http://en.wikipedia.org/wiki/Naive_Bayes_classifier for more details.
"""

from __future__ import with_statement

from flask import Flask, render_template, flash, request, Markup
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

from random import randint

import os
import folium
import pandas as pd

import numpy as np

import math
import sys

import category_predictor

# App config.
# DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

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

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    input_file = 'category_predictor_merged.json'
    form = ReusableForm(request.form)
    print form.errors
    if request.method == 'POST':
        food=request.form['food']
        print food
        text = food
        guesses = ReviewCategoryClassifier(input_file).classify(text)
        best_guesses = sorted(guesses.iteritems(), key=lambda (_, prob): prob, reverse=True)[0:8]
        locations(best_guesses)
        del list1[:]
        del values1[:]
        if form.validate():
            for guess, prob in best_guesses:
                data = 'Category: "%s" - %.2f%% chance' % (guess, prob * 100)
                print str(data)
                list1.append(guess)
                values1.append(round(prob * 100,2)) #round(prob*100,2), '%'
                flash('Predicted ' + str(data))
        else:
                flash('All the form fields are required. ')

    # locations()
    return render_template('index.html', form=form)

@app.route("/chart")
def chart():
    labels = ["January","February","March","April","May","June","July","August"]
    values = [10,9,8,7,6,4,7,8]
    colors = [ "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC"  ]
    return render_template('chart.html', set=zip(values1, list1, colors))

@app.route("/map")
def map():
    return render_template('map.html')


def map_locations(lons, lats, names, stars, full_address):

    locations = list(zip(lats, lons))
    popups = ['{},\n {},\n Rating = {}'.format(name, full_address, stars) for name, full_address, stars in zip(names, full_address, stars)]

    from folium.plugins import MarkerCluster

    m = folium.Map(location=[np.mean(lats), np.mean(lons)],
                      tiles='Cartodb Positron', zoom_start=3)

    m.add_child(MarkerCluster(locations=locations, popups=popups))

    m.save('templates/map.html')
    print "Done."

def locations(best_guesses):
    df = pd.read_csv('../../dataset/business.csv',  low_memory=False)
    df_test = df[df['stars'] > 3.0]
    df2 = df_test[['latitude', 'longitude', 'name', 'stars', 'full_address']]
    lons = df2.head(10).longitude.tolist()
    lats = df2.head(10).latitude.tolist()
    names = df2.head(10).name.tolist()
    stars = df2.head(10).stars.tolist()
    full_address = df2.head(10).full_address.tolist()
    print "Best guess = " + best_guesses[0][0]
    map_locations(lons, lats, names, stars, full_address)

app.run(host='0.0.0.0', port=5002)
