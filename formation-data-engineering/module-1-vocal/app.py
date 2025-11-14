"""
Application Streamlit pour les démonstrations de traitement vocal
Module 1 - Formation Data Engineering
"""

import streamlit as st
import pyttsx3
from gtts import gTTS
import speech_recognition as sr
import whisper
import tempfile
import os
from datetime import datetime
import pandas as pd
import numpy as np
from deep_translator import GoogleTranslator
import asyncio
import edge_tts
import soundfile as sf
from pydub import AudioSegment
from pydub.playback import play
import io
import base64

# Configuration de la page
st.set_page_config(
    page_title="Module Traitement Vocal",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-header {
        text-align: center;
        padding: 2rem;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .demo-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🎤 Module 1: Traitement Vocal</h1>
    <p>Text-to-Speech | Speech-to-Text | Speech-to-Speech</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    demo_mode = st.selectbox(
        "Choisir une démo",
        ["Text-to-Speech", "Speech-to-Text", "Speech-to-Speech", "Analyse Audio", "Exercices"]
    )
    
    st.divider()
    
    # Informations système
    st.info("""
    **Ressources disponibles:**
    - Whisper (Tiny model)
    - Vosk (Offline STT)
    - gTTS (Google TTS)
    - Edge TTS (Microsoft)
    - pyttsx3 (Offline)
    """)

# ============================================================================
# DEMO 1: TEXT-TO-SPEECH
# ============================================================================
if demo_mode == "Text-to-Speech":
    st.header("🔊 Text-to-Speech (TTS)")
    
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
            "Texte à convertir",
            value="Bonjour et bienvenue dans la formation Data Engineering. "
                  "Aujourd'hui, nous allons explorer le traitement vocal avec Python.",
            height=100
        )
        
        # Paramètres selon le moteur
        if tts_engine == "pyttsx3 (Offline)":
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
            rate = st.selectbox("Vitesse", ["-50%", "-25%", "+0%", "+25%", "+50%"])
        
        # Bouton de génération
        if st.button("🎵 Générer Audio", key="generate_tts"):
            with st.spinner("Génération en cours..."):
                try:
                    audio_file = None
                    
                    if tts_engine == "pyttsx3 (Offline)":
                        # pyttsx3 implementation
                        engine = pyttsx3.init()
                        engine.setProperty('rate', rate)
                        engine.setProperty('volume', volume)
                        
                        # Sauvegarder dans un fichier temporaire
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                            engine.save_to_file(text_input, tmp_file.name)
                            engine.runAndWait()
                            audio_file = tmp_file.name
                    
                    elif tts_engine == "gTTS (Google)":
                        # gTTS implementation
                        tts = gTTS(text=text_input, lang=lang, slow=slow)
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                            tts.save(tmp_file.name)
                            audio_file = tmp_file.name
                    
                    elif tts_engine == "Edge-TTS (Microsoft)":
                        # Edge-TTS implementation (async)
                        async def generate_edge_tts():
                            communicate = edge_tts.Communicate(text_input, voice, rate=rate)
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                                await communicate.save(tmp_file.name)
                                return tmp_file.name
                        
                        audio_file = asyncio.run(generate_edge_tts())
                    
                    # Afficher le lecteur audio
                    if audio_file and os.path.exists(audio_file):
                        st.success("✅ Audio généré avec succès!")
                        st.audio(audio_file, format='audio/mp3')
                        
                        # Option de téléchargement
                        with open(audio_file, 'rb') as f:
                            audio_bytes = f.read()
                        st.download_button(
                            label="📥 Télécharger l'audio",
                            data=audio_bytes,
                            file_name=f"tts_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                            mime="audio/mp3"
                        )
                        
                        # Nettoyage
                        os.unlink(audio_file)
                        
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
    
    with col2:
        st.subheader("📚 Concepts Théoriques")
        
        with st.expander("Comment fonctionne le TTS ?"):
            st.markdown("""
            ### 1. Analyse du texte
            - Tokenisation et parsing
            - Détection de la ponctuation
            - Expansion des abréviations
            
            ### 2. Synthèse phonétique
            - Conversion texte → phonèmes
            - Application des règles de prononciation
            - Gestion des accents et intonations
            
            ### 3. Génération audio
            - **Synthèse concatenative**: Assemblage de segments audio
            - **Synthèse paramétrique**: Modélisation du conduit vocal
            - **Synthèse neuronale**: Réseaux de neurones (WaveNet, Tacotron)
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

# ============================================================================
# DEMO 2: SPEECH-TO-TEXT
# ============================================================================
elif demo_mode == "Speech-to-Text":
    st.header("🎙️ Speech-to-Text (STT)")
    
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
            "Méthode d'entrée",
            ["📁 Uploader un fichier", "🎤 Enregistrer (simulation)"]
        )
        
        audio_file = None
        
        if input_method == "📁 Uploader un fichier":
            uploaded_file = st.file_uploader(
                "Choisir un fichier audio",
                type=['wav', 'mp3', 'ogg', 'm4a']
            )
            
            if uploaded_file:
                # Sauvegarder temporairement
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{uploaded_file.name.split(".")[-1]}') as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    audio_file = tmp_file.name
                
                st.audio(uploaded_file)
        
        else:
            st.info("🎤 Fonction d'enregistrement simulée (nécessite accès microphone)")
            
            # Créer un fichier audio de test
            if st.button("Générer audio de test"):
                test_text = "Ceci est un test de reconnaissance vocale"
                tts = gTTS(text=test_text, lang='fr')
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                    tts.save(tmp_file.name)
                    audio_file = tmp_file.name
                st.success("Audio de test généré!")
                st.audio(audio_file)
        
        # Paramètres selon le moteur
        if stt_engine == "Whisper (OpenAI)":
            model_size = st.selectbox("Taille du modèle", ["tiny", "base", "small"])
            language = st.selectbox("Langue", ["auto", "fr", "en", "es"])
            
        elif stt_engine == "Google Speech Recognition":
            language = st.selectbox("Langue", ["fr-FR", "en-US", "es-ES"])
            
        elif stt_engine == "Vosk (Offline)":
            st.info("Utilise le modèle pré-téléchargé (anglais)")
        
        # Bouton de transcription
        if st.button("📝 Transcrire", key="transcribe") and audio_file:
            with st.spinner("Transcription en cours..."):
                try:
                    transcription = ""
                    
                    if stt_engine == "Whisper (OpenAI)":
                        # Charger le modèle Whisper
                        model = whisper.load_model(model_size)
                        
                        # Transcrire
                        if language == "auto":
                            result = model.transcribe(audio_file)
                        else:
                            result = model.transcribe(audio_file, language=language)
                        
                        transcription = result["text"]
                        detected_language = result.get("language", "unknown")
                        
                        st.info(f"Langue détectée: {detected_language}")
                    
                    elif stt_engine == "Google Speech Recognition":
                        # Utiliser SpeechRecognition
                        r = sr.Recognizer()
                        
                        # Convertir en WAV si nécessaire
                        audio = AudioSegment.from_file(audio_file)
                        wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                        audio.export(wav_file.name, format="wav")
                        
                        with sr.AudioFile(wav_file.name) as source:
                            audio_data = r.record(source)
                        
                        lang_code = language.split('-')[0]
                        transcription = r.recognize_google(audio_data, language=language)
                        
                        os.unlink(wav_file.name)
                    
                    elif stt_engine == "Vosk (Offline)":
                        import json
                        import vosk
                        
                        # Charger le modèle Vosk
                        model = vosk.Model("/app/models/vosk-model-small-en-us-0.15")
                        rec = vosk.KaldiRecognizer(model, 16000)
                        
                        # Convertir en WAV mono 16kHz
                        audio = AudioSegment.from_file(audio_file)
                        audio = audio.set_channels(1).set_frame_rate(16000)
                        
                        wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                        audio.export(wav_file.name, format="wav")
                        
                        # Transcrire
                        wf = open(wav_file.name, 'rb')
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
                        os.unlink(wav_file.name)
                    
                    # Afficher les résultats
                    if transcription:
                        st.success("✅ Transcription réussie!")
                        st.text_area("Résultat", transcription, height=150)
                        
                        # Statistiques
                        words = transcription.split()
                        st.metric("Nombre de mots", len(words))
                        st.metric("Nombre de caractères", len(transcription))
                        
                        # Option de téléchargement
                        st.download_button(
                            label="📥 Télécharger transcription",
                            data=transcription,
                            file_name=f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                    
                    # Nettoyage
                    if audio_file and os.path.exists(audio_file):
                        os.unlink(audio_file)
                        
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
    
    with col2:
        st.subheader("📚 Concepts Théoriques")
        
        with st.expander("Technologies STT"):
            st.markdown("""
            ### Modèles Classiques
            - **HMM** (Hidden Markov Models)
            - **GMM** (Gaussian Mixture Models)
            - **DTW** (Dynamic Time Warping)
            
            ### Deep Learning
            - **RNN/LSTM**: Séquences temporelles
            - **Transformer**: Attention mechanism
            - **CTC** (Connectionist Temporal Classification)
            - **Whisper**: End-to-end transformer
            
            ### Métriques
            - **WER** (Word Error Rate)
            - **CER** (Character Error Rate)
            - **Latence** et temps réel
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

# ============================================================================
# DEMO 3: SPEECH-TO-SPEECH
# ============================================================================
elif demo_mode == "Speech-to-Speech":
    st.header("🔄 Speech-to-Speech Translation")
    
    st.info("💡 Cette démo combine STT → Translation → TTS pour créer un traducteur vocal temps réel")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1️⃣ Entrée Audio")
        
        # Upload audio
        uploaded_file = st.file_uploader(
            "Fichier audio source",
            type=['wav', 'mp3', 'ogg']
        )
        
        if uploaded_file:
            st.audio(uploaded_file)
            
        # Langue source
        source_lang = st.selectbox(
            "Langue source",
            ["auto", "fr", "en", "es", "de", "it"]
        )
    
    with col2:
        st.subheader("2️⃣ Configuration")
        
        # Langue cible
        target_lang = st.selectbox(
            "Langue cible",
            ["en", "fr", "es", "de", "it", "ja", "zh"]
        )
        
        # Voix de sortie
        voice_gender = st.radio("Genre de voix", ["Femme", "Homme"])
        
        # Options avancées
        with st.expander("Options avancées"):
            keep_timing = st.checkbox("Conserver le timing original")
            enhance_audio = st.checkbox("Améliorer la qualité audio")
    
    with col3:
        st.subheader("3️⃣ Résultat")
        
        if st.button("🔄 Traduire", key="translate_speech") and uploaded_file:
            with st.spinner("Traitement en cours..."):
                try:
                    # Étape 1: STT
                    with st.status("Transcription...", expanded=True) as status:
                        # Sauvegarder le fichier temporairement
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                            tmp.write(uploaded_file.getvalue())
                            audio_path = tmp.name
                        
                        # Transcrire avec Whisper
                        model = whisper.load_model("tiny")
                        if source_lang == "auto":
                            result = model.transcribe(audio_path)
                        else:
                            result = model.transcribe(audio_path, language=source_lang)
                        
                        source_text = result["text"]
                        detected_lang = result.get("language", "unknown")
                        
                        st.write(f"**Texte détecté** ({detected_lang}):")
                        st.write(source_text)
                        status.update(label="✅ Transcription terminée", state="complete")
                    
                    # Étape 2: Translation
                    with st.status("Traduction...", expanded=True) as status:
                        if source_lang == "auto":
                            src = detected_lang
                        else:
                            src = source_lang
                        
                        translator = GoogleTranslator(source=src, target=target_lang)
                        translated_text = translator.translate(source_text)
                        
                        st.write(f"**Texte traduit** ({target_lang}):")
                        st.write(translated_text)
                        status.update(label="✅ Traduction terminée", state="complete")
                    
                    # Étape 3: TTS
                    with st.status("Synthèse vocale...", expanded=True) as status:
                        # Sélectionner la voix appropriée
                        voice_map = {
                            'fr': {'Femme': 'fr-FR-DeniseNeural', 'Homme': 'fr-FR-HenriNeural'},
                            'en': {'Femme': 'en-US-AriaNeural', 'Homme': 'en-US-GuyNeural'},
                            'es': {'Femme': 'es-ES-ElviraNeural', 'Homme': 'es-ES-AlvaroNeural'},
                            'de': {'Femme': 'de-DE-KatjaNeural', 'Homme': 'de-DE-ConradNeural'},
                            'it': {'Femme': 'it-IT-ElsaNeural', 'Homme': 'it-IT-DiegoNeural'},
                        }
                        
                        # Utiliser Edge-TTS si disponible pour la langue
                        if target_lang in voice_map:
                            voice = voice_map[target_lang][voice_gender]
                            
                            async def generate_tts():
                                communicate = edge_tts.Communicate(translated_text, voice)
                                output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                                await communicate.save(output_file.name)
                                return output_file.name
                            
                            output_audio = asyncio.run(generate_tts())
                        else:
                            # Fallback sur gTTS
                            tts = gTTS(text=translated_text, lang=target_lang)
                            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                            tts.save(output_file.name)
                            output_audio = output_file.name
                        
                        status.update(label="✅ Synthèse terminée", state="complete")
                    
                    # Afficher le résultat
                    st.success("🎉 Traduction vocale réussie!")
                    st.audio(output_audio, format='audio/mp3')
                    
                    # Téléchargement
                    with open(output_audio, 'rb') as f:
                        audio_bytes = f.read()
                    
                    st.download_button(
                        label="📥 Télécharger l'audio traduit",
                        data=audio_bytes,
                        file_name=f"translation_{target_lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                        mime="audio/mp3"
                    )
                    
                    # Nettoyage
                    os.unlink(audio_path)
                    os.unlink(output_audio)
                    
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
    
    # Pipeline diagram
    st.divider()
    st.subheader("🔧 Architecture du Pipeline")
    
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

# ============================================================================
# DEMO 4: ANALYSE AUDIO
# ============================================================================
elif demo_mode == "Analyse Audio":
    st.header("📊 Analyse Audio Avancée")
    
    uploaded_file = st.file_uploader("Choisir un fichier audio", type=['wav', 'mp3', 'ogg'])
    
    if uploaded_file:
        # Sauvegarder temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            tmp.write(uploaded_file.getvalue())
            audio_path = tmp.name
        
        st.audio(uploaded_file)
        
        # Charger l'audio avec librosa
        import librosa
        import librosa.display
        import matplotlib.pyplot as plt
        
        # Charger le signal audio
        y, sr = librosa.load(audio_path)
        duration = len(y) / sr
        
        # Métriques de base
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Durée", f"{duration:.2f} sec")
        with col2:
            st.metric("Fréquence d'échantillonnage", f"{sr} Hz")
        with col3:
            st.metric("Échantillons", f"{len(y):,}")
        with col4:
            st.metric("Amplitude max", f"{np.max(np.abs(y)):.3f}")
        
        # Visualisations
        st.subheader("Visualisations")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Waveform", "Spectrogramme", "MFCC", "Analyse Pitch"])
        
        with tab1:
            fig, ax = plt.subplots(figsize=(12, 4))
            librosa.display.waveshow(y, sr=sr, ax=ax)
            ax.set_title("Forme d'onde")
            ax.set_xlabel("Temps (s)")
            ax.set_ylabel("Amplitude")
            st.pyplot(fig)
        
        with tab2:
            fig, ax = plt.subplots(figsize=(12, 6))
            D = librosa.stft(y)
            S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
            img = librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz', ax=ax)
            fig.colorbar(img, ax=ax, format='%+2.0f dB')
            ax.set_title("Spectrogramme")
            st.pyplot(fig)
        
        with tab3:
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            fig, ax = plt.subplots(figsize=(12, 6))
            img = librosa.display.specshow(mfccs, sr=sr, x_axis='time', ax=ax)
            fig.colorbar(img, ax=ax)
            ax.set_title("MFCC (Mel-frequency cepstral coefficients)")
            ax.set_ylabel("MFCC")
            st.pyplot(fig)
        
        with tab4:
            # Extraction du pitch
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            
            # Sélectionner le pitch avec la magnitude maximale à chaque frame
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                pitch_values.append(pitch)
            
            fig, ax = plt.subplots(figsize=(12, 4))
            times = np.arange(len(pitch_values)) * 512 / sr  # hop_length=512 par défaut
            ax.plot(times, pitch_values)
            ax.set_xlabel("Temps (s)")
            ax.set_ylabel("Fréquence (Hz)")
            ax.set_title("Analyse du Pitch")
            ax.set_ylim([0, 500])
            st.pyplot(fig)
        
        # Statistiques avancées
        st.subheader("📈 Statistiques Avancées")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Caractéristiques temporelles**")
            zero_crossings = librosa.feature.zero_crossing_rate(y)[0]
            st.metric("Zero Crossing Rate (moy)", f"{np.mean(zero_crossings):.4f}")
            
            rms = librosa.feature.rms(y=y)[0]
            st.metric("RMS Energy (moy)", f"{np.mean(rms):.4f}")
            
        with col2:
            st.write("**Caractéristiques fréquentielles**")
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            st.metric("Centroïde spectral (moy)", f"{np.mean(spectral_centroids):.2f} Hz")
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            st.metric("Rolloff spectral (moy)", f"{np.mean(spectral_rolloff):.2f} Hz")
        
        # Nettoyage
        os.unlink(audio_path)

# ============================================================================
# EXERCICES
# ============================================================================
elif demo_mode == "Exercices":
    st.header("💻 Exercices Pratiques")
    
    exercise = st.selectbox(
        "Choisir un exercice",
        [
            "Ex1: Créer un lecteur de news",
            "Ex2: Transcripteur de réunions",
            "Ex3: Assistant vocal multilingue",
            "Ex4: Analyseur d'émotions vocales"
        ]
    )
    
    if exercise == "Ex1: Créer un lecteur de news":
        st.subheader("📰 Exercice 1: Lecteur de News Automatique")
        
        with st.expander("📋 Instructions"):
            st.markdown("""
            ### Objectif
            Créer une application qui récupère les dernières actualités et les lit à haute voix.
            
            ### Étapes
            1. Récupérer des articles depuis une API news (RSS, NewsAPI, etc.)
            2. Extraire le titre et le résumé
            3. Formater le texte pour la lecture
            4. Convertir en audio avec différentes voix
            5. Ajouter des options (vitesse, pause entre articles)
            
            ### Bonus
            - Traduire les articles dans différentes langues
            - Générer un podcast quotidien
            - Ajouter de la musique de transition
            """)
        
        with st.expander("💡 Indices"):
            st.code("""
import feedparser
from gtts import gTTS
from pydub import AudioSegment

# 1. Récupérer les news RSS
feed = feedparser.parse("https://example.com/rss")
articles = feed.entries[:5]

# 2. Créer le script
script = "Voici les actualités du jour. "
for i, article in enumerate(articles, 1):
    script += f"Article {i}. {article.title}. "
    script += f"{article.summary}. "

# 3. Générer l'audio
tts = gTTS(script, lang='fr')
tts.save("news.mp3")

# 4. Ajouter des effets
audio = AudioSegment.from_mp3("news.mp3")
audio = audio.speedup(playback_speed=1.2)
            """, language='python')
    
    elif exercise == "Ex2: Transcripteur de réunions":
        st.subheader("📝 Exercice 2: Transcripteur de Réunions")
        
        with st.expander("📋 Instructions"):
            st.markdown("""
            ### Objectif
            Créer un système qui transcrit automatiquement les réunions et génère un compte-rendu.
            
            ### Fonctionnalités
            1. Transcrire un enregistrement de réunion
            2. Identifier les différents intervenants (speaker diarization)
            3. Extraire les points clés et actions
            4. Générer un résumé structuré
            5. Exporter en différents formats (PDF, Word, Markdown)
            
            ### Technologies suggérées
            - Whisper pour la transcription
            - pyannote pour la diarization
            - spaCy/NLTK pour l'extraction d'informations
            """)
        
        st.code("""
# Exemple de structure
class MeetingTranscriber:
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
        
    def transcribe(self, audio_file):
        # Transcription avec timestamps
        result = self.whisper_model.transcribe(
            audio_file,
            verbose=True,
            word_timestamps=True
        )
        return result
    
    def identify_speakers(self, audio_file):
        # Utiliser pyannote pour identifier les speakers
        pass
    
    def extract_key_points(self, transcript):
        # NLP pour extraire les points importants
        pass
    
    def generate_summary(self, transcript):
        # Créer un résumé structuré
        pass
        """, language='python')
    
    elif exercise == "Ex3: Assistant vocal multilingue":
        st.subheader("🌍 Exercice 3: Assistant Vocal Multilingue")
        
        with st.expander("📋 Instructions"):
            st.markdown("""
            ### Objectif
            Créer un assistant vocal qui comprend et répond dans plusieurs langues.
            
            ### Fonctionnalités
            1. Détection automatique de la langue
            2. Compréhension des commandes vocales
            3. Traduction en temps réel
            4. Réponses contextuelles
            5. Support d'au moins 5 langues
            
            ### Architecture suggérée
            ```
            Entrée vocale → Détection langue → STT → 
            Traitement commande → Génération réponse → 
            TTS (langue appropriée) → Sortie vocale
            ```
            """)
        
        # Template de code
        st.code("""
class MultilingualAssistant:
    def __init__(self):
        self.whisper = whisper.load_model("base")
        self.commands = {
            'en': {'hello': self.greet, 'time': self.tell_time},
            'fr': {'bonjour': self.greet, 'heure': self.tell_time},
            'es': {'hola': self.greet, 'hora': self.tell_time}
        }
    
    def detect_language(self, audio):
        result = self.whisper.transcribe(audio)
        return result['language']
    
    def process_command(self, text, language):
        # Parser la commande et exécuter l'action
        pass
    
    def respond(self, message, language):
        # Générer réponse vocale dans la bonne langue
        pass
        """, language='python')
    
    elif exercise == "Ex4: Analyseur d'émotions vocales":
        st.subheader("😊 Exercice 4: Analyseur d'Émotions Vocales")
        
        with st.expander("📋 Instructions"):
            st.markdown("""
            ### Objectif
            Analyser les émotions dans la voix (joie, tristesse, colère, etc.)
            
            ### Techniques
            1. Extraction de caractéristiques audio (pitch, énergie, MFCC)
            2. Classification avec ML (SVM, Random Forest, CNN)
            3. Visualisation en temps réel
            4. Rapport détaillé avec recommandations
            
            ### Dataset suggéré
            - RAVDESS (Ryerson Audio-Visual Database)
            - TESS (Toronto Emotional Speech Set)
            """)
        
        st.code("""
import librosa
from sklearn.svm import SVC
import joblib

class EmotionAnalyzer:
    def __init__(self):
        self.model = joblib.load('emotion_model.pkl')
        self.emotions = ['neutral', 'happy', 'sad', 'angry', 'fearful']
    
    def extract_features(self, audio_file):
        y, sr = librosa.load(audio_file)
        
        # Extraction des caractéristiques
        features = []
        
        # MFCC
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features.extend(np.mean(mfcc, axis=1))
        
        # Pitch
        pitches, _ = librosa.piptrack(y=y, sr=sr)
        features.append(np.mean(pitches))
        
        # Energy
        rms = librosa.feature.rms(y=y)
        features.append(np.mean(rms))
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y)
        features.append(np.mean(zcr))
        
        return np.array(features)
    
    def predict_emotion(self, audio_file):
        features = self.extract_features(audio_file)
        prediction = self.model.predict([features])[0]
        confidence = self.model.predict_proba([features])[0]
        
        return {
            'emotion': self.emotions[prediction],
            'confidence': confidence
        }
        """, language='python')

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>Module 1 - Traitement Vocal | Formation Data Engineering</p>
    <p>🚀 Propulsé par Streamlit, Whisper, et Edge-TTS</p>
</div>
""", unsafe_allow_html=True)