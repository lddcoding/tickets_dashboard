import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import webbrowser
import pandas as pd
import openpyxl

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator =stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized'])


if st.session_state["authentication_status"]:
    st.title("Upload and Convert File")
    uploaded_file = st.file_uploader("Choose a file", type=["xlsx", "csv"])

    if st.button('Import file'):

        if uploaded_file is not None:
            # File is uploaded
            file_extension = uploaded_file.name.split(".")[-1]
            
            if file_extension == "xlsx":
                # Load Excel file
                df = pd.read_excel(uploaded_file)
            elif file_extension == "csv":
                # Load CSV file
                df = pd.read_csv(uploaded_file)


        # Code to access specific events according to there ID
        st.dataframe(df)
    
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')