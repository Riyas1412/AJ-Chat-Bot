# main.py
import streamlit as st
import google.generativeai as genai
import requests
import base64
import io
from PIL import Image
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

st.set_page_config(
    page_title="AJ Chatbot",
    page_icon="🤖",
    layout="wide",
)

# Function to encode image as base64
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("img2.png")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

page = st.selectbox("Select a section:", ["Text-Text", "Text-Image", "Image-Text"], index=0)

genai.configure(api_key=GENAI_API_KEY)

available_models = []
try:
    available_models = [model.name for model in genai.list_models()]
except Exception as e:
    st.error(f"Error fetching models: {e}")

selected_model = next((model for model in [
    "models/gemini-2.0-pro-exp",
    "models/gemini-1.5-pro-latest",
    "models/gemini-1.5-pro-002",
    "models/gemini-1.5-pro-001",
    "models/gemini-1.5-pro"
] if model in available_models), None)

if not selected_model:
    st.error("No valid Gemini model found. Check API key or enable models in Google AI Studio.")

custom_responses = {
    "who is your creator": "My creator is AJ Riyas!",
    "who built you": "AJ Riyas built me using AI technology!",
    "who owns you": "AJ Riyas owns me!"
}

def show_content(page):
    if page == "Text-Text":
        st.markdown("<h2 class='section-title'>Text-Text (Chatbot)</h2>", unsafe_allow_html=True)
        text = st.text_input("Enter your question:")
        if st.button("Send") and selected_model:
            try:
                user_question = text.lower().strip()
                response_text = custom_responses.get(user_question, None)
                if not response_text:
                    model = genai.GenerativeModel(selected_model)
                    chat = model.start_chat(history=[])
                    response = chat.send_message(text)
                    response_text = response.text
                st.write(response_text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    
    elif page == "Text-Image":
        st.markdown('<h2 class="section-title">Text-Image</h2>', unsafe_allow_html=True)
        API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}

        def query_image_generation(payload):
            response = requests.post(API_URL, headers=headers, json=payload)
            return response.content if response.status_code == 200 else None

        prompt = st.text_input("Enter prompt for image generation:")
        if st.button('Generate Image'):
            image_bytes = query_image_generation({"inputs": prompt})
            if image_bytes:
                image = Image.open(io.BytesIO(image_bytes))
                st.image(image)
            else:
                st.error("Failed to generate image. Try again!")

    elif page == "Image-Text":
        st.markdown('<h2 class="section-title">Image-Text</h2>', unsafe_allow_html=True)
        API_URL = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}

        def query_image_captioning(uploaded_file):
            response = requests.post(API_URL, headers=headers, files={"file": uploaded_file})
            return response.json() if response.status_code == 200 else None

        uploaded_file = st.file_uploader("Upload an image:", type=["jpg", "png"])
        if uploaded_file is not None and st.button("Generate Caption"):
            output = query_image_captioning(uploaded_file)
            if output and "generated_text" in output[0]:
                caption = output[0]['generated_text']
                st.markdown(f'<div class="caption">{caption}</div>', unsafe_allow_html=True)
            else:
                st.error("Failed to generate caption. Try again!")

show_content(page)
