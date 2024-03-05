import streamlit as st
import requests
import json
from streamlit_extras.grid import grid
from requests.auth import HTTPBasicAuth

sidebar_name = "Admin"
        
        
@st.cache_data(ttl=60)        
def api_call_connect_admin(endpoint, username, password):
    try:
        response = requests.get(f"http://127.0.0.1:8000/{endpoint}", 
                                auth=HTTPBasicAuth(username, password)).json()
        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def api_call_create_movie(title, year, genres_list, username, password):
    try:
        payload = {
            "title": title,
            "year": year,
            "genres": genres_list
        }
        response = requests.post("http://127.0.0.1:8000/create-movie",
                                 auth=(username, password),
                                 json=payload)
        st.write('response')
        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return None
    
def run_create_movie(username, password):
    title = st.text_input("Title")
    year = st.number_input("Year", min_value=1900, max_value=2024)
    genres_list = ["comedy", "romance"]
    selected_genres = st.selectbox("Genres", genres_list,)
    
    create = st.button('Create movie')

    if create and st.session_state.selected_action == "Create Movie":
        if title:
            if api_call_create_movie(title, year, selected_genres, username, password):
                st.success("Movie created successfully!")
        else:
            st.warning("Please fill title and genres")
            
def run_auth():
    with st.sidebar:
        st.write("### Authentication")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        plateform_button = st.button("Login as Admin")
        equipe_ds_button = st.button("Login as Data Scientist")

    if plateform_button:
        if username and password:
            response_admin = api_call_connect_admin("admin", username, password)
            if response_admin and 'message' in response_admin:
                st.success(response_admin['message'])
                st.session_state.login = True
                st.session_state.role = "plateforme"

            else:
                st.error("Failed to authenticate as admin. Please check your credentials.")
        else:
            st.warning("Please provide both username and password for admin.")

    if equipe_ds_button:
        if username and password:
            response_ds = api_call_connect_admin("equipe_ds", username, password)
            if response_ds and 'message' in response_ds:
                st.success(response_ds['message'])
                st.session_state.login = True
                st.session_state.role = "equipe_ds"
            else:
                st.error("Failed to authenticate as data scientist. Please check your credentials.")
        else:
            st.warning("Please provide both username and password for data scientist.")

    return username, password

def call_action():
    st.session_state.action = True


def run():
    if "action" not in st.session_state:
        st.session_state.action = False
    if "role" not in st.session_state :
        st.session_state.role = None
        
    username, password = run_auth()

    if st.session_state.role == "plateforme":
        actions = ["" ,"Create Movie", "Action 2"]
        selected_action = st.selectbox("Select Action", actions, 
                                       on_change=call_action
                                       )
        if st.session_state.action :
            st.session_state.selected_action = selected_action
            if selected_action == "Create Movie":
                run_create_movie(username, password)
            elif selected_action == "Action 2":
                st.write("Action loading ...")        

    elif st.session_state.role == "equipe_ds":
        st.write("Hello Data Scientist!")
