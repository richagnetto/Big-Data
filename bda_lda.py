
# coding: utf-8

# In[ ]:

from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import re
import string
from pyspark.mllib.clustering import LDA, LDAModel
from pyspark.mllib.linalg import Vectors
import os
from os import walk


# In[1]:

from pyspark import SparkContext
sc = SparkContext("local", "App Name")
cwd = os.getcwd()

# In[5]:

mydir = cwd + '/data/'
filenames = None
for dirpath, dirnames, filename in walk(mydir):
    filenames = filename
with open(mydir + 'data_aug.txt', 'w') as outfile:
    for fname in filenames:
        if fname.endswith('txt'):
            print fname
            with open(mydir + "/" + fname) as infile:
                for line in infile:
                    outfile.write(line)


# In[3]:

f = open(mydir + "data_aug.txt", 'r')
txt = f.read()

# In[5]:

emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""
 
regex_str = [
    #emoticons_str,
    #r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    #r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
 
    #r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    #r'(?:[\w_]+)', # other words
    #r'(?:\S)' # anything else
]
    
tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)
 
def tokenize(s):
    return tokens_re.findall(s)
 
def preprocess(s, lowercase=False):
    tokens = tokenize(s)
    tokens = [re.sub(r"(#|@|\s)*","", token) for token in tokens]
    
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens


# In[6]:

tokens = preprocess(txt, lowercase = True)
punctuation = list(string.punctuation)
en_stop = get_stop_words('en')
stop = stopwords.words('english') + punctuation + ['http', 'html', 'com', ':/','rt', 'via', "https", "com"]
terms_stop = [term for term in tokens if term not in stop and len(term) > 2 and not term in en_stop]
stopped_tokens = [i for i in terms_stop if not i in en_stop]

# In[8]:

p_stemmer = PorterStemmer()
texts = [p_stemmer.stem(i) for i in terms_stop]
print len(texts)

# In[22]:

#with open('processed_texts.txt', 'w') as fp:
#        fp.write(str(texts))


# In[34]:

#f = open(mydir + "processed_texts.txt", 'r')
#texts = f.read()
#texts = texts.split()
#len(texts)


# In[38]:

for i in range(len(texts)):
    if re.search('(hillary|hillari)', texts[i]):
        texts[i] = 'u\'clinton\''
    elif re.search('trump', texts[i]):
        texts[i] = 'u\'donald\''


# In[40]:

li = [texts]
dictionary = corpora.Dictionary(li)
corpus = [dictionary.doc2bow(text) for text in li]
dictionary.token2id
token_ids = [idx for token, idx in corpus[0]]


# In[42]:

parsedData = Vectors.dense([float(x) for x in token_ids])
parsedData = [parsedData]
parsedData = sc.parallelize(parsedData)
corpus = parsedData.zipWithIndex().map(lambda x: [x[1], x[0]]).cache()
num_clusters = 10
iters = 100
ldaModel = LDA.train(corpus, k=num_clusters, maxIterations = iters)
num_words_topic = 20
top = ldaModel.describeTopics(num_words_topic)


# In[44]:

id2token = {y:x for x, y in dictionary.token2id.items()}
token_to_ids = dictionary.token2id
mytopics = list()
for words_weight in top:
    tmp = list()
    for word_id, weight in zip(*words_weight):
        tmp.append((id2token[word_id], weight))
    mytopics.append(tmp)


# In[46]:

mydir = cwd + '/result/'
if not os.path.exists(mydir):
    os.mkdir(mydir)
for i in range(1, (len(mytopics)+1)):
    with open(mydir + 'Topic_{0}_{1}_TopWords.txt'.format(i, num_words_topic), 'w') as fp:
        fp.write('\n'.join('%s %s' % (x,j) for x,j in mytopics[i-1]))

