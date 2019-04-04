import boto3
import nltk

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_selection import VarianceThreshold
from imblearn.over_sampling import SMOTE
from sklearn.naive_bayes import MultinomialNB

nltk.data.path.append('/tmp')
nltk.download('stopwords', download_dir='/tmp')

# # Data preparation
# ## Load data
titles = []
categories = []

# retrieve training articles
s3 = boto3.resource('s3')
obj = s3.Object('askcrowd', 'classify/titles.txt')
body = obj.get()['Body'].read().decode()
titles = body.split('\n')[:-1]
obj = s3.Object('askcrowd', 'classify/categories.txt')
body = obj.get()['Body'].read().decode()
categories = body.split('\n')[:-1]

# ## Split data
title_tr, title_te, category_tr, category_te = train_test_split(titles, categories)
title_tr, title_de, category_tr, category_de = train_test_split(title_tr, category_tr)

# # Data Preprocessing
# ## Vectorization of data
# Vectorize the data using Bag of words (BOW)
tokenizer = nltk.tokenize.RegexpTokenizer(r"\w+")
stop_words = nltk.corpus.stopwords.words("english")
vectorizer = CountVectorizer(tokenizer=tokenizer.tokenize, stop_words=stop_words)

vectorizer.fit(iter(title_tr))
Xtr = vectorizer.transform(iter(title_tr))

encoder = LabelEncoder()
encoder.fit(category_tr)
Ytr = encoder.transform(category_tr)

# ## Feature Reduction
# We can check the variance of the feature and drop them based on a threshold
selection = VarianceThreshold(threshold=0.001)
selection.fit(Xtr)
Xtr = selection.transform(Xtr)

# ## Sampling data
sm = SMOTE(random_state=42)
Xtr, Ytr = sm.fit_sample(Xtr, Ytr)
nb = MultinomialNB()
nb.fit(Xtr, Ytr)



def classify(post):

    test = vectorizer.transform(iter([post]))
    test = selection.transform(test)
    pred_final = nb.predict(test)
    return encoder.inverse_transform([pred_final[0]])[0]

