/**
 * Service client pour l'API STT backend.
 */

// URL de l'API backend via ngrok
const API_BASE_URL = 'https://d072fa3c3606.ngrok.app';

export type STTEngine = 'whisper' | 'vosk' | 'google';

export interface TranscriptionResult {
  text: string;
  language: string;
  engine: string;
  model_size?: string;
}

export interface EngineInfo {
  available: boolean;
  languages: string[];
}

export class STTApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public details?: string
  ) {
    super(message);
    this.name = 'STTApiError';
  }
}

/**
 * Transcrit un fichier audio via l'API backend.
 */
export async function transcribe(
  audioUri: string,
  engine: STTEngine = 'whisper',
  language: string = 'fr'
): Promise<TranscriptionResult> {
  console.log('[STT] Transcribing:', { audioUri, engine, language });

  const formData = new FormData();
  formData.append('audio', {
    uri: audioUri,
    type: 'audio/m4a',
    name: 'recording.m4a',
  } as unknown as Blob);
  formData.append('engine', engine);
  formData.append('language', language);

  try {
    const response = await fetch(`${API_BASE_URL}/api/stt/transcribe`, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
      },
    });

    console.log('[STT] Response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new STTApiError(
        errorData.error || `HTTP ${response.status}`,
        response.status,
        JSON.stringify(errorData)
      );
    }

    const result = await response.json();
    console.log('[STT] Transcription result:', result);
    return result;

  } catch (error) {
    console.error('[STT] Transcription error:', error);
    throw error;
  }
}

/**
 * Recupere la liste des moteurs STT disponibles.
 */
export async function getEngines(): Promise<Record<STTEngine, EngineInfo>> {
  console.log('[STT] Fetching engines from:', `${API_BASE_URL}/api/stt/engines`);

  try {
    const response = await fetch(`${API_BASE_URL}/api/stt/engines`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    console.log('[STT] Engines response status:', response.status);

    if (!response.ok) {
      throw new STTApiError(`Failed to fetch engines`, response.status);
    }

    const data = await response.json();
    console.log('[STT] Engines:', data);
    return data;

  } catch (error) {
    console.error('[STT] Get engines error:', error);
    throw error;
  }
}

/**
 * Verifie si l'API backend est accessible.
 */
export async function checkHealth(): Promise<boolean> {
  const url = `${API_BASE_URL}/api/stt/health`;
  console.log('[STT] Health check:', url);

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(url, {
      method: 'GET',
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    console.log('[STT] Health response:', response.status, response.ok);
    return response.ok;

  } catch (error) {
    console.error('[STT] Health check error:', error);
    return false;
  }
}

export function getApiUrl(): string {
  return API_BASE_URL;
}
