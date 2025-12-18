"""
Demo Text-to-Speech (TTS)
Conversion de texte en parole avec plusieurs moteurs
"""

import streamlit as st
import tempfile
import os
from datetime import datetime
from gtts import gTTS
import asyncio
import edge_tts

from utils.cache import get_pyttsx3_engine


def render():
    """Affiche la démo Text-to-Speech."""
    st.header("Text-to-Speech (TTS)")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Configuration TTS")

        # Choix du moteur
        tts_engine = st.selectbox(
            "Moteur TTS",
            ["pyttsx3 (Offline)", "gTTS (Google)", "Edge-TTS (Microsoft)"]
        )

        # Texte à convertir
        text_input = st.text_area(
            "Texte a convertir",
            value="Bonjour et bienvenue dans la formation Data Engineering. "
                  "Aujourd'hui, nous allons explorer le traitement vocal avec Python.",
            height=100
        )

        # Paramètres selon le moteur
        if tts_engine == "pyttsx3 (Offline)":
            pyttsx3_lang = st.selectbox(
                "Langue",
                ["fr", "en"],
                format_func=lambda x: "Français" if x == "fr" else "English"
            )
            rate = st.slider("Vitesse (mots/min)", 100, 300, 200)
            volume = st.slider("Volume", 0.0, 1.0, 0.9)

        elif tts_engine == "gTTS (Google)":
            lang = st.selectbox("Langue", ["fr", "en", "es", "de", "it"])
            slow = st.checkbox("Parler lentement")

        elif tts_engine == "Edge-TTS (Microsoft)":
            voice = st.selectbox(
                "Voix",
                ["fr-FR-HenriNeural", "fr-FR-DeniseNeural",
                 "en-US-AriaNeural", "en-US-GuyNeural"]
            )
            rate_option = st.selectbox("Vitesse", ["-50%", "-25%", "+0%", "+25%", "+50%"])

        # Bouton de génération
        if st.button("Generer Audio", key="generate_tts"):
            with st.spinner("Generation en cours..."):
                try:
                    audio_file = None

                    if tts_engine == "pyttsx3 (Offline)":
                        engine = get_pyttsx3_engine()
                        engine.setProperty('rate', rate)
                        engine.setProperty('volume', volume)

                        # Set voice based on language selection
                        voices = engine.getProperty('voices')
                        target_voice = None
                        for voice_obj in voices:
                            voice_lang = voice_obj.languages[0] if voice_obj.languages else ""
                            voice_id_lower = voice_obj.id.lower()
                            if pyttsx3_lang == "fr" and ("french" in voice_id_lower or "fr" in str(voice_lang).lower()):
                                target_voice = voice_obj.id
                                break
                            elif pyttsx3_lang == "en" and ("english" in voice_id_lower or "en" in str(voice_lang).lower()):
                                target_voice = voice_obj.id
                                break
                        if target_voice:
                            engine.setProperty('voice', target_voice)

                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                            engine.save_to_file(text_input, tmp_file.name)
                            engine.runAndWait()
                            audio_file = tmp_file.name

                    elif tts_engine == "gTTS (Google)":
                        tts = gTTS(text=text_input, lang=lang, slow=slow)
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                            tts.save(tmp_file.name)
                            audio_file = tmp_file.name

                    elif tts_engine == "Edge-TTS (Microsoft)":
                        async def generate_edge_tts():
                            communicate = edge_tts.Communicate(text_input, voice, rate=rate_option)
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                                await communicate.save(tmp_file.name)
                                return tmp_file.name

                        audio_file = asyncio.run(generate_edge_tts())

                    # Afficher le lecteur audio
                    if audio_file and os.path.exists(audio_file):
                        st.success("Audio genere avec succes!")
                        st.audio(audio_file, format='audio/mp3')

                        # Option de téléchargement
                        with open(audio_file, 'rb') as f:
                            audio_bytes = f.read()
                        st.download_button(
                            label="Telecharger l'audio",
                            data=audio_bytes,
                            file_name=f"tts_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                            mime="audio/mp3"
                        )

                        # Nettoyage
                        os.unlink(audio_file)

                except Exception as e:
                    st.error(f"Erreur: {str(e)}")

    with col2:
        st.subheader("Concepts Theoriques")

        with st.expander("Comment fonctionne le TTS ?"):
            st.markdown("""
            ### 1. Analyse du texte
            - Tokenisation et parsing
            - Detection de la ponctuation
            - Expansion des abreviations

            ### 2. Synthese phonetique
            - Conversion texte → phonemes
            - Application des regles de prononciation
            - Gestion des accents et intonations

            ### 3. Generation audio
            - **Synthese concatenative**: Assemblage de segments audio
            - **Synthese parametrique**: Modelisation du conduit vocal
            - **Synthese neuronale**: Reseaux de neurones (WaveNet, Tacotron)
            """)

        with st.expander("Code Example"):
            st.code("""
# Example 1: pyttsx3 (Offline)
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.say("Hello World")
engine.runAndWait()

# Example 2: gTTS (Online)
from gtts import gTTS

tts = gTTS(text='Bonjour', lang='fr')
tts.save("output.mp3")

# Example 3: Edge-TTS (Free Microsoft TTS)
import edge_tts
import asyncio

async def main():
    voice = "fr-FR-DeniseNeural"
    text = "Ceci est un test"

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("output.mp3")

asyncio.run(main())
            """, language='python')
