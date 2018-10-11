# -*- coding: utf-8 -*-
# @Author: Abhilash Sarwade
# @Date:   2018-10-03 20:25:03
# @Last Modified by:   Abhilash Sarwade
# @Last Modified time: 2018-10-11 07:50:17

from bs4 import BeautifulSoup
import numpy as np
import urllib3
import collections
import matplotlib.pyplot as plt
import re

fid = open('State of the Union Addresses of the Presidents of the United States.html','rb')
l = fid.read()

http = urllib3.PoolManager()
# soup = BeautifulSoup(l)

# tas = soup.find_all('table')

# table = tas[11]

# rows = table.find_all('tr')

adrs = re.findall(r'<td align="center" class="ver12"><a href="(.*?)">(.*?)</a>',str(l))

speeches = {}

for adr in adrs:
    url = adr[0]
    response = http.request('GET', url,retries=10)
    #if response.status != 200:
    #    sys.exit('Could not request the url')
    soup = BeautifulSoup(response.data)
    if not soup.find('span',{'class':'displaytext'}):
        continue
    spch = soup.find('span',{'class':'displaytext'}).get_text()
    speeches[adr[1]] = spch

list_speeches = []
years = []
for k in speeches.keys():
    years.append(k)
    spch_tmp = speeches[k]
    spch_tmp = re.sub(r"([\w]+['][\w]+)",'',spch_tmp)
    list_speeches.append(spch_tmp)

years[41] = '1973'
#years[65] = '1956'
years.pop(65)
list_speeches.pop(65)

############# Only considering years after 1950
years = years[:70]
list_speeches = list_speeches[:70]


#######################
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

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



################################
f_potus = open('potus.txt')
p_lines = f_potus.readlines()
f_potus.close()
p_names = {}
years_p = {}

for p_line in p_lines:
    tmp1 = p_line.split(',')
    tmp2 = tmp1[1][1:-1].split('-')
    year_range = list(np.arange(int(tmp2[0]),int(tmp2[1])))
    if tmp1[0] in p_names.keys():
        p_names[tmp1[0]] = p_names[tmp1[0]] + year_range
        for yyy in year_range:
            years_p[yyy] = tmp1[0]
    else:
        p_names[tmp1[0]] = year_range
        for yyy in year_range:
            years_p[yyy] = tmp1[0]

fid_party = open('parites.txt')
party_lines = fid_party.readlines()
fid_party.close()

p_party = {}
party = []
for party_line in party_lines:
    tmp1 = party_line.split(',')
    p_party[tmp1[0]] = tmp1[-1][1]
    party.append(tmp1[-1][1])
##################

years = np.array(years)
list_speeches = np.array(list_speeches)

ind = np.argsort(years)
years = years[ind]
list_speeches = list_speeches[ind]

avg_counts = []
for spch in list_speeches:
    avg_counts.append(len(spch))

avg_counts = np.array(avg_counts)

xx = []

for yyy in years:
    xx.append(years_p[int(yyy)])

xx = np.array(xx)

list_presi = []
for yyy in years:
    list_presi.append(years_p[int(yyy)].split(' ')[-1]+' ('+str(yyy)+')')

list_presi[28] = 'Carter (1977)'
list_presi[29] = 'Carter (1978)'
list_presi[30] = 'Carter (1979)'
list_presi[31] = 'Carter (1980)'


list_presi = np.array(list_presi)

fig, ax = plt.subplots()    
fig.set_size_inches(12,18)
width = 0.2 # the width of the bars 

x = list_presi
y = avg_counts
ind = np.arange(len(y))  # the x locations for the groups

barlist = ax.barh(ind, y, width, color="blue",align='center', alpha=0.8)

ax.set_ylim(-1,71)

for i,b_tmp in enumerate(barlist):
    if p_party[xx[i]] == 'R':
        b_tmp.set_color('r')
    elif p_party[xx[i]] == 'N':
        b_tmp.set_color('k')
    elif p_party[xx[i]] == 'D':
    	b_tmp.set_color('b')

ax.set_yticks(ind+width/2)
ax.set_yticklabels(x, minor=False,fontweight='bold')
ax.set_title('Average word count at State of the Union address by POTUS \n and their Most Distinguishing words',fontweight='bold',fontsize=20)
ax.set_xlabel('Average word count')
ax.set_xlim([0,360000])

for i, v in enumerate(y):
    ax.text(v + 5000, i - 0.1, ','.join(top_words[years[i]][:5]), color='black', fontweight='bold')
fig.savefig('test_3.png',dpi=300,bbox_inches='tight')