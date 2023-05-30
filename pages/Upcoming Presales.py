import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import webbrowser
import requests
from datetime import date
from datetime import datetime
import json
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from streamlit_extras.colored_header import colored_header

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator =stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized'])

def all_the_presale_after_todays_date(presale_name):
    today = datetime.now().date()
    formatted_time = today.strftime("%Y-%m-%dT%H:%M:%SZ")
    size_of_requests = 200

    #Start by accessing the requests
    URL = f'https://app.ticketmaster.com/discovery/v2/events.json?&apikey={st.session_state["api_ticketmaster"]}'
    PARAMS = {'onsaleOnAfterStartDate' : today,
            'size' : size_of_requests,
            'preSaleDateTime': f'{formatted_time},*'}

    r = requests.get(url = URL, params = PARAMS)
    data = r.json()
    nb_of_concert = data['page']['totalElements']
    nb_of_page = data['page']['totalPages']
    info_list = []

    for i in range(nb_of_page):
        URL = f'https://app.ticketmaster.com/discovery/v2/events.json?&apikey={st.session_state["api_ticketmaster"]}'
        PARAMS = {'onsaleOnAfterStartDate' : today,
                'size' : size_of_requests,
                'preSaleDateTime': f'{formatted_time},*',
                'page' : i}

        r = requests.get(url = URL, params = PARAMS)
        data = r.json()
        
        for y in range(size_of_requests):
            info_dict = {'name': 'value1', 'id': 'value2', 'Place': 'value3', 'City' : 'value4', 
                        'url': 'value5', 'Date' : 'value6', 'presale': 'value7'}
            
            #Get all the information necessary
            try:
                name = data['_embedded']['events'][y]['name']
                info_dict['name'] = name
                id = data['_embedded']['events'][i]['id']
                info_dict['id'] = id
                url = data['_embedded']['events'][y]['url']
                info_dict['url'] = url
                date_of_event = data['_embedded']['events'][y]['dates']['start']['localDate']
                try:
                    time_of_event = data['_embedded']['events'][y]['dates']['start']['localTime']
                except KeyError:
                    time_of_event = ''
                date = str(date_of_event + ' ' + time_of_event)
                info_dict['Date'] = date
                name_of_venues = data['_embedded']['events'][y]['_embedded']['venues'][0]['name']
                info_dict['Place'] = name_of_venues
                city_of_venues = data['_embedded']['events'][y]['_embedded']['venues'][0]['city']['name']
                info_dict['City'] = city_of_venues
                try:
                    sales_private = data['_embedded']['events'][y]['sales']['presales']
                    info_dict['presale'] = sales_private
                except KeyError:
                    info_dict['presale'] = np.nan
            except IndexError:
                break
                
            info_list.append(info_dict)
                    
                
    # Check for certain presale and subset on the choosen presale             
    lookup = presale_name.lower()
    for i in range(len(info_list)):
        presale = info_list[i]['presale']
        presale_string = str(presale)
        if presale_string == 'nan':
            info_list[i]['Presale lookup'] = False
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
                    
            info_list[i]['Presale lookup'] = found
            
            
    # convert info_list to a dataframe
    df = pd.DataFrame(info_list)
    return df

    # Remove the rows that don't have the specific presale
    #filtered_df = df[df['Presale lookup'] != False]
    #return filtered_df


if st.session_state["authentication_status"]:
    colored_header(label='Upcoming Presales', description = '', color_name='violet-70')
    st.sidebar.markdown("# Standard Presale Passwords:")

    # Webscrape the ticketcrusader website to get the standart presale codes (put it on the sidebar)
    url = "https://ticketcrusader.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    div_element = soup.find("div", class_="textwidget")
    text = div_element.get_text()
    lines = text.strip().split("\n")
    st.sidebar.markdown("\n".join([f"- {line}" for line in lines]))

    presalename = st.text_input('Enter the type of presale you want to look at')
    show_all_events = st.checkbox('Want to simply see all the upcoming events with presale ?')
    if st.button("Let's cook!"):
        df = all_the_presale_after_todays_date(str(presalename))
        if show_all_events == True:
            st.subheader('All the upcoming events with presales')
            st.dataframe(df)
            st.write('Download the data in excel format')        
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button('Press to Download', csv, 'data.csv', 'text/csv', key='download-csv')

        elif show_all_events == False:
            filtered_df = df[df['Presale lookup'] != False]
            if filtered_df.empty:
                st.warning(f'No events were found for the **{presalename}** presale...')
            else:
                st.subheader(f'All the upcoming events with the {presalename} presale')
                st.dataframe(df)
                st.write('Download the data in excel format')        
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button('Press to Download', csv, 'data.csv', 'text/csv', key='download-csv')


elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password at the home page')



