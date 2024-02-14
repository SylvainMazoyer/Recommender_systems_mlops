import streamlit as st

st.set_page_config(
    page_title="Dataflix",
)


def run():

    if 'connect' not in st.session_state:
        st.session_state['connect'] = False

    if 'user' not in st.session_state:
        st.session_state['user'] = ""

    def callback_connect():
        st.session_state['connect'] = True


    if st.session_state['connect'] == False :
        col1, col2 = st.columns([0.7,0.3])
        with col2:
            st.button('Se connecter', on_click=callback_connect)

    if st.session_state['connect'] == True :
        col1, col2 = st.columns([0.7,0.3])
        with col2:
            st.session_state['user'] = st.text_input("User ID", key='uid', placeholder="Your ID", label_visibility="collapsed")
    
    if st.session_state['user'] == "":
        st.image("assets/dataflix.png")

    else:

        # si le user n'est pas connu :
        st.write('Bienvenue ', st.session_state['user'], '!')

        st.write('Les films les plus populaires')
        film1, film2, film3 = st.columns(3)

        with film1:
            st.header("Toy story")
            st.video("https://www.youtube.com/watch?v=K26_sDKnvMU")

        with film2:
            st.header("Babe")
            st.video("https://www.youtube.com/watch?v=tVxeoUtVF0o")






if __name__ == "__main__":
    run()
