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

options = ["Login", "Register", "Forgot password", "Forgot username"]
selected_option = st.selectbox("Select an option", options)


if selected_option == 'Login':
    name, authentication_status, username = authenticator.login('Login', 'main')
    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.write(f'Welcome *{name}*')
        st.title('Some content')
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

elif selected_option == 'Register':
    try:
        if authenticator.register_user('Register user', preauthorization=False):
            st.success('User registered successfully')
            with open('./config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)

elif selected_option == 'Forgot password':
    try:
        username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password('Forgot password')
        if username_forgot_pw:

            # SEND EMAIL

            st.success('New password sent securely')
            with open('../config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            # Random password to be transferred to user securely
        else:
            st.error('Username not found')
    except Exception as e:
        st.error(e)

elif selected_option == 'Forgot username':
    try:
        username_forgot_username, email_forgot_username = authenticator.forgot_username('Forgot username')
        if username_forgot_username:
            st.success('Username sent securely')
            with open('../config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            # Username to be transferred to user securely
        else:
            st.error('Email not found')
    except Exception as e:
        st.error(e)

    




