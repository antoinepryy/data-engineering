"""
Fonctions de visualisation audio avec librosa et matplotlib
"""

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np


def create_waveform(y, sr, title="Forme d'onde"):
    """
    Crée une visualisation de la forme d'onde.

    Args:
        y: Signal audio
        sr: Sample rate
        title: Titre du graphique

    Returns:
        Figure matplotlib
    """
    fig, ax = plt.subplots(figsize=(12, 3))
    librosa.display.waveshow(y, sr=sr, ax=ax, color='#667eea')
    ax.set_title(title)
    ax.set_xlabel("Temps (s)")
    ax.set_ylabel("Amplitude")
    plt.tight_layout()
    return fig


def create_spectrogram(y, sr, n_fft=2048, hop_length=512, spec_type='mel', n_mels=128, cmap='viridis'):
    """
    Crée un spectrogramme (STFT ou Mel).

    Args:
        y: Signal audio
        sr: Sample rate
        n_fft: Taille de la FFT
        hop_length: Pas entre les fenêtres
        spec_type: 'mel' ou 'stft'
        n_mels: Nombre de bandes Mel (si spec_type='mel')
        cmap: Colormap matplotlib

    Returns:
        Figure matplotlib
    """
    fig, ax = plt.subplots(figsize=(12, 4))

    if spec_type == 'mel':
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels)
        S_db = librosa.power_to_db(S, ref=np.max)
        img = librosa.display.specshow(S_db, sr=sr, hop_length=hop_length,
                                       x_axis='time', y_axis='mel', ax=ax, cmap=cmap)
        ax.set_title("Spectrogramme Mel")
    else:  # STFT
        D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
        S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        img = librosa.display.specshow(S_db, sr=sr, hop_length=hop_length,
                                       x_axis='time', y_axis='hz', ax=ax, cmap=cmap)
        ax.set_title("Spectrogramme STFT")

    fig.colorbar(img, ax=ax, format='%+2.0f dB')
    ax.set_xlabel("Temps (s)")
    plt.tight_layout()
    return fig


def create_mfcc_plot(y, sr, n_mfcc=13):
    """
    Crée une visualisation des MFCC.

    Args:
        y: Signal audio
        sr: Sample rate
        n_mfcc: Nombre de coefficients MFCC

    Returns:
        Tuple (Figure matplotlib, matrice MFCC)
    """
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)

    fig, ax = plt.subplots(figsize=(12, 4))
    img = librosa.display.specshow(mfccs, sr=sr, x_axis='time', ax=ax, cmap='coolwarm')
    fig.colorbar(img, ax=ax)
    ax.set_title(f"MFCC ({n_mfcc} coefficients)")
    ax.set_ylabel("Coefficient MFCC")
    ax.set_xlabel("Temps (s)")
    plt.tight_layout()

    return fig, mfccs


def create_pitch_plot(y, sr):
    """
    Crée une visualisation du pitch (F0).

    Args:
        y: Signal audio
        sr: Sample rate

    Returns:
        Tuple (Figure matplotlib, valeurs F0)
    """
    # Extraction du pitch avec pyin
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7')
    )

    times = librosa.times_like(f0, sr=sr)

    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(times, f0, color='#e74c3c', linewidth=1.5)
    ax.set_title("Analyse du Pitch (F0)")
    ax.set_xlabel("Temps (s)")
    ax.set_ylabel("Fréquence (Hz)")
    ax.set_ylim([0, 500])
    plt.tight_layout()

    return fig, f0


def create_energy_plot(y, sr, frame_length=2048, hop_length=512):
    """
    Crée une visualisation de l'énergie RMS.

    Args:
        y: Signal audio
        sr: Sample rate
        frame_length: Longueur de la fenêtre
        hop_length: Pas entre les fenêtres

    Returns:
        Tuple (Figure matplotlib, valeurs RMS)
    """
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    times = librosa.times_like(rms, sr=sr, hop_length=hop_length)

    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(times, rms, color='#2ecc71', linewidth=1.5)
    ax.fill_between(times, rms, alpha=0.3, color='#2ecc71')
    ax.set_title("Energie RMS")
    ax.set_xlabel("Temps (s)")
    ax.set_ylabel("Amplitude RMS")
    plt.tight_layout()

    return fig, rms


def extract_audio_features(y, sr):
    """
    Extrait un ensemble complet de caractéristiques audio.

    Args:
        y: Signal audio
        sr: Sample rate

    Returns:
        Dictionnaire de caractéristiques
    """
    features = {
        'duration': librosa.get_duration(y=y, sr=sr),
        'sample_rate': sr,
        'rms_mean': float(np.mean(librosa.feature.rms(y=y))),
        'rms_std': float(np.std(librosa.feature.rms(y=y))),
        'zcr_mean': float(np.mean(librosa.feature.zero_crossing_rate(y))),
        'spectral_centroid_mean': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
        'spectral_bandwidth_mean': float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))),
        'spectral_rolloff_mean': float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))),
    }

    # Tempo (peut être lent sur de longs fichiers)
    try:
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = float(tempo)
    except Exception:
        features['tempo'] = None

    # Pitch analysis
    try:
        f0, voiced_flag, _ = librosa.pyin(
            y,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7')
        )
        if f0 is not None:
            features['pitch_mean'] = float(np.nanmean(f0))
            features['pitch_std'] = float(np.nanstd(f0))
            features['voiced_ratio'] = float(np.sum(voiced_flag) / len(voiced_flag)) if voiced_flag is not None else None
        else:
            features['pitch_mean'] = None
            features['pitch_std'] = None
            features['voiced_ratio'] = None
    except Exception:
        features['pitch_mean'] = None
        features['pitch_std'] = None
        features['voiced_ratio'] = None

    return features


def estimate_emotion(features: dict) -> dict:
    """
    Estimation basique de l'émotion basée sur les caractéristiques audio.
    AVERTISSEMENT: Cette analyse est simplifiée et à but éducatif uniquement.

    Args:
        features: Dictionnaire de caractéristiques audio

    Returns:
        Dictionnaire avec scores d'émotion et label estimé
    """
    # Normalisation simplifiée des features pour scoring
    energy = min(features.get('rms_mean', 0) * 10, 1.0)
    pitch_var = min(features.get('pitch_std', 0) / 100, 1.0) if features.get('pitch_std') else 0.3
    brightness = min(features.get('spectral_centroid_mean', 0) / 4000, 1.0)
    speech_rate = min(features.get('zcr_mean', 0) * 5, 1.0)

    # Calcul des scores d'émotion (heuristiques simplifiées)
    scores = {
        'Calme': max(0, 1 - energy - pitch_var),
        'Joyeux': max(0, energy * 0.5 + brightness * 0.3 + pitch_var * 0.2),
        'Triste': max(0, (1 - energy) * 0.4 + (1 - brightness) * 0.3 + (1 - speech_rate) * 0.3),
        'Energique': max(0, energy * 0.4 + speech_rate * 0.3 + pitch_var * 0.3),
    }

    # Normaliser pour que la somme soit 1
    total = sum(scores.values())
    if total > 0:
        scores = {k: v / total for k, v in scores.items()}

    # Label dominant
    dominant = max(scores, key=scores.get)

    return {
        'scores': scores,
        'dominant': dominant,
        'raw_features': {
            'energy': energy,
            'pitch_variance': pitch_var,
            'brightness': brightness,
            'speech_rate': speech_rate,
        }
    }
