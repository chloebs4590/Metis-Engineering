import pandas as pd
import pydeck as pdk
import pymongo
from pymongo import MongoClient
import streamlit as st

# Part 1: Data Setup
# Part 1a: cars emissions data

#connect to cloud Mongodb server
uri = 'mongodb://udunkhpo2nmne8de5ygi:37Ke4KMMHIcBlSPVlmYL@bitnqlsaoiuc1yk-mongodb.services.clever-cloud.com:27017/bitnqlsaoiuc1yk'
client = MongoClient( uri )

# MongoDB connection info
hostname = 'bitnqlsaoiuc1yk-mongodb.services.clever-cloud.com'
port = 27017
username = st.secrets["db_username"]
password = st.secrets["db_password"]
databaseName = 'bitnqlsaoiuc1yk'

# authenticate the database
client = MongoClient(hostname, username=username, password=password, authSource = databaseName, 
                    authMechanism = 'SCRAM-SHA-256')
db = client[databaseName]

#read data from the database into dataframe
@st.cache(allow_output_mutation=True, suppress_st_warning=True, hash_funcs={"MyUnhashableClass": lambda _: None})
def retrieving_cars_data():
    return pd.DataFrame(list(db.cars_emission_gmaps.find({})))

#this dataframe will be used to calculate vehicle emissions
cars_emissions = retrieving_cars_data()

# Part 1b: trains emissions data

# since this dataset is much smaller, it's stored in a CSV on Github and has to be read in as raw
url = "https://raw.githubusercontent.com/chloebs4590/Metis-Engineering/main/train_emissions_42.csv"
trains_emissions = pd.read_csv(url)

st.title('Passenger Train vs Car Emissions')

st.markdown(
    '''
    The purpose of this web app is to allow users to compare the carbon footprint of train versus car travel in the U.S.

    **User instructions:**  
    * Select an origin city, train route, and desination city  
    * After making those selections, find the distance and emissions **per passenger** by train versus car below the map showing all cities with Amtrak stations
    * View a zoomed-in map that plots the cities on the Amtrak route between the origin and destination cities and a list of the cities in the entire route
    
    ''')

# Part 2 - drop-down lists, selection and data filtering

# setup first drop-down list for origin location
default_value_city = 'Select or type location'
origin_list = [default_value_city] + sorted(trains_emissions.origin_location.unique())

#create origin city selection
origin_choice = st.sidebar.selectbox('Origin city', origin_list, index=0)

#after city choice is chosen, filter route options based on the route(s) in which city is found
origin_indices = [idx for idx,loc in enumerate(trains_emissions.origin_location) if loc == origin_choice]
routes = [trains_emissions.iloc[idx,11] for idx in origin_indices]
route_list = [""] + sorted(list(set(routes)))
route_choice = st.sidebar.selectbox('Route', route_list, index=0)
#st.sidebar.write('Route selected:', route_choice)

# after route is chosen, filter destination options to show only those in selected route
route_df = trains_emissions[trains_emissions.route_locations == route_choice].reset_index(drop=True)
try:
  origin_idx = route_df[route_df['origin_location']==origin_choice].index.values.astype(int)[0]
except:
  pass
destinations = route_df[route_df.dest_location != origin_choice]['dest_location']
destinations_list = [""] + sorted(list(set(destinations)))
dest_choice = st.sidebar.selectbox('Destination city', destinations_list, index=0)

# base map
stations_data_url = 'https://raw.githubusercontent.com/chloebs4590/Metis-Engineering/main/stations_locations.csv'
stations_locations = pd.read_csv(stations_data_url)
stations_locations['lon'] = stations_locations['origin_long']
stations_locations['lat'] = stations_locations['origin_lat']
st.map(stations_locations[['lat','lon']],zoom=3)

# calculate and show distance (in miles) and c02 emissions (in kg)
# first, for trains

# distance
try:
  dest_idx = route_df[route_df.dest_location == dest_choice].index.values.astype(int)[0]
except:
  pass
try:
  if dest_idx > origin_idx:
    trains_distance = sum(list(route_df.distance_mi)[origin_idx:dest_idx+1])
  elif origin_idx > dest_idx:
    trains_distance = sum(list(route_df.distance_mi)[dest_idx:origin_idx])
  else:
    trains_distance = route_df.iloc[origin_idx,12]
except:
  pass

# emissions
try:
  if dest_idx > origin_idx:
    trains_emissions = sum(list(route_df.co2e_kg_round)[origin_idx:dest_idx+1])
  elif origin_idx > dest_idx:
    trains_emissions = sum(list(route_df.co2e_kg_round)[dest_idx:origin_idx])
  else:
    trains_emissions = route_df.iloc[origin_idx,12]
except:
  pass

#second, for cars

# distance
try:
  cars_distance = cars_emissions.loc[((cars_emissions.origin_location == origin_choice)&(cars_emissions.dest_location == dest_choice))\
                                      | ((cars_emissions.origin_location == dest_choice)&(cars_emissions.dest_location == origin_choice))]['distance_mi'].values[0]
except:
  pass

# emissions
try:
  cars_emissions = cars_emissions.loc[((cars_emissions.origin_location == origin_choice)&(cars_emissions.dest_location == dest_choice))\
                                      | ((cars_emissions.origin_location == dest_choice)&(cars_emissions.dest_location == origin_choice))]['co2e_kg_round'].values[0]
except:
  pass

col1, col2 = st.columns(2)
try:
  with col1:
    st.subheader(f'Train distance: {trains_distance:.0f} miles')
    st.subheader(f'Train emissions: {trains_emissions:.0f} kg')
except:
  pass

try:
  with col2:
    st.subheader(f'Car distance: {cars_distance:.0f} miles')
    st.subheader(f'Car emissions: {cars_emissions:.0f} kg')
except:
  pass

# filtered map
route_df['lat'] = route_df['origin_lat']
route_df['lon'] = route_df['origin_lon']
try:
  if dest_idx > origin_idx:
    route_df_filtered = route_df.iloc[origin_idx:dest_idx+1,]
    #route_df_filtered = route_df.filter(items = [origin_idx,dest_idx+1], axis=0)
  elif origin_idx > dest_idx:
    route_df_filtered = route_df.iloc[dest_idx+1:origin_idx,]
    #route_df_filtered = route_df.filter(items = [dest_idx+1, origin_idx], axis=0)
  else:
    route_df_filtered = route_df.iloc[origin_idx:dest_idx+1,]
    #route_df_filtered = route_df.filter(items = [origin_idx, dest_idx+1], axis=0)
except:
  pass
try:
  st.map(route_df_filtered[['lat','lon']],zoom=5)
except:
  pass

# show selected route below distance and emissions
route_raw_list = route_choice.split(';')
route_raw_list = [item.strip() for item in route_raw_list]
route_raw_list_rev = []
for item in route_raw_list:
  if ':' in item:
    item = item[item.find(':')+2:]
    route_raw_list_rev.append(item)
  else:
    route_raw_list_rev.append(item)
route_display = '\n'.join(str(n)+". "+ c for n, c in enumerate(route_raw_list_rev, 1))
st.text_area('Cities in route selected:', route_display)

for i in range(3):  
    st.text("")

st.markdown('''     

    About the data:
 
    * Distances are calculated using [Google's Distance Matrix API](https://developers.google.com/maps/documentation/distance-matrix), which allows one to specify the mode/travel mode (in this case, driving or train).
    * Emissions data come from the [Climatiq.io API](https://www.climatiq.io/) and the primary source is the EPA. Both train and vehicle emissions reflect per passenger amounts.       
    * Amtrak station locations come from the [Homeland Infrastructure Foundation-Level Data (HIFLD)](https://hifld-geoplatform.opendata.arcgis.com/datasets/amtrak-stations/explore?location=29.200042%2C71.570775%2C3.00)
      and train routes come from both [Amtrak.com](https://www.amtrak.com/train-routes) and the [Wikipedia page](https://en.wikipedia.org/wiki/List_of_Amtrak_routes).
    
    An inspiration for this project was [this web app](https://share.streamlit.io/ninaksweeney/flight_emissions/main/flight_emissions_app.py) 
    on the carbon footprint of flying, which was created by a fellow Metis bootcamp student.

''')
