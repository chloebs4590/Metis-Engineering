### Background

The goal of this project was to build a web that would allow climate-conscious individuals - specifically those looking for alternative modes of travel to flying - to compare the carbon emissions of passenger train travel versus passenger vehicle travel between cities serviced by Amtrak. To that end, I created [Rail or Road?](https://share.streamlit.io/chloebs4590/metis-engineering/main/emissions_app.py), an interactive web app that allows users to select an origin city, destination city and Amtrak route and compare the distance in miles and carbon emissions of traveling between these two cities by train or car.

### Data Engineering Pipeline

***Data Ingestion and Processing***

I identified the location of Amtrak stations using data from the [Homeland Infrastructure Foundation-Level Data (HIFLD)](https://www.huduser.gov/portal/dataset/chas-api.html) and data on train routes from both [Amtrak.com](https://www.amtrak.com/train-routes) and [this Wikipedia page](https://en.wikipedia.org/wiki/List_of_Amtrak_routes).
Next, I focused on calculating the travel distance between train stations by train. To do this, I created sequentialing pairings of stations within the same route and used these pairings to calculate the distances between them. These distances were calculated by automating a call to Google's Distance Matrix API for every sequential pairing. This API allows a user to specify the transit mode between two locations (in this case, transit mode was set to "train"). Using these distances, I automated an API call to Climatiq.io, specifying intercity train travel as the emission factor and the number of passengers as one, to calculate the carbon emissions for each distance between sequential pairings of stations. After collecting all of the train emissions data, I converted it to a dataframe and joined it with the station location data.

After ingesting and processing the train data, I focused on the car data. I first created combinations of all stations within a route, since car travel is not constrained in the same way as train travel is to an ordered sequence. Next, I automated a call to Google's Distance Matrix API for every combination of stations within a route, this time specifying the transit mode as driving. Using these distances, I automated an API call to Climatiq.io, specifying passenger vehicle travel as the emission factor and the number of passengers as one, to calculate the carbon emissions for the distances between combinations of stations within a route.

***Data Storage***

The train distances and emissions dataset was saved in a csv file and committed to Github for storage. This is because there were fewer than 1000 observations (i.e., sequential station pairings within each route).

The car distances and emissions dataset was much larger - over 10,000 observations - so these data were stored in a cloud-based MongoDB database through Clever Cloud.

***Deployment***

I pulled the data from MongoDB and Github into a .py file containing the Streamlit web app code. Within the .py file, I used pandas to manipulate the train and car distance and emissions data to calculate distances and emissions between cities as well as create a map.

### Tools

- Data Ingestion: Requests, Google's Distance Matrix API, Climatiq.io API
- Data Processing: Pandas
- Data Storage: pyMongo, MongoDB, Github
- Data Processing: Pandas
- Data Visualization: Streamlit
- Web App Deployment: Streamlit

### Communication
In addition to this write-up, I delivered a five-minute presentation to my peers and instructors. The slides from that presentation are saved in this repo.

