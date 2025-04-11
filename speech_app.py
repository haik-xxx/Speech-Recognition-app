import streamlit as st
import speech_recognition as sr
from deepgram import Deepgram
import asyncio

# Sidebar for API and Language selection
def select_api():
    apis = ["Google Speech Recognition", "Deepgram"]
    st.sidebar.title("Select Speech Recognition API")
    selected_api = st.sidebar.selectbox("Choose API:", apis)
    return selected_api

def select_language():
    languages = {
        "English": "en-US",
        "Spanish": "es-ES",
        "French": "fr-FR"
    }
    st.sidebar.title("Select Language")
    selected_language = st.sidebar.radio("Choose Language:", list(languages.keys()))
    return languages[selected_language]

selected_api = select_api()
language_code = select_language()

st.write(f"Using: {selected_api}")
st.write(f"Language Code: {language_code}")

# Main section: File upload and transcription
audio_file = st.file_uploader("Upload your audio file (WAV format recommended)", type=["wav"])

async def transcribe_with_deepgram(audio_file, language_code):
    dg_client = Deepgram("71b345db-e23e-4ec7-83ea-1cd1d463a1a8") 
    with open(audio_file, 'rb') as audio:
        source = {'buffer': audio, 'mimetype': 'audio/wav'}
        response = await dg_client.transcription.prerecorded(source, {'punctuate': True, 'language': language_code})
        return response['results']['channels'][0]['alternatives'][0]['transcript']

def transcribe_speech(audio_file, selected_api, language_code):
    try:
        if selected_api == "Google Speech Recognition":
            # Google Speech Recognition Logic
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_file) as source:
                st.text("Processing...")
                audio = recognizer.record(source)
                transcription = recognizer.recognize_google(audio, language=language_code)
                return transcription

        elif selected_api == "Deepgram":
            # Deepgram API Logic
            transcription = asyncio.run(transcribe_with_deepgram(audio_file, language_code))
            return transcription

        else:
            raise Exception("Invalid API Selection.")

    except FileNotFoundError:
        st.error("Error: The audio file could not be found. Please try again.")
    except sr.UnknownValueError:
        st.error("Error: Could not understand the audio.")
    except sr.RequestError as e:
        st.error(f"API Error: {e}")
    except Exception as e:
        st.error(f"Unexpected error occurred: {str(e)}")

if audio_file:
    transcription = transcribe_speech(audio_file.name, selected_api, language_code)
    if transcription:
        st.success("Transcription Successful!")
        st.text_area("Transcribed Text", transcription, height=150)

        # Saving transcription to file
        def save_to_file(transcription):
            file_name = st.text_input("Enter file name to save transcription (e.g., transcription.txt):")
            if st.button("Save Transcription"):
                if file_name:
                    with open(file_name, "w") as file:
                        file.write(transcription)
                    st.success(f"Transcription saved as {file_name}")
                else:
                    st.error("Please provide a file name!")

        save_to_file(transcription)