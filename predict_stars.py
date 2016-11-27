import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import pos_tag
from gensim import matutils,corpora
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV
from sklearn.ensemble import RandomForestClassifier as RFC
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import pickle
import re

#read the sampled csv file and drop the resaurant without reviews
def read_file(f):
	df = pd.read_csv(f)
	df = df.loc[:,['stars','reviews']]
	return df

f = 'id_stars_text.csv'
df = read_file(f)
print(df.head())

#remove stopwords and lemmatize data
lmtzr = WordNetLemmatizer()
negation = re.compile(r"(?:^(?:never|no|nothing|nowhere|noone|none|not|havent|hasnt|hadnt|cant|couldnt|shouldnt|wont|wouldnt|dont|doesnt|didnt|isnt|arent|aint)$)|n't",re.I)
clp = re.compile(r"^[.:;!?]$",re.I)

def extract_words_from_reviews(df):
    comments_tok = []
    for index, datapoint in df.iterrows():
        tokenized_words = word_tokenize(datapoint["reviews"].lower(),language='english')
        pos_tagged_words = pos_tag(tokenized_words)
        tokenized_words = ["_".join([lmtzr.lemmatize(i[0]),i[1]]) for i in pos_tagged_words if (i[0] not in stopwords.words("english") and len(i[0]) > 2)]
        comments_tok.append(tokenized_words)
    df["comment_tok"] = comments_tok
    return df

df = extract_words_from_reviews(df)
print(df.head())

#vectorize words
def vectorize_comments(df):
    d = corpora.Dictionary(df["comment_tok"])
    d.filter_extremes(no_below=2, no_above=0.8)
    d.compactify()
    corpus = [d.doc2bow(text) for text in df["comment_tok"]]
    corpus = matutils.corpus2csc(corpus, num_terms=len(d.token2id))
    corpus = corpus.transpose()
    return d, corpus

dictionary,corpus = vectorize_comments(df)
print (corpus.shape)

#Train Random forest classifer
def train_classifier(X,y):
    n_estimators = [100]
    min_samples_split = [2]
    min_samples_leaf = [1]
    bootstrap = [True]

    parameters = {'n_estimators': n_estimators, 'min_samples_leaf': min_samples_leaf,
                  'min_samples_split': min_samples_split}

    clf = GridSearchCV(RFC(verbose=1,n_jobs=4), cv=4, param_grid=parameters)
    clf.fit(X, y)
    return clf

X_train, X_test, y_train, y_test = cross_validation.train_test_split(corpus, df["stars"], test_size=0.02, random_state=17)
classifier = train_classifier(X_train,y_train)

print (classifier.best_score_, "----------------Best Accuracy score on Cross Validation Sets")
print (classifier.score(X_test,y_test))

