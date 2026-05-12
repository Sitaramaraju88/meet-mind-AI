# Meet Mind AI – Voice-Based Intelligent Avatar System

Meet Mind AI is a voice-enabled conversational avatar system that allows users to speak naturally with an AI assistant. The system processes audio or video input, understands user intent, retrieves relevant knowledge using **Retrieval-Augmented Generation (RAG)**, and responds with safe, context-aware spoken output.

The project focuses on **accessibility**, **safety**, and **natural interaction**.

---

## Demo

### Voice-Based Avatar Interaction

* [https://drive.google.com/file/d/1neE9fXwbzf_6kQcACfmxZaK1x2kl7iNF/view?usp=sharing](https://drive.google.com/file/d/1neE9fXwbzf_6kQcACfmxZaK1x2kl7iNF/view?usp=sharing)

### Video Dubbing & Multilingual Accessibility

* [https://drive.google.com/file/d/1sncbTsvVcJpte0t1L-Wn-WhhPvZSEcdW/view?usp=sharing](https://drive.google.com/file/d/1sncbTsvVcJpte0t1L-Wn-WhhPvZSEcdW/view?usp=sharing)

---

## System Flow

```
Audio Input
   ↓
Noise Reduction
   ↓
Voice Activity Detection
   ↓
Speech to Text
   ↓
Language Detection & Validation
   ↓
Intent and Semantic Analysis
   ↓
Safety Guard
   ↓
LLM with RAG
   ↓
Response Text
   ↓
Text to Speech
```

This pipeline ensures clean input, safe processing, and accurate responses.

---

## Key Features

* Voice-based interaction with AI avatars
* Noise reduction for improved audio quality
* Automatic language detection
* Intent and semantic understanding
* Safety checks for unprofessional or harmful content
* Knowledge-grounded responses using RAG
* Response caching for faster repeated queries
* Video-to-audio dubbing for enhanced accessibility

---

## Tech Stack

* **Python**
* **Speech-to-Text**: SpeechRecognition, Whisper
* **Audio Processing**: librosa, noisereduce, soundfile
* **NLP & Intent Detection**: spaCy
* **Language Detection**: langdetect
* **LLM APIs**: Groq (or similar)
* **Vector Database**: for RAG
* **Frontend**: HTML, CSS, JavaScript

---

## Project Modules (High Level)

### Audio Preprocessing

Cleans raw audio by reducing background noise and removing silence to improve speech recognition accuracy.

### Language Detection

Detects the spoken language after transcription to support multilingual users.

### Intent and Semantics

Analyzes user input to understand intent and extract key information.

### Safety Guard

Filters or masks unprofessional or harmful content before sending queries to the language model.

### Retrieval-Augmented Generation (RAG)

Fetches relevant context from a knowledge base and combines it with the language model to generate accurate responses.

### Text-to-Speech

Converts the final response into spoken output for a natural conversational experience.

### Video Dubbing

Extracts audio from video, processes it, and generates dubbed audio to make content usable by a wider audience.

---

## Team Contribution

* RAG pipeline design and frontend integration
* Audio and video dubbing implementation
* Audio preprocessing, safety checks, and NLP processing

---

## Challenges Faced

* Dependency and package installation issues (especially **FFmpeg**)
* Compatibility problems with newer Python versions
* Integrating multiple AI components into a single pipeline

These issues were resolved through environment adjustments and modular development.

---

## Future Enhancements

* Real-time audio streaming
* Expanded multilingual support
* Emotion-aware responses
* Cloud deployment and scalability
* Avatar animation and lip-syncing

---

## Conclusion

SafeTalk AI demonstrates how voice processing, NLP, safety mechanisms, and RAG can be combined to create a reliable and accessible AI avatar system. The project emphasizes **safe interaction**, **knowledge-based responses**, and **ease of use** for diverse users.
