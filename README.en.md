# Google Gemini Live API Test Sample

This repository contains test code for verifying real-time system instruction updates using the `google-genai` (Unified SDK) with the Gemini Live API.

## ✅ Verified Features

This project has successfully verified the **real-time system instruction update** capability using the **`gemini-live-2.5-flash-native-audio`** model in a Vertex AI environment.

### Key Achievements
- ✅ Real-time Persona Switching (Helpful Assistant → Pirate Character)
- ✅ Real-time Locale Switching (English → Korean)
- ✅ Verified correct usage of the `google-genai` v1.56.0 SDK

## 🔊 Audio Playback Setup (Mac)

This project uses the `PyAudio` library to play real-time audio responses. To use this on a Mac, you must check the following:

1. **Install PortAudio** (Requires Homebrew):
   ```bash
   brew install portaudio
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Authentication Setup

Configure Google Cloud authentication:

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 3. Execution

```bash
python test_gemini_live_vertexai.py
```

## ⚠️ Important Note on Audio Playback (Technical Findings)

**CRITICAL**: When using the `gemini-live-2.5-flash-native-audio` model, it has been confirmed that updating system instructions mid-session using `role="system"` results in the **interruption of the audio stream (Silent Response)**.

Therefore, if **audio playback is essential**, we highly recommend the **Separate Sessions approach**—establishing a new session whenever you need to change the persona or locale.

This sample code is configured to use a `run_scenario` helper function to create a clean, fresh session for each test case to ensure stable audio output.

## 🧪 Test Scenarios
1. **Basic Conversation**: Connect to Live API & send/receive messages (Audio Output Verified)
2. **Persona Change**: Switch to Pirate character -> Test in a new session (Audio Output Verified)
3. **Locale Change**: Switch to Korean Assistant -> Test in a new session (Audio Output Verified)

Real-time audio playback has been successfully verified for all scenarios using this approach.

## 📁 File Structure

```
gemini_live_01/
├── test_gemini_live_vertexai.py  # Vertex AI Test Code (Main)
├── test_gemini_live_api.py       # Google AI Studio Version (Reference)
├── requirements.txt               # Dependencies
├── .env.example                   # API Key Template
├── README.md                      # Korean Documentation
└── README.en.md                   # English Documentation (This File)
```

## 🔑 Key Findings

### Correct Message Sending Method

In `google-genai` SDK v1.56.0, you must use the `send_client_content()` method:

```python
# ✅ Correct Usage
await session.send_client_content(
    turns=[
        types.Content(
            role="user",
            parts=[types.Part(text="Hello!")]
        )
    ],
    turn_complete=True
)
```

### System Instruction Updates

While the Live API allows changing settings mid-session via `role="system"` messages, **this is NOT recommended for audio modes**.

```python
# Valid for text-only modes, but audio stream may be cut off
await session.send_client_content(
    turns=[
        types.Content(
            role="system",
            parts=[types.Part(text="You are now a pirate.")]
        )
    ],
    turn_complete=False
)
```

## 🛠️ Technology Stack

- **SDK**: `google-genai` v1.56.0
- **Model**: `gemini-live-2.5-flash-native-audio`
- **Platform**: Vertex AI (Google Cloud)
- **Language**: Python 3.14+

## 📖 References

- [Google Gen AI Python SDK](https://github.com/googleapis/python-genai)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
