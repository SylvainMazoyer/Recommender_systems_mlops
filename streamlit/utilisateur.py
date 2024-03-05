import streamlit as st
import requests
import json
from streamlit_extras.grid import grid

sidebar_name = "Utilisateur"

# Affichage des 5 films recommandés via la méthode corresondant au endpoint fourni
def print_reco(titre, endpoint, username):
    my_grid = grid(1, 3, 2, vertical_align="center")
    my_grid.title(titre)

    r = json.loads(requests.get(f"http://127.0.0.1:8000/{endpoint}").json())
    for i in range(5) :
        with my_grid.expander(r[i]["title"], expanded=False):
            st.write("Genre : ", r[i]["genres"])
            st.video(r[i]["youtubeId"])
            st.button("Lancer le film", key=str(r[i]["movieId"])+"button", on_click=click_movie, args=(r[i]["movieId"],username,))
            st.slider('Votre avis sur le film',1,5,3,1,key=str(r[i]["movieId"])+"slider", on_change=click_note, args=(r[i]["movieId"],username,))

# Simule la visualisation d'un film
def click_movie(movie_id,username):
    st.write("movie watched : ",movie_id,username)
    #requests.post("http://127.0.0.1:8000/user_activity", 
    #                    headers={"Content-Type": "application/json"}, 
    #                    data=json.dumps({"username":username, "movieId":movie_id}) )
    

# Ajout d'une note à un film
def click_note(movie_id,username):
    st.write("movie rated : ",movie_id,username, st.session_state[str(movie_id)+"slider"])
    #requests.post("http://127.0.0.1:8000/user_activity", 
    #                    headers={"Content-Type": "application/json"}, 
    #                    data=json.dumps({"username":username, "movieId":movie_id,"rating":st.session_state[str(movie_id)+"slider"]}) )
    


@st.cache_data(ttl=60)
def api_call_create_user(username):
    response = requests.post("http://127.0.0.1:8000/create-user", 
                        headers={"Content-Type": "application/json"}, 
                        data=json.dumps({"name":username}) ).json()["message"]
    if 'api_call_create_user' not in st.session_state :
        st.session_state['api_call_create_user'] = response


def run():   
    form = st.form(key='my-form')
    username = form.text_input('Enter your name')
    submit = form.form_submit_button('Submit', on_click=api_call_create_user, args=(username,))

    if 'api_call_create_user' in st.session_state :
        if st.session_state['api_call_create_user'] == 'user already exists':
            print_reco('5 films aléatoires', 'predict/rand_model', username)
            print_reco('5 films aléatoires', 'predict/rand_model', username)


        elif st.session_state['api_call_create_user'] == 'user créé' : 
            print_reco('5 films aléatoires', 'predict/rand_model')


