import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('API_KEY')

st.title("Welcome to AJ Chat")
genai.configure(api_key=api_key)
text = st.text_input("Enter your question")

if st.button("Click"):
    if not text.strip():
        st.write("Please enter a question!")
    else:
        model = genai.GenerativeModel('gemini-pro')
        chat = model.start_chat(history=[])
        response = chat.send_message(text)
        st.write(response.text)
