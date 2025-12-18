"""
Demo Speech-to-Speech Translation
Pipeline complet: Audio -> STT -> Translation -> TTS
"""

import streamlit as st
import tempfile
import os
from datetime import datetime
from gtts import gTTS
import asyncio
import edge_tts
from deep_translator import GoogleTranslator

from utils.cache import get_whisper_model
from utils.audio import save_uploaded_file, cleanup_temp_file


def render():
    """Affiche la demo Speech-to-Speech Translation."""
    st.header("Speech-to-Speech Translation")

    # Initialize session state
    if 's2s_audio_file' not in st.session_state:
        st.session_state.s2s_audio_file = None

    st.info("Cette demo combine STT -> Translation -> TTS pour creer un traducteur vocal")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("1. Entree Audio")

        uploaded_file = st.file_uploader(
            "Fichier audio source",
            type=['wav', 'mp3', 'ogg'],
            key="s2s_uploader"
        )

        if uploaded_file:
            st.session_state.s2s_audio_file = save_uploaded_file(uploaded_file)
            st.audio(uploaded_file)

        source_lang = st.selectbox(
            "Langue source",
            ["auto", "fr", "en", "es", "de", "it"]
        )

    with col2:
        st.subheader("2. Configuration")

        target_lang = st.selectbox(
            "Langue cible",
            ["en", "fr", "es", "de", "it", "ja", "zh"]
        )

        voice_gender = st.radio("Genre de voix", ["Femme", "Homme"])

        with st.expander("Options avancees"):
            st.checkbox("Conserver le timing original")
            st.checkbox("Ameliorer la qualite audio")

    with col3:
        st.subheader("3. Resultat")

        if st.button("Traduire", key="translate_speech") and st.session_state.s2s_audio_file:
            with st.spinner("Traitement en cours..."):
                try:
                    audio_path = st.session_state.s2s_audio_file

                    # Etape 1: STT
                    with st.status("Transcription...", expanded=True) as status:
                        model = get_whisper_model("tiny")
                        if source_lang == "auto":
                            result = model.transcribe(audio_path)
                        else:
                            result = model.transcribe(audio_path, language=source_lang)

                        source_text = result["text"]
                        detected_lang = result.get("language", "unknown")

                        st.write(f"**Texte detecte** ({detected_lang}):")
                        st.write(source_text)
                        status.update(label="Transcription terminee", state="complete")

                    # Etape 2: Translation
                    with st.status("Traduction...", expanded=True) as status:
                        if source_lang == "auto":
                            src = detected_lang
                        else:
                            src = source_lang

                        translator = GoogleTranslator(source=src, target=target_lang)
                        translated_text = translator.translate(source_text)

                        st.write(f"**Texte traduit** ({target_lang}):")
                        st.write(translated_text)
                        status.update(label="Traduction terminee", state="complete")

                    # Etape 3: TTS
                    with st.status("Synthese vocale...", expanded=True) as status:
                        voice_map = {
                            'fr': {'Femme': 'fr-FR-DeniseNeural', 'Homme': 'fr-FR-HenriNeural'},
                            'en': {'Femme': 'en-US-AriaNeural', 'Homme': 'en-US-GuyNeural'},
                            'es': {'Femme': 'es-ES-ElviraNeural', 'Homme': 'es-ES-AlvaroNeural'},
                            'de': {'Femme': 'de-DE-KatjaNeural', 'Homme': 'de-DE-ConradNeural'},
                            'it': {'Femme': 'it-IT-ElsaNeural', 'Homme': 'it-IT-DiegoNeural'},
                        }

                        if target_lang in voice_map:
                            voice = voice_map[target_lang][voice_gender]

                            async def generate_tts():
                                communicate = edge_tts.Communicate(translated_text, voice)
                                output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                                await communicate.save(output_file.name)
                                return output_file.name

                            output_audio = asyncio.run(generate_tts())
                        else:
                            tts = gTTS(text=translated_text, lang=target_lang)
                            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                            tts.save(output_file.name)
                            output_audio = output_file.name

                        status.update(label="Synthese terminee", state="complete")

                    # Afficher le resultat
                    st.success("Traduction vocale reussie!")
                    st.audio(output_audio, format='audio/mp3')

                    # Telechargement
                    with open(output_audio, 'rb') as f:
                        audio_bytes = f.read()

                    st.download_button(
                        label="Telecharger l'audio traduit",
                        data=audio_bytes,
                        file_name=f"translation_{target_lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                        mime="audio/mp3"
                    )

                    # Nettoyage
                    cleanup_temp_file(output_audio)

                except Exception as e:
                    st.error(f"Erreur: {str(e)}")

    # Pipeline diagram
    st.divider()
    st.subheader("Architecture du Pipeline")

    st.mermaid("""
    graph LR
        A[Audio Source] --> B[STT/Whisper]
        B --> C[Texte Source]
        C --> D[Traduction API]
        D --> E[Texte Traduit]
        E --> F[TTS Engine]
        F --> G[Audio Traduit]

        style A fill:#f9f,stroke:#333,stroke-width:2px
        style G fill:#9f9,stroke:#333,stroke-width:2px
    """)
