"""
Demo Enregistrement Live
Enregistrement depuis le microphone et transcription
"""

import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime

from utils.cache import get_whisper_model
from utils.audio import save_audio_input, load_audio, get_audio_info, cleanup_temp_file
from utils.visualization import create_waveform, extract_audio_features


def render():
    """Affiche la demo Enregistrement Live."""
    st.header("Enregistrement Live")

    st.info("Utilisez votre microphone pour enregistrer puis analysez ou transcrivez l'audio.")

    # Initialize session state
    if 'realtime_audio_file' not in st.session_state:
        st.session_state.realtime_audio_file = None
    if 'realtime_transcription' not in st.session_state:
        st.session_state.realtime_transcription = ""

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Enregistrement")

        # Widget d'enregistrement natif Streamlit
        audio_data = st.audio_input(
            "Cliquez pour enregistrer",
            key="realtime_recorder"
        )

        if audio_data:
            st.session_state.realtime_audio_file = save_audio_input(audio_data)
            st.audio(audio_data)

            # Afficher les infos
            try:
                info = get_audio_info(st.session_state.realtime_audio_file)
                st.success(f"Enregistrement: {info['duration']:.1f}s @ {info['sample_rate']}Hz")
            except Exception:
                pass

    with col2:
        st.subheader("Actions")

        if st.session_state.realtime_audio_file:
            # Choix du modele Whisper
            model_size = st.selectbox(
                "Modele Whisper",
                ["tiny", "base", "small"],
                help="tiny = plus rapide, small = plus precis"
            )

            language = st.selectbox(
                "Langue",
                ["auto", "fr", "en", "es", "de"]
            )

            col_a, col_b = st.columns(2)

            with col_a:
                transcribe_btn = st.button("Transcrire", type="primary", use_container_width=True)

            with col_b:
                analyze_btn = st.button("Analyser", use_container_width=True)

            if transcribe_btn:
                with st.spinner("Transcription en cours..."):
                    try:
                        model = get_whisper_model(model_size)

                        if language == "auto":
                            result = model.transcribe(st.session_state.realtime_audio_file)
                        else:
                            result = model.transcribe(
                                st.session_state.realtime_audio_file,
                                language=language
                            )

                        st.session_state.realtime_transcription = result["text"]
                        detected_lang = result.get("language", "?")

                        st.success(f"Transcription terminee (langue: {detected_lang})")

                    except Exception as e:
                        st.error(f"Erreur: {str(e)}")

            if analyze_btn:
                with st.spinner("Analyse en cours..."):
                    try:
                        y, sr = load_audio(st.session_state.realtime_audio_file)
                        features = extract_audio_features(y, sr)

                        st.success("Analyse terminee!")

                        # Metriques rapides
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.metric("Energie", f"{features['rms_mean']:.4f}")
                        with m2:
                            if features.get('pitch_mean'):
                                st.metric("Pitch", f"{features['pitch_mean']:.0f} Hz")
                            else:
                                st.metric("Pitch", "N/A")
                        with m3:
                            st.metric("ZCR", f"{features['zcr_mean']:.4f}")

                        # Waveform
                        fig = create_waveform(y, sr, title="Forme d'onde de l'enregistrement")
                        st.pyplot(fig)
                        plt.close(fig)

                    except Exception as e:
                        st.error(f"Erreur: {str(e)}")

        else:
            st.warning("Enregistrez d'abord un audio avec le bouton ci-dessus.")

    # Afficher la transcription
    if st.session_state.realtime_transcription:
        st.divider()
        st.subheader("Transcription")

        st.text_area(
            "Resultat",
            st.session_state.realtime_transcription,
            height=150
        )

        # Stats
        words = st.session_state.realtime_transcription.split()
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Mots", len(words))
        with c2:
            st.metric("Caracteres", len(st.session_state.realtime_transcription))

        # Telecharger
        st.download_button(
            "Telecharger la transcription",
            st.session_state.realtime_transcription,
            file_name=f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

    # Section educative
    st.divider()
    with st.expander("Comment fonctionne l'enregistrement web ?"):
        st.markdown("""
        ### Capture Audio dans le Navigateur

        **Technologies utilisees:**
        - `MediaRecorder API` : Capture le flux audio du microphone
        - `WebRTC` : Pour le streaming temps reel (non utilise ici)
        - `st.audio_input` : Widget Streamlit natif

        ### Pipeline de traitement:
        ```
        Microphone → MediaRecorder → Blob audio → Upload serveur → Whisper STT → Texte
        ```

        ### Limitations:
        - Necessite l'autorisation du navigateur pour le microphone
        - L'audio est traite apres l'enregistrement (pas en temps reel)
        - Qualite dependante du materiel

        ### Pour aller plus loin:
        - `streamlit-webrtc` pour le streaming temps reel
        - `Silero VAD` pour la detection d'activite vocale
        - `faster-whisper` pour une transcription plus rapide
        """)

    with st.expander("Code Example - Enregistrement et Transcription"):
        st.code("""
# Avec Streamlit (simple)
import streamlit as st
import whisper

# Enregistrement
audio = st.audio_input("Enregistrer")

if audio:
    # Sauvegarder
    with open("recording.wav", "wb") as f:
        f.write(audio.getvalue())

    # Transcrire
    model = whisper.load_model("tiny")
    result = model.transcribe("recording.wav")
    st.write(result["text"])

# ---

# Avec PyAudio (avance - hors navigateur)
import pyaudio
import wave

# Configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True, frames_per_buffer=CHUNK)

frames = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

stream.stop_stream()
stream.close()
p.terminate()

# Sauvegarder
wf = wave.open("output.wav", 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
        """, language='python')
