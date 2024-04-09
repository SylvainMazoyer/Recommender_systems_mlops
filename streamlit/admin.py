import streamlit as st
import requests
import json
from streamlit_extras.grid import grid
from requests.auth import HTTPBasicAuth
import base64
import pandas as pd

sidebar_name = "Admin"
        
    
def api_call_connect_admin(username,password,role):
    response = requests.get(f'http://api_model_container:5000/admin/{role}', 
                            auth=(username,password)).json()
    return response

def api_call_entrainer_model():
    entrainer = st.button('Entrainer le modèle')
    if entrainer :
        try:
            response = requests.get("http://api_model_container:5000/train/train_cbf").json()
            st.success(response)
        except Exception as e:
            st.error(f"Error: {e}")
            return None


def api_call_create_movie(title, year, youtubeid, genres_list, username, password):
    title_vf = title + ' (' + str(year) + ')'
    try:
        payload = {
            "title": title_vf,
            "genres": genres_list,
            "youtubeId": youtubeid
        }
        response = requests.post("http://api_model_container:5000/create-movie",
                                 auth=(username, password),
                                 json=payload).json()
        st.success('Le film a été ajouté')
    except Exception as e:
        st.error(f"Error: {e}")
        return None
    
def run_create_movie(username, password):
    title = st.text_input("Titre")
    year = st.number_input("Année de sortie", min_value=1900, max_value=2024)
    youtubeid = st.text_input("Lien Youtube du trailer")
    genres_list = list(pd.read_csv('assets/genres.csv').columns)
    selected_genres = st.multiselect("Genres", genres_list)
    selected_genres2 = '|'.join(selected_genres)
    
    create = st.button('Ajouter le film')

    if create and st.session_state.action == "Ajout d'un film":
        if title:
            api_call_create_movie(title, year, youtubeid, selected_genres2, username, password)
            requests.get("http://api_model_container:5000/train/train_cbf").json()
                
        else:
            st.warning("Merci de renseigner le titre et les genres")
            
def run_auth():
    with st.sidebar:
        st.write("### Authentification")
        username = st.text_input("Nom")
        password = st.text_input("Mot de passe", type="password")
        role = st.text_input("Rôle")
        
        login_button = st.button("Se connecter",on_click=reset)

    if login_button :
        if role and (username and password):
            response_admin = api_call_connect_admin(username, password,role)
            if response_admin and 'message' in response_admin:
                st.success(f"Bienvenue {username} !")
                st.session_state.login = True
                st.session_state.role = role
            else:
                st.session_state.login = False
                st.error(f"Nous n'avons pas pu vous connecter en tant que {role}. Vérifiez vos habilitations.")
        else:
            st.session_state.login = False
            st.warning("Renseignez votre nom et votre mot de passe")
    return username, password

def reset():
    selected_action = None

def run():
    if "action" not in st.session_state:
        st.session_state.action = None
    if "role" not in st.session_state :
        st.session_state.role = None
        
    username, password = run_auth()

    if 'login' in st.session_state:
        if st.session_state['login']== True:

            if st.session_state.role == "Plateforme":
                actions = ["Ajout d'un film"]
            elif st.session_state.role == 'Data':
                actions = ["Ajout d'un film", "Entrainement du modèle"]

            if 'actions' in locals() or 'actions' in globals() :
                global selected_action
                selected_action = st.selectbox("Select Action", actions)

                st.session_state.action = selected_action
            
            if st.session_state.action == "Ajout d'un film":
                run_create_movie(username, password)
            elif st.session_state.action == "Entrainement du modèle":
                api_call_entrainer_model()    
