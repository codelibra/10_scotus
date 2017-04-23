import logging, sys, pprint
import gensim
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

### Generating a training/background corpus from your own source of documents
from gensim.corpora import TextCorpus
from gensim.corpora import  MmCorpus
from gensim.corpora import  Dictionary

# gensim docs: "Provide a filename or a file-like object as input and TextCorpus will be initialized with a
# dictionary in `self.dictionary`and will support the `iter` corpus method. For other kinds of corpora, you only
# need to override `get_texts` and provide your own implementation."
import pickle

class MyCorpus(gensim.corpora.TextCorpus):
    def get_texts(self):
        for filename in self.input: # for each relevant file
            res = pickle.load(open( filename, "rb" ))
            res = " ".join(res)
            yield [res]

background_corpus = MyCorpus(c)




# Important -- save the dictionary generated by the corpus, or future operations will not be able to map results
# back to original words.
background_corpus.dictionary.save(
    "my_dict.dict")

MmCorpus.serialize("background_corpus.mm",
    background_corpus)  #  Uses numpy to persist wiki corpus in Matrix Market format. File will be several GBs.

### Working with persisted corpus and dictionary
#bow_corpus = MmCorpus("wiki_corpus.mm")  # Revive a corpus

#dictionary = Dictionary.load("wiki_dict.dict")  # Load a dictionary

### Transformations among vector spaces
from gensim.models import LsiModel, LogEntropyModel

logent_transformation = LogEntropyModel(background_corpus,
    id2word=background_corpus.dictionary)  # Log Entropy weights frequencies of all document features in the corpus


def func(doc):
    res = pickle.load(open( doc, "rb" ))
    res = " ".join(res)
    yield res

tokenize_func = func # The tokenizer used to create the Wikipedia corpus
document = "../data/circuit-scbd-mapped-files/X4AFJ8.p"
# First, tokenize document using the same tokenization as was used on the background corpus, and then convert it to
# BOW representation using the dictionary created when generating the background corpus.
bow_document = background_corpus.dictionary.doc2bow(tokenize_func(document))
# converts a single document to log entropy representation. document must be in the same vector space as corpus.
logent_document = logent_transformation[[bow_document]]

# Transform arbitrary documents by getting them into the same BOW vector space created by your training corpus
documents = ["../data/circuit-scbd-mapped-files/X443SJ.p", "../data/circuit-scbd-mapped-files/X40Q0P.p"]
bow_documents = (dictionary.doc2bow(tokenize_func(document)) for document in documents)  # use a generator expression because...
logent_documents = logent_transformation[bow_documents]
# ...transformation is done during iteration of documents using generators, so this uses constant memory

### Chained transformations
# This builds a new corpus from iterating over documents of bow_corpus as transformed to log entropy representation.
# Will also take many hours if bow_corpus is the Wikipedia corpus created above.
logent_corpus = MmCorpus(corpus=logent_transformation[background_corpus])

# Creates LSI transformation model from log entropy corpus representation. Takes several hours with Wikipedia corpus.
lsi_transformation = LsiModel(corpus=background_corpus, id2word=background_corpus.dictionary)

# Alternative way of performing same operation as above, but with implicit chaining
# lsi_transformation = LsiModel(corpus=logent_transformation[bow_corpus], id2word=dictionary,
#    num_features=400)

# Can persist transformation models, too.
logent_transformation.save("logent.model")
lsi_transformation.save("lsi.model")

### Similarities (the best part)
from gensim.similarities import Similarity

# This index corpus consists of what you want to compare future queries against
index_documents = ["../data/circuit-scbd-mapped-files/X443SJ.p", "../data/circuit-scbd-mapped-files/X40Q0P.p"]

# A corpus can be anything, as long as iterating over it produces a representation of the corpus documents as vectors.
corpus = (background_corpus.dictionary.doc2bow(tokenize_func(document)) for document in index_documents)

index = Similarity(corpus=lsi_transformation[logent_transformation[corpus]], num_features=400, output_prefix="shard")

print "Index corpus:"
pprint.pprint(documents)

print "Similarities of index corpus documents to one another:"
pprint.pprint([s for s in index])

query = "../data/circuit-scbd-mapped-files/X40PNC.p"
sims_to_query = index[lsi_transformation[logent_transformation[background_corpus.dictionary.doc2bow(tokenize_func(query))]]]
print "Similarities of index corpus documents to '%s'" % query
pprint.pprint(sims_to_query)

best_score = max(sims_to_query)
index = sims_to_query.tolist().index(best_score)
most_similar_doc = documents[index]
print "The document most similar to the query is '%s' with a score of %.2f." % (most_similar_doc, best_score)

def get_texts(self):
    for filename in self.input: # for each relevant file
        res = pickle.load(open( filename, "rb" ))
        res = " ".join(res)
        yield [res]

lsi_transformation.save("lsi.model")

documents_base = "../data/circuit-scbd-mapped-files//"
documents_list = ['X3C7IC.p','X3P5AQ.p',       'X40SL9.p',       'X445JB.p'   ,    'X4APLP.p'   ,    'XNT2KKII8BG0.p', 'X3C7JJ.p'  ,     'X3P6PG.p'  ,     'X40SLT.p'   ,    'X445L9.p'   ,    'X4ARHN.p'   ,    'XUI0EU003.p', 'X3C7KV.p', 'X3P6QR.p','X40SNF.p','X445NK.p','X4G4PI.p','XVNUS7.p']

documents =[documents_base +b for b in documents_list]
corpus = []
for filename in documents:
    res = pickle.load(open( filename, "rb" ))
    res = " ".join(res)
    res = [res]
    corpus.append(res)

from gensim import corpora
from gensim.models import TfidfModel
from gensim.models import LsiModel
from gensim.similarities import MatrixSimilarity

dictionary = corpora.Dictionary(corpus)
corpus_gensim = [dictionary.doc2bow(doc) for doc in corpus]

tfidf = TfidfModel(corpus_gensim)





corpus_tfidf = tfidf[corpus_gensim]
lsi = LsiModel(corpus_tfidf, id2word=dictionary, num_topics=50)

lsi_index = MatrixSimilarity(lsi[corpus_tfidf])
