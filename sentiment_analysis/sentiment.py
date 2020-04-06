import pickle
import re
import pandas as pd
import numpy as np

model = pickle.load(open('sentiment_model.sav', 'rb'))

with pd.HDFStore('datascience.h5') as hdf:
    word_embeddings = pd.read_hdf(hdf, key='embeddings')

file = open("stop_words.txt", "r")
stop_words = file.readlines()
file.close()
stop_words = [word.strip('\n') for word in stop_words]


def text_to_sentiment(text):
    cleaned_text = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split()
    tokens = [token.lower() for token in cleaned_text if not token.lower() in stop_words]
    vectors = word_embeddings.reindex(tokens).dropna()
    if len(vectors) == 0:
        return "no valid words in text"
    predictions = model.predict_log_proba(vectors)
    return np.mean(predictions[:, 1] - predictions[:, 0])


print(text_to_sentiment('the of but'))
print(text_to_sentiment("@peter I really love that shirt at #Macy. http://bet.ly//WjdiW4"))

