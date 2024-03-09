import streamlit as st
import requests

def run():   

    response = requests.get("http://api_model_container:5000/").json()["message"]
    st.write("Test appel API : ",response)
    st.write(requests.get("http://api_model_container:5000/predict/rand_model").json())



if __name__ == "__main__":
    run()
