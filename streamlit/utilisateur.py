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

# Simule la visualisation d'un film
def click_movie(movie_id,userid):
    st.write("début click_movie")
    requests.post("http://api_model_container:5000/user_activity", 
                        json={"userId":userid, "movieId":movie_id})
    

# Ajout d'une note à un film
def click_note(movie_id,userid):
    requests.post("http://api_model_container:5000/user_activity", 
                        json={"userId":userid, "movieId":movie_id,"rating":st.session_state[str(movie_id)+"slider"]})
    


# Affichage des 5 films recommandés via la méthode corresondant au endpoint fourni
def print_reco(titre, endpoint, username, userId, session):

    if st.session_state["new_reco"]==True:
        st.session_state[session]  = json.loads(requests.get(f"http://api_model_container:5000/{endpoint}",json={"name": username, "id": userId}).json())

    if st.session_state[session] == {"Last viewed movie": "None"}:
        pass

    elif st.session_state[session] is not None: 
        my_grid = grid(1, 3, 2, vertical_align="center")
        my_grid.title(titre)
        
        for movie in st.session_state[session]  :
            with my_grid.expander(movie["title"], expanded=True):
                st.write("Genre : ", movie["genres"])
                st.video(movie["youtubeid"])
                st.button("Lancer le film", key=str(movie["movieid"])+"button", on_click=click_movie, args=(movie["movieid"],userId))
                st.slider('Votre avis sur le film',1,5,3,1,key=str(movie["movieid"])+"slider", on_change=click_note, args=(movie["movieid"],userId))
        
    st.session_state["new_reco"]=False


# @st.cache_data(ttl=6000)
def api_call_create_user(username):
    response = requests.post("http://api_model_container:5000/create-user", 
                        json = {'name': username}).json()
    st.session_state['userId'] = response["userId"]

def run():   

    st.image('assets/dataflix.png')

    username = st.text_input('Enter your username')
    api_call_create_user(username)

    if "new_reco" not in st.session_state : 
        st.session_state["new_reco"] = True

    if "rand_model" not in st.session_state:
        st.session_state["rand_model"] = None

    if "CBF_model" not in st.session_state:
        st.session_state["CBF_model"] = None

    # Ajouter un bouton pour regénérer des reco et sinon les mêmes sont conservées
    
    if username != "": 
        print_reco('5 films aléatoires', 'predict/rand_model', username, st.session_state["userId"] ,"rand_model")
        print_reco("D'après ce que vous avez vu récemment", 'predict/predict_CBF_model', username, st.session_state["userId"],"CBF_model" )

