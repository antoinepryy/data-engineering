# Module 5 - Application Expo STT

Application mobile React Native (Expo) pour la transcription Speech-to-Text via une API backend Flask.

## Architecture

```
module-5-expo/
├── api/                    # Backend Flask (monte dans vocal-python)
│   ├── routes.py           # Endpoints API STT
│   └── engines/            # Moteurs STT (extensible)
│       ├── base.py         # Classe de base
│       ├── whisper_engine.py
│       ├── vosk_engine.py
│       └── google_engine.py
│
└── app/                    # Frontend Expo React Native
    ├── App.tsx             # Composant principal
    ├── src/
    │   ├── hooks/
    │   │   └── useRecording.ts  # Hook enregistrement audio
    │   └── services/
    │       └── stt.ts           # Client API STT
    ├── app.json
    └── package.json
```

## Fonctionnalites

- **Enregistrement audio** via expo-av
- **Transcription** avec 3 moteurs:
  - **Whisper** (OpenAI) - Haute qualite, offline
  - **Vosk** - Leger, offline
  - **Google** - API cloud
- **Selection de langue** (francais, anglais, auto)
- **Interface intuitive** avec feedback en temps reel

## Demarrage

### 1. Backend (API Flask)

L'API est automatiquement lancee avec le conteneur `vocal-python`:

```bash
cd formation-data-engineering
docker-compose up vocal-python
```

L'API est disponible sur `http://localhost:5000`

#### Endpoints

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/stt/transcribe` | Transcrit un fichier audio |
| GET | `/api/stt/engines` | Liste les moteurs disponibles |
| GET | `/api/stt/health` | Health check |

#### Exemple d'appel

```bash
curl -X POST http://localhost:5000/api/stt/transcribe \
  -F "audio=@recording.m4a" \
  -F "engine=whisper" \
  -F "language=fr"
```

### 2. Frontend (App Expo)

```bash
cd formation-data-engineering/module-5-expo/app

# Installer les dependances
npm install

# Demarrer l'app
npx expo start
```

Puis scanner le QR code avec l'app Expo Go sur votre telephone.

**Note**: Pour que l'app mobile communique avec l'API backend:
- Sur simulateur iOS: `http://localhost:5000`
- Sur appareil physique: utiliser l'IP de votre machine (ex: `http://192.168.1.x:5000`)

Modifier `src/services/stt.ts` pour ajuster l'URL de l'API.

## Extensibilite

### Ajouter un nouveau moteur STT

1. Creer `api/engines/nouveau_engine.py`:

```python
from .base import BaseSTTEngine

class NouveauEngine(BaseSTTEngine):
    name = "nouveau"

    def transcribe(self, audio_path: str, language: str = "fr") -> dict:
        # Implementation
        return {
            "text": "...",
            "language": language,
            "engine": self.name
        }
```

2. L'ajouter dans `api/routes.py`:

```python
from .engines.nouveau_engine import NouveauEngine

ENGINES["nouveau"] = NouveauEngine()
```

3. Mettre a jour le frontend si necessaire.

## Dependances

### Backend (Python)
- Flask, flask-cors
- whisper (OpenAI)
- vosk
- speech_recognition
- pydub

### Frontend (Expo)
- expo ~51.0.0
- expo-av ~14.0.0
- expo-file-system ~17.0.0
- react-native 0.74.0

## Ports

| Service | Port | Description |
|---------|------|-------------|
| API STT | 5000 | Flask backend |
| Streamlit | 8501 | Interface module-1 |
