import streamlit as st

def add_character():
    st.session_state.characters.append({
        "name": "",
        "age": "",
        "height": "",
        "skin_tone": ""
    })






