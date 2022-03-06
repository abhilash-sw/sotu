# -*- coding: utf-8 -*-
# @Author: Abhilash
# @Date:   2022-03-03 22:13:11
# @Last Modified by:   Abhilash
# @Last Modified time: 2022-03-04 07:47:50

import os
import glob
import numpy as np

fls = glob.glob(os.path.join('speeches','*'))
fls.sort()

list_speeches = []
years = []
speeches = {}

for fl in fls:
	year = os.path.basename(fl)[:-4]
	years.append(year)
	fid = open(fl,'r',encoding="utf-8")
	spch = fid.read()
	fid.close()
	list_speeches.append(spch)
	speeches[year] = spch


################################
f_potus = open('potus.txt')
p_lines = f_potus.readlines()
f_potus.close()
p_names = {}
for p_line in p_lines:
    tmp1 = p_line.split(',')
    tmp2 = tmp1[1][1:-1].split('-')
    year_range = list(np.arange(int(tmp2[0]),int(tmp2[1])))
    if tmp1[0] in p_names.keys():
        p_names[tmp1[0]] = p_names[tmp1[0]] + year_range
    else:
        p_names[tmp1[0]] = year_range


p_speeches = {}

for p in p_names:
    p_speeches[p] = ''
    for y in p_names[p]:
        if str(y) not in speeches.keys():
        	continue
        p_speeches[p] = p_speeches[p] + speeches[str(y)]

list_p_speeches = []
presi = []

for k in p_speeches.keys():
	list_p_speeches.append(p_speeches[k])
	presi.append(k)



from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

####################### per year
count_vect = CountVectorizer(stop_words='english',token_pattern=r'[a-z]{3,}',max_df=0.09)
X_train_counts = count_vect.fit_transform(list_speeches)


tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

###### for a single row
vocab = count_vect.get_feature_names()
vocab = np.array(vocab)
#years = list(speeches.keys())

top_words = {}

for i in range(len(list_speeches)):
    tt = X_train_tfidf.getrow(i)
    itt = np.fliplr(np.argsort(tt.toarray()))[0]
    #print(years[i])
    #print(vocab[itt[:10]])
    top_words[years[i]] = vocab[itt]

####################### per president
count_vect = CountVectorizer(stop_words='english',token_pattern=r'[a-z]{3,}',max_df=0.08)
X_train_counts = count_vect.fit_transform(list_p_speeches)


tfidf_transformer = TfidfTransformer(norm='l2',smooth_idf=False)
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

###### for a single row
vocab = count_vect.get_feature_names()
vocab = np.array(vocab)
#years = list(speeches.keys())

top_words = {}

for i in range(len(list_p_speeches)):
    tt = X_train_tfidf.getrow(i)
    itt = np.fliplr(np.argsort(tt.toarray()))[0]
    #print(years[i])
    #print(vocab[itt[:10]])
    top_words[presi[i]] = vocab[itt]

