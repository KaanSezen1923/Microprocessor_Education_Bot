import streamlit as st
import requests
import os 
import google.generativeai as genai
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import speech_recognition as sr 

st.set_page_config(page_title="MicroMentor AI")
with st.sidebar:
    gemini_api_key=st.text_input("Enter Gemini Api Key",type="password")
    
    
API_URL="http://127.0.0.1:8000/ask"
    
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Konuşmaya başlayabilirsiniz...")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="tr-TR")
            st.success(f"Saptanan metin: {text}")
            return text
        except sr.UnknownValueError:
            st.error("Ses anlaşılamadı, lütfen tekrar deneyin.")
        except sr.RequestError as e:
            st.error(f"Ses tanıma servisiyle ilgili bir sorun oluştu: {e}")
        return None
    
    
def play_response_text(response_text, lang="tr"):
    tts = gTTS(text=response_text, lang=lang)
    tts.save("response.mp3")
    with open("response.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3")
    os.remove("response.mp3")

st.title("Microprocessor Education Bot")
st.write("This assistant is designed to answer your questions about microprocessors. You can type your questions in the box below.")


if "messages" not in st.session_state:
    st.session_state["messages"] = []


for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

record_audio=audio_recorder()
if user_query := st.chat_input("Soru yazın ve Enter'a basın..."):
    
    with st.chat_message("user"):
        st.write(user_query)

    
    st.session_state["messages"].append({"role": "user", "content": user_query})

    try:
        
       
        response=requests.post(API_URL,json={"question":user_query,"api_key":gemini_api_key})
        response_data=response.json()
        context=response_data.get("context", "Maalesef, sorunuza bir yanıt veremedim.")
        assistant_response = response_data.get("response", "Maalesef, sorunuza bir yanıt veremedim.")

       
        with st.chat_message("assistant"):
            st.write("**Yanıt:**")
            st.write(assistant_response)

        
        st.session_state["messages"].append({"role": "assistant", "content": assistant_response})

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
elif record_audio:
    user_query=recognize_speech()
    with st.chat_message("user"):
        st.write(user_query)

    
    st.session_state["messages"].append({"role": "user", "content": user_query})

    try:
        
       
        response=requests.post(API_URL,json={"question":user_query,"api_key":gemini_api_key})
        response_data=response.json()
        context=response_data.get("context", "Maalesef, sorunuza bir yanıt veremedim.")
        assistant_response = response_data.get("response", "Maalesef, sorunuza bir yanıt veremedim.")

       
        with st.chat_message("assistant"):
            st.write("**Yanıt:**")
            st.write(assistant_response)
            play_response_text(assistant_response)

        
        st.session_state["messages"].append({"role": "assistant", "content": assistant_response})

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
