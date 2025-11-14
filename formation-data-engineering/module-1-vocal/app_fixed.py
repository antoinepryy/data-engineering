"""
Version corrigée de l'application Streamlit pour les démonstrations de traitement vocal
Module 1 - Formation Data Engineering
"""

import streamlit as st
from gtts import gTTS
import tempfile
import os
from datetime import datetime
import asyncio
import edge_tts
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
    <h1>🎤 Module 1: Traitement Vocal (Version Corrigée)</h1>
    <p>Text-to-Speech optimisé pour Docker</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    demo_mode = st.selectbox(
        "Choisir une démo",
        ["Text-to-Speech", "Générateur Multi-voix", "Comparaison TTS"]
    )
    
    st.divider()
    
    # Informations système
    st.success("""
    **Moteurs TTS disponibles:**
    - ✅ gTTS (Google) - Fonctionnel
    - ✅ Edge TTS (Microsoft) - Fonctionnel
    - ⚠️ pyttsx3 - Désactivé (incompatible Docker)
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

def get_audio_download_link(audio_file, filename="audio.mp3"):
    """Créer un lien de téléchargement pour le fichier audio"""
    with open(audio_file, 'rb') as f:
        audio_bytes = f.read()
    b64 = base64.b64encode(audio_bytes).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">📥 Télécharger l\'audio</a>'
    return href

# ============================================================================
# DEMO 1: TEXT-TO-SPEECH SIMPLE
# ============================================================================

if demo_mode == "Text-to-Speech":
    st.header("🔊 Text-to-Speech Simple et Fonctionnel")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Configuration")
        
        # Choix du moteur (sans pyttsx3)
        tts_engine = st.selectbox(
            "Moteur TTS",
            ["gTTS (Google)", "Edge-TTS (Microsoft)"]
        )
        
        # Texte à convertir
        text_input = st.text_area(
            "Texte à convertir",
            value="Bonjour et bienvenue dans la formation Data Engineering. Cette version fonctionne parfaitement dans Docker avec gTTS et Edge-TTS.",
            height=100
        )
        
        # Paramètres selon le moteur
        if tts_engine == "gTTS (Google)":
            lang = st.selectbox("Langue", [
                ("Français", "fr"),
                ("English", "en"),
                ("Español", "es"),
                ("Deutsch", "de"),
                ("Italiano", "it"),
                ("Português", "pt"),
                ("日本語", "ja"),
                ("中文", "zh")
            ], format_func=lambda x: x[0])
            slow = st.checkbox("Parler lentement", value=False)
            
        elif tts_engine == "Edge-TTS (Microsoft)":
            voice = st.selectbox(
                "Voix",
                [
                    ("Denise (FR Femme)", "fr-FR-DeniseNeural"),
                    ("Henri (FR Homme)", "fr-FR-HenriNeural"),
                    ("Aria (US Femme)", "en-US-AriaNeural"),
                    ("Guy (US Homme)", "en-US-GuyNeural"),
                    ("Jenny (UK Femme)", "en-GB-SoniaNeural"),
                    ("Ryan (UK Homme)", "en-GB-RyanNeural"),
                    ("Elvira (ES Femme)", "es-ES-ElviraNeural"),
                    ("Alvaro (ES Homme)", "es-ES-AlvaroNeural"),
                ],
                format_func=lambda x: x[0]
            )
            rate = st.select_slider(
                "Vitesse",
                options=["-50%", "-25%", "+0%", "+25%", "+50%"],
                value="+0%"
            )
        
        # Bouton de génération
        if st.button("🎵 Générer Audio", key="generate_tts", type="primary"):
            if not text_input.strip():
                st.error("❌ Veuillez entrer du texte")
            else:
                with st.spinner("Génération en cours..."):
                    try:
                        audio_file = None
                        error = None
                        
                        if tts_engine == "gTTS (Google)":
                            # gTTS implementation
                            tts = gTTS(text=text_input, lang=lang[1], slow=slow)
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                                tts.save(tmp_file.name)
                                audio_file = tmp_file.name
                        
                        elif tts_engine == "Edge-TTS (Microsoft)":
                            # Edge-TTS implementation
                            async def generate():
                                communicate = edge_tts.Communicate(text_input, voice[1], rate=rate)
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                                    await communicate.save(tmp_file.name)
                                    return tmp_file.name
                            
                            audio_file = asyncio.run(generate())
                        
                        # Vérifier que le fichier existe et n'est pas vide
                        if audio_file and os.path.exists(audio_file):
                            file_size = os.path.getsize(audio_file)
                            if file_size > 0:
                                st.success(f"✅ Audio généré avec succès! (Taille: {file_size:,} bytes)")
                                
                                # Lire le fichier audio
                                with open(audio_file, 'rb') as f:
                                    audio_bytes = f.read()
                                
                                # Afficher le lecteur audio avec les bytes
                                st.audio(audio_bytes, format='audio/mpeg')
                                
                                # Option de téléchargement
                                # Créer un nom de fichier propre
                                if "gTTS" in tts_engine:
                                    engine_name = "gtts"
                                else:
                                    engine_name = "edge_tts"
                                
                                st.download_button(
                                    label="📥 Télécharger l'audio",
                                    data=audio_bytes,
                                    file_name=f"audio_{engine_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                                    mime="audio/mpeg"
                                )
                                
                                # Nettoyer après un délai
                                # Note: En production, utilisez un système de nettoyage asynchrone
                                # os.unlink(audio_file)
                            else:
                                st.error(f"❌ Le fichier audio est vide (0 bytes)")
                        else:
                            st.error(f"❌ Erreur lors de la génération du fichier audio")
                            
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
                        st.info("💡 Conseil: Vérifiez votre connexion internet pour gTTS et Edge-TTS")
    
    with col2:
        st.subheader("📚 Informations")
        
        with st.expander("✅ Pourquoi ces moteurs fonctionnent dans Docker"):
            st.markdown("""
            ### gTTS (Google Text-to-Speech)
            - **Cloud-based**: Utilise l'API Google
            - **Qualité**: Excellente, voix naturelles
            - **Langues**: 50+ langues supportées
            - **Limitation**: Nécessite internet
            
            ### Edge-TTS (Microsoft Edge)
            - **Cloud-based**: Utilise l'API Microsoft Edge
            - **Qualité**: Très haute, voix neuronales
            - **Voix**: Multiples voix par langue
            - **Avantage**: Gratuit et illimité
            
            ### Pourquoi pas pyttsx3?
            - Docker n'a pas d'accès direct au système audio
            - Les fichiers générés sont souvent vides
            - Solution: Utiliser les alternatives cloud
            """)
        
        with st.expander("💻 Code Example"):
            st.code("""
# gTTS - Simple et efficace
from gtts import gTTS

def text_to_speech_gtts(text, lang='fr'):
    tts = gTTS(text=text, lang=lang)
    tts.save("output.mp3")
    return "output.mp3"

# Edge-TTS - Plus d'options
import edge_tts
import asyncio

async def text_to_speech_edge(text, voice='fr-FR-DeniseNeural'):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("output.mp3")
    return "output.mp3"

# Utilisation
audio_file = text_to_speech_gtts("Bonjour le monde!", 'fr')
# ou
audio_file = asyncio.run(
    text_to_speech_edge("Hello world!", 'en-US-AriaNeural')
)
            """, language='python')

# ============================================================================
# DEMO 2: GÉNÉRATEUR MULTI-VOIX
# ============================================================================

elif demo_mode == "Générateur Multi-voix":
    st.header("🎭 Générateur Multi-voix avec Edge-TTS")
    
    st.info("Cette démo génère le même texte avec différentes voix pour comparaison")
    
    # Texte d'entrée
    text = st.text_area(
        "Texte à générer",
        value="La technologie de synthèse vocale a fait d'énormes progrès. Écoutez la différence entre ces voix.",
        height=80
    )
    
    # Sélection des voix
    voices_to_test = st.multiselect(
        "Sélectionner les voix à tester",
        [
            "fr-FR-DeniseNeural",
            "fr-FR-HenriNeural",
            "fr-CA-SylvieNeural",
            "fr-CH-ArianeNeural",
            "en-US-AriaNeural",
            "en-US-GuyNeural",
            "en-GB-SoniaNeural",
            "es-ES-ElviraNeural"
        ],
        default=["fr-FR-DeniseNeural", "fr-FR-HenriNeural"]
    )
    
    if st.button("🎵 Générer toutes les voix", type="primary"):
        if not text.strip():
            st.error("Veuillez entrer du texte")
        elif not voices_to_test:
            st.error("Veuillez sélectionner au moins une voix")
        else:
            st.write(f"Génération de {len(voices_to_test)} voix...")
            
            # Créer des colonnes pour afficher les résultats
            cols = st.columns(2)
            
            for idx, voice in enumerate(voices_to_test):
                col = cols[idx % 2]
                
                with col:
                    with st.container():
                        st.write(f"**{voice}**")
                        
                        with st.spinner(f"Génération {voice}..."):
                            try:
                                # Générer l'audio
                                async def generate():
                                    communicate = edge_tts.Communicate(text, voice)
                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                                        await communicate.save(tmp_file.name)
                                        return tmp_file.name
                                
                                audio_file = asyncio.run(generate())
                                
                                if audio_file and os.path.exists(audio_file):
                                    file_size = os.path.getsize(audio_file)
                                    if file_size > 0:
                                        # Lire le fichier audio
                                        with open(audio_file, 'rb') as f:
                                            audio_bytes = f.read()
                                        st.audio(audio_bytes, format='audio/mpeg')
                                        st.caption(f"Taille: {file_size:,} bytes")
                                    else:
                                        st.error("Fichier vide")
                                else:
                                    st.error("Erreur de génération")
                                    
                            except Exception as e:
                                st.error(f"Erreur: {str(e)}")

# ============================================================================
# DEMO 3: COMPARAISON TTS
# ============================================================================

elif demo_mode == "Comparaison TTS":
    st.header("🔬 Comparaison des Moteurs TTS")
    
    # Texte de test
    test_text = st.text_area(
        "Texte de test",
        value="Ceci est un test de comparaison entre différents moteurs de synthèse vocale. Chaque moteur a ses propres caractéristiques.",
        height=80
    )
    
    if st.button("🚀 Lancer la comparaison", type="primary"):
        if not test_text.strip():
            st.error("Veuillez entrer du texte")
        else:
            results = {}
            
            col1, col2 = st.columns(2)
            
            # Test gTTS
            with col1:
                st.subheader("gTTS (Google)")
                with st.spinner("Génération..."):
                    try:
                        import time
                        start = time.time()
                        
                        tts = gTTS(text=test_text, lang='fr')
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                            tts.save(tmp_file.name)
                            audio_file = tmp_file.name
                        
                        elapsed = time.time() - start
                        file_size = os.path.getsize(audio_file)
                        
                        if file_size > 0:
                            st.success(f"✅ Succès en {elapsed:.2f}s")
                            # Lire le fichier audio
                            with open(audio_file, 'rb') as f:
                                audio_bytes = f.read()
                            st.audio(audio_bytes, format='audio/mpeg')
                            st.metric("Taille du fichier", f"{file_size:,} bytes")
                            st.metric("Temps de génération", f"{elapsed:.2f} secondes")
                        else:
                            st.error("Fichier vide généré")
                            
                    except Exception as e:
                        st.error(f"Erreur: {str(e)}")
            
            # Test Edge-TTS
            with col2:
                st.subheader("Edge-TTS (Microsoft)")
                with st.spinner("Génération..."):
                    try:
                        import time
                        start = time.time()
                        
                        async def generate():
                            communicate = edge_tts.Communicate(test_text, 'fr-FR-DeniseNeural')
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                                await communicate.save(tmp_file.name)
                                return tmp_file.name
                        
                        audio_file = asyncio.run(generate())
                        elapsed = time.time() - start
                        file_size = os.path.getsize(audio_file)
                        
                        if file_size > 0:
                            st.success(f"✅ Succès en {elapsed:.2f}s")
                            # Lire le fichier audio
                            with open(audio_file, 'rb') as f:
                                audio_bytes = f.read()
                            st.audio(audio_bytes, format='audio/mpeg')
                            st.metric("Taille du fichier", f"{file_size:,} bytes")
                            st.metric("Temps de génération", f"{elapsed:.2f} secondes")
                        else:
                            st.error("Fichier vide généré")
                            
                    except Exception as e:
                        st.error(f"Erreur: {str(e)}")
            
            # Résumé
            st.divider()
            st.subheader("📊 Résumé")
            st.info("""
            **Recommandations:**
            - **Qualité audio**: Edge-TTS > gTTS
            - **Vitesse**: gTTS ≈ Edge-TTS
            - **Options de voix**: Edge-TTS (multiple) > gTTS (une par langue)
            - **Fiabilité**: Les deux sont très fiables
            - **Coût**: Les deux sont gratuits
            """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>Module 1 - Version corrigée pour Docker</p>
    <p>✅ gTTS et Edge-TTS fonctionnels | ⚠️ pyttsx3 désactivé (incompatible Docker)</p>
</div>
""", unsafe_allow_html=True)