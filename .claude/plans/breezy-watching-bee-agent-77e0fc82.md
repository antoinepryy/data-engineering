# Module 1 (Vocal) Code Consolidation and Quality Plan

## Executive Summary

This plan consolidates 7 Python application versions, a Node.js server, and 3 Dockerfiles into a clean, maintainable structure. The goal is to reduce complexity while improving code quality and establishing a foundation for future "Agent Vocal" capabilities.

---

## 1. Current State Analysis

### 1.1 Existing Files Inventory

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `app.py` | 942 | Full demo with TTS, STT, S2S, Audio Analysis, Exercises | Uses `asyncio.run()` directly (problematic) |
| `app_complete.py` | 1250 | Most complete version with all features | Better structure, uses `@st.cache_resource` |
| `app_fixed.py` | 460 | TTS-only version, Docker-optimized | Clean, but limited functionality |
| `app_patch.py` | 86 | pyttsx3 test utility | Can be deleted (superseded) |
| `app_s2s_test.py` | 247 | Speech-to-Speech translation test | Good S2S implementation |
| `app_stt_test.py` | 217 | Speech-to-Text test | Good STT test patterns |
| `simple_test.py` | 44 | Minimal TTS test | Can be deleted |
| `server.js` | 272 | Node.js REST + WebSocket server | **Mock implementations only** |

### 1.2 Key Issues Identified

#### A. Async/Await Problems
- **Problem**: `asyncio.run()` called multiple times in Streamlit context
- **Location**: `app.py` lines 159, 553; `app_complete.py` lines 268, 938-939
- **Impact**: Can cause `RuntimeError: asyncio.run() cannot be called from a running event loop`

#### B. Temp File Cleanup Inconsistencies
```
app.py:         os.unlink() called inconsistently
app_complete.py: Better cleanup, but still gaps in error paths
app_s2s_test.py: Good cleanup with try/finally pattern
```

#### C. Duplicated Code Patterns
- TTS generation function duplicated 5+ times across files
- STT transcription logic copied with slight variations
- Audio analysis code repeated in multiple files

#### D. No Tests
- Zero unit tests
- No integration tests
- No test fixtures for audio files

#### E. Node.js Server Issues
- STT endpoint returns mock data (lines 93-126)
- Audio analysis returns hardcoded values (lines 143-182)
- Not connected to actual backends

---

## 2. Proposed Architecture

### 2.1 Target File Structure

```
formation-data-engineering/module-1-vocal/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Main Streamlit entry point
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── 01_text_to_speech.py   # TTS demo page
│   │   ├── 02_speech_to_text.py   # STT demo page
│   │   ├── 03_translation.py      # S2S translation page
│   │   ├── 04_audio_analysis.py   # Audio analysis page
│   │   └── 05_exercises.py        # Interactive exercises
│   └── components/
│       ├── __init__.py
│       ├── audio_player.py        # Reusable audio player component
│       └── file_uploader.py       # Enhanced file upload component
├── core/
│   ├── __init__.py
│   ├── tts/
│   │   ├── __init__.py
│   │   ├── base.py                # TTSEngine abstract base class
│   │   ├── gtts_engine.py         # gTTS implementation
│   │   ├── edge_tts_engine.py     # Edge-TTS implementation
│   │   └── factory.py             # Engine factory
│   ├── stt/
│   │   ├── __init__.py
│   │   ├── base.py                # STTEngine abstract base class
│   │   ├── whisper_engine.py      # Whisper implementation
│   │   ├── google_sr_engine.py    # Google Speech Recognition
│   │   └── factory.py             # Engine factory
│   ├── translation/
│   │   ├── __init__.py
│   │   ├── translator.py          # Translation wrapper
│   │   └── pipeline.py            # S2S pipeline orchestrator
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── analyzer.py            # Audio analysis (librosa wrapper)
│   │   ├── converter.py           # Format conversion utilities
│   │   └── temp_manager.py        # Temp file lifecycle management
│   └── session.py                 # Streamlit session state manager
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── fixtures/
│   │   └── sample_audio.mp3       # Test audio file
│   ├── unit/
│   │   ├── test_tts_engines.py
│   │   ├── test_stt_engines.py
│   │   ├── test_translation.py
│   │   └── test_audio_analyzer.py
│   └── integration/
│       └── test_s2s_pipeline.py
├── config/
│   ├── __init__.py
│   ├── settings.py                # Configuration constants
│   └── voices.py                  # Voice mappings by language
├── Dockerfile                     # Single optimized Dockerfile
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project metadata + pytest config
└── README.md                      # Documentation
```

### 2.2 Core Module Design

#### A. TTS Engine Abstraction

```python
# core/tts/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class TTSResult:
    audio_path: Path
    duration_seconds: float
    engine_name: str
    
class TTSEngine(ABC):
    """Abstract base class for TTS engines."""
    
    @abstractmethod
    async def synthesize(
        self, 
        text: str, 
        voice: Optional[str] = None,
        rate: float = 1.0
    ) -> TTSResult:
        """Generate audio from text."""
        pass
    
    @abstractmethod
    def get_available_voices(self, language: str = "fr") -> list[str]:
        """Return available voices for a language."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Engine identifier."""
        pass
```

#### B. Async Wrapper for Streamlit

```python
# core/async_utils.py
import asyncio
from typing import Coroutine, TypeVar

T = TypeVar('T')

def run_async(coro: Coroutine[None, None, T]) -> T:
    """
    Safely run async code in Streamlit context.
    Handles existing event loops gracefully.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, safe to use asyncio.run()
        return asyncio.run(coro)
    else:
        # Loop already running, use nest_asyncio or create task
        import nest_asyncio
        nest_asyncio.apply()
        return loop.run_until_complete(coro)
```

#### C. Temp File Manager

```python
# core/audio/temp_manager.py
import tempfile
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Generator
import atexit

class TempAudioManager:
    """Manages temporary audio file lifecycle."""
    
    _active_files: set[Path] = set()
    
    @classmethod
    @contextmanager
    def create_temp_audio(
        cls, 
        suffix: str = ".mp3"
    ) -> Generator[Path, None, None]:
        """Create temp file with guaranteed cleanup."""
        tmp = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=suffix
        )
        path = Path(tmp.name)
        cls._active_files.add(path)
        tmp.close()
        
        try:
            yield path
        finally:
            cls._cleanup_file(path)
    
    @classmethod
    def _cleanup_file(cls, path: Path) -> None:
        """Remove file and deregister."""
        try:
            if path.exists():
                os.unlink(path)
            cls._active_files.discard(path)
        except OSError:
            pass
    
    @classmethod
    def cleanup_all(cls) -> None:
        """Cleanup all registered temp files."""
        for path in list(cls._active_files):
            cls._cleanup_file(path)

# Register cleanup on exit
atexit.register(TempAudioManager.cleanup_all)
```

---

## 3. Implementation Plan

### Phase 1: Foundation (Days 1-2)

#### Day 1: Core Module Setup

| Task | Files to Create | Effort |
|------|-----------------|--------|
| Create directory structure | All folders | 30 min |
| Implement `core/audio/temp_manager.py` | 1 file | 1 hour |
| Implement `core/async_utils.py` | 1 file | 30 min |
| Create `config/settings.py` | 1 file | 30 min |
| Create `config/voices.py` | 1 file | 30 min |

#### Day 2: TTS Engine Extraction

| Task | Source | Target |
|------|--------|--------|
| Extract TTS base class | - | `core/tts/base.py` |
| Implement gTTS engine | `app_fixed.py:76-84` | `core/tts/gtts_engine.py` |
| Implement Edge-TTS engine | `app_fixed.py:86-94` | `core/tts/edge_tts_engine.py` |
| Create factory | - | `core/tts/factory.py` |
| Write unit tests | - | `tests/unit/test_tts_engines.py` |

### Phase 2: STT & Translation (Days 3-4)

#### Day 3: STT Engine Extraction

| Task | Source | Target |
|------|--------|--------|
| Extract STT base class | - | `core/stt/base.py` |
| Implement Whisper engine | `app_complete.py:137-148` | `core/stt/whisper_engine.py` |
| Implement Google SR engine | `app_complete.py:150-167` | `core/stt/google_sr_engine.py` |
| Create factory | - | `core/stt/factory.py` |
| Write unit tests | - | `tests/unit/test_stt_engines.py` |

#### Day 4: Translation Pipeline

| Task | Source | Target |
|------|--------|--------|
| Create translator wrapper | `app_s2s_test.py:111-117` | `core/translation/translator.py` |
| Implement S2S pipeline | `app_s2s_test.py:84-145` | `core/translation/pipeline.py` |
| Write integration tests | - | `tests/integration/test_s2s_pipeline.py` |

### Phase 3: Application Layer (Days 5-6)

#### Day 5: Main App + TTS/STT Pages

| Task | Source | Target |
|------|--------|--------|
| Create main entry point | `app_complete.py:26-111` | `app/main.py` |
| Create TTS page | `app_fixed.py:108-278` | `app/pages/01_text_to_speech.py` |
| Create STT page | `app_complete.py:314-456` | `app/pages/02_speech_to_text.py` |
| Create session manager | - | `core/session.py` |

#### Day 6: Remaining Pages

| Task | Source | Target |
|------|--------|--------|
| Create translation page | `app_s2s_test.py` (full) | `app/pages/03_translation.py` |
| Create audio analysis page | `app_complete.py:668-821` | `app/pages/04_audio_analysis.py` |
| Create exercises page | `app_complete.py:827-1241` | `app/pages/05_exercises.py` |

### Phase 4: Cleanup & Documentation (Day 7)

| Task | Effort |
|------|--------|
| Delete deprecated files | 30 min |
| Update Dockerfile | 1 hour |
| Write README.md | 1 hour |
| Create pyproject.toml | 30 min |
| Final testing | 2 hours |

---

## 4. Files to Delete After Migration

| File | Reason |
|------|--------|
| `app.py` | Replaced by modular structure |
| `app_complete.py` | Replaced by modular structure |
| `app_fixed.py` | Functionality moved to core/tts |
| `app_patch.py` | Test utility, no longer needed |
| `app_s2s_test.py` | Replaced by translation page |
| `app_stt_test.py` | Replaced by STT page |
| `simple_test.py` | Minimal test, replaced by pytest |
| `Dockerfile.python.lite` | Single Dockerfile preferred |
| `Dockerfile.node` | Node.js server being deprecated |
| `server.js` | Mock implementation, not production-ready |
| `public/index.html` | Related to Node.js server |
| `package.json` | Related to Node.js server |

---

## 5. Key Code Changes

### 5.1 Fixing Async Issues

**Current Problem** (in `app_complete.py:268`):
```python
audio_file, error = asyncio.run(
    generate_audio_with_edge_tts(text_input, voice[1], rate)
)
```

**Solution**:
```python
from core.async_utils import run_async
from core.tts.factory import create_tts_engine

engine = create_tts_engine("edge-tts")
result = run_async(engine.synthesize(text_input, voice=voice[1], rate=rate))
```

### 5.2 Improving Error Handling

**Current** (scattered try/except):
```python
try:
    # ... lots of code
except Exception as e:
    st.error(f"Erreur: {str(e)}")
```

**Solution** (typed exceptions + context managers):
```python
# core/exceptions.py
class VocalModuleError(Exception):
    """Base exception for vocal module."""
    pass

class TTSError(VocalModuleError):
    """TTS generation failed."""
    pass

class STTError(VocalModuleError):
    """STT transcription failed."""
    pass

# Usage in pages:
from core.exceptions import TTSError
from core.audio.temp_manager import TempAudioManager

try:
    with TempAudioManager.create_temp_audio() as audio_path:
        result = run_async(engine.synthesize(text, voice=voice))
        # ... use audio_path
except TTSError as e:
    st.error(f"Erreur de synthese vocale: {e}")
    logger.exception("TTS failed")
```

### 5.3 Session State Management

**Current** (ad-hoc):
```python
st.session_state['example_audio'] = audio_bytes
if 'stt_example' in st.session_state:
    ...
```

**Solution** (typed session manager):
```python
# core/session.py
from dataclasses import dataclass, field
from typing import Optional
import streamlit as st

@dataclass
class VocalSession:
    """Type-safe session state wrapper."""
    example_audio: Optional[bytes] = None
    transcription_result: Optional[str] = None
    translation_results: dict = field(default_factory=dict)
    
    @classmethod
    def get(cls) -> "VocalSession":
        if "vocal_session" not in st.session_state:
            st.session_state.vocal_session = cls()
        return st.session_state.vocal_session
    
    def clear(self) -> None:
        self.example_audio = None
        self.transcription_result = None
        self.translation_results.clear()

# Usage:
session = VocalSession.get()
session.example_audio = audio_bytes
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

```python
# tests/unit/test_tts_engines.py
import pytest
from core.tts.gtts_engine import GTTSEngine
from core.tts.edge_tts_engine import EdgeTTSEngine

@pytest.fixture
def gtts_engine():
    return GTTSEngine()

@pytest.fixture
def edge_tts_engine():
    return EdgeTTSEngine()

class TestGTTSEngine:
    @pytest.mark.asyncio
    async def test_synthesize_french(self, gtts_engine):
        result = await gtts_engine.synthesize("Bonjour", voice="fr")
        assert result.audio_path.exists()
        assert result.audio_path.stat().st_size > 0
        
    def test_get_available_voices(self, gtts_engine):
        voices = gtts_engine.get_available_voices("fr")
        assert "fr" in voices
```

### 6.2 Integration Tests

```python
# tests/integration/test_s2s_pipeline.py
import pytest
from core.translation.pipeline import SpeechToSpeechPipeline

class TestS2SPipeline:
    @pytest.mark.asyncio
    async def test_french_to_english(self, sample_french_audio):
        pipeline = SpeechToSpeechPipeline()
        result = await pipeline.translate(
            audio_path=sample_french_audio,
            source_lang="fr",
            target_lang="en"
        )
        assert result.translated_text
        assert result.output_audio_path.exists()
```

---

## 7. Dependencies Update

### New requirements.txt

```
# TTS
gtts>=2.5.0
edge-tts>=6.1.0

# STT
SpeechRecognition>=3.10.0
openai-whisper>=20231117

# Audio Processing
pydub>=0.25.1
librosa>=0.10.0
soundfile>=0.12.0
numpy>=1.24.0

# Translation
googletrans==4.0.0-rc1
deep-translator>=1.11.0

# Web Framework
streamlit>=1.29.0

# Async Support
nest-asyncio>=1.5.8

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0

# Utilities
python-dotenv>=1.0.0
```

---

## 8. Agent Vocal Foundation

The new architecture prepares for "Agent Vocal" by:

1. **Modular Engines**: TTS/STT engines can be easily swapped or extended
2. **Pipeline Pattern**: S2S pipeline can be extended for conversational flows
3. **Session Management**: Typed session state supports conversation history
4. **Async-Ready**: All core operations support async for real-time streaming

### Future Extension Points

```python
# core/agent/vocal_agent.py (future)
class VocalAgent:
    """Conversational agent with voice I/O."""
    
    def __init__(
        self,
        stt_engine: STTEngine,
        tts_engine: TTSEngine,
        llm_client: Any  # Future LLM integration
    ):
        self.stt = stt_engine
        self.tts = tts_engine
        self.llm = llm_client
        self.conversation_history: list[Message] = []
    
    async def process_voice_input(self, audio_path: Path) -> VocalResponse:
        """Process voice input and generate voice response."""
        # 1. Transcribe user speech
        user_text = await self.stt.transcribe(audio_path)
        
        # 2. Get LLM response
        response_text = await self.llm.generate(
            user_text, 
            history=self.conversation_history
        )
        
        # 3. Synthesize response
        response_audio = await self.tts.synthesize(response_text)
        
        return VocalResponse(
            transcription=user_text,
            response_text=response_text,
            response_audio=response_audio
        )
```

---

## 9. Critical Files for Implementation

### Most Important Files to Read Before Starting:

1. **`/Users/antoine/IdeaProjects/imagesimages/formation-data-engineering/module-1-vocal/app_complete.py`**
   - Reason: Most comprehensive feature set, best patterns to extract
   - Key sections: TTS generation (210-291), STT (314-456), Audio analysis (668-821)

2. **`/Users/antoine/IdeaProjects/imagesimages/formation-data-engineering/module-1-vocal/app_fixed.py`**
   - Reason: Cleanest TTS implementation, Docker-optimized patterns
   - Key sections: `generate_audio_with_gtts()` (76-84), `generate_audio_with_edge_tts()` (86-94)

3. **`/Users/antoine/IdeaProjects/imagesimages/formation-data-engineering/module-1-vocal/app_s2s_test.py`**
   - Reason: Best S2S pipeline implementation
   - Key sections: Translation pipeline (84-154)

4. **`/Users/antoine/IdeaProjects/imagesimages/formation-data-engineering/module-1-vocal/Dockerfile.python`**
   - Reason: Reference for all required system dependencies
   - Key sections: apt-get installs (6-26), pip installs (29-58)

5. **`/Users/antoine/IdeaProjects/imagesimages/formation-data-engineering/module-1-vocal/config/voices.py`** (to create)
   - Reason: Centralize voice mappings currently scattered across files
   - Reference: `app.py` lines 536-541, `app_complete.py` lines 243-250

---

## 10. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking changes during migration | Keep old files until new structure is validated |
| Async issues in Streamlit | Use `nest_asyncio` + comprehensive testing |
| Missing edge cases | Extract all error handling patterns from existing code |
| Docker compatibility | Test each phase in Docker environment |

---

## Summary

This consolidation reduces **11 files** (7 Python apps + 3 Dockerfiles + Node.js) to a **clean modular structure** with:

- **5 page modules** (Streamlit multipage app)
- **4 core packages** (TTS, STT, Translation, Audio)
- **Comprehensive tests** (unit + integration)
- **Single Dockerfile**
- **Foundation for Agent Vocal**

Estimated effort: **5-7 days** for a single developer.
