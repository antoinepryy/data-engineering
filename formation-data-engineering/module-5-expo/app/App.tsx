/**
 * Application STT Demo - SDK 54
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
  Alert,
} from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';

import { useRecording } from './src/hooks/useRecording';
import {
  transcribe,
  getEngines,
  checkHealth,
  getApiUrl,
  STTEngine,
  TranscriptionResult,
  EngineInfo,
} from './src/services/stt';

function MainApp() {
  const {
    isRecording,
    formattedDuration,
    startRecording,
    stopRecording,
    error: recordingError,
  } = useRecording();

  const [selectedEngine, setSelectedEngine] = useState<STTEngine>('whisper');
  const [language, setLanguage] = useState('fr');
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [transcription, setTranscription] = useState<TranscriptionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [engines, setEngines] = useState<Record<STTEngine, EngineInfo> | null>(null);
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    checkApiStatus();
    loadEngines();
  }, []);

  const checkApiStatus = async () => {
    console.log('[App] Checking API status...');
    setApiStatus('checking');
    const isOnline = await checkHealth();
    console.log('[App] API online:', isOnline);
    setApiStatus(isOnline ? 'online' : 'offline');
  };

  const loadEngines = async () => {
    try {
      const enginesData = await getEngines();
      setEngines(enginesData);
    } catch (e) {
      console.log('[App] Failed to load engines:', e);
    }
  };

  const handleRecordPress = async () => {
    console.log('[App] handleRecordPress called, isRecording:', isRecording);
    setError(null);

    if (isRecording) {
      console.log('[App] Stopping recording...');
      const uri = await stopRecording();
      console.log('[App] Recording stopped, URI:', uri);
      if (uri) {
        console.log('[App] Starting transcription...');
        await handleTranscribe(uri);
      } else {
        console.log('[App] No URI returned, skipping transcription');
        setError('Aucun fichier audio enregistre');
      }
    } else {
      console.log('[App] Starting recording...');
      setTranscription(null);
      await startRecording();
      console.log('[App] Recording started');
    }
  };

  const handleTranscribe = async (audioUri: string) => {
    if (apiStatus !== 'online') {
      setError('API backend non disponible. Verifiez la connexion.');
      return;
    }

    setIsTranscribing(true);
    setError(null);

    try {
      const result = await transcribe(audioUri, selectedEngine, language);
      setTranscription(result);
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Erreur de transcription';
      setError(message);
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleCopy = () => {
    if (transcription?.text) {
      Alert.alert('Info', 'Texte: ' + transcription.text);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />

      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>STT Demo</Text>
        <Text style={styles.subtitle}>Speech-to-Text avec Whisper, Vosk, Google</Text>

        {/* API Status */}
        <View style={styles.statusContainer}>
          <View style={[
            styles.statusDot,
            apiStatus === 'online' && styles.statusOnline,
            apiStatus === 'offline' && styles.statusOffline,
            apiStatus === 'checking' && styles.statusChecking,
          ]} />
          <Text style={styles.statusText}>
            API: {apiStatus === 'online' ? 'Connectee' : apiStatus === 'offline' ? 'Hors ligne' : 'Verification...'}
          </Text>
          <TouchableOpacity onPress={checkApiStatus} style={styles.refreshBtn}>
            <Text style={styles.refreshText}>Rafraichir</Text>
          </TouchableOpacity>
        </View>

        {/* Debug: Show API URL */}
        <Text style={styles.debugText}>URL: {getApiUrl()}</Text>

        {/* Engine Selection */}
        <Text style={styles.sectionTitle}>Moteur STT</Text>
        <View style={styles.engineContainer}>
          {(['whisper', 'vosk', 'google'] as STTEngine[]).map((eng) => {
            const isAvailable = engines?.[eng]?.available ?? true;
            const isSelected = selectedEngine === eng;

            return (
              <TouchableOpacity
                key={eng}
                style={[
                  styles.engineBtn,
                  isSelected && styles.engineSelected,
                  !isAvailable && styles.engineDisabled,
                ]}
                onPress={() => isAvailable && setSelectedEngine(eng)}
                disabled={!isAvailable}
              >
                <Text style={[
                  styles.engineText,
                  isSelected && styles.engineTextSelected,
                  !isAvailable && styles.engineTextDisabled,
                ]}>
                  {eng.charAt(0).toUpperCase() + eng.slice(1)}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Language Selection */}
        <Text style={styles.sectionTitle}>Langue</Text>
        <View style={styles.languageContainer}>
          {['fr', 'en', 'auto'].map((lang) => (
            <TouchableOpacity
              key={lang}
              style={[
                styles.languageBtn,
                language === lang && styles.languageSelected,
              ]}
              onPress={() => setLanguage(lang)}
            >
              <Text style={[
                styles.languageText,
                language === lang && styles.languageTextSelected,
              ]}>
                {lang === 'fr' ? 'Francais' : lang === 'en' ? 'English' : 'Auto'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Record Button */}
        <TouchableOpacity
          style={[
            styles.recordBtn,
            isRecording && styles.recordBtnActive,
            isTranscribing && styles.recordBtnDisabled,
          ]}
          onPress={handleRecordPress}
          disabled={isTranscribing}
        >
          {isTranscribing ? (
            <ActivityIndicator color="#fff" size="large" />
          ) : (
            <>
              <Text style={styles.recordIcon}>
                {isRecording ? '⏹' : '🎤'}
              </Text>
              <Text style={styles.recordText}>
                {isRecording ? `Stop (${formattedDuration})` : 'Enregistrer'}
              </Text>
            </>
          )}
        </TouchableOpacity>

        {/* Errors */}
        {(error || recordingError) && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error || recordingError}</Text>
          </View>
        )}

        {/* Result */}
        {transcription && (
          <View style={styles.resultContainer}>
            <View style={styles.resultHeader}>
              <Text style={styles.resultTitle}>Transcription</Text>
              <TouchableOpacity onPress={handleCopy} style={styles.copyBtn}>
                <Text style={styles.copyText}>Copier</Text>
              </TouchableOpacity>
            </View>

            <Text style={styles.resultText}>{transcription.text}</Text>

            <View style={styles.resultMeta}>
              <Text style={styles.metaText}>
                Moteur: {transcription.engine}
                {transcription.model_size && ` (${transcription.model_size})`}
              </Text>
              <Text style={styles.metaText}>
                Langue: {transcription.language}
              </Text>
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <MainApp />
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 10,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
    marginBottom: 15,
  },
  debugText: {
    fontSize: 10,
    color: '#999',
    marginBottom: 10,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
    padding: 10,
    backgroundColor: '#fff',
    borderRadius: 8,
    width: '100%',
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  statusOnline: {
    backgroundColor: '#4CAF50',
  },
  statusOffline: {
    backgroundColor: '#f44336',
  },
  statusChecking: {
    backgroundColor: '#FFC107',
  },
  statusText: {
    flex: 1,
    fontSize: 14,
    color: '#333',
  },
  refreshBtn: {
    padding: 5,
  },
  refreshText: {
    color: '#007AFF',
    fontSize: 14,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    alignSelf: 'flex-start',
    marginBottom: 8,
    marginTop: 8,
  },
  engineContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 8,
    width: '100%',
  },
  engineBtn: {
    flex: 1,
    padding: 12,
    marginHorizontal: 4,
    borderRadius: 8,
    backgroundColor: '#fff',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#ddd',
  },
  engineSelected: {
    borderColor: '#007AFF',
    backgroundColor: '#e6f2ff',
  },
  engineDisabled: {
    opacity: 0.5,
  },
  engineText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  engineTextSelected: {
    color: '#007AFF',
  },
  engineTextDisabled: {
    color: '#999',
  },
  languageContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 20,
    width: '100%',
  },
  languageBtn: {
    flex: 1,
    padding: 10,
    marginHorizontal: 4,
    borderRadius: 8,
    backgroundColor: '#fff',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#ddd',
  },
  languageSelected: {
    borderColor: '#007AFF',
    backgroundColor: '#e6f2ff',
  },
  languageText: {
    fontSize: 14,
    color: '#333',
  },
  languageTextSelected: {
    color: '#007AFF',
    fontWeight: '600',
  },
  recordBtn: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 8,
  },
  recordBtnActive: {
    backgroundColor: '#ff3b30',
  },
  recordBtnDisabled: {
    backgroundColor: '#ccc',
  },
  recordIcon: {
    fontSize: 36,
  },
  recordText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginTop: 6,
  },
  errorContainer: {
    backgroundColor: '#ffebee',
    padding: 15,
    borderRadius: 8,
    width: '100%',
    marginBottom: 15,
  },
  errorText: {
    color: '#c62828',
    fontSize: 14,
    textAlign: 'center',
  },
  resultContainer: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    width: '100%',
    marginTop: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  copyBtn: {
    padding: 8,
    backgroundColor: '#e6f2ff',
    borderRadius: 6,
  },
  copyText: {
    color: '#007AFF',
    fontSize: 14,
    fontWeight: '500',
  },
  resultText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
    marginBottom: 15,
  },
  resultMeta: {
    borderTopWidth: 1,
    borderTopColor: '#eee',
    paddingTop: 10,
  },
  metaText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
});
