"""
Application Streamlit pour les demonstrations de traitement vocal
Module 1 - Formation Data Engineering

Architecture modulaire avec demos separees
"""

import streamlit as st

# Import des styles
from styles import apply_styles, render_header

# Import des demos
from demos import tts, stt, s2s, analysis, realtime


# Configuration de la page
st.set_page_config(
    page_title="Module Traitement Vocal",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Appliquer les styles CSS
apply_styles(st)

# Afficher l'en-tete
render_header(st)

# Sidebar
with st.sidebar:
    st.title("Configuration")

    demo_mode = st.selectbox(
        "Choisir une demo",
        [
            "Text-to-Speech",
            "Speech-to-Text",
            "Speech-to-Speech",
            "Analyse Audio",
            "Enregistrement Live"
        ]
    )

    st.divider()

    # Informations systeme
    st.info("""
    **Ressources disponibles:**
    - Whisper (Tiny model)
    - Vosk (Offline STT)
    - gTTS (Google TTS)
    - Edge TTS (Microsoft)
    - pyttsx3 (Offline)
    - librosa (Analyse Audio)
    """)

# Router vers la demo selectionnee
if demo_mode == "Text-to-Speech":
    tts.render()

elif demo_mode == "Speech-to-Text":
    stt.render()

elif demo_mode == "Speech-to-Speech":
    s2s.render()

elif demo_mode == "Analyse Audio":
    analysis.render()

elif demo_mode == "Enregistrement Live":
    realtime.render()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>Module 1 - Traitement Vocal | Formation Data Engineering</p>
    <p>Propulse par Streamlit, Whisper, librosa et Edge-TTS</p>
</div>
""", unsafe_allow_html=True)
