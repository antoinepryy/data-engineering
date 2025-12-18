"""
Demo Speech-to-Text (STT)
Transcription de la parole en texte avec plusieurs moteurs
"""

import streamlit as st
import tempfile
import os
import json
from datetime import datetime
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment

from utils.cache import get_whisper_model, get_vosk_model
from utils.audio import save_uploaded_file, convert_to_wav, cleanup_temp_file


def render():
    """Affiche la demo Speech-to-Text."""
    st.header("Speech-to-Text (STT)")

    # Initialize session state
    if 'stt_audio_file' not in st.session_state:
        st.session_state.stt_audio_file = None

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Configuration STT")

        # Choix du moteur
        stt_engine = st.selectbox(
            "Moteur STT",
            ["Whisper (OpenAI)", "Google Speech Recognition", "Vosk (Offline)"]
        )

        # Upload audio ou enregistrement
        input_method = st.radio(
            "Methode d'entree",
            ["Uploader un fichier", "Enregistrer (simulation)"]
        )

        if input_method == "Uploader un fichier":
            uploaded_file = st.file_uploader(
                "Choisir un fichier audio",
                type=['wav', 'mp3', 'ogg', 'm4a'],
                key="stt_uploader"
            )

            if uploaded_file:
                st.session_state.stt_audio_file = save_uploaded_file(uploaded_file)
                st.audio(uploaded_file)

        else:
            st.info("Fonction d'enregistrement simulee (necessite acces microphone)")

            if st.button("Generer audio de test"):
                test_text = "Ceci est un test de reconnaissance vocale"
                tts = gTTS(text=test_text, lang='fr')
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                    tts.save(tmp_file.name)
                    st.session_state.stt_audio_file = tmp_file.name
                st.success("Audio de test genere!")
                st.audio(st.session_state.stt_audio_file)

            elif st.session_state.stt_audio_file and os.path.exists(st.session_state.stt_audio_file):
                st.audio(st.session_state.stt_audio_file)

        # Parametres selon le moteur
        if stt_engine == "Whisper (OpenAI)":
            model_size = st.selectbox("Taille du modele", ["tiny", "base", "small"])
            language = st.selectbox("Langue", ["auto", "fr", "en", "es"])

        elif stt_engine == "Google Speech Recognition":
            language = st.selectbox("Langue", ["fr-FR", "en-US", "es-ES"])

        elif stt_engine == "Vosk (Offline)":
            vosk_language = st.selectbox(
                "Langue Vosk",
                ["fr", "en"],
                format_func=lambda x: "Français" if x == "fr" else "English"
            )

        # Bouton de transcription
        if st.button("Transcrire", key="transcribe") and st.session_state.stt_audio_file:
            with st.spinner("Transcription en cours..."):
                try:
                    transcription = ""
                    audio_file = st.session_state.stt_audio_file

                    if stt_engine == "Whisper (OpenAI)":
                        model = get_whisper_model(model_size)

                        if language == "auto":
                            result = model.transcribe(audio_file)
                        else:
                            result = model.transcribe(audio_file, language=language)

                        transcription = result["text"]
                        detected_language = result.get("language", "unknown")
                        st.info(f"Langue detectee: {detected_language}")

                    elif stt_engine == "Google Speech Recognition":
                        r = sr.Recognizer()

                        wav_file = convert_to_wav(audio_file)

                        with sr.AudioFile(wav_file) as source:
                            audio_data = r.record(source)

                        transcription = r.recognize_google(audio_data, language=language)
                        cleanup_temp_file(wav_file)

                    elif stt_engine == "Vosk (Offline)":
                        import vosk

                        model = get_vosk_model(vosk_language)
                        rec = vosk.KaldiRecognizer(model, 16000)

                        wav_file = convert_to_wav(audio_file, output_sr=16000)

                        wf = open(wav_file, 'rb')
                        # Skip WAV header
                        wf.read(44)

                        results = []
                        while True:
                            data = wf.read(4000)
                            if len(data) == 0:
                                break
                            if rec.AcceptWaveform(data):
                                results.append(json.loads(rec.Result()))

                        results.append(json.loads(rec.FinalResult()))
                        transcription = " ".join([r.get('text', '') for r in results])

                        wf.close()
                        cleanup_temp_file(wav_file)

                    # Afficher les resultats
                    if transcription:
                        st.success("Transcription reussie!")
                        st.text_area("Resultat", transcription, height=150)

                        # Statistiques
                        words = transcription.split()
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Nombre de mots", len(words))
                        with col_b:
                            st.metric("Nombre de caracteres", len(transcription))

                        # Option de telechargement
                        st.download_button(
                            label="Telecharger transcription",
                            data=transcription,
                            file_name=f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )

                except Exception as e:
                    st.error(f"Erreur: {str(e)}")

    with col2:
        st.subheader("Concepts Theoriques")

        with st.expander("Technologies STT"):
            st.markdown("""
            ### Modeles Classiques
            - **HMM** (Hidden Markov Models)
            - **GMM** (Gaussian Mixture Models)
            - **DTW** (Dynamic Time Warping)

            ### Deep Learning
            - **RNN/LSTM**: Sequences temporelles
            - **Transformer**: Attention mechanism
            - **CTC** (Connectionist Temporal Classification)
            - **Whisper**: End-to-end transformer

            ### Metriques
            - **WER** (Word Error Rate)
            - **CER** (Character Error Rate)
            - **Latence** et temps reel
            """)

        with st.expander("Code Example"):
            st.code("""
# Example 1: Whisper
import whisper

model = whisper.load_model("base")
result = model.transcribe("audio.mp3")
print(result["text"])

# Example 2: Google Speech
import speech_recognition as sr

r = sr.Recognizer()
with sr.AudioFile("audio.wav") as source:
    audio = r.record(source)
text = r.recognize_google(audio, language='fr-FR')

# Example 3: Vosk (Offline)
import vosk
import json

model = vosk.Model("model")
rec = vosk.KaldiRecognizer(model, 16000)

# Process audio chunks
with open("audio.wav", 'rb') as f:
    while True:
        data = f.read(4000)
        if not data:
            break
        if rec.AcceptWaveform(data):
            print(json.loads(rec.Result()))
            """, language='python')
