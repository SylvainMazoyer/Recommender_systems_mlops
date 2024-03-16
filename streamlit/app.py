import streamlit as st
import requests
import base64
from requests.auth import HTTPBasicAuth

def api_call_admin(username,password,role):
    str_to_encode = username + ':' + password
    encoded_str = "Basic " + base64.b64encode(str_to_encode.encode()).decode()
    response = requests.get(f'http://api_model_container:5000/admin/{role}', 
                        headers={"Authorization": encoded_str})
    st.write(response.content)

def run():   

    response = requests.get("http://api_model_container:5000/").json()["message"]
    st.write("Test appel API : ",response)
    st.write(requests.get("http://api_model_container:5000/predict/rand_model").json())
    response2 = requests.post("http://api_model_container:5000/create-user", json={'name': 'Charles'}).json()
    st.write("Test appel API create user : ", response2['message'], response2['userId'])
    response3 = requests.post("http://api_model_container:5000/user_activity", json={'userId': '1', 'movieId':9999900})
    st.write(response3.content)
    response3bis = requests.post("http://api_model_container:5000/user_activity", json={'userId': '1', 'movieId':5})
    st.write(response3bis.content)
    response4 = requests.post("http://api_model_container:5000/create-movie", json={'title': 'Lalalala', 'genres':'Comedy'},auth=("Nolwenn", "54321"))
    st.write(response4.content)
    response4bis = requests.post("http://api_model_container:5000/create-movie", json={'title': 'Toy Story (1995)', 'genres':'Comedy'},auth=("Nolwenn","54321"))
    st.write(response4bis.content)



    form = st.form(key='my-form')
    username = form.text_input('Enter your name')
    password = form.text_input('Enter your password')
    role = form.text_input('Enter your role')
    submit = form.form_submit_button('Submit', on_click=api_call_admin, args=(username,password,role))




if __name__ == "__main__":
    run()
