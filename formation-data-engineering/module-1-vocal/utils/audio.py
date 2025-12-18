"""
Fonctions utilitaires pour le traitement audio
"""

import tempfile
import os
import streamlit as st
import librosa
import numpy as np
from pydub import AudioSegment


def load_audio(file_path: str, sr: int = 22050):
    """
    Charge un fichier audio avec librosa.

    Args:
        file_path: Chemin vers le fichier audio
        sr: Sample rate cible (défaut: 22050 Hz)

    Returns:
        Tuple (signal audio, sample rate)
    """
    y, sr = librosa.load(file_path, sr=sr)
    return y, sr


def save_uploaded_file(uploaded_file) -> str:
    """
    Sauvegarde un fichier uploadé dans un fichier temporaire.

    Args:
        uploaded_file: Fichier uploadé via st.file_uploader

    Returns:
        Chemin vers le fichier temporaire
    """
    suffix = f'.{uploaded_file.name.split(".")[-1]}'
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name


def save_audio_input(audio_data) -> str:
    """
    Sauvegarde un enregistrement st.audio_input dans un fichier temporaire.

    Args:
        audio_data: Données audio de st.audio_input

    Returns:
        Chemin vers le fichier temporaire WAV
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        tmp_file.write(audio_data.getvalue())
        return tmp_file.name


def convert_to_wav(input_path: str, output_sr: int = 16000) -> str:
    """
    Convertit un fichier audio en WAV mono avec le sample rate spécifié.
    Utile pour Vosk et autres moteurs STT.

    Args:
        input_path: Chemin vers le fichier audio source
        output_sr: Sample rate de sortie (défaut: 16000 Hz pour Vosk)

    Returns:
        Chemin vers le fichier WAV converti
    """
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(output_sr)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        audio.export(tmp_file.name, format="wav")
        return tmp_file.name


def get_audio_info(file_path: str) -> dict:
    """
    Extrait les informations de base d'un fichier audio.

    Args:
        file_path: Chemin vers le fichier audio

    Returns:
        Dictionnaire avec durée, sample rate, nombre d'échantillons
    """
    y, sr = librosa.load(file_path, sr=None)  # Garder le SR original
    return {
        'duration': librosa.get_duration(y=y, sr=sr),
        'sample_rate': sr,
        'samples': len(y),
        'channels': 1 if y.ndim == 1 else y.shape[0],
        'max_amplitude': float(np.max(np.abs(y))),
    }


def cleanup_temp_file(file_path: str):
    """
    Supprime un fichier temporaire de manière sécurisée.

    Args:
        file_path: Chemin vers le fichier à supprimer
    """
    if file_path and os.path.exists(file_path):
        try:
            os.unlink(file_path)
        except Exception:
            pass  # Ignorer les erreurs de suppression
