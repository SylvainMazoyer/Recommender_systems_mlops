import streamlit as st
import requests
import json
from streamlit_extras.grid import grid
from requests.auth import HTTPBasicAuth


st.title("Projet de recommandation des films Dataflix")
st.sidebar.title("Sommaire")

pages=["Introduction", "Plateform", "Equipe_data_scientist"]
page=st.sidebar.radio("Aller vers", pages)

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
        
@st.cache_data(ttl=60)        
def api_call_connect_admin(endpoint, username, password):
    try:
        response = requests.get(f"http://127.0.0.1:8000/{endpoint}", 
                                auth=HTTPBasicAuth(username, password)).json()
        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return None

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
        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return None
    
def run_create_movie(username, password):
    title = st.text_input("Title")
    year = st.number_input("Year", min_value=1900, max_value=2024)
    genres = st.text_input("Genres (comma-separated)")
    
    create = st.button('Create movie')

    if create:
        if title != None and genres_list != [] :
            genres_list = genres.split(",")
            if api_call_create_movie(title, year, genres_list, username, password):
                st.success("Movie created successfully!")
        else:
            st.warning("Please fill title and genres")
            
def run_admin():   
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    plateform_button = st.button("Login as Admin")
    equuipe_ds_button = st.button("Login as Data Scientist")
    
    # Login button for "/admin" endpoint
    if plateform_button :
        if username and password:
            response_admin = api_call_connect_admin("admin", username, password)
            if response_admin and 'message' in response_admin:
                st.success(response_admin['message'])
                # Clear username and password fields after successful login
                st.switch_page("pages/page1.py")
            else:
                st.error("Failed to authenticate as admin. Please check your credentials.")
        else:
            st.warning("Please provide both username and password for admin.")

    # Login button for "/equipe_ds" endpoint
    if equuipe_ds_button :
        if username and password:
            response_ds = api_call_connect_admin("equipe_ds", username, password)
            if response_ds and 'message' in response_ds:
                st.success(response_ds['message'])
            else:
                st.error("Failed to authenticate as data scientist. Please check your credentials.")
        else:
            st.warning("Please provide both username and password for data scientist.")
 
if page == pages[0] : 
    # Config de la page 
    # st.set_page_config(page_title="Dataflix",)  
    st.write("### Welcome")

if page == pages[1] :
    run()
    
    
if page == pages[2] :
    st.write("Data scientist teams Authentication")
    run_admin()
