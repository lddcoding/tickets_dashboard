import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import webbrowser
from streamlit_extras.let_it_rain import rain

st.set_page_config(layout="wide")

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator =stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized'])

selectbox_placeholder = st.empty()
options = ["Login", "Register", "Forgot password", "Forgot username"]
selected_option = selectbox_placeholder.selectbox("Select an option", options)


if selected_option == 'Login':
    name, authentication_status, username = authenticator.login('Login', 'main')
    if authentication_status:
        authenticator.logout('Logout', 'main')

        # Emoji rain
        rain(emoji="🍇", font_size=54, falling_speed=5, animation_length="infinite")
        
        col1, col2, col3 = st.columns((1,2,1))
        with col1:
            pass

        with col2: 
            # Side bar and everything
            st.title('Ticket Analyser Dashboard')
            st.write(f'Welcome *{name}*')
            selectbox_placeholder.empty()

            st.write('Hey and welcome to the ticket analyzer, which the goal is to help you, print money finding good concerts to flip (all of that, using data!)')

            if 'api' not in st.session_state:
                st.session_state.api_ticketmaster = 'value'

            API = st.text_input('Provide your TicketMaster API key: ')
            st.session_state.api_ticketmaster = API
            st.write(f"Your ticketmaster API key: {st.session_state['api_ticketmaster']}") #THE WAY TO STORE THE TICKETMASTER API KEY ACCROSS THE APPLICATION


            image_path = './image.png'
            st.image(image_path, caption='*Quick note: for security purpose, the API key is not gonna be saved in the application so keep it close', use_column_width=True)

            st.text_input('Provide your timezone: (ex: America/New_York)')

        with col2:
            pass 

        # Sidebar
        st.sidebar.title('Ressources: ')
        if st.sidebar.button('Create my own Tickemaster API key'):
            url = 'https://developer-acct.ticketmaster.com/user/login?destination=user'
            webbrowser.open_new_tab(url)

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

    




