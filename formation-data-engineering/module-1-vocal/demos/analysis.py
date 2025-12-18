"""
Demo Analyse Audio
Visualisation et extraction de caracteristiques audio avec librosa
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from utils.audio import save_uploaded_file, save_audio_input, load_audio, get_audio_info
from utils.visualization import (
    create_waveform, create_spectrogram, create_mfcc_plot,
    create_pitch_plot, create_energy_plot, extract_audio_features, estimate_emotion
)


def render():
    """Affiche la demo Analyse Audio."""
    st.header("Analyse Audio")

    # Initialize session state
    if 'analysis_audio_file' not in st.session_state:
        st.session_state.analysis_audio_file = None

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Source Audio")

        input_method = st.radio(
            "Methode d'entree",
            ["Uploader un fichier", "Enregistrer"],
            horizontal=True
        )

        if input_method == "Uploader un fichier":
            uploaded_file = st.file_uploader(
                "Choisir un fichier audio",
                type=['wav', 'mp3', 'ogg', 'm4a'],
                key="analysis_uploader"
            )
            if uploaded_file:
                st.session_state.analysis_audio_file = save_uploaded_file(uploaded_file)
                st.audio(uploaded_file)

        else:
            audio_data = st.audio_input("Enregistrez votre voix")
            if audio_data:
                st.session_state.analysis_audio_file = save_audio_input(audio_data)
                st.audio(audio_data)

    with col2:
        if st.session_state.analysis_audio_file:
            st.subheader("Informations")
            try:
                info = get_audio_info(st.session_state.analysis_audio_file)
                st.metric("Duree", f"{info['duration']:.2f} s")
                st.metric("Sample Rate", f"{info['sample_rate']} Hz")
                st.metric("Amplitude Max", f"{info['max_amplitude']:.3f}")
            except Exception as e:
                st.error(f"Erreur: {e}")

    # Analyse si fichier disponible
    if st.session_state.analysis_audio_file:
        st.divider()

        # Charger l'audio
        try:
            y, sr = load_audio(st.session_state.analysis_audio_file)
        except Exception as e:
            st.error(f"Erreur de chargement: {e}")
            return

        # Onglets d'analyse
        tab1, tab2, tab3, tab4 = st.tabs(["Waveform", "Spectrogramme", "MFCC", "Metriques & Emotion"])

        with tab1:
            st.subheader("Forme d'onde")
            fig = create_waveform(y, sr)
            st.pyplot(fig)
            plt.close(fig)

            with st.expander("Qu'est-ce que la forme d'onde ?"):
                st.markdown("""
                La **forme d'onde** represente l'amplitude du signal audio au cours du temps.
                - **Axe X**: Temps en secondes
                - **Axe Y**: Amplitude (entre -1 et 1 apres normalisation)

                Elle permet de visualiser:
                - Les zones de silence vs parole
                - L'intensite relative du son
                - La duree totale de l'enregistrement
                """)

        with tab2:
            st.subheader("Spectrogramme")

            col_a, col_b = st.columns(2)
            with col_a:
                spec_type = st.selectbox("Type", ["mel", "stft"])
            with col_b:
                n_fft = st.selectbox("FFT Size", [512, 1024, 2048, 4096], index=2)

            fig = create_spectrogram(y, sr, n_fft=n_fft, spec_type=spec_type)
            st.pyplot(fig)
            plt.close(fig)

            with st.expander("Qu'est-ce qu'un spectrogramme ?"):
                st.markdown("""
                Le **spectrogramme** montre comment les frequences du signal evoluent dans le temps.
                - **Axe X**: Temps
                - **Axe Y**: Frequence (Hz pour STFT, echelle Mel pour Mel)
                - **Couleur**: Intensite en dB

                **Mel vs STFT**:
                - **STFT**: Echelle lineaire, montre toutes les frequences egalement
                - **Mel**: Echelle perceptuelle, plus proche de l'audition humaine
                """)

        with tab3:
            st.subheader("MFCC (Mel-Frequency Cepstral Coefficients)")

            n_mfcc = st.slider("Nombre de coefficients", 5, 40, 13)

            fig, mfccs = create_mfcc_plot(y, sr, n_mfcc=n_mfcc)
            st.pyplot(fig)
            plt.close(fig)

            # Stats MFCC
            st.write("**Statistiques MFCC:**")
            mfcc_stats = {
                f"MFCC {i+1}": {"Moyenne": f"{np.mean(mfccs[i]):.2f}", "Ecart-type": f"{np.std(mfccs[i]):.2f}"}
                for i in range(min(5, n_mfcc))
            }
            st.dataframe(mfcc_stats)

            with st.expander("Qu'est-ce que le MFCC ?"):
                st.markdown("""
                Les **MFCC** sont des caracteristiques audio tres utilisees en reconnaissance vocale.

                **Processus d'extraction:**
                1. Decoupage en trames (windowing)
                2. FFT sur chaque trame
                3. Application de filtres Mel
                4. Log du spectre
                5. DCT (Discrete Cosine Transform)

                **Utilisation:**
                - Reconnaissance vocale (ASR)
                - Identification de locuteur
                - Classification de genre musical
                """)

        with tab4:
            st.subheader("Metriques Audio")

            with st.spinner("Extraction des caracteristiques..."):
                features = extract_audio_features(y, sr)

            # Affichage des metriques
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Duree", f"{features['duration']:.2f} s")
                st.metric("Energie RMS", f"{features['rms_mean']:.4f}")

            with col2:
                st.metric("Centroide Spectral", f"{features['spectral_centroid_mean']:.0f} Hz")
                if features.get('tempo'):
                    st.metric("Tempo estime", f"{features['tempo']:.0f} BPM")

            with col3:
                if features.get('pitch_mean'):
                    st.metric("Pitch moyen", f"{features['pitch_mean']:.0f} Hz")
                if features.get('voiced_ratio'):
                    st.metric("Ratio voix", f"{features['voiced_ratio']*100:.0f}%")

            # Analyse d'emotion
            st.divider()
            st.subheader("Estimation de l'emotion (experimentale)")

            st.warning("Cette analyse est basee sur des heuristiques simples et n'est pas fiable pour une utilisation reelle.")

            emotion_result = estimate_emotion(features)

            # Afficher le resultat dominant
            st.markdown(f"### Emotion dominante: **{emotion_result['dominant']}**")

            # Barres de progression pour chaque emotion
            for emotion, score in emotion_result['scores'].items():
                st.progress(score, text=f"{emotion}: {score*100:.0f}%")

            # Radar des features brutes
            with st.expander("Caracteristiques utilisees"):
                raw = emotion_result['raw_features']
                st.write(f"- Energie: {raw['energy']:.2f}")
                st.write(f"- Variance pitch: {raw['pitch_variance']:.2f}")
                st.write(f"- Brillance: {raw['brightness']:.2f}")
                st.write(f"- Vitesse parole: {raw['speech_rate']:.2f}")

    else:
        st.info("Uploadez ou enregistrez un fichier audio pour commencer l'analyse.")

    # Section theorique
    st.divider()
    with st.expander("Code Example - Analyse Audio avec Librosa"):
        st.code("""
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

# Charger l'audio
y, sr = librosa.load("audio.wav", sr=22050)

# 1. Waveform
librosa.display.waveshow(y, sr=sr)

# 2. Mel Spectrogram
S = librosa.feature.melspectrogram(y=y, sr=sr)
S_dB = librosa.power_to_db(S, ref=np.max)
librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel')

# 3. MFCC
mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

# 4. Caracteristiques
rms = librosa.feature.rms(y=y)
zcr = librosa.feature.zero_crossing_rate(y)
spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)

# 5. Pitch avec pyin
f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=80, fmax=400)
        """, language='python')
