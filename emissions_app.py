import config
import pandas as pd
import pymongo
from pymongo import MongoClient
import streamlit as st

#this will make the web app easier to read
st.set_page_config(layout="wide")

###Read in car emissions data from database on the cloud

#connect to cloud MongoDB server
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
    return pd.DataFrame(list(db.cars_emission_gmaps_rev.find({})))

#this dataframe will be used to calculate vehicle distance and emissions
cars_emissions = retrieving_cars_data()

###Read in train emissions data a csv file saved in this project's Github repo

# since this dataset is much smaller, it's stored in a CSV on Github and has to be read in as raw
url = "https://raw.githubusercontent.com/chloebs4590/Metis-Engineering/main/train_emissions_42.csv"
trains_emissions = pd.read_csv(url)

st.title('Passenger Train vs Car Emissions')

st.markdown(
    '''
    The purpose of this web app is to allow users to compare the carbon footprint of train versus car travel between cities serviced by Amtrak.

    **User instructions:**  
    1. Select an origin city
    2. Select an Amtrak route 
    3. Select a destination city
    4. View the distance and emissions **per passenger** by train versus car
    5. View and/or zoom in on a map that plots the cities on the Amtrak route between the origin and destination cities
    
    ''')

###Set up selection boxes in side bar

# setup first drop-down list for origin and destination locations
default_value_origin_city = 'Select or type location'
origin_list = [default_value_origin_city] + sorted(trains_emissions.origin_location.unique())
default_value_route = ""
default_value_dest_city = ""

#create origin city selection
origin_choice = st.sidebar.selectbox('Origin city', origin_list, index=0)

#after city choice is chosen, filter route options based on the route(s) in which city is found
origin_indices = [idx for idx,loc in enumerate(trains_emissions.origin_location) if loc == origin_choice]
routes = [trains_emissions.iloc[idx,10] for idx in origin_indices]
route_list = [""] + sorted(list(set(routes)))
route_choice = st.sidebar.selectbox('Route', route_list, index=0)

# after route is chosen, filter destination options to show only those in selected route
route_df = trains_emissions[trains_emissions.route == route_choice].reset_index(drop=True)
try:
  origin_idx = route_df[route_df['origin_location']==origin_choice].index.values.astype(int)[0]
except:
  pass
destinations = route_df[route_df.dest_location != origin_choice]['dest_location']
destinations_list = [""] + sorted(list(set(destinations)))
dest_choice = st.sidebar.selectbox('Destination city', destinations_list, index=0)


###Calculate and show distance and emissions by train versus car

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

###Create and show a list of cities that train passes through, including origin and destination

# origin idx
try:
  if len(route_df[route_df['origin_location']==origin_choice].index.values.astype(int)) > 1:
    origin_idx_route_tr = route_df[route_df['origin_location']==origin_choice].index.values.astype(int)[1]
  else:
    origin_idx_route_tr = route_df[route_df['origin_location']==origin_choice].index.values.astype(int)[0]
except:
  pass

# dest idx
try:
  dest_idx_route_tr = route_df[route_df['dest_location']==dest_choice].index.values.astype(int)[0]
except:
  pass

# names of cities in filtered route
try:
  if dest_idx_route_tr > origin_idx_route_tr:
    train_route_display_list = route_df.iloc[origin_idx_route_tr:dest_idx_route_tr+2,][['origin_location']].values.flatten().tolist()
    train_route_display = '\n'.join(str(n)+". "+ c for n, c in enumerate(train_route_display_list, 1))
  elif origin_idx_route_tr > dest_idx_route_tr:
    train_route_display_list = route_df.iloc[dest_idx_route_tr+1:origin_idx_route_tr+1,][['origin_location']].values.flatten().tolist()[::-1]
    train_route_display = '\n'.join(str(n)+". "+ c for n, c in enumerate(train_route_display_list, 1))
  else:
    train_route_display_list = route_df.iloc[origin_idx_route_tr:dest_idx_route_tr+2,][['origin_location']].values.flatten().tolist()
    train_route_display = '\n'.join(str(n)+". "+ c for n, c in enumerate(train_route_display_list, 1))
except:
  pass

col1, col2 = st.columns(2)
try:
  with col1:
    st.subheader(f'Train results...')
    st.write(f'**Distance**: {trains_distance:.0f} miles')
    st.write(f'**Carbon Emissions**: {trains_emissions:.0f} kg')
    st.text_area('Cities in route:', train_route_display)
except:
  pass

try:
  with col2:
    st.subheader(f'Car results...')
    st.write(f'**Distance**: {cars_distance:.0f} miles')
    st.write(f'**Carbon Emissions**: {cars_emissions:.0f} kg')
    st.write("The exact route is unknown; Google's Distance Matrix API (which was used to calculate distance) returns distance based on the recommended route between start and end points, as calculated by the Google Maps API.")
except:
  pass

for i in range(3):  
    st.text("")

###Show map, first of all cities in which Amtrak is located and then filtered down and zoomed into cities on the train route

# base map
stations_data_url = 'https://raw.githubusercontent.com/chloebs4590/Metis-Engineering/main/stations_locations.csv'
stations_locations = pd.read_csv(stations_data_url)
stations_locations['lon'] = stations_locations['origin_long']
stations_locations['lat'] = stations_locations['origin_lat']
try:
  if dest_choice == default_value_dest_city:
    st.map(zoom=3)
    #st.map(stations_locations[['lat','lon']],zoom=3)
  else:
    pass
except:
  pass

# filtered map
route_df['lat'] = route_df['origin_lat']
route_df['lon'] = route_df['origin_lon']
try:
  if dest_idx_route_tr > origin_idx_route_tr:
    route_df_filtered = route_df.iloc[origin_idx_route_tr:dest_idx_route_tr+2,]
  elif origin_idx_route_tr > dest_idx_route_tr:
    route_df_filtered = route_df.iloc[dest_idx_route_tr+1:origin_idx_route_tr+1,]
  else:
    route_df_filtered = route_df.iloc[origin_idx_route_tr:dest_idx_route_tr+2,]
except:
  pass
try:
  st.map(route_df_filtered[['lat','lon']],zoom=5)
except:
  pass

for i in range(3):  
    st.text("")

st.markdown('''     

    **About the data:**
 
    * Distances are calculated using [Google's Distance Matrix API](https://developers.google.com/maps/documentation/distance-matrix), which allows one to specify the mode/travel mode (in this case, driving or train).
    * Emissions data come from the [Climatiq.io API](https://www.climatiq.io/) and the primary source is the EPA. Both train and vehicle emissions reflect per passenger amounts.       
    * Amtrak station locations come from the [Homeland Infrastructure Foundation-Level Data (HIFLD)](https://hifld-geoplatform.opendata.arcgis.com/datasets/amtrak-stations/explore?location=29.200042%2C71.570775%2C3.00)
      and train routes come from both [Amtrak.com](https://www.amtrak.com/train-routes) and the [Wikipedia page](https://en.wikipedia.org/wiki/List_of_Amtrak_routes).
    
    An inspiration for this project was [this web app](https://share.streamlit.io/ninaksweeney/flight_emissions/main/flight_emissions_app.py) 
    on the carbon footprint of flying, which was created by a fellow Metis bootcamp student.

''')
