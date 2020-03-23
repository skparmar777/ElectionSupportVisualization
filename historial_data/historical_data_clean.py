import pandas as pd

df = pd.read_csv('countypres_2000-2016.csv')
df = df.drop(['state', 'state_po', 'FIPS', 'office', 'totalvotes', 'version'], axis=1)
rows_to_drop = df[(df['party'] == 'green') | (df['party'].isna())].index
df.drop(rows_to_drop, inplace=True)
df.to_csv('historical_data.csv', index=False)
