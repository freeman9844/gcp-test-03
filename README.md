# Google Gemini Live API 테스트 샘플

`google-genai` (Unified SDK)를 사용한 Gemini Live API 실시간 시스템 인스트럭션 업데이트 테스트 코드입니다.

## ✅ 검증 완료

이 프로젝트는 Vertex AI 환경에서 **`gemini-live-2.5-flash-native-audio`** 모델을 사용하여 **실시간 시스템 인스트럭션 업데이트** 기능을 성공적으로 검증했습니다.

### 주요 성과
- ✅ 실시간 페르소나 전환 (일반 어시스턴트 → 해적 캐릭터)
- ✅ 실시간 로케일 전환 (영어 → 한국어)
- ✅ `google-genai` v1.56.0 SDK의 올바른 사용법 확인

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

## 📋 주요 기능

### 실시간 시스템 인스트럭션 업데이트

세션 도중에 시스템 인스트럭션을 동적으로 변경할 수 있습니다:

```python
# 인스트럭션 업데이트
await session.send_client_content(
    turns=[
        types.Content(
            role="system",
            parts=[types.Part(text="새로운 인스트럭션")]
        )
    ],
    turn_complete=False
)
```

## 🧪 테스트 시나리오

1. **기본 대화**: Live API 세션 연결 및 메시지 송수신
2. **페르소나 변경**: 일반 어시스턴트 → 해적 캐릭터로 실시간 전환
3. **로케일 변경**: 영어 어시스턴트 → 한국어 비서로 실시간 전환

모든 시나리오가 성공적으로 검증되었습니다.

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

최신 Live API에서는 `role="system"`을 가진 메시지를 전송하여 인스트럭션을 업데이트합니다:

```python
# ✅ 실시간 업데이트
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

## 📄 라이선스

이 프로젝트는 교육 및 테스트 목적으로 자유롭게 사용할 수 있습니다.
