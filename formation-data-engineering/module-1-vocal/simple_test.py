import streamlit as st
from gtts import gTTS
import tempfile
import os

st.title("Test TTS Simple")

text = st.text_input("Texte:", value="Test audio")

if st.button("Générer"):
    try:
        # Generate with gTTS
        tts = gTTS(text=text, lang='fr')
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            temp_audio_file = tmp_file.name
        
        # Check file
        file_size = os.path.getsize(temp_audio_file)
        st.success(f"✅ Fichier généré: {file_size} bytes")
        
        # Display audio player
        with open(temp_audio_file, 'rb') as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')
            
        # Download button
        st.download_button(
            label="Télécharger",
            data=audio_bytes,
            file_name="audio.mp3",
            mime="audio/mp3"
        )
        
        # Clean up
        os.unlink(temp_audio_file)
        
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
