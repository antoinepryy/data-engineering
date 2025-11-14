# 🔊 Guide Text-to-Speech (TTS) - Module Vocal

## ✅ État Actuel des Moteurs TTS

| Moteur | Status | Recommandation | Notes |
|--------|--------|----------------|-------|
| **gTTS (Google)** | ✅ Fonctionnel | ⭐⭐⭐⭐⭐ | Meilleure qualité, nécessite internet |
| **Edge-TTS (Microsoft)** | ✅ Fonctionnel | ⭐⭐⭐⭐⭐ | Excellente qualité, gratuit, nécessite internet |
| **pyttsx3 (Offline)** | ⚠️ Limité | ⭐⭐⭐ | Fonctionne mais génère des fichiers, pas de lecture directe |

---

## 🚀 Solutions pour pyttsx3 dans Docker

### Problème
pyttsx3 ne peut pas lire directement l'audio dans Docker car il n'y a pas d'accès au périphérique audio du host.

### Solution Actuelle
pyttsx3 génère maintenant des fichiers audio `.wav` qui peuvent être téléchargés et lus dans le navigateur.

### Configuration pyttsx3
- **141 voix disponibles** avec eSpeak
- Langues supportées : Français, Anglais, Espagnol, Allemand, et 130+ autres
- Vitesse ajustable : 100-300 mots/minute
- Volume ajustable : 0.0-1.0

---

## 💡 Recommandations d'Usage

### Pour la Production
Utilisez **gTTS** ou **Edge-TTS** :
- Qualité audio supérieure
- Voix plus naturelles
- Support multilingue étendu

### Pour le Développement Offline
Utilisez **pyttsx3** avec sauvegarde de fichiers :
- Fonctionne sans internet
- 141 voix disponibles
- Idéal pour tests et prototypage

---

## 📝 Exemples de Code

### gTTS (Recommandé)
```python
from gtts import gTTS
import tempfile

def generate_gtts(text, lang='fr'):
    tts = gTTS(text=text, lang=lang, slow=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        tts.save(tmp_file.name)
        return tmp_file.name
```

### Edge-TTS (Recommandé)
```python
import edge_tts
import asyncio
import tempfile

async def generate_edge_tts(text, voice='fr-FR-DeniseNeural'):
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        await communicate.save(tmp_file.name)
        return tmp_file.name
```

### pyttsx3 (Docker-compatible)
```python
import pyttsx3
import tempfile

def generate_pyttsx3(text, rate=150, volume=0.9):
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        engine.save_to_file(text, tmp_file.name)
        engine.runAndWait()
        return tmp_file.name
```

---

## 🔧 Dépannage

### Si pyttsx3 ne fonctionne pas
```bash
# Installer les dépendances dans le container
docker exec vocal-python apt-get update
docker exec vocal-python apt-get install -y espeak espeak-ng alsa-utils

# Tester
docker exec vocal-python python -c "import pyttsx3; engine = pyttsx3.init(); print('OK')"
```

### Pour redémarrer Streamlit
```bash
docker exec vocal-python pkill streamlit
docker exec -d vocal-python streamlit run /app/app.py --server.port=8501 --server.address=0.0.0.0
```

---

## 🎯 Exercices Pratiques

### Exercice 1 : Comparer les Moteurs
1. Ouvrir http://localhost:8501
2. Tester le même texte avec les 3 moteurs
3. Comparer :
   - Qualité audio
   - Temps de génération
   - Taille du fichier

### Exercice 2 : Multilangue
1. Utiliser gTTS pour générer en 5 langues différentes
2. Texte : "Hello, how are you?"
3. Langues : en, fr, es, de, ja

### Exercice 3 : Voix Personnalisées
1. Avec Edge-TTS, tester différentes voix :
   - `fr-FR-DeniseNeural` (femme)
   - `fr-FR-HenriNeural` (homme)
   - `en-US-AriaNeural` (femme US)
   - `en-GB-RyanNeural` (homme UK)

---

## 📚 Ressources

- [Documentation gTTS](https://gtts.readthedocs.io/)
- [Edge-TTS GitHub](https://github.com/rany2/edge-tts)
- [pyttsx3 Documentation](https://pyttsx3.readthedocs.io/)
- [Liste des voix Edge-TTS](https://github.com/rany2/edge-tts#voices)

---

## ✨ Astuce Pro

Pour une expérience optimale dans Docker, créez un pipeline hybride :
1. Utilisez Edge-TTS pour la qualité quand internet disponible
2. Fallback sur gTTS si Edge-TTS échoue
3. Fallback final sur pyttsx3 pour le mode offline

```python
async def smart_tts(text, lang='fr'):
    try:
        # Essayer Edge-TTS d'abord
        return await generate_edge_tts(text)
    except:
        try:
            # Fallback sur gTTS
            return generate_gtts(text, lang)
        except:
            # Fallback final sur pyttsx3
            return generate_pyttsx3(text)
```

---

**Note**: La formation est conçue pour fonctionner avec tous les moteurs. Les limitations de pyttsx3 dans Docker sont normales et n'affectent pas l'apprentissage des concepts TTS.