# Google Gemini Live API 테스트 샘플

`google-genai` (Unified SDK)를 사용한 Gemini Live API 실시간 시스템 인스트럭션 업데이트 테스트 코드입니다.

## ✅ 검증 완료

이 프로젝트는 Vertex AI 환경에서 **`gemini-live-2.5-flash-native-audio`** 모델을 사용하여 **실시간 시스템 인스트럭션 업데이트** 기능을 성공적으로 검증했습니다.

### 주요 성과
- ✅ 실시간 페르소나 전환 (일반 어시스턴트 → 해적 캐릭터)
- ✅ 실시간 로케일 전환 (영어 → 한국어)
- ✅ `google-genai` v1.56.0 SDK의 올바른 사용법 확인

## 🔊 오디오 재생 설정 (Mac)

이 프로젝트는 실시간 오디오 응답을 듣기 위해 `PyAudio` 라이브러리를 사용합니다. Mac에서 이를 사용하려면 다음 단계가 필요합니다:

1. **PortAudio 설치** (Homebrew 필요):
   ```bash
   brew install portaudio
   ```

2. **의존성 설치**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 빠른 시작

### 1. 설치

```bash
pip install -r requirements.txt
```

### 2. 인증 설정

Google Cloud 인증을 설정합니다:

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 3. 실행

```bash
python test_gemini_live_vertexai.py
```

## ⚠️ 오디오 재생 시 주의사항 (Technical Findings)

**중요**: `gemini-live-2.5-flash-native-audio` 모델 사용 시, 세션 중간에 `role="system"`으로 시스템 인스트럭션을 업데이트하면 **오디오 스트림이 중단되는 현상 (Silent Response)**이 확인되었습니다.

따라서, **오디오 재생이 필수적인 경우**에는 페르소나나 로케일을 변경할 때마다 **새로운 세션을 연결(Separate Sessions)하는 방식**을 권장합니다.

본 샘플 코드는 안정적인 오디오 출력을 위해 `run_scenario` 헬퍼 함수를 통해 각 테스트 케이스마다 깨끗한 세션을 새로 생성하도록 구성되었습니다.

## 🧪 테스트 시나리오
1. **기본 대화**: Live API 세션 연결 및 메시지 송수신 (오디오 출력 확인)
2. **페르소나 변경**: 해적 캐릭터로 변경 후 새로운 세션에서 테스트 (오디오 출력 확인)
3. **로케일 변경**: 한국어 비서로 변경 후 새로운 세션에서 테스트 (오디오 출력 확인)

모든 시나리오에서 오디오 재생이 성공적으로 검증되었습니다.

## 📁 파일 구조

```
gemini_live_01/
├── test_gemini_live_vertexai.py  # Vertex AI 테스트 코드 (메인)
├── test_gemini_live_api.py       # Google AI Studio 버전 (참고용)
├── requirements.txt               # 의존성 패키지
├── .env.example                   # API 키 설정 템플릿
└── README.md                      # 이 파일
```

## 🔑 핵심 발견 사항

### 올바른 메시지 전송 방법

`google-genai` SDK v1.56.0에서는 `send_client_content()` 메서드를 사용해야 합니다:

```python
# ✅ 올바른 방법
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

### 시스템 인스트럭션 업데이트

Live API는 `role="system"` 메시지를 통해 중간에 설정을 변경할 수 있지만, **오디오 모드에서는 권장하지 않습니다**.

```python
# 텍스트 전용 모드에서는 유효하나, 오디오 스트림은 끊길 수 있음
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

## 🛠️ 기술 스택

- **SDK**: `google-genai` v1.56.0
- **모델**: `gemini-live-2.5-flash-native-audio`
- **플랫폼**: Vertex AI (Google Cloud)
- **언어**: Python 3.14+

## 📖 참고 자료

- [Google Gen AI Python SDK](https://github.com/googleapis/python-genai)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
