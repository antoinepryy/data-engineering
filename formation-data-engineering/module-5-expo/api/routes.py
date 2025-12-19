"""
Routes Flask pour l'API STT.
Endpoints pour la transcription audio avec plusieurs moteurs.
"""

from flask import Blueprint, request, jsonify
import tempfile
import os
import logging

from .engines import WhisperEngine, VoskEngine, GoogleEngine

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint Flask
stt_bp = Blueprint('stt', __name__, url_prefix='/api/stt')

# Registre des moteurs STT disponibles
# Pour ajouter un nouveau moteur: l'importer et l'ajouter ici
ENGINES = {
    "whisper": WhisperEngine(model_size="tiny"),
    "vosk": VoskEngine(),
    "google": GoogleEngine(),
}


@stt_bp.route('/transcribe', methods=['POST'])
def transcribe():
    """
    POST /api/stt/transcribe

    Transcrit un fichier audio en texte.

    Form Data:
        - audio: Fichier audio (wav, mp3, m4a, ogg, webm)
        - engine: Moteur STT a utiliser (whisper, vosk, google). Defaut: whisper
        - language: Code langue (fr, en, auto, etc.). Defaut: fr

    Returns:
        JSON:
            - text: Texte transcrit
            - language: Langue detectee/utilisee
            - engine: Moteur utilise

        Ou en cas d'erreur:
            - error: Message d'erreur
    """
    # Verifier qu'un fichier audio est present
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']

    if audio_file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # Recuperer les parametres
    engine_name = request.form.get('engine', 'whisper')
    language = request.form.get('language', 'fr')

    # Verifier que le moteur existe
    if engine_name not in ENGINES:
        available = list(ENGINES.keys())
        return jsonify({
            "error": f"Unknown engine: {engine_name}. Available: {available}"
        }), 400

    engine = ENGINES[engine_name]

    # Verifier que le moteur est disponible
    if not engine.is_available():
        return jsonify({
            "error": f"Engine {engine_name} is not available"
        }), 503

    # Sauvegarder le fichier temporairement
    suffix = os.path.splitext(audio_file.filename)[1] or '.wav'

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        audio_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        logger.info(f"Transcribing with {engine_name}, language={language}")

        # Transcrire
        result = engine.transcribe(tmp_path, language)

        logger.info(f"Transcription complete: {len(result.get('text', ''))} chars")

        return jsonify(result)

    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@stt_bp.route('/engines', methods=['GET'])
def list_engines():
    """
    GET /api/stt/engines

    Liste les moteurs STT disponibles et leur statut.

    Returns:
        JSON avec pour chaque moteur:
            - available: bool - Si le moteur peut etre utilise
            - languages: list - Langues supportees
    """
    result = {}

    for name, engine in ENGINES.items():
        result[name] = {
            "available": engine.is_available(),
            "languages": engine.get_supported_languages()
        }

    return jsonify(result)


@stt_bp.route('/health', methods=['GET'])
def health():
    """
    GET /api/stt/health

    Health check endpoint.

    Returns:
        JSON avec status 'ok'
    """
    return jsonify({"status": "ok", "service": "stt-api"})
