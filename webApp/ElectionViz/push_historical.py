import pandas as pd
import geopandas as gpd
from django.db import connection

from historical.models import Historical

df = pd.read_csv('data/historical_data.csv')
df_geo = gpd.read_file('data/illinois.json').set_index('COUNTY_NAM')

# should always find the lookup
def county_to_id(county):
    county = county.upper()
    if county == 'DE WITT':
        county = 'DEWITT'
    elif county == 'JO DAVIESS':
        county = 'JODAVIESS'
    if county not in df_geo.index:
        raise ValueError("missing county: {}".format(county))
    return df_geo.loc[county].DISTRICT

df['county'] = df['county'].apply(county_to_id)
for _, r in df.iterrows():
    query = "INSERT INTO historical VALUES ({}, '{}', '{}', {}, {})".format(r.year, r.party.title(), r.candidate, r.county, r.candidatevotes)
    with connection.cursor() as cursor:
        cursor.execute(query)
