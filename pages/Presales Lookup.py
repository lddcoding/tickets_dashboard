import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import numpy as np
import pandas as pd
import requests
from streamlit_extras.colored_header import colored_header
from datetime import datetime
import pytz

# PUT IN IN THE SESSION STATE
local_timezone = pytz.timezone('America/New_York')

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator =stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized'])

def event_checker_after_specific_date(city, onsaleafterdate):
    p_city = city
    p_onsaleafterdate = onsaleafterdate
    size_of_requests = 200
    
    URL = f'https://app.ticketmaster.com/discovery/v2/events.json?&apikey={st.session_state["api_ticketmaster"]}'
    PARAMS = {'city': p_city,
            'onsaleOnAfterStartDate': p_onsaleafterdate,
            'size' : size_of_requests,
            'sort': 'name,asc'} # Get all the event in the database after a certain date
    
    r = requests.get(url = URL, params = PARAMS)
    data = r.json()
    nb_of_event = data['page']['totalElements']
    nb_of_page = int(data['page']['totalPages']) # if number of page exceed 200 than switch page
    
    if nb_of_page == 1:
        info_list = []
        for i in range(nb_of_event):
            info_dict = {'name': 'value1',
                         'id': 'value2', 
                         'Place': 'value3', 
                         'City' : 'value4', 
                         'url': 'value5', 
                         'Date' : 'value6', 
                         'presale': 'value7'} #create dict to add value and then have a list of dict
            
            name = data['_embedded']['events'][i]['name']
            info_dict['name'] = name
            id = data['_embedded']['events'][i]['id']
            info_dict['id'] = id
            url = data['_embedded']['events'][i]['url']
            info_dict['url'] = url
            date_of_event = data['_embedded']['events'][i]['dates']['start']['localDate']
            try:
                time_of_event = data['_embedded']['events'][i]['dates']['start']['localTime']
            except:
                time_of_event = ''
            date = str(date_of_event + ' ' + time_of_event)
            info_dict['Date'] = date
            name_of_venues = data['_embedded']['events'][i]['_embedded']['venues'][0]['name']
            info_dict['Place'] = name_of_venues
            city_of_venues = data['_embedded']['events'][i]['_embedded']['venues'][0]['city']['name']
            info_dict['City'] = city_of_venues
            try:
                sales_private = data['_embedded']['events'][i]['sales']['presales']
                info_dict['presale'] = sales_private
            except KeyError:
                info_dict['presale'] = np.nan
            info_list.append(info_dict)
        
    # If multiple page then extract data from each page
    elif nb_of_page > 1:
        info_list = []
        print('nb of page exceed!') #for test purpose
        
        for i in range(nb_of_page):
            URL = f'https://app.ticketmaster.com/discovery/v2/events.json?size=200&apikey={st.session_state["api_ticketmaster"]}'
            PARAMS = {'city': p_city,
                    'onsaleOnAfterStartDate': p_onsaleafterdate,
                    'page' : i,
                    'sort': 'name,asc'}
            r = requests.get(url = URL, params = PARAMS)
            data = r.json()
            for i in range(size_of_requests):
                info_dict = {'name': 'value1',
                             'id' : 'value2', 
                             'Place': 'value3', 
                             'City' : 'value4', 
                             'url': 'value5', 
                            'Date' : 'value6', 
                            'presale': 'value7'}
                try:
                    name = data['_embedded']['events'][i]['name']
                    info_dict['name'] = name
                    id = data['_embedded']['events'][i]['id']
                    info_dict['id'] = id
                    url = data['_embedded']['events'][i]['url']
                    info_dict['url'] = url
                    date_of_event = data['_embedded']['events'][i]['dates']['start']['localDate']
                    try:
                        time_of_event = data['_embedded']['events'][i]['dates']['start']['localTime']
                    except KeyError:
                        time_of_event = ''
                    date = str(date_of_event + ' ' + time_of_event)
                    info_dict['Date'] = date
                    name_of_venues = data['_embedded']['events'][i]['_embedded']['venues'][0]['name']
                    info_dict['Place'] = name_of_venues
                    city_of_venues = data['_embedded']['events'][i]['_embedded']['venues'][0]['city']['name']
                    info_dict['City'] = city_of_venues
                    try:
                        sales_private = data['_embedded']['events'][i]['sales']['presales']
                        info_dict['presale'] = sales_private
                    except KeyError:
                        info_dict['presale'] = np.nan
                except IndexError:
                    break #if the number of element inside the page is over 200, than break
        
                info_list.append(info_dict)
        
    # Check for the specified presale and create column    
    lookup = 'Artist Presale'.lower()
    for i in range(len(info_list)):
        presale = info_list[i]['presale']
        presale_string = str(presale)
        if presale_string == 'nan':
            info_list[i][f'presale lookup: {lookup}'] = False
            pass
        else:
            found = False
            for y in presale:
                check = y['name'].lower()
                if lookup in check:
                    found = True
                    break 
                else:
                    found = False
                    
            info_list[i][f'presale lookup: {lookup}'] = found 
    

    # Convert the data into a dataframe
    df = pd.DataFrame(info_list)
    df = df[~df.duplicated(subset='url')]
        
    #filter the dataframe with only concerts that have presales
    only_with_presales_df = df[df['presale'].notna()]

    return only_with_presales_df

if st.session_state["authentication_status"]:

    # Initialize a list for saved events in session state
    if 'saved_events' not in st.session_state:
        st.session_state.saved_event = []

    colored_header(label='Presale Lookup', description = '', color_name='violet-70')
    city = st.text_input('For what city are you aiming for (if you want multiple cities, separate them with a ,)')
    onsaleafterdate = st.date_input('After what date do you want to access events: ')
    if st.button("Let's cook!"):
        df = event_checker_after_specific_date(city, onsaleafterdate)
        if df.empty:
            st.write('No events were found for the past request')
        else:
            info_list_presales = df.to_dict(orient='records')

            #Display the data in columns so it's nicer
            for i in range(len(info_list_presales)):
                expander = st.expander(f"**#{i + 1}** Info about {info_list_presales[i]['name']} event")
                with expander:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write('***--Information about event--***')

                        # Display the date of the event
                        st.write(f"Date of the event: {info_list_presales[i]['Date']}")

                        # Display the place of the event
                        st.write(f"Place of the event: {info_list_presales[i]['Place']}")

                        # Display the city of the event
                        st.write(f"City of the event: {info_list_presales[i]['City']}")

                        # Display the url of the event
                        url = info_list_presales[i]['url']
                        name = info_list_presales[i]['name']
                        link = f"[{name} Ticketmaster URL]({url})"
                        st.markdown(link, unsafe_allow_html=True)

                        # Button to save the event in session state (save the url, event name, etc)
                        
                        st.button('Save event', key=i)
                            


                    with col2:
                        #Display the different presales name
                        st.write('***--Different Presales--***')
                        for y in range(len(info_list_presales[i]['presale'])):
                            name = info_list_presales[i]['presale'][y]['name']
                            start_utc = datetime.strptime(info_list_presales[i]['presale'][y]['startDateTime'], "%Y-%m-%dT%H:%M:%SZ")
                            end_utc = datetime.strptime(info_list_presales[i]['presale'][y]['endDateTime'], "%Y-%m-%dT%H:%M:%SZ")
    
                            utc_timezone = pytz.timezone('UTC')
                            start = utc_timezone.localize(start_utc).astimezone(local_timezone)
                            end = utc_timezone.localize(end_utc).astimezone(local_timezone)
    
    
                            presale = f'({name}) **STARTS:** {start} **END:** {end}'
                            st.write(presale)

            # If you want to download the dataframe 
            st.write('---')   
            st.write('Download the data in excel format')        
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button('Press to Download', csv, 'data.csv', 'text/csv', key='download-csv')
        

             
    
    
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')