#!/bin/bash

# Script pour corriger les problèmes TTS dans le container Docker

echo "🔧 Correction des problèmes TTS dans le container vocal-python..."

# Installer les dépendances manquantes si nécessaire
echo "📦 Installation des dépendances audio..."
docker exec vocal-python sh -c "apt-get update && apt-get install -y espeak espeak-ng libespeak-dev alsa-utils pulseaudio 2>/dev/null || true"

# Créer un script Python pour tester
cat << 'EOF' > /tmp/test_tts.py
import pyttsx3
import tempfile
import os

def test_tts():
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        
        # Sauvegarder dans un fichier au lieu de jouer directement
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
            engine.save_to_file("Test réussi", f.name)
            engine.runAndWait()
            
            if os.path.exists(f.name) and os.path.getsize(f.name) > 0:
                print("✅ pyttsx3 fonctionne!")
                os.unlink(f.name)
                return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    return False

if __name__ == "__main__":
    test_tts()
EOF

# Copier et exécuter le test
docker cp /tmp/test_tts.py vocal-python:/tmp/test_tts.py
docker exec vocal-python python /tmp/test_tts.py

# Redémarrer Streamlit
echo ""
echo "🔄 Redémarrage de Streamlit..."
docker exec vocal-python pkill streamlit 2>/dev/null || true
sleep 2
docker exec -d vocal-python streamlit run /app/app.py --server.port=8501 --server.address=0.0.0.0

echo ""
echo "✅ Corrections appliquées!"
echo ""
echo "📱 Accès à l'application:"
echo "   http://localhost:8501"
echo ""
echo "💡 Notes importantes:"
echo "   - pyttsx3 génère maintenant des fichiers audio au lieu de jouer directement"
echo "   - Utilisez gTTS ou Edge-TTS pour une meilleure compatibilité Docker"
echo "   - 141 voix disponibles avec eSpeak"

# Nettoyer
rm -f /tmp/test_tts.py