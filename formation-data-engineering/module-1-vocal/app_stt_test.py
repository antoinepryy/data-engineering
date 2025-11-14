"""
Test simple pour Speech-to-Text
"""

import streamlit as st
import tempfile
import os
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment

st.set_page_config(page_title="Test STT", page_icon="🎙️")

st.title("🎙️ Test Speech-to-Text")

# Créer un fichier audio exemple
if st.button("🎤 Créer un fichier audio exemple"):
    text = "Bonjour, ceci est un test de reconnaissance vocale. Comment allez-vous aujourd'hui?"
    
    # Générer avec gTTS
    tts = gTTS(text=text, lang='fr')
    
    # Sauvegarder dans session state
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        tts.save(tmp_file.name)
        
        # Lire le fichier
        with open(tmp_file.name, 'rb') as f:
            audio_bytes = f.read()
            
        st.session_state['example_audio'] = audio_bytes
        st.session_state['example_path'] = tmp_file.name
        st.success("✅ Fichier exemple créé!")

# Afficher l'audio si disponible
if 'example_audio' in st.session_state:
    st.audio(st.session_state['example_audio'], format='audio/mpeg')
    
    if st.button("🎯 Transcrire avec Google Speech Recognition"):
        try:
            # Convertir MP3 en WAV pour Speech Recognition
            audio = AudioSegment.from_mp3(st.session_state['example_path'])
            
            # Sauvegarder en WAV
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as wav_file:
                audio.export(wav_file.name, format='wav')
                wav_path = wav_file.name
            
            # Utiliser Speech Recognition
            r = sr.Recognizer()
            
            with sr.AudioFile(wav_path) as source:
                audio_data = r.record(source)
                
                # Essayer différentes langues
                st.write("Transcription en cours...")
                
                # Français
                try:
                    text_fr = r.recognize_google(audio_data, language='fr-FR')
                    st.success("**Transcription (FR):**")
                    st.write(text_fr)
                except Exception as e:
                    st.error(f"Erreur FR: {e}")
                
                # Anglais (pour tester)
                try:
                    text_en = r.recognize_google(audio_data, language='en-US')
                    st.info("**Transcription (EN):**")
                    st.write(text_en)
                except Exception as e:
                    st.error(f"Erreur EN: {e}")
            
            # Nettoyer
            os.unlink(wav_path)
            
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

st.divider()

# Upload de fichier
st.subheader("📤 Upload de fichier audio")

uploaded_file = st.file_uploader(
    "Choisir un fichier audio",
    type=['mp3', 'wav', 'ogg', 'm4a'],
    help="Formats supportés: MP3, WAV, OGG, M4A"
)

if uploaded_file is not None:
    # Afficher l'audio
    st.audio(uploaded_file)
    
    # Sauvegarder temporairement
    file_extension = uploaded_file.name.split('.')[-1]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    
    if st.button("🎯 Transcrire le fichier uploadé"):
        try:
            # Convertir en WAV si nécessaire
            if file_extension != 'wav':
                st.info(f"Conversion de {file_extension.upper()} vers WAV...")
                audio = AudioSegment.from_file(tmp_path)
                wav_path = tmp_path.replace(f'.{file_extension}', '.wav')
                audio.export(wav_path, format='wav')
            else:
                wav_path = tmp_path
            
            # Transcrire
            r = sr.Recognizer()
            
            with sr.AudioFile(wav_path) as source:
                st.info("Lecture du fichier audio...")
                audio_data = r.record(source)
                
                st.info("Transcription en cours...")
                
                # Sélection de la langue
                lang = st.selectbox(
                    "Langue",
                    ['fr-FR', 'en-US', 'es-ES', 'de-DE'],
                    key="lang_select"
                )
                
                text = r.recognize_google(audio_data, language=lang)
                
                st.success("✅ Transcription réussie!")
                st.text_area(
                    "Résultat",
                    value=text,
                    height=150
                )
                
                # Statistiques
                words = len(text.split())
                chars = len(text)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Mots", words)
                with col2:
                    st.metric("Caractères", chars)
                
                # Download
                st.download_button(
                    label="📥 Télécharger transcription",
                    data=text,
                    file_name="transcription.txt",
                    mime="text/plain"
                )
            
            # Nettoyer
            if file_extension != 'wav':
                os.unlink(wav_path)
            os.unlink(tmp_path)
            
        except sr.UnknownValueError:
            st.error("❌ Impossible de comprendre l'audio. Essayez avec un fichier plus clair.")
        except sr.RequestError as e:
            st.error(f"❌ Erreur avec le service Google: {e}")
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

# Test Whisper séparé
st.divider()
st.subheader("🔬 Test Whisper")

if st.button("Tester si Whisper fonctionne"):
    try:
        import whisper
        st.info("Chargement du modèle Whisper (tiny)...")
        model = whisper.load_model("tiny")
        st.success("✅ Whisper est installé et fonctionne!")
        
        # Info sur le modèle
        st.write("**Modèle chargé:** tiny (39M paramètres)")
        st.write("**Langues supportées:** 99+")
        
    except Exception as e:
        st.error(f"❌ Erreur Whisper: {str(e)}")
        st.info("Utilisation de Google Speech Recognition comme alternative")

# Info
with st.expander("ℹ️ Informations"):
    st.markdown("""
    ### Moteurs disponibles:
    
    1. **Google Speech Recognition**
       - ✅ Fonctionne sans clé API
       - ✅ Support multilingue
       - ⚠️ Nécessite internet
       - ⚠️ Limite de durée (~1 minute)
    
    2. **Whisper (OpenAI)**
       - ✅ Modèle local
       - ✅ Pas de limite de durée
       - ✅ Très précis
       - ⚠️ Plus lent
       - ⚠️ Nécessite plus de RAM
    
    ### Formats supportés:
    - MP3, WAV, OGG, M4A
    - Conversion automatique en WAV pour la transcription
    
    ### Conseils:
    - Audio clair sans bruit de fond
    - Parler distinctement
    - Fichiers < 10 MB recommandés
    """)