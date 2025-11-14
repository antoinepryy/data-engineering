/**
 * Serveur Node.js pour les démonstrations de traitement vocal
 * Module 1 - Formation Data Engineering
 */

const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { Server } = require('socket.io');
const http = require('http');
const say = require('say');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Configuration multer pour upload de fichiers
const upload = multer({
  dest: 'uploads/',
  limits: { fileSize: 10 * 1024 * 1024 } // 10MB max
});

// ============================================================================
// API ROUTES
// ============================================================================

/**
 * Route principale - Interface web
 */
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

/**
 * Text-to-Speech endpoint
 */
app.post('/api/tts', async (req, res) => {
  try {
    const { text, voice, speed, language } = req.body;
    
    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }
    
    // Générer un nom de fichier unique
    const fileName = `tts_${Date.now()}.wav`;
    const filePath = path.join(__dirname, 'outputs', fileName);
    
    // Créer le dossier outputs s'il n'existe pas
    if (!fs.existsSync('outputs')) {
      fs.mkdirSync('outputs');
    }
    
    // Utiliser say.js pour générer l'audio
    say.export(text, voice || null, speed || 1.0, filePath, (err) => {
      if (err) {
        console.error('TTS Error:', err);
        return res.status(500).json({ error: 'TTS generation failed' });
      }
      
      // Envoyer le fichier audio
      res.sendFile(filePath, (err) => {
        // Nettoyer le fichier après envoi
        setTimeout(() => {
          fs.unlink(filePath, (err) => {
            if (err) console.error('Cleanup error:', err);
          });
        }, 5000);
      });
    });
    
  } catch (error) {
    console.error('TTS Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * Speech-to-Text endpoint (simulation)
 */
app.post('/api/stt', upload.single('audio'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'Audio file is required' });
    }
    
    // Simulation de transcription
    // En production, utiliser Google Cloud Speech ou Azure
    const mockTranscription = {
      text: "Ceci est une transcription simulée de votre audio.",
      confidence: 0.95,
      language: "fr-FR",
      duration: 3.5,
      words: [
        { word: "Ceci", start: 0.0, end: 0.5 },
        { word: "est", start: 0.5, end: 0.8 },
        { word: "une", start: 0.8, end: 1.0 },
        { word: "transcription", start: 1.0, end: 1.8 },
        { word: "simulée", start: 1.8, end: 2.4 }
      ]
    };
    
    // Nettoyer le fichier uploadé
    fs.unlink(req.file.path, (err) => {
      if (err) console.error('Cleanup error:', err);
    });
    
    res.json(mockTranscription);
    
  } catch (error) {
    console.error('STT Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * Liste des voix disponibles
 */
app.get('/api/voices', (req, res) => {
  say.getInstalledVoices((err, voices) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to get voices' });
    }
    res.json({ voices });
  });
});

/**
 * Analyse audio endpoint
 */
app.post('/api/analyze', upload.single('audio'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'Audio file is required' });
    }
    
    // Simulation d'analyse audio
    const analysis = {
      duration: 5.2,
      sampleRate: 44100,
      channels: 2,
      bitDepth: 16,
      format: 'wav',
      features: {
        averagePitch: 220.5,
        averageAmplitude: 0.65,
        silenceRatio: 0.15,
        speakingRate: 150, // words per minute
        emotion: {
          neutral: 0.4,
          happy: 0.3,
          sad: 0.1,
          angry: 0.1,
          surprised: 0.1
        }
      }
    };
    
    // Nettoyer le fichier
    fs.unlink(req.file.path, (err) => {
      if (err) console.error('Cleanup error:', err);
    });
    
    res.json(analysis);
    
  } catch (error) {
    console.error('Analysis Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ============================================================================
// WEBSOCKET pour streaming audio
// ============================================================================

io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  // Streaming TTS
  socket.on('tts-stream', async (data) => {
    const { text, voice, language } = data;
    
    try {
      // Diviser le texte en phrases
      const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
      
      for (let i = 0; i < sentences.length; i++) {
        const sentence = sentences[i].trim();
        
        // Émettre la progression
        socket.emit('tts-progress', {
          current: i + 1,
          total: sentences.length,
          text: sentence
        });
        
        // Générer l'audio pour cette phrase
        const fileName = `stream_${Date.now()}_${i}.wav`;
        const filePath = path.join(__dirname, 'outputs', fileName);
        
        await new Promise((resolve, reject) => {
          say.export(sentence, voice, 1.0, filePath, (err) => {
            if (err) reject(err);
            else resolve();
          });
        });
        
        // Lire le fichier et l'envoyer
        const audioData = fs.readFileSync(filePath);
        socket.emit('tts-chunk', {
          audio: audioData.toString('base64'),
          index: i,
          isLast: i === sentences.length - 1
        });
        
        // Nettoyer
        fs.unlink(filePath, () => {});
      }
      
    } catch (error) {
      console.error('Streaming error:', error);
      socket.emit('tts-error', { error: error.message });
    }
  });
  
  // STT streaming simulation
  socket.on('stt-stream', (audioChunk) => {
    // Simulation de transcription en temps réel
    const words = ['Bonjour', 'comment', 'allez', 'vous', '?'];
    const randomWord = words[Math.floor(Math.random() * words.length)];
    
    socket.emit('stt-result', {
      text: randomWord,
      isFinal: Math.random() > 0.5,
      confidence: Math.random() * 0.3 + 0.7
    });
  });
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// ============================================================================
// Démarrage du serveur
// ============================================================================

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════╗
║   Module 1: Traitement Vocal (Node.js)  ║
╠════════════════════════════════════════╣
║   Serveur démarré sur le port ${PORT}      ║
║   Interface web: http://localhost:${PORT}  ║
║   API REST: http://localhost:${PORT}/api  ║
║   WebSocket: ws://localhost:${PORT}       ║
╚════════════════════════════════════════╝
  `);
});