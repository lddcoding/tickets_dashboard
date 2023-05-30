import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator =stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized'])



if st.session_state["authentication_status"]:
    with st.container():

        #Side bar and everything
        st.markdown("# Artist Situation / Popularity Score ❄️")
        st.sidebar.markdown("# Artist Situation / Popularity Score ❄️")
        st.sidebar.write('This page goal is to help you search specific artist and see there popularity score accross various indicators')

elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password at the home page')