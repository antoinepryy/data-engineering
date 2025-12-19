"""
Serveur API Flask pour le module STT.
Point d'entree pour l'API de transcription audio.

Usage:
    python api_server.py

Ou via gunicorn:
    gunicorn -w 2 -b 0.0.0.0:5000 api_server:app
"""

import sys
import os

# Ajouter le chemin du module-5-expo pour les imports
sys.path.insert(0, '/app/module-5-expo')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS

# Import du blueprint STT
from api.routes import stt_bp

# Creer l'application Flask
app = Flask(__name__)

# Activer CORS pour toutes les origines (necessaire pour l'app Expo)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Enregistrer le blueprint STT
app.register_blueprint(stt_bp)


@app.route('/')
def index():
    """Page d'accueil de l'API."""
    return jsonify({
        "service": "STT API",
        "version": "1.0.0",
        "endpoints": {
            "transcribe": "POST /api/stt/transcribe",
            "engines": "GET /api/stt/engines",
            "health": "GET /api/stt/health"
        }
    })


@app.route('/health')
def health():
    """Health check global."""
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    print("Starting STT API server on http://0.0.0.0:5000")
    print("Endpoints:")
    print("  POST /api/stt/transcribe - Transcription audio")
    print("  GET  /api/stt/engines    - Liste des moteurs")
    print("  GET  /api/stt/health     - Health check")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    )
