import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from streamlit_extras.colored_header import colored_header

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator =stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized'])

# Set your Spotify API credentials
client_id = '14d50f69558f4d7b84f91cf1ce9d3dde'
client_secret = 'd1a6265ddbb74d938b2d12803194f93a'

# Create an instance of the Spotify API client with client credentials flow
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)


if st.session_state["authentication_status"]:
    #Side bar and everything
    colored_header(label='**Concert Annoncement**', description = '', color_name='violet-70')
    st.sidebar.markdown("# Concert Annoncement 🍇")
    st.sidebar.write('This page will help you find artist that just annonced there tour dates, be ahead of the game! ')

    # Fetch the HTML content of the page
    url = 'https://concertfix.com/tour-announcements'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the concert announcement elements
    articles = soup.find_all('article', class_='latest-article grid-item')

    # Extract the titles, dates, and descriptions
    concerts = []
    for article in articles:
        title = article.find('h3').text.strip()
        date = article.find('div', class_='time').span.text.strip()
        description = article.find('div', class_='article-excerpt').p.text.strip()
        continue_reading = article.find('div', class_='article-excerpt').p.a.text.strip()
        full_description = description.replace(continue_reading, '')

        # Get the artist name, followers and popularity score according to spotify API
        title_element = article.find('h3')
        if title_element:
            title_text = title_element.text.strip()
            if 'announce' in title_text or 'announces' in title_text:
                # Extract the artist name before the keyword
                artist_name_fromrequest = title_text.split('announce')[0].strip()
                artist_name_fromrequest = artist_name_fromrequest.split('announces')[0].strip()
                
                artist_name = artist_name_fromrequest
                
                results = sp.search(q='artist:' + artist_name, type='artist', limit=1)

                # Extract the artist's information and popularity and number of followers
                if results['artists']['items']:
                    artist = results['artists']['items'][0]
                    artist_name = artist['name']
                    popularity = artist['popularity']

                    artist_id = artist['id']
                    artist_info = sp.artist(artist_id)
                    total_followers = artist_info['followers']['total']

        concert = {'title' : title, 'date': date, 'description': full_description, 'Artist Name': artist_name, 'Popularity': popularity, 'Total Followers': total_followers} #Create your own dictionnary to store the data more easily
        concerts.append(concert)

    # Display concert information in Streamlit
    col1, col2 = st.columns(2)
    num_concert = len(concerts)
    half_concerts = num_concert // 2
    
    with col1: 
        for concert in concerts[0:half_concerts]:
            st.write('***-- Annoncement details --***')
            st.write('**Title:**', concert['title'])
            st.write('**Date of annoncement:**', concert['date'])
            st.write('**Description:**', concert['description'])

            st.write('***-- Spotify Information --***')
            st.write('**Artist Name**', concert['Artist Name'])
            st.write('**Popularity score**', concert['Popularity'])
            st.write('**Total Followers**', concert['Total Followers'])
            st.write('---')

            

    with col2: 
        for concert in concerts[half_concerts:num_concert]:
            st.write('***-- Annoncement details --***')
            st.write('**Title:**', concert['title'])
            st.write('**Date of annoncement:**', concert['date'])
            st.write('**Description:**', concert['description'])

            st.write('***-- Spotify Information --***')
            st.write('**Artist Name**', concert['Artist Name'])
            st.write('**Popularity score**', concert['Popularity'])
            st.write('**Total Followers**', concert['Total Followers'])
            st.write('---')

elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password at the home page')