from collections import OrderedDict
import streamlit as st
import admin, utilisateur


st.set_page_config(
    page_title='Dataflix',
    page_icon="https://datascientest.com/wp-content/uploads/2020/08/new-logo.png",
)


TABS = OrderedDict(
    [
        (utilisateur.sidebar_name, utilisateur),
        (admin.sidebar_name, admin),
    ]
)

def run():
    st.sidebar.image(
        "https://dst-studio-template.s3.eu-west-3.amazonaws.com/logo-datascientest.png",
        width=200,
    )
    st.title("Projet de recommandation des films")
    st.sidebar.title("Sommaire")

    page_name = st.sidebar.radio("allez vers", TABS.keys())
    st.sidebar.markdown("---")
    
    tab = TABS[page_name]
    tab.run()


if __name__ == "__main__":
    run()