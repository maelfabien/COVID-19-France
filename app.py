import streamlit as st

# Base packages
import pandas as pd
import numpy as np
import datetime

# Visualization
import matplotlib.pyplot as plt
import altair as alt

# Find coordinates
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="myapp2")
import time

# Plot static maps
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Plot interactive maps with Bokeh
import geopandas as gpd
from shapely import wkt
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, ColumnDataSource
import json
from bokeh.models import HoverTool

st.title("COVID-19 in France")

st.write("An analysis of COVID-19 cases in France, day by day, department by department.")

df = pd.read_csv("https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv")
df['date'] = pd.to_datetime(df['date'])
df = df[['date', 'granularite', 'maille_code', 'maille_nom', 'cas_confirmes', 'deces', 'reanimation']]
df = df[df['granularite'] == 'departement']


date_time_str = '2020-01-24'
base = datetime.datetime.strptime(date_time_str, '%Y-%m-%d')

date_list = [base + datetime.timedelta(days=x) for x in range(56)]
list_maille_code = np.unique(df['maille_code'])

for date in date_list:
    for dep in list_maille_code:
        if len(df[(df['date'] == date) & (df['maille_code'] == dep)]) == 0:
            if date == '2020-01-24':
                if list(df[(df['maille_code'] == dep) & (df['date'] == date)]['cas_confirmes']) == [] and list(df[(df['maille_code'] == dep) & (df['date'] == date)]['deces']) == [] and list(df[(df['maille_code'] == dep) & (df['date'] == date)]['reanimation']) == [] :
                    df = df.append({'date':date, 'granularite':'departement', 'maille_code': dep, 'maille_nom':list(df[df['maille_code'] == dep]['maille_nom'])[0], 'cas_confirmes':0, 'deces':0, 'reanimation':0}, ignore_index=True)
            else:
                yesterday = date - datetime.timedelta(days=1)
                if list(df[(df['maille_code'] == dep) & (df['date'] == yesterday)]['cas_confirmes']) == [] and list(df[(df['maille_code'] == dep) & (df['date'] == yesterday)]['deces']) == [] and list(df[(df['maille_code'] == dep) & (df['date'] == yesterday)]['reanimation']) == [] :
                    df = df.append({'date':date, 'granularite':'departement', 'maille_code': dep, 'maille_nom':list(df[df['maille_code'] == dep]['maille_nom'])[0], 'cas_confirmes':0, 'deces':0, 'reanimation':0}, ignore_index=True)
                else:
                    df = df.append({'date':date, 'granularite':'departement', 'maille_code': dep, 'maille_nom':list(df[df['maille_code'] == dep]['maille_nom'])[0], 'cas_confirmes':list(df[(df['maille_code'] == dep) & (df['date'] == yesterday)]['cas_confirmes'])[0], 'deces':list(df[(df['maille_code'] == dep) & (df['date'] == yesterday)]['deces'])[0], 'reanimation': list(df[(df['maille_code'] == dep) & (df['date'] == yesterday)]['reanimation'])[0]}, ignore_index=True)
            
df = df.sort_values(by=['date', 'maille_code'])

st.write(df)

st.markdown("---")
st.subheader("Evolution of the cases per department")

total_days = list(np.unique(df['date'].apply(lambda x: str(x))))

department = st.selectbox("Select a department", list(np.unique(df['maille_nom'])))
start_date = st.selectbox("Select a start date", total_days)
end_date = st.selectbox("Select an end date", total_days, len(total_days)-1)

df_restrict = df[(df['maille_nom'] == department) & (df['date'] >= start_date) & (df['date'] <= end_date)]

chart = alt.Chart(df_restrict).mark_line().encode(
    x='date:T',
    y='cas_confirmes:Q'
).properties(title="Number of cases in " + department, height=400, width=600)

st.write(chart)

st.markdown("---")
st.subheader("Map of the cases in France")

df2 = pd.read_csv("coordinates_region.csv")

def find_lat(x):
    return float(df2[df2['Region'] == x]['Latitude'])

def find_long(x):
    return float(df2[df2['Region'] == x]['Longitude'])

df['latitude'] = df['maille_nom'].apply(lambda x: find_lat(x))
df['longitude'] = df['maille_nom'].apply(lambda x: find_long(x))

MAX_LONGITUDE = 10
MIN_LONGITUDE = -5
MIN_LATITUDE = 35

# Zoom on continental France
df_france = df[(df['longitude'] < MAX_LONGITUDE) & (df['longitude'] > MIN_LONGITUDE) & (df['latitude']>MIN_LATITUDE)]
df_dep = df_france[df_france['granularite'] == "departement"]
df_dep = df_dep.fillna(0)

shapefile = 'ne_110m_admin_0_countries.shp'

#Read shapefile using Geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
#Rename columns.
gdf.columns = ['country', 'country_code', 'geometry']
gdf = gdf[gdf['country']=="France"]
# Keep Only continental France and Corsica
gdf['geometry'][43] = wkt.loads('MULTIPOLYGON (((6.186320428094177 49.46380280211451, 6.658229607783568 49.20195831969157, 8.099278598674744 49.01778351500333, 7.593676385131062 48.33301911070372, 7.466759067422231 47.62058197691181, 7.192202182655507 47.44976552997102, 6.736571079138059 47.54180125588285, 6.768713820023606 47.2877082383037, 6.037388950229001 46.72577871356187, 6.022609490593538 46.27298981382047, 6.500099724970426 46.42967275652944, 6.843592970414505 45.99114655210061, 6.802355177445605 45.70857982032864, 7.096652459347837 45.33309886329589, 6.749955275101655 45.02851797136758, 7.007562290076635 44.25476675066136, 7.549596388386107 44.12790110938481, 7.435184767291872 43.69384491634922, 6.52924523278304 43.12889232031831, 4.556962517931424 43.3996509873116, 3.100410597352663 43.07520050716705, 2.985998976258458 42.47301504166986, 1.826793247087153 42.34338471126569, 0.7015906103638941 42.79573436133261, 0.3380469091905809 42.57954600683955, -1.502770961910528 43.03401439063043, -1.901351284177764 43.42280202897834, -1.384225226232985 44.02261037859012, -1.193797573237418 46.01491771095486, -2.225724249673846 47.06436269793822, -2.963276129559603 47.57032664650795, -4.491554938159481 47.95495433205637, -4.592349819344776 48.68416046812699, -3.295813971357802 48.90169240985963, -1.616510789384961 48.64442129169454, -1.933494025063311 49.77634186461574, -0.98946895995536 49.34737580016091, 1.338761020522696 50.12717316344526, 1.6390010921385 50.9466063502975, 2.513573032246143 51.14850617126183, 2.658422071960274 50.79684804951575, 3.123251580425688 50.78036326761455, 3.588184441755658 50.37899241800356, 4.286022983425084 49.90749664977255, 4.799221632515724 49.98537303323637, 5.674051954784829 49.5294835475575, 5.897759230176348 49.44266714130711, 6.186320428094177 49.46380280211451)), ((6.186320428094177 49.46380280211451, 6.658229607783568 49.20195831969157, 8.099278598674744 49.01778351500333, 7.593676385131062 48.33301911070372, 7.466759067422231 47.62058197691181, 7.192202182655507 47.44976552997102, 6.736571079138059 47.54180125588285, 6.768713820023606 47.2877082383037, 6.037388950229001 46.72577871356187, 6.022609490593538 46.27298981382047, 6.500099724970426 46.42967275652944, 6.843592970414505 45.99114655210061, 6.802355177445605 45.70857982032864, 7.096652459347837 45.33309886329589, 6.749955275101655 45.02851797136758, 7.007562290076635 44.25476675066136, 7.549596388386107 44.12790110938481, 7.435184767291872 43.69384491634922, 6.52924523278304 43.12889232031831, 4.556962517931424 43.3996509873116, 3.100410597352663 43.07520050716705, 2.985998976258458 42.47301504166986, 1.826793247087153 42.34338471126569, 0.7015906103638941 42.79573436133261, 0.3380469091905809 42.57954600683955, -1.502770961910528 43.03401439063043, -1.901351284177764 43.42280202897834, -1.384225226232985 44.02261037859012, -1.193797573237418 46.01491771095486, -2.225724249673846 47.06436269793822, -2.963276129559603 47.57032664650795, -4.491554938159481 47.95495433205637, -4.592349819344776 48.68416046812699, -3.295813971357802 48.90169240985963, -1.616510789384961 48.64442129169454, -1.933494025063311 49.77634186461574, -0.98946895995536 49.34737580016091, 1.338761020522696 50.12717316344526, 1.6390010921385 50.9466063502975, 2.513573032246143 51.14850617126183, 2.658422071960274 50.79684804951575, 3.123251580425688 50.78036326761455, 3.588184441755658 50.37899241800356, 4.286022983425084 49.90749664977255, 4.799221632515724 49.98537303323637, 5.674051954784829 49.5294835475575, 5.897759230176348 49.44266714130711, 6.186320428094177 49.46380280211451)), ((8.746009148807559 42.62812185319392, 9.390000848028876 43.00998484961471, 9.560016310269134 42.15249197037952, 9.229752231491773 41.38000682226446, 8.775723097375362 41.58361196549443, 8.544212680707773 42.25651662858306, 8.746009148807559 42.62812185319392)))')
grid_crs=gdf.crs

#Read data to json.
gdf_json = json.loads(gdf.to_json())
#Convert to String like object.
grid = json.dumps(gdf_json)

day = st.selectbox("Show map on the day:", total_days, len(total_days) -1)

df_dep_today = df_dep[df_dep['date'] == day]
df_dep_today['size'] = df_dep_today['cas_confirmes']/5

#Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = grid)
pointsource = ColumnDataSource(df_dep_today)

hover = HoverTool(
    tooltips = [('Place', '@maille_nom'), ('Confirmed cases','@cas_confirmes'),('Deaths','@deces'), ('Reanimation','@reanimation')]
)

#Create figure object.
p = figure(title = 'Geographic distribution of 2019-nCov cases in France', plot_height = 600 , plot_width = 600, tools=[hover, 'pan', 'wheel_zoom'])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

patch=p.patches('xs','ys', source = geosource,fill_color = '#fff7bc',
          line_color = 'black', line_width = 0.35, fill_alpha = 1, 
                hover_fill_color="#fec44f")

#Add patch renderer to figure. 
patch = p.patches('xs','ys', source = geosource,fill_color = 'lightgrey',
          line_color = 'black', line_width = 0.25, fill_alpha = 1)

#p.add_tools(HoverTool(tooltips=[('Confirmed cases','@cas_confirmes'),('Deaths','@deces'), ('Reanimation','@reanimation')], renderers=[patch]))

p.circle('longitude','latitude',source=pointsource, size='size')
#Display figure inline in Jupyter Notebook.

#output_notebook()
#Display figure.
#show(p)

st.bokeh_chart(p)
