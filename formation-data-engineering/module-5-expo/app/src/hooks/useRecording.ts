/**
 * Hook pour l'enregistrement audio avec expo-audio (SDK 54+)
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import {
  useAudioRecorder,
  useAudioRecorderState,
  AudioModule,
  RecordingPresets,
  setAudioModeAsync,
} from 'expo-audio';

interface RecordingState {
  isRecording: boolean;
  uri: string | null;
  duration: number;
  error: string | null;
}

export function useRecording() {
  const [state, setState] = useState<RecordingState>({
    isRecording: false,
    uri: null,
    duration: 0,
    error: null,
  });

  const audioRecorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const recorderState = useAudioRecorderState(audioRecorder);

  // Initialiser le mode audio au montage
  useEffect(() => {
    const initAudio = async () => {
      try {
        console.log('[useRecording] Initializing audio mode...');
        await setAudioModeAsync({
          playsInSilentMode: true,
          allowsRecording: true,
        });
        console.log('[useRecording] Audio mode initialized');
      } catch (error) {
        console.error('[useRecording] Failed to init audio mode:', error);
      }
    };
    initAudio();
  }, []);

  // Mettre a jour la duree depuis recorderState
  useEffect(() => {
    if (recorderState.isRecording) {
      setState(s => ({
        ...s,
        duration: recorderState.durationMillis || 0,
        isRecording: true,
      }));
    }
  }, [recorderState.isRecording, recorderState.durationMillis]);

  const startRecording = useCallback(async () => {
    try {
      console.log('[useRecording] Starting recording...');
      setState(s => ({ ...s, error: null, uri: null, duration: 0 }));

      // Demander les permissions
      console.log('[useRecording] Requesting permissions...');
      const status = await AudioModule.requestRecordingPermissionsAsync();
      console.log('[useRecording] Permission status:', status);

      if (!status.granted) {
        setState(s => ({ ...s, error: 'Permission microphone refusee' }));
        return;
      }

      // Preparer l'enregistrement (IMPORTANT!)
      console.log('[useRecording] Preparing to record...');
      await audioRecorder.prepareToRecordAsync();
      console.log('[useRecording] Prepared, now recording...');

      // Demarrer l'enregistrement
      audioRecorder.record();
      console.log('[useRecording] Recording started');

      setState(s => ({ ...s, isRecording: true }));

    } catch (error) {
      const message = error instanceof Error ? error.message : 'Erreur enregistrement';
      console.error('[useRecording] Recording error:', error);
      setState(s => ({ ...s, error: message }));
    }
  }, [audioRecorder]);

  const stopRecording = useCallback(async (): Promise<string | null> => {
    try {
      console.log('[useRecording] Stopping recording...');

      await audioRecorder.stop();
      console.log('[useRecording] Recording stopped');

      // L'URI devrait etre disponible apres stop()
      const uri = audioRecorder.uri;
      console.log('[useRecording] URI from recorder:', uri);

      if (!uri) {
        console.error('[useRecording] No URI returned from recorder!');
        setState(s => ({
          ...s,
          isRecording: false,
          error: 'Aucun fichier audio enregistre',
        }));
        return null;
      }

      setState(s => ({
        ...s,
        isRecording: false,
        uri,
      }));

      console.log('[useRecording] Returning URI:', uri);
      return uri;

    } catch (error) {
      const message = error instanceof Error ? error.message : 'Erreur arret';
      console.error('[useRecording] Stop recording error:', error);
      setState(s => ({
        ...s,
        isRecording: false,
        error: message,
      }));
      return null;
    }
  }, [audioRecorder]);

  const cancelRecording = useCallback(async () => {
    console.log('[useRecording] Cancelling recording...');

    try {
      await audioRecorder.stop();
    } catch {
      // Ignorer
    }

    setState({
      isRecording: false,
      uri: null,
      duration: 0,
      error: null,
    });
  }, [audioRecorder]);

  const formatDuration = useCallback((ms: number): string => {
    const seconds = Math.floor(ms / 1000);
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }, []);

  return {
    isRecording: state.isRecording || recorderState.isRecording,
    uri: state.uri,
    duration: state.duration,
    formattedDuration: formatDuration(state.duration),
    error: state.error,
    startRecording,
    stopRecording,
    cancelRecording,
  };
}
