import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import pandas as pd
import pytz
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import base64
import time

# Set your Spotify API credentials
client_id = '14d50f69558f4d7b84f91cf1ce9d3dde'
client_secret = 'd1a6265ddbb74d938b2d12803194f93a'

# Create an instance of the Spotify API client with client credentials flow
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Function to return true or false if a presale is present in the list
def certified_fan_recognition(presale_list, presale_to_check):
    if presale_list == 'NAN':
        return False
    else: 
        for i in presale_list:
            if presale_to_check.title() in i['name'] :
                return True
        return False

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator =stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized'])

if st.session_state["authentication_status"]:

    #Side bar and everything
    st.markdown("# OnSaleOnstartdate ❄️")
    st.sidebar.markdown("# OnsSaleOnstartdate ❄️")
    st.sidebar.write('This page will help you find concert that have a public sale on a specific date, for a specific city using the ticketmaster API')

    def get_info_on_startdate(city, date, presaletocheck):
        p_city = city
        p_onsaleonstartdate = date

            #Start by accessing the requests
        URL = f'https://app.ticketmaster.com/discovery/v2/events.json?size=1&apikey={st.session_state["api_ticketmaster"]}'
        PARAMS = {'city': p_city, 
                'onsaleOnStartDate': p_onsaleonstartdate}

        r = requests.get(url = URL, params = PARAMS)
        data = r.json()

        # See the total number of pages (0 based)
        nb_of_page = int(data['page']['totalPages'])

        # The loop on the number of page in the request

        donne_global = []
        for i in range(nb_of_page):
            insider_list = []
            PARAMS = {'city':p_city, 
                    'onsaleOnStartDate': p_onsaleonstartdate,
                    'page': i}
            
            r = requests.get(url = URL, params = PARAMS)
            data = r.json()
            try:
                # Append all value to list named "insider list" and then added those values to a global list (DOIT ÊTRE EN ORDRE!!)
                event = data['_embedded']['events'][0]
                sales = data['_embedded']['events'][0]['sales']
                
                insider_list.append(event['name'])
                
                insider_list.append(event['url'])
                
                insider_list.append(sales['public'])
                
                try: 
                    insider_list.append(sales['presales'])
                except:
                    insider_list.append('NAN')
                    
                
                try:
                    insider_list.append(event['_embedded']['attractions'][0]['name']) #can get the genre, type, name of artist
                except:
                    insider_list.append('NAN')
                
                    
                
                donne_global.append(insider_list)  
                
            
            except KeyError:
                pass

        # Create a dictionnary from the values previously 
        list_of_name = []
        list_of_url = []
        list_of_public = []
        list_of_presale = []
        list_of_name_artist = []
        for name, url, public, presale, artist in donne_global:
            list_of_name.append(name)
            list_of_url.append(url)
            list_of_public.append(public)
            list_of_presale.append(presale)
            list_of_name_artist.append(artist)
            
        empty_dict = {'name': list_of_name, 'url': list_of_url, 'public': list_of_public, 'presale': list_of_presale, 'Artist Name': list_of_name_artist}
        df = pd.DataFrame.from_dict(empty_dict)

        # Convert the dates for the public sales to local timezone 
        local_timezone = pytz.timezone('America/New_York')
        public_start_list = []
        public_end_list = []

        for i in empty_dict['public']:
            public_start = datetime.strptime(i['startDateTime'], "%Y-%m-%dT%H:%M:%SZ")
            public_end = datetime.strptime(i['endDateTime'], "%Y-%m-%dT%H:%M:%SZ")
            
            #Convert the utc to the local timezone define previously
            utc_timezone = pytz.timezone('UTC')
            public_start_local = utc_timezone.localize(public_start).astimezone(local_timezone)
            public_end_local = utc_timezone.localize(public_end).astimezone(local_timezone)
            
            public_start_list.append(str(public_start_local))
            public_end_list.append(str(public_end_local))
        
        # Create new colonne with the new data for the public start and end date
        df['public_start'] = public_start_list
        df['public_end'] = public_end_list 
        df = df.drop('public', axis=1)


        # Create new column with popularity score on spotify
        Popularity_score_list = []
        Spotify_followers_list = []
        for i in empty_dict['Artist Name']:
            # Specify the name of the artist
            artist_name = str(i)
            
            # To prevent returning a popularity score for no artist name
            if artist_name == 'NAN':
                Popularity_score_list.append('NAN')
                Spotify_followers_list.append('NAN')
                
            else:

                # Search for the artist
                results = sp.search(q='artist:' + artist_name, type='artist', limit=1)

                # Extract the artist's information and popularity
                if results['artists']['items']:
                    
                    # Get the popularity score
                    artist = results['artists']['items'][0]
                    artist_name = artist['name']
                    popularity = artist['popularity']
                    
                    # Get the number of followers
                    artist_id = artist['id']
                    artist_info = sp.artist(artist_id)
                    total_followers = artist_info['followers']['total']
                    
                    
                    Spotify_followers_list.append(total_followers)
                    Popularity_score_list.append(popularity)
                else:
                    Spotify_followers_list.append('NAN')
                    Popularity_score_list.append('NAN')
                    

        df['Spotify Popularity Score'] = Popularity_score_list
        df['Spotify Followers'] = Spotify_followers_list

        # Check if a particular presale name is present in the list of presales
        presale_there_or_not_list = []
        presale_to_check = presaletocheck 
        for i in empty_dict['presale']:
            result_boolean = certified_fan_recognition(i, presale_to_check)
            presale_there_or_not_list.append(result_boolean)
            
        df[f'{presale_to_check} there ?'] = presale_there_or_not_list


        # Using the 300 most popular artist according to kworb.net, check if the artist is popular or not

        url = 'https://kworb.net/itunes/'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')
        headers = [th.text.strip() for th in table.find_all('th')]

        rows = []
        for tr in table.find_all('tr'):
            row = [td.text.strip() for td in tr.find_all('td')]
            if row:
                rows.append(row)

        df_popular_artist = pd.DataFrame(rows, columns=headers)

        # Compare the two datafames
        df['Popular according to Kworb'] = df['Artist Name'].isin(df_popular_artist['Artist'])


        # Adjust the column name
        df = df[['name', 'Artist Name', 'url', 'public_start', 'public_end', 'presale', f'{presale_to_check} there ?', 'Spotify Popularity Score', 'Spotify Followers', 'Popular according to Kworb']]

        # Remove all the rows that have the show in double ?
        df = df[~df.duplicated(subset='name')]

        return df
    
    # DISPLAY THE DATA FROM THE PREVIOUS REQUEST  
    city = st.text_input('From what city do you need the info (ex: Miami)')
    date = st.date_input('What date would the event be onsale') 
    presaletocheck = st.text_input('What type of presale do you want to look into? (ex: Verified Fan Presale)')
    if st.button('submit request'):
        df = get_info_on_startdate(city, date, presaletocheck)
        if df.empty:
            st.info(f'No event has been found for {city} the {date}. Try for another date or another city...')
        else:
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button('Press to Download', csv, 'data.csv', 'text/csv', key='download-csv')
                
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password at the home page')
    

