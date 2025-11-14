"""
Application Streamlit complète pour le Module 1 - Traitement Vocal
Inclut TTS, STT, Speech-to-Speech, Analyse Audio et Exercices
"""

import streamlit as st
from gtts import gTTS
import tempfile
import os
from datetime import datetime
import asyncio
import edge_tts
import base64
import speech_recognition as sr
import whisper
from googletrans import Translator
import numpy as np
import librosa
import matplotlib.pyplot as plt
import soundfile as sf
import io
import wave
import json
from pydub import AudioSegment

# Configuration de la page
st.set_page_config(
    page_title="Module Traitement Vocal - Complet",
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
    .metric-card {
        background: rgba(255,255,255,0.9);
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🎤 Module 1: Traitement Vocal Complet</h1>
    <p>TTS, STT, Translation, Analyse Audio & Exercices</p>
</div>
""", unsafe_allow_html=True)

# Initialiser le modèle Whisper en session state
@st.cache_resource
def load_whisper_model():
    """Charger le modèle Whisper une seule fois"""
    try:
        return whisper.load_model("tiny")
    except:
        return None

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    demo_mode = st.selectbox(
        "Choisir un module",
        [
            "🔊 Text-to-Speech",
            "🎙️ Speech-to-Text (Whisper)",
            "🔄 Speech-to-Speech Translation",
            "📊 Analyse Audio",
            "💻 Exercices Interactifs"
        ]
    )
    
    st.divider()
    
    # État des services
    st.subheader("📡 État des Services")
    
    # Vérifier les dépendances
    status_gtts = "✅" if os.system("python -c 'import gtts' 2>/dev/null") == 0 else "❌"
    status_edge = "✅" if os.system("python -c 'import edge_tts' 2>/dev/null") == 0 else "❌"
    status_whisper = "✅" if load_whisper_model() is not None else "⚠️"
    
    st.info(f"""
    **Services disponibles:**
    - {status_gtts} gTTS (Text-to-Speech)
    - {status_edge} Edge-TTS (Neural Voices)
    - {status_whisper} Whisper (Speech-to-Text)
    - ✅ Google Translate
    - ✅ Librosa (Analyse Audio)
    """)

# ============================================================================
# FONCTIONS HELPER
# ============================================================================

def generate_audio_with_gtts(text, lang='fr'):
    """Générer l'audio avec gTTS"""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name, None
    except Exception as e:
        return None, str(e)

async def generate_audio_with_edge_tts(text, voice='fr-FR-DeniseNeural', rate='+0%'):
    """Générer l'audio avec Edge-TTS"""
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            await communicate.save(tmp_file.name)
            return tmp_file.name, None
    except Exception as e:
        return None, str(e)

def transcribe_audio_whisper(audio_file):
    """Transcrire l'audio avec Whisper"""
    try:
        model = load_whisper_model()
        if model is None:
            return None, "Modèle Whisper non disponible"
        
        # Transcrire avec paramètres par défaut
        result = model.transcribe(audio_file, fp16=False)
        return result["text"], None
    except Exception as e:
        return None, f"Erreur Whisper: {str(e)}"

def transcribe_audio_google(audio_file):
    """Transcrire l'audio avec Google Speech Recognition"""
    try:
        r = sr.Recognizer()
        
        # Convertir en WAV si nécessaire
        if not audio_file.endswith('.wav'):
            audio = AudioSegment.from_file(audio_file)
            wav_file = audio_file.replace(audio_file.split('.')[-1], 'wav')
            audio.export(wav_file, format='wav')
            audio_file = wav_file
        
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language='fr-FR')
            return text, None
    except Exception as e:
        return None, str(e)

def analyze_audio(audio_file):
    """Analyser les caractéristiques audio avec librosa"""
    try:
        # Charger l'audio
        y, sr_rate = librosa.load(audio_file, sr=None)
        
        # Calculer les caractéristiques
        duration = librosa.get_duration(y=y, sr=sr_rate)
        
        # Pitch (hauteur)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr_rate)
        pitch_mean = np.mean(pitches[magnitudes > np.max(magnitudes) * 0.1])
        
        # Énergie
        rms = librosa.feature.rms(y=y)[0]
        energy_mean = np.mean(rms)
        
        # Tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr_rate)
        
        # Spectrogramme
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        
        return {
            'duration': duration,
            'sample_rate': sr_rate,
            'pitch_mean': pitch_mean,
            'energy_mean': energy_mean,
            'tempo': tempo,
            'spectrogram': D,
            'waveform': y,
            'sr': sr_rate
        }, None
        
    except Exception as e:
        return None, str(e)

# ============================================================================
# MODULE 1: TEXT-TO-SPEECH (Déjà implémenté dans app_fixed.py)
# ============================================================================

if demo_mode == "🔊 Text-to-Speech":
    st.header("🔊 Text-to-Speech Avancé")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Configuration")
        
        # Choix du moteur
        tts_engine = st.selectbox(
            "Moteur TTS",
            ["gTTS (Google)", "Edge-TTS (Microsoft)"]
        )
        
        # Texte à convertir
        text_input = st.text_area(
            "Texte à convertir",
            value="Bienvenue dans le module complet de traitement vocal. Cette version inclut la reconnaissance vocale, la traduction et l'analyse audio.",
            height=100
        )
        
        # Paramètres selon le moteur
        if tts_engine == "gTTS (Google)":
            lang = st.selectbox("Langue", [
                ("Français", "fr"),
                ("English", "en"),
                ("Español", "es"),
                ("Deutsch", "de"),
            ], format_func=lambda x: x[0])
            slow = st.checkbox("Parler lentement", value=False)
            
        else:  # Edge-TTS
            voice = st.selectbox(
                "Voix",
                [
                    ("Denise (FR Femme)", "fr-FR-DeniseNeural"),
                    ("Henri (FR Homme)", "fr-FR-HenriNeural"),
                    ("Aria (US Femme)", "en-US-AriaNeural"),
                    ("Guy (US Homme)", "en-US-GuyNeural"),
                ],
                format_func=lambda x: x[0]
            )
            rate = st.select_slider(
                "Vitesse",
                options=["-50%", "-25%", "+0%", "+25%", "+50%"],
                value="+0%"
            )
        
        # Génération
        if st.button("🎵 Générer Audio", type="primary"):
            if not text_input.strip():
                st.error("❌ Veuillez entrer du texte")
            else:
                with st.spinner("Génération en cours..."):
                    try:
                        if tts_engine == "gTTS (Google)":
                            audio_file, error = generate_audio_with_gtts(text_input, lang[1])
                        else:
                            audio_file, error = asyncio.run(
                                generate_audio_with_edge_tts(text_input, voice[1], rate)
                            )
                        
                        if audio_file and os.path.exists(audio_file):
                            file_size = os.path.getsize(audio_file)
                            if file_size > 0:
                                st.success(f"✅ Audio généré! ({file_size:,} bytes)")
                                
                                with open(audio_file, 'rb') as f:
                                    audio_bytes = f.read()
                                
                                st.audio(audio_bytes, format='audio/mpeg')
                                
                                st.download_button(
                                    label="📥 Télécharger",
                                    data=audio_bytes,
                                    file_name=f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                                    mime="audio/mpeg"
                                )
                        else:
                            st.error(f"❌ Erreur: {error}")
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
    
    with col2:
        st.subheader("📚 Guide d'utilisation")
        st.info("""
        **Fonctionnalités:**
        - ✅ 2 moteurs TTS disponibles
        - ✅ Support multilingue
        - ✅ Voix neuronales (Edge-TTS)
        - ✅ Contrôle de la vitesse
        - ✅ Téléchargement MP3
        
        **Cas d'usage:**
        - Accessibilité web
        - Apprentissage des langues
        - Création de podcasts
        - Assistants vocaux
        """)

# ============================================================================
# MODULE 2: SPEECH-TO-TEXT (WHISPER)
# ============================================================================

elif demo_mode == "🎙️ Speech-to-Text (Whisper)":
    st.header("🎙️ Speech-to-Text avec Whisper")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload Audio")
        
        # Upload de fichier
        audio_file = st.file_uploader(
            "Choisir un fichier audio",
            type=['mp3', 'wav', 'ogg', 'm4a', 'flac'],
            help="Formats supportés: MP3, WAV, OGG, M4A, FLAC"
        )
        
        # Ou enregistrement (simulé avec un exemple)
        if st.button("🎤 Créer un exemple audio"):
            # Créer un fichier exemple
            text_exemple = "Bonjour et bienvenue dans le module de reconnaissance vocale. Ceci est un exemple de texte qui sera transcrit automatiquement."
            
            with st.spinner("Génération de l'audio..."):
                audio_file_path, error = generate_audio_with_gtts(text_exemple, 'fr')
                if audio_file_path and os.path.exists(audio_file_path):
                    with open(audio_file_path, 'rb') as f:
                        audio_bytes = f.read()
                    
                    # Créer un BytesIO pour simuler un upload
                    audio_file = io.BytesIO(audio_bytes)
                    audio_file.name = "exemple.mp3"
                    
                    # Stocker dans session state
                    st.session_state['stt_example'] = audio_file
                    st.session_state['stt_example_text'] = text_exemple
                    st.success("✅ Fichier exemple créé!")
                else:
                    st.error(f"Erreur: {error}")
        
        # Utiliser l'exemple de session state si disponible
        if 'stt_example' in st.session_state and audio_file is None:
            audio_file = st.session_state['stt_example']
            st.info("📌 Utilisation de l'exemple audio généré")
        
        # Choix du moteur
        stt_engine = st.selectbox(
            "Moteur de reconnaissance",
            ["Whisper (OpenAI)", "Google Speech Recognition"]
        )
        
        if audio_file is not None:
            st.audio(audio_file)
            
            if st.button("🎯 Transcrire", type="primary"):
                with st.spinner("Transcription en cours..."):
                    try:
                        # Sauvegarder temporairement le fichier uploadé
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                            # Réinitialiser la position du curseur si nécessaire
                            if hasattr(audio_file, 'seek'):
                                audio_file.seek(0)
                            
                            # Lire et écrire le contenu
                            content = audio_file.read()
                            tmp_file.write(content)
                            tmp_path = tmp_file.name
                            
                            # Réinitialiser pour la lecture audio
                            if hasattr(audio_file, 'seek'):
                                audio_file.seek(0)
                        
                        # Transcrire
                        if stt_engine == "Whisper (OpenAI)":
                            text, error = transcribe_audio_whisper(tmp_path)
                        else:
                            text, error = transcribe_audio_google(tmp_path)
                        
                        if text:
                            st.success("✅ Transcription réussie!")
                            
                            # Afficher le résultat
                            st.text_area(
                                "Transcription",
                                value=text,
                                height=150,
                                key="transcription_result"
                            )
                            
                            # Statistiques
                            words = len(text.split())
                            chars = len(text)
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("Mots", words)
                            with col_b:
                                st.metric("Caractères", chars)
                            
                            # Options d'export
                            st.download_button(
                                label="📥 Télécharger transcription",
                                data=text,
                                file_name=f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain"
                            )
                        else:
                            st.error(f"❌ Erreur: {error}")
                        
                        # Nettoyer
                        os.unlink(tmp_path)
                        
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
    
    with col2:
        st.subheader("📊 Informations")
        
        with st.expander("🔍 À propos de Whisper"):
            st.markdown("""
            **Whisper** est un modèle de reconnaissance vocale d'OpenAI:
            - Entraîné sur 680,000 heures d'audio multilingue
            - Supporte 99+ langues
            - Résistant au bruit et aux accents
            - Modèles: tiny, base, small, medium, large
            
            **Avantages:**
            - Précision élevée
            - Multilingue natif
            - Détection automatique de langue
            - Timestamps précis
            """)
        
        with st.expander("💡 Conseils d'utilisation"):
            st.markdown("""
            **Pour de meilleurs résultats:**
            1. Utilisez des fichiers audio de bonne qualité
            2. Évitez les bruits de fond excessifs
            3. Parlez clairement et distinctement
            4. Format WAV recommandé pour la meilleure qualité
            
            **Limitations:**
            - Fichiers < 25 MB recommandés
            - Audio mono préférable
            - Durée < 5 minutes pour le modèle tiny
            """)

# ============================================================================
# MODULE 3: SPEECH-TO-SPEECH TRANSLATION
# ============================================================================

elif demo_mode == "🔄 Speech-to-Speech Translation":
    st.header("🔄 Traduction Speech-to-Speech")
    
    st.info("🎯 Ce module combine STT + Translation + TTS pour une traduction vocale complète")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Configuration")
        
        # Upload audio source
        audio_source = st.file_uploader(
            "Audio source",
            type=['mp3', 'wav', 'ogg'],
            help="Uploadez l'audio à traduire",
            key="s2s_upload"
        )
        
        # Ou générer un exemple
        if st.button("🎤 Créer un exemple", key="s2s_create_example"):
            text_fr = "Bonjour, comment allez-vous aujourd'hui? J'espère que vous passez une excellente journée."
            
            with st.spinner("Génération de l'exemple..."):
                audio_path, error = generate_audio_with_gtts(text_fr, 'fr')
                if audio_path and os.path.exists(audio_path):
                    with open(audio_path, 'rb') as f:
                        audio_bytes = f.read()
                    
                    # Créer un BytesIO
                    audio_source = io.BytesIO(audio_bytes)
                    audio_source.name = "exemple_fr.mp3"
                    
                    # Stocker dans session state
                    st.session_state['s2s_example'] = audio_source
                    st.session_state['s2s_example_text'] = text_fr
                    st.success("✅ Exemple créé en français")
                    st.rerun()
                else:
                    st.error(f"Erreur: {error}")
        
        # Utiliser l'exemple si disponible
        if 's2s_example' in st.session_state and audio_source is None:
            audio_source = st.session_state['s2s_example']
            st.info("📌 Utilisation de l'exemple audio généré")
        
        # Langues
        col_lang1, col_lang2 = st.columns(2)
        with col_lang1:
            source_lang = st.selectbox(
                "Langue source",
                ["fr", "en", "es", "de", "it", "pt", "ja", "zh"],
                format_func=lambda x: {
                    'fr': '🇫🇷 Français',
                    'en': '🇬🇧 English',
                    'es': '🇪🇸 Español',
                    'de': '🇩🇪 Deutsch',
                    'it': '🇮🇹 Italiano',
                    'pt': '🇵🇹 Português',
                    'ja': '🇯🇵 日本語',
                    'zh': '🇨🇳 中文'
                }.get(x, x)
            )
        
        with col_lang2:
            target_lang = st.selectbox(
                "Langue cible",
                ["en", "fr", "es", "de", "it", "pt", "ja", "zh"],
                format_func=lambda x: {
                    'fr': '🇫🇷 Français',
                    'en': '🇬🇧 English',
                    'es': '🇪🇸 Español',
                    'de': '🇩🇪 Deutsch',
                    'it': '🇮🇹 Italiano',
                    'pt': '🇵🇹 Português',
                    'ja': '🇯🇵 日本語',
                    'zh': '🇨🇳 中文'
                }.get(x, x)
            )
        
        if audio_source is not None:
            st.audio(audio_source)
            
            if st.button("🔄 Traduire", type="primary"):
                with st.spinner("Traitement en cours..."):
                    try:
                        # Étape 1: STT
                        with st.status("📝 Transcription...", expanded=True) as status:
                            # Réinitialiser le curseur
                            if hasattr(audio_source, 'seek'):
                                audio_source.seek(0)
                            
                            # Sauvegarder temporairement
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                                content = audio_source.read()
                                tmp.write(content)
                                tmp_path = tmp.name
                            
                            # Réinitialiser pour affichage
                            if hasattr(audio_source, 'seek'):
                                audio_source.seek(0)
                            
                            text_original, error = transcribe_audio_google(tmp_path)
                            if error:
                                text_original, error = transcribe_audio_whisper(tmp_path)
                            
                            if text_original:
                                st.write(f"**Texte original:** {text_original}")
                                status.update(label="✅ Transcription terminée", state="complete")
                            else:
                                st.error(f"Erreur STT: {error}")
                                status.update(label="❌ Erreur transcription", state="error")
                                raise Exception(error)
                        
                        # Étape 2: Translation
                        with st.status("🌐 Traduction...", expanded=True) as status:
                            translator = Translator()
                            translation = translator.translate(
                                text_original,
                                src=source_lang,
                                dest=target_lang
                            )
                            text_translated = translation.text
                            st.write(f"**Texte traduit:** {text_translated}")
                            status.update(label="✅ Traduction terminée", state="complete")
                        
                        # Étape 3: TTS
                        with st.status("🔊 Synthèse vocale...", expanded=True) as status:
                            audio_output, error = generate_audio_with_gtts(
                                text_translated,
                                target_lang
                            )
                            
                            if audio_output:
                                status.update(label="✅ Synthèse terminée", state="complete")
                            else:
                                st.error(f"Erreur TTS: {error}")
                                status.update(label="❌ Erreur synthèse", state="error")
                        
                        # Résultats
                        if audio_output:
                            st.success("✅ Traduction Speech-to-Speech réussie!")
                            
                            # Audio traduit
                            with open(audio_output, 'rb') as f:
                                audio_bytes = f.read()
                            
                            st.audio(audio_bytes, format='audio/mpeg')
                            
                            # Téléchargements
                            col_dl1, col_dl2 = st.columns(2)
                            with col_dl1:
                                st.download_button(
                                    "📥 Audio traduit",
                                    data=audio_bytes,
                                    file_name=f"translation_{target_lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                                    mime="audio/mpeg"
                                )
                            with col_dl2:
                                st.download_button(
                                    "📝 Transcriptions",
                                    data=f"Original ({source_lang}):\n{text_original}\n\nTraduction ({target_lang}):\n{text_translated}",
                                    file_name=f"transcriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    mime="text/plain"
                                )
                        
                        # Nettoyer
                        os.unlink(tmp_path)
                        
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
    
    with col2:
        st.subheader("📊 Pipeline de traduction")
        
        st.markdown("""
        ### Processus en 3 étapes:
        
        1️⃣ **Speech-to-Text (STT)**
        - Extraction du texte de l'audio source
        - Moteurs: Whisper ou Google SR
        
        2️⃣ **Translation**
        - Traduction du texte
        - API: Google Translate
        - 100+ langues supportées
        
        3️⃣ **Text-to-Speech (TTS)**
        - Génération audio dans la langue cible
        - Moteurs: gTTS ou Edge-TTS
        """)
        
        with st.expander("🚀 Applications"):
            st.markdown("""
            **Cas d'usage:**
            - 🎬 Doublage automatique
            - 📞 Interprétation téléphonique
            - 🎓 Apprentissage des langues
            - 🌍 Communication internationale
            - 📱 Applications de voyage
            - 🎤 Conférences multilingues
            """)

# ============================================================================
# MODULE 4: ANALYSE AUDIO
# ============================================================================

elif demo_mode == "📊 Analyse Audio":
    st.header("📊 Analyse Audio Avancée")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configuration")
        
        # Upload audio
        audio_file = st.file_uploader(
            "Fichier audio",
            type=['mp3', 'wav', 'ogg', 'flac']
        )
        
        # Ou créer un exemple
        if st.button("🎵 Générer exemple"):
            text = "Analyse audio avec différentes intonations. Question? Exclamation! Normal."
            audio_path, _ = generate_audio_with_gtts(text, 'fr')
            if audio_path:
                with open(audio_path, 'rb') as f:
                    audio_file = io.BytesIO(f.read())
                    audio_file.name = "exemple_analyse.mp3"
                st.success("✅ Exemple généré")
        
        if audio_file is not None:
            st.audio(audio_file)
            
            if st.button("📊 Analyser", type="primary"):
                with st.spinner("Analyse en cours..."):
                    try:
                        # Sauvegarder temporairement
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                            tmp.write(audio_file.read())
                            tmp_path = tmp.name
                        
                        # Analyser
                        analysis, error = analyze_audio(tmp_path)
                        
                        if analysis:
                            st.success("✅ Analyse terminée!")
                            
                            # Métriques de base
                            st.subheader("📈 Métriques")
                            col_m1, col_m2, col_m3 = st.columns(3)
                            with col_m1:
                                st.metric("Durée", f"{analysis['duration']:.2f} s")
                            with col_m2:
                                st.metric("Sample Rate", f"{analysis['sample_rate']} Hz")
                            with col_m3:
                                st.metric("Tempo", f"{analysis['tempo']:.0f} BPM")
                            
                            # Stocker pour l'affichage
                            st.session_state['audio_analysis'] = analysis
                        else:
                            st.error(f"❌ Erreur: {error}")
                        
                        # Nettoyer
                        os.unlink(tmp_path)
                        
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
    
    with col2:
        if 'audio_analysis' in st.session_state:
            analysis = st.session_state['audio_analysis']
            
            st.subheader("📉 Visualisations")
            
            # Tabs pour différentes vues
            tab1, tab2, tab3 = st.tabs(["Forme d'onde", "Spectrogramme", "Statistiques"])
            
            with tab1:
                # Waveform
                fig, ax = plt.subplots(figsize=(10, 4))
                time = np.linspace(0, analysis['duration'], len(analysis['waveform']))
                ax.plot(time, analysis['waveform'])
                ax.set_xlabel('Temps (s)')
                ax.set_ylabel('Amplitude')
                ax.set_title('Forme d\'onde audio')
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
            
            with tab2:
                # Spectrogramme
                fig, ax = plt.subplots(figsize=(10, 6))
                img = librosa.display.specshow(
                    analysis['spectrogram'],
                    sr=analysis['sr'],
                    x_axis='time',
                    y_axis='hz',
                    ax=ax
                )
                fig.colorbar(img, ax=ax, format='%+2.0f dB')
                ax.set_title('Spectrogramme')
                st.pyplot(fig)
            
            with tab3:
                # Statistiques détaillées
                st.markdown("""
                ### 📊 Statistiques détaillées
                """)
                
                # Calculs supplémentaires
                y = analysis['waveform']
                
                # Énergie RMS
                rms = librosa.feature.rms(y=y)[0]
                
                # Zero crossing rate
                zcr = librosa.feature.zero_crossing_rate(y)[0]
                
                # Créer un DataFrame pour les stats
                stats_data = {
                    'Métrique': [
                        'Durée totale',
                        'Taux d\'échantillonnage',
                        'Nombre d\'échantillons',
                        'Énergie moyenne (RMS)',
                        'Énergie max',
                        'Zero Crossing Rate moyen',
                        'Tempo estimé',
                        'Pitch moyen'
                    ],
                    'Valeur': [
                        f"{analysis['duration']:.3f} secondes",
                        f"{analysis['sample_rate']} Hz",
                        f"{len(y):,}",
                        f"{np.mean(rms):.4f}",
                        f"{np.max(rms):.4f}",
                        f"{np.mean(zcr):.4f}",
                        f"{analysis['tempo']:.1f} BPM",
                        f"{analysis['pitch_mean']:.2f} Hz"
                    ]
                }
                
                st.table(stats_data)
                
                # Export JSON
                export_data = {
                    'duration': float(analysis['duration']),
                    'sample_rate': int(analysis['sample_rate']),
                    'tempo': float(analysis['tempo']),
                    'pitch_mean': float(analysis['pitch_mean']),
                    'energy_mean': float(analysis['energy_mean'])
                }
                
                st.download_button(
                    "📥 Exporter analyse (JSON)",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"audio_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        else:
            st.info("👆 Uploadez un fichier audio pour voir l'analyse")

# ============================================================================
# MODULE 5: EXERCICES INTERACTIFS
# ============================================================================

elif demo_mode == "💻 Exercices Interactifs":
    st.header("💻 Exercices Pratiques")
    
    # Sélection de l'exercice
    exercise = st.selectbox(
        "Choisir un exercice",
        [
            "Exercice 1: Prononciation",
            "Exercice 2: Dictée Audio",
            "Exercice 3: Traduction Vocale",
            "Exercice 4: Analyse Comparative"
        ]
    )
    
    if exercise == "Exercice 1: Prononciation":
        st.subheader("🎯 Exercice de Prononciation")
        
        st.markdown("""
        ### Objectif
        Comparer votre prononciation avec une référence TTS.
        """)
        
        # Phrase à prononcer
        phrases = [
            "Les chaussettes de l'archiduchesse sont-elles sèches?",
            "Un chasseur sachant chasser doit savoir chasser sans son chien.",
            "Trois tortues trottaient sur un trottoir très étroit.",
            "Seize jacinthes sèchent dans seize sachets secs."
        ]
        
        phrase = st.selectbox("Phrase à prononcer", phrases)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📖 Référence")
            
            if st.button("🔊 Générer référence"):
                audio_ref, _ = generate_audio_with_gtts(phrase, 'fr')
                if audio_ref:
                    with open(audio_ref, 'rb') as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format='audio/mpeg')
                    st.session_state['reference_audio'] = audio_bytes
        
        with col2:
            st.subheader("🎤 Votre tentative")
            
            uploaded = st.file_uploader(
                "Uploadez votre enregistrement",
                type=['mp3', 'wav', 'ogg'],
                key="user_recording"
            )
            
            if uploaded is not None:
                st.audio(uploaded)
                
                if st.button("📊 Comparer"):
                    with st.spinner("Analyse en cours..."):
                        # Transcrire l'audio utilisateur
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                            tmp.write(uploaded.read())
                            tmp_path = tmp.name
                        
                        user_text, _ = transcribe_audio_google(tmp_path)
                        
                        if user_text:
                            # Comparer les textes
                            from difflib import SequenceMatcher
                            similarity = SequenceMatcher(None, phrase.lower(), user_text.lower()).ratio()
                            
                            st.metric("Score de similarité", f"{similarity*100:.1f}%")
                            
                            if similarity > 0.9:
                                st.success("🎉 Excellent! Prononciation très proche!")
                            elif similarity > 0.7:
                                st.warning("👍 Bien! Quelques différences mineures.")
                            else:
                                st.error("🎯 Continuez à pratiquer!")
                            
                            st.text_area("Votre transcription", user_text)
                        
                        os.unlink(tmp_path)
    
    elif exercise == "Exercice 2: Dictée Audio":
        st.subheader("✍️ Dictée Audio")
        
        st.markdown("""
        ### Objectif
        Écoutez l'audio et écrivez ce que vous entendez.
        """)
        
        # Textes de dictée
        dictees = {
            "Facile": "Le chat noir dort sur le canapé rouge.",
            "Moyen": "Les oiseaux chantent mélodieusement dans les arbres fleuris du jardin.",
            "Difficile": "L'inexorable passage du temps transforme imperceptiblement nos souvenirs les plus précieux."
        }
        
        niveau = st.select_slider("Niveau", options=["Facile", "Moyen", "Difficile"])
        texte_dictee = dictees[niveau]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔊 Audio")
            
            if st.button("🎵 Générer dictée"):
                # Vitesse selon le niveau
                vitesse = "+0%" if niveau == "Facile" else "-25%" if niveau == "Moyen" else "-40%"
                
                audio_dictee, _ = asyncio.run(
                    generate_audio_with_edge_tts(texte_dictee, 'fr-FR-DeniseNeural', vitesse)
                )
                
                if audio_dictee:
                    with open(audio_dictee, 'rb') as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format='audio/mpeg')
                    st.session_state['dictee_text'] = texte_dictee
        
        with col2:
            st.subheader("✍️ Votre réponse")
            
            user_text = st.text_area(
                "Écrivez ce que vous entendez",
                height=100,
                placeholder="Tapez ici..."
            )
            
            if st.button("✅ Vérifier") and 'dictee_text' in st.session_state:
                correct_text = st.session_state['dictee_text']
                
                # Calculer le score
                from difflib import SequenceMatcher
                score = SequenceMatcher(None, correct_text.lower(), user_text.lower()).ratio()
                
                st.metric("Score", f"{score*100:.1f}%")
                
                if score == 1.0:
                    st.balloons()
                    st.success("🎉 Parfait! Aucune erreur!")
                elif score > 0.8:
                    st.success("👍 Très bien! Quelques petites erreurs.")
                else:
                    st.warning("📝 Réessayez, vous pouvez mieux faire!")
                
                # Afficher la correction
                with st.expander("Voir la correction"):
                    st.text_area("Texte correct", correct_text, disabled=True)
    
    elif exercise == "Exercice 3: Traduction Vocale":
        st.subheader("🌍 Traduction Vocale Interactive")
        
        st.markdown("""
        ### Objectif
        Traduisez oralement des phrases d'une langue à une autre.
        """)
        
        # Configuration
        col1, col2 = st.columns(2)
        
        with col1:
            lang_source = st.selectbox(
                "Langue source",
                ["fr", "en", "es"],
                format_func=lambda x: {'fr': 'Français', 'en': 'English', 'es': 'Español'}[x]
            )
        
        with col2:
            lang_target = st.selectbox(
                "Langue cible",
                ["en", "fr", "es"],
                format_func=lambda x: {'fr': 'Français', 'en': 'English', 'es': 'Español'}[x]
            )
        
        # Phrases d'exercice
        phrases_exercise = {
            "fr": [
                "Bonjour, comment allez-vous?",
                "J'aimerais commander un café s'il vous plaît.",
                "Où se trouve la gare?"
            ],
            "en": [
                "Hello, how are you?",
                "I would like to order a coffee please.",
                "Where is the train station?"
            ],
            "es": [
                "Hola, ¿cómo estás?",
                "Me gustaría pedir un café por favor.",
                "¿Dónde está la estación de tren?"
            ]
        }
        
        phrase = st.selectbox(
            "Phrase à traduire",
            phrases_exercise.get(lang_source, [])
        )
        
        if st.button("🎯 Commencer l'exercice"):
            st.session_state['exercise_phrase'] = phrase
            st.session_state['exercise_lang_target'] = lang_target
            
            # Générer l'audio source
            audio_source, _ = generate_audio_with_gtts(phrase, lang_source)
            if audio_source:
                st.subheader("Étape 1: Écoutez")
                with open(audio_source, 'rb') as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format='audio/mpeg')
                
                st.subheader("Étape 2: Traduisez et enregistrez")
                lang_names = {'fr': 'français', 'en': 'anglais', 'es': 'espagnol'}
                st.info(f"Traduisez en {lang_names[lang_target]} et uploadez votre enregistrement")
                
                user_translation = st.file_uploader(
                    "Votre traduction vocale",
                    type=['mp3', 'wav', 'ogg'],
                    key="translation_upload"
                )
                
                if user_translation:
                    st.audio(user_translation)
                    
                    if st.button("📊 Vérifier"):
                        # Transcrire et comparer
                        translator = Translator()
                        correct_translation = translator.translate(phrase, src=lang_source, dest=lang_target).text
                        
                        st.success(f"✅ Traduction correcte: {correct_translation}")
                        
                        # Générer audio de la traduction correcte
                        audio_correct, _ = generate_audio_with_gtts(correct_translation, lang_target)
                        if audio_correct:
                            st.subheader("🔊 Version correcte")
                            with open(audio_correct, 'rb') as f:
                                audio_bytes = f.read()
                            st.audio(audio_bytes, format='audio/mpeg')
    
    elif exercise == "Exercice 4: Analyse Comparative":
        st.subheader("🔬 Analyse Comparative d'Audio")
        
        st.markdown("""
        ### Objectif
        Comparez deux fichiers audio et identifiez les différences.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Audio 1")
            
            option1 = st.radio(
                "Source",
                ["Générer avec gTTS", "Générer avec Edge-TTS", "Uploader"],
                key="audio1_source"
            )
            
            if option1 == "Générer avec gTTS":
                text1 = st.text_input("Texte", value="Analyse comparative des voix", key="text1")
                if st.button("Générer", key="gen1"):
                    audio1, _ = generate_audio_with_gtts(text1, 'fr')
                    if audio1:
                        with open(audio1, 'rb') as f:
                            st.session_state['audio1_bytes'] = f.read()
                        st.audio(st.session_state['audio1_bytes'], format='audio/mpeg')
            
            elif option1 == "Générer avec Edge-TTS":
                text1 = st.text_input("Texte", value="Analyse comparative des voix", key="text1_edge")
                voice1 = st.selectbox("Voix", ["fr-FR-DeniseNeural", "fr-FR-HenriNeural"], key="voice1")
                if st.button("Générer", key="gen1_edge"):
                    audio1, _ = asyncio.run(generate_audio_with_edge_tts(text1, voice1))
                    if audio1:
                        with open(audio1, 'rb') as f:
                            st.session_state['audio1_bytes'] = f.read()
                        st.audio(st.session_state['audio1_bytes'], format='audio/mpeg')
            
            else:
                uploaded1 = st.file_uploader("Upload", type=['mp3', 'wav'], key="upload1")
                if uploaded1:
                    st.session_state['audio1_bytes'] = uploaded1.read()
                    st.audio(st.session_state['audio1_bytes'], format='audio/mpeg')
        
        with col2:
            st.subheader("Audio 2")
            
            option2 = st.radio(
                "Source",
                ["Générer avec gTTS", "Générer avec Edge-TTS", "Uploader"],
                key="audio2_source"
            )
            
            if option2 == "Générer avec gTTS":
                text2 = st.text_input("Texte", value="Analyse comparative des voix", key="text2")
                if st.button("Générer", key="gen2"):
                    audio2, _ = generate_audio_with_gtts(text2, 'fr')
                    if audio2:
                        with open(audio2, 'rb') as f:
                            st.session_state['audio2_bytes'] = f.read()
                        st.audio(st.session_state['audio2_bytes'], format='audio/mpeg')
            
            elif option2 == "Générer avec Edge-TTS":
                text2 = st.text_input("Texte", value="Analyse comparative des voix", key="text2_edge")
                voice2 = st.selectbox("Voix", ["fr-FR-DeniseNeural", "fr-FR-HenriNeural"], key="voice2")
                if st.button("Générer", key="gen2_edge"):
                    audio2, _ = asyncio.run(generate_audio_with_edge_tts(text2, voice2))
                    if audio2:
                        with open(audio2, 'rb') as f:
                            st.session_state['audio2_bytes'] = f.read()
                        st.audio(st.session_state['audio2_bytes'], format='audio/mpeg')
            
            else:
                uploaded2 = st.file_uploader("Upload", type=['mp3', 'wav'], key="upload2")
                if uploaded2:
                    st.session_state['audio2_bytes'] = uploaded2.read()
                    st.audio(st.session_state['audio2_bytes'], format='audio/mpeg')
        
        # Analyse comparative
        if 'audio1_bytes' in st.session_state and 'audio2_bytes' in st.session_state:
            if st.button("🔬 Comparer", type="primary"):
                with st.spinner("Analyse comparative..."):
                    # Sauvegarder temporairement
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp1:
                        tmp1.write(st.session_state['audio1_bytes'])
                        path1 = tmp1.name
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp2:
                        tmp2.write(st.session_state['audio2_bytes'])
                        path2 = tmp2.name
                    
                    # Analyser les deux
                    analysis1, _ = analyze_audio(path1)
                    analysis2, _ = analyze_audio(path2)
                    
                    if analysis1 and analysis2:
                        st.success("✅ Analyse comparative terminée!")
                        
                        # Tableau comparatif
                        comparison_data = {
                            'Métrique': ['Durée', 'Sample Rate', 'Tempo', 'Énergie moyenne', 'Pitch moyen'],
                            'Audio 1': [
                                f"{analysis1['duration']:.2f} s",
                                f"{analysis1['sample_rate']} Hz",
                                f"{analysis1['tempo']:.0f} BPM",
                                f"{analysis1['energy_mean']:.4f}",
                                f"{analysis1['pitch_mean']:.1f} Hz"
                            ],
                            'Audio 2': [
                                f"{analysis2['duration']:.2f} s",
                                f"{analysis2['sample_rate']} Hz",
                                f"{analysis2['tempo']:.0f} BPM",
                                f"{analysis2['energy_mean']:.4f}",
                                f"{analysis2['pitch_mean']:.1f} Hz"
                            ],
                            'Différence': [
                                f"{abs(analysis1['duration'] - analysis2['duration']):.2f} s",
                                f"{abs(analysis1['sample_rate'] - analysis2['sample_rate'])} Hz",
                                f"{abs(analysis1['tempo'] - analysis2['tempo']):.0f} BPM",
                                f"{abs(analysis1['energy_mean'] - analysis2['energy_mean']):.4f}",
                                f"{abs(analysis1['pitch_mean'] - analysis2['pitch_mean']):.1f} Hz"
                            ]
                        }
                        
                        st.table(comparison_data)
                        
                        # Graphiques comparatifs
                        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
                        
                        # Waveforms
                        axes[0, 0].plot(analysis1['waveform'][:10000], alpha=0.7, label='Audio 1')
                        axes[0, 0].plot(analysis2['waveform'][:10000], alpha=0.7, label='Audio 2')
                        axes[0, 0].set_title('Formes d\'onde (10k samples)')
                        axes[0, 0].legend()
                        axes[0, 0].grid(True, alpha=0.3)
                        
                        # Métriques en barres
                        metrics = ['Durée', 'Tempo', 'Énergie', 'Pitch']
                        values1 = [
                            analysis1['duration'],
                            analysis1['tempo']/100,
                            analysis1['energy_mean']*100,
                            analysis1['pitch_mean']/100
                        ]
                        values2 = [
                            analysis2['duration'],
                            analysis2['tempo']/100,
                            analysis2['energy_mean']*100,
                            analysis2['pitch_mean']/100
                        ]
                        
                        x = np.arange(len(metrics))
                        width = 0.35
                        
                        axes[0, 1].bar(x - width/2, values1, width, label='Audio 1')
                        axes[0, 1].bar(x + width/2, values2, width, label='Audio 2')
                        axes[0, 1].set_xlabel('Métriques normalisées')
                        axes[0, 1].set_xticks(x)
                        axes[0, 1].set_xticklabels(metrics)
                        axes[0, 1].legend()
                        axes[0, 1].grid(True, alpha=0.3)
                        
                        # Spectrogrammes (portions)
                        axes[1, 0].imshow(analysis1['spectrogram'][:, :100], aspect='auto', origin='lower')
                        axes[1, 0].set_title('Spectrogramme Audio 1')
                        
                        axes[1, 1].imshow(analysis2['spectrogram'][:, :100], aspect='auto', origin='lower')
                        axes[1, 1].set_title('Spectrogramme Audio 2')
                        
                        plt.tight_layout()
                        st.pyplot(fig)
                    
                    # Nettoyer
                    os.unlink(path1)
                    os.unlink(path2)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>Module 1 - Formation Data Engineering - Version Complète</p>
    <p>TTS | STT | Translation | Analyse Audio | Exercices</p>
</div>
""", unsafe_allow_html=True)