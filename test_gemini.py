import google.generativeai as genai
import streamlit as st
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Say 'Gemini working' for nanoatmosphere.")

print(response.text)

