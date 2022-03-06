# -*- coding: utf-8 -*-
# @Author: Abhilash
# @Date:   2022-03-03 22:13:11
# @Last Modified by:   Abhilash
# @Last Modified time: 2022-03-06 18:56:25

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
n_speeches = {}

for p in p_names:
    p_speeches[p] = ''
    n_speeches[p] = 0
    for y in p_names[p]:
        if str(y) not in speeches.keys():
        	continue
        p_speeches[p] = p_speeches[p] + speeches[str(y)]
        n_speeches[p] = n_speeches[p] + 1

list_p_speeches = []
presi = []

for k in p_speeches.keys():
	list_p_speeches.append(p_speeches[k])
	presi.append(k)

fid_party = open('parites.txt')
party_lines = fid_party.readlines()
fid_party.close()

p_party = {}
party = []
for party_line in party_lines:
    tmp1 = party_line.split(',')
    p_party[tmp1[0]] = tmp1[-1][1]
    party.append(tmp1[-1][1])

######################

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


## avg counts

avg_counts = []#{}
presi = []

for k in p_speeches.keys():
    #avg_counts[k] = len(p_speeches[k].split(' '))/n_speeches[k]
    avg_counts.append(len(p_speeches[k].split(' '))/n_speeches[k])
    presi.append(k)


## plotting
rcParams['font.family'] = 'serif'

fig, ax = plt.subplots()    
fig.set_size_inches(12,20)
width = 0.5 # the width of the bars 
x = presi
y = avg_counts
ind = np.arange(len(y))  # the x locations for the groups
                                                                                                                                            
barlist = ax.barh(ind, y, width, color="blue",align='center', alpha=0.8)

for i,b_tmp in enumerate(barlist):
    if p_party[x[i]] == 'R':
        b_tmp.set_color('#FF0000')
    elif p_party[x[i]] == 'N':
        b_tmp.set_color('k')
    elif p_party[x[i]] == 'D':
    	b_tmp.set_color('#0015BC')
                                                                                                                                            
ax.set_yticks(ind)
ax.set_yticklabels(x, minor=False,fontweight='bold',fontsize=18)
plt.title('Average word count at State of the Union address by POTUS \n and their Most Distinguishing words',fontweight='bold',fontsize=20)
plt.xlabel('Average word count',fontsize=18)
ax.set_xlim([0,38000])
ax.set_ylim([-1,len(x)])

xtck = ax.get_xticks()
ax.set_xticklabels(xtck,minor=False,fontsize=16)
                                                                                                                                            
for i, v in enumerate(y):
    ax.text(v + 500, i - 0.1, ', '.join(top_words[presi[i]][:5]), color='black', fontweight='bold',fontsize=13)

fig.savefig('test_4.png',dpi=300,bbox_inches='tight')
