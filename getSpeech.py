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


year = []
counts = []
year_count = {}

for k in speeches.keys():
    year.append(k)
    counts.append(len(speeches[k]))
    year_count[k] = len(speeches[k])

counts = np.array(counts)
ind = np.argsort(counts)
ind = np.flip(ind,0)
counts = counts[ind]
year = np.array(year)
year = year[ind]

#########################################################
word_counts = {}

for y in speeches.keys():
    words = re.findall(r'\w+',speeches[y].lower())
    word_counts[y] = collections.Counter(words)


my_index = {}

for k in word_counts.keys():
    tmp_index = {}
    for wrd in word_counts[k].keys():
        Nwrd = 0
        for kk in word_counts.keys():
            Nwrd = Nwrd + word_counts[kk][wrd]

        tmp_index[wrd] = (word_counts[k][wrd])**1.6/Nwrd * sum(counts)/year_count[k]
    my_index[k] = tmp_index


top_words = {}

for k in my_index.keys():
    wrds = []
    cnts = []
    for wrd in my_index[k].keys():
        wrds.append(wrd)
        cnts.append(my_index[k][wrd])
    cnts = np.array(cnts)
    wrds = np.array(wrds)

    ind = np.argsort(cnts)
    ind = np.flip(ind,0)
    wrds = wrds[ind]
    top_words[k] = list(wrds)


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

################################

presi = []
counts = []
presi_count = {}
avg_counts = []

for k in p_speeches.keys():
    presi.append(k)
    counts.append(len(p_speeches[k]))
    avg_counts.append(len(p_speeches[k])/len(p_names[k]))
    presi_count[k] = len(p_speeches[k])

counts = np.array(counts)
ind = np.argsort(counts)
ind = np.flip(ind,0)
counts = counts[ind]
presi_orgin = presi
presi = np.array(presi)
presi = presi[ind]
avg_counts = np.array(avg_counts)
avg_counts_orgin = avg_counts
avg_counts = avg_counts[ind]

word_counts = {}

for p in p_speeches.keys():
    p_speech_tmp = re.sub(" \d+", " ",p_speeches[p])
    words = re.findall(r'\w+',p_speech_tmp.lower())
    word_counts[p] = collections.Counter(words)


my_index = {}

for k in word_counts.keys():
    tmp_index = {}
    for wrd in word_counts[k].keys():
        Nwrd = 0
        for kk in word_counts.keys():
            Nwrd = Nwrd + word_counts[kk][wrd]

        tmp_index[wrd] = (word_counts[k][wrd])**1.2/Nwrd * sum(counts)/presi_count[k]
    my_index[k] = tmp_index


top_words = {}

for k in my_index.keys():
    wrds = []
    cnts = []
    for wrd in my_index[k].keys():
        wrds.append(wrd)
        cnts.append(my_index[k][wrd])
    cnts = np.array(cnts)
    wrds = np.array(wrds)

    ind = np.argsort(cnts)
    ind = np.flip(ind,0)
    wrds = wrds[ind]
    top_words[k] = list(wrds)

fid_party = open('parites.txt')
party_lines = fid_party.readlines()
fid_party.close()

p_party = {}
party = []
for party_line in party_lines:
	tmp1 = party_line.split(',')
	p_party[tmp1[0]] = tmp1[-1][1]
	party.append(tmp1[-1][1])
#################
fig, ax = plt.subplots()    
fig.set_size_inches(12,16)
width = 0.2 # the width of the bars 
x = presi_orgin
y = avg_counts_orgin
ind = np.arange(len(y))  # the x locations for the groups

barlist = ax.barh(ind, y, width, color="blue",align='center', alpha=0.8)

for i,b_tmp in enumerate(barlist):
    if p_party[x[i]] == 'R':
        b_tmp.set_color('r')
    elif p_party[x[i]] == 'N':
        b_tmp.set_color('k')
    elif p_party[x[i]] == 'D':
    	b_tmp.set_color('b')

ax.set_yticks(ind+width/2)
ax.set_yticklabels(x, minor=False,fontweight='bold')
plt.title('Average word count at State of the Union address by POTUS \n and their Most Distinguishing words',fontweight='bold',fontsize=20)
plt.xlabel('Average word count')
ax.set_xlim([0,220000])

for i, v in enumerate(y):
    ax.text(v + 5000, i - 0.1, ','.join(top_words[presi_orgin[i]][:5]), color='black', fontweight='bold')
fig.savefig('test.png',dpi=300,bbox_inches='tight')
