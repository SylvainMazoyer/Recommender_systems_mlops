import streamlit as st
import requests
import json
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from streamlit_extras.grid import grid

def print_reco(titre, endpoint):
    my_grid = grid(1, 3, 2, vertical_align="center")
    my_grid.title(titre)

    r = json.loads(requests.get(f"http://127.0.0.1:8000/{endpoint}").json())
    for i in range(5) :
        with my_grid.expander(r[i]["title"], expanded=False):
            st.video("https://www.youtube.com/watch?v=K26_sDKnvMU")

st.set_page_config(
    page_title="Dataflix",
)

with open('streamlit/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )


def run():

    if st.session_state["authentication_status"] is None:
        st.image("streamlit/assets/dataflix.png")

    # Formulaire d'authentification sur la plateforme de streaming
    name, authentication_status, username = authenticator.login('main')

    # Si la personne est authentifiée : 
    if st.session_state["authentication_status"]:
        col1, col2 = st.columns([0.85,0.15])
        with col2:
            authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')

        print_reco("5 films aléatoires", "predict/rand_model")
        #print_reco("5 derniers films ajoutés", "predict/last")
        #print_reco("5 films selon les films que vous avez aimés", "predict/content_model")
        #print_reco("5 films aimés par des utilisateurs ayant les mêmes goûts que vous", "predict/social")



    # Si l'authentification a échoué
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')


if __name__ == "__main__":
    run()
