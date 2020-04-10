import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

# embeddings is a list of word vectors
# pos_words and neg_words store a list of positive and
# negative words respectively
with pd.HDFStore('datascience.h5') as hdf:
    embeddings = pd.read_hdf(hdf, key='embeddings')
    pos_words = pd.read_hdf(hdf, key='pos_words')
    neg_words = pd.read_hdf(hdf, key='neg_words')

pos_vectors = embeddings.reindex(pos_words).dropna()
neg_vectors = embeddings.reindex(neg_words).dropna()

vectors = pd.concat([pos_vectors, neg_vectors])
targets = np.array([1 for entry in pos_vectors.index] + [-1 for entry in neg_vectors.index])
labels = list(pos_vectors.index) + list(neg_vectors.index)

# Pre-determined this model performs the best
model = LogisticRegression(C=1.0, class_weight=None, dual=False, fit_intercept=True,
                           intercept_scaling=1, l1_ratio=None, max_iter=100,
                           multi_class='warn', n_jobs=-1, penalty='l2',
                           random_state=None, solver='warn', tol=0.0001, verbose=0,
                           warm_start=False)

# Fitting all data into the model
model.fit(vectors, targets)

pickle.dump(model, open('sentiment_model.sav', 'wb'))



