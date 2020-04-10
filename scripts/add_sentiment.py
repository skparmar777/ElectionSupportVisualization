import pandas as pd
from sentiment import text_to_sentiment
print("opened hdf")

df = pd.read_csv('tweets.csv')
df['sentiments'] = df['text'].apply(lambda x: text_to_sentiment(x)[0]) # 0th index has sentiment
df.to_csv('tweets_full.csv')
