import pandas as pd

# reading in voting data and removing unimportant columns
df = pd.read_csv('countypres_2000-2016.csv')
df = df.drop(['state_po', 'FIPS', 'office', 'totalvotes', 'version'], axis=1)

# removing voting results for green and undocumented candiates
party_rows_to_drop = df[(df['party'] == 'green') | (df['party'].isna())].index
df.drop(party_rows_to_drop, inplace=True)

# removing voting results not from IL
df = df[df['state'] == 'Illinois']

# no longer need the state column
df = df.drop(['state'], axis=1)

# exporting data frame as CSV
df.to_csv('historical_data.csv', index=False)


