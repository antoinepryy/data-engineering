"""
Patch pour le module TTS dans Docker
Ce fichier contient une version modifiée pour gérer pyttsx3 dans Docker
"""

import pyttsx3
import tempfile
import os
import streamlit as st

def test_pyttsx3_docker():
    """Test pyttsx3 avec génération de fichier au lieu de lecture directe"""
    try:
        # Initialiser pyttsx3
        engine = pyttsx3.init()
        
        # Configurer les propriétés
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        # Texte de test
        text = "Test de pyttsx3 dans Docker. La synthèse vocale fonctionne maintenant."
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            # Sauvegarder dans le fichier
            engine.save_to_file(text, tmp_file.name)
            engine.runAndWait()
            
            # Vérifier que le fichier existe et n'est pas vide
            if os.path.exists(tmp_file.name) and os.path.getsize(tmp_file.name) > 0:
                print(f"✅ Fichier audio créé: {tmp_file.name}")
                print(f"   Taille: {os.path.getsize(tmp_file.name)} bytes")
                return tmp_file.name
            else:
                print("❌ Fichier audio vide ou non créé")
                return None
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def get_pyttsx3_voices():
    """Obtenir la liste des voix disponibles"""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        voice_list = []
        for voice in voices:
            voice_info = {
                'id': voice.id,
                'name': voice.name,
                'languages': voice.languages,
                'gender': voice.gender,
                'age': voice.age
            }
            voice_list.append(voice_info)
            print(f"Voice: {voice.name} - {voice.id}")
        
        return voice_list
    except Exception as e:
        print(f"Erreur lors de la récupération des voix: {e}")
        return []

if __name__ == "__main__":
    print("=== Test pyttsx3 dans Docker ===")
    
    # Test de génération de fichier
    audio_file = test_pyttsx3_docker()
    
    if audio_file:
        print(f"\n✅ pyttsx3 fonctionne correctement!")
        print(f"   Fichier audio: {audio_file}")
        
        # Lister les voix disponibles
        print("\n=== Voix disponibles ===")
        voices = get_pyttsx3_voices()
        print(f"Nombre de voix: {len(voices)}")
        
        # Nettoyer
        if os.path.exists(audio_file):
            os.unlink(audio_file)
            print(f"\n🧹 Fichier temporaire supprimé")
    else:
        print("\n❌ pyttsx3 ne fonctionne pas correctement")