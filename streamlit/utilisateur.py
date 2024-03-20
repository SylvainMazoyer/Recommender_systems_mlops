import streamlit as st
import requests
import json
from streamlit_extras.grid import grid

sidebar_name = "Utilisateur"

def api_call_admin(username,password,role):
    str_to_encode = username + ':' + password
    encoded_str = "Basic " + base64.b64encode(str_to_encode.encode()).decode()
    response = requests.get(f'http://api_model_container:5000/admin/{role}', 
                        headers={"Authorization": encoded_str})
    st.write(response.content)

# Affichage des 5 films recommandés via la méthode corresondant au endpoint fourni
def print_reco(titre, endpoint, username, userId):
    response = json.loads(requests.get(f"http://api_model_container:5000/{endpoint}",json={"name": username, "id": userId}).json())

    if response == {"Last viewed movie": "None"}:
        pass

    else: 
        my_grid = grid(1, 3, 2, vertical_align="center")
        my_grid.title(titre)
        
        for movie in response :
            with my_grid.expander(movie["title"], expanded=False):
                st.write("Genre : ", movie["genres"])
                st.video(movie["youtubeid"])
                st.button("Lancer le film", key=str(movie["movieid"])+"button", on_click=click_movie, args=(movie["movieid"],userId,))
                st.slider('Votre avis sur le film',1,5,3,1,key=str(movie["movieid"])+"slider", on_change=click_note, args=(movie["movieid"],userId,))

# Simule la visualisation d'un film
def click_movie(movie_id,userid):
    requests.post("http://api_model_container:5000/user_activity", 
                        json={"userId":userid, "movieId":movie_id})
    

# Ajout d'une note à un film
def click_note(movie_id,userid):
    requests.post("http://api_model_container:5000/user_activity", 
                        json={"userId":userid, "movieId":movie_id,"rating":st.session_state[str(movie_id)+"slider"]})
    

@st.cache_data(ttl=6000)
def api_call_create_user(username):
    response = requests.post("http://api_model_container:5000/create-user", 
                        json = {'name': username}).json()
    st.session_state['userId'] = response["userId"]

def run():   

    response = requests.get("http://api_model_container:5000/").json()["message"]
    st.write("Test appel API : ",response)

    st.image('assets/dataflix.png')

    username = st.text_input('Enter your username')
    
    if username != "": 
        api_call_create_user(username)
        print_reco('5 films aléatoires', 'predict/rand_model', username, st.session_state["userId"] )
        print_reco("D'après ce que vous avez vu récemment", 'predict/predict_CBF_model', username, st.session_state["userId"] )