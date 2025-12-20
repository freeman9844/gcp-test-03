"""
Google Gemini Live API 테스트 샘플 코드 (Vertex AI 버전)
google-genai SDK를 사용하여 Vertex AI로 실시간 오디오 및 텍스트 대화를 테스트합니다.
"""

import asyncio
import os
from google import genai
from google.genai import types

try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False


class GeminiLiveAPITestVertexAI:
    """Gemini Live API 테스트 클래스 (Vertex AI)"""
    
    def __init__(self, project_id: str, location: str = "us-central1", model_name: str = "gemini-live-2.5-flash-native-audio"):
        """
        Args:
            project_id: Google Cloud 프로젝트 ID
            location: 리전 (기본값: us-central1)
            model_name: 사용할 모델 이름 (기본값: gemini-live-2.5-flash-native-audio)
        """
        print(f"🔧 Initializing client for Vertex AI...")
        print(f"   Project: {project_id}")
        print(f"   Location: {location}")
        
        self.client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )
        self.model_name = model_name
        self.session = None
        
        # 오디오 관련 초기화
        self.audio = None
        self.audio_stream = None
        self.audio_available = HAS_PYAUDIO
        
        if self.audio_available:
            try:
                self.audio = pyaudio.PyAudio()
                print("✅ Audio system initialized.")
            except Exception as e:
                print(f"⚠️  Failed to initialize PyAudio: {e}")
                self.audio_available = False
        else:
            print("⚠️  PyAudio not found. Audio playback will be disabled.")
    
    def _setup_audio_stream(self):
        """오디오 스트림을 설정합니다 (24kHz, 16-bit PCM, Mono)."""
        if not self.audio_available or not self.audio:
            return
            
        try:
            print("🔈 Opening audio output stream (24kHz, 16-bit PCM, Mono)...")
            self.audio_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                output=True
            )
        except Exception as e:
            print(f"❌ Failed to open audio stream: {e}")
            self.audio_available = False
    
    async def connect(self, initial_instruction: str = "You are a helpful assistant."):
        """
        Live API 세션 연결을 반환합니다.
        """
        print(f"\n📡 Connecting to Live API (Model: {self.model_name})")
        
        config = types.LiveConnectConfig(
            system_instruction=types.Content(
                parts=[types.Part(text=initial_instruction)]
            )
        )
        
        return self.client.aio.live.connect(
            model=self.model_name,
            config=config
        )
    
    async def handle_session_events(self):
        """세션으로부터 응답을 수신하고 처리합니다."""
        if not self.session:
            return
            
        print("\n👂 Listening for responses (Audio & Text)...")
        self._setup_audio_stream()
        
        try:
            async for response in self.session.receive():
                if response.server_content:
                    model_turn = response.server_content.model_turn
                    if model_turn:
                        for part in model_turn.parts:
                            # 텍스트 응답 출력
                            if part.text:
                                # 어시스턴트 접두어는 한 번만 출력되도록 처리
                                print(f"{part.text}", end="", flush=True)
                            
                            # 오디오 데이터 재생
                            if part.inline_data and self.audio_available and self.audio_stream:
                                try:
                                    self.audio_stream.write(part.inline_data.data)
                                except Exception as e:
                                    print(f"\n❌ Audio playback error: {e}")
                                    self.audio_available = False
                    
                    if response.server_content.turn_complete:
                        print("\n✅ Turn complete.")

                elif response.tool_call:
                    print(f"\n🔧 Tool call: {response.tool_call}")
                    
        except asyncio.CancelledError:
            print("\n🛑 Listening task cancelled.")
        except Exception as e:
            print(f"\n⚠️  Session ended or error occurred: {e}")
        finally:
            self._close_audio_stream()

    def _close_audio_stream(self):
        """오디오 스트림만 닫습니다."""
        if self.audio_stream:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            except:
                pass
            self.audio_stream = None
            print("\n🔈 Audio stream closed.")

    def close(self):
        """전체 오디오 시스템을 종료합니다."""
        self._close_audio_stream()
        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass
            self.audio = None
    
    async def send_text(self, text: str, end_of_turn: bool = True):
        """텍스트 메시지 전송"""
        if not self.session:
            raise RuntimeError("Session not connected.")
        
        print(f"\n💬 Sending user message: {text}")
        
        await self.session.send_client_content(
            turns=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=text)]
                )
            ],
            turn_complete=end_of_turn
        )


async def run_scenario(tester, title, instruction, message):
    """지정된 시나리오를 새로운 세션에서 실행합니다."""
    print("\n" + "=" * 60)
    print(f"SCENARIO: {title}")
    # print(f"Instruction: {instruction[:50]}...")
    print("=" * 60)
    
    async with await tester.connect(initial_instruction=instruction) as session:
        tester.session = session
        listener = asyncio.create_task(tester.handle_session_events())
        
        await tester.send_text(message)
        
        # 충분한 응답 시간을 위해 대기 (모델의 말하기 속도 고려)
        await asyncio.sleep(12)
        
        listener.cancel()
        await asyncio.gather(listener, return_exceptions=True)


async def main():
    """메인 함수"""
    print("\n🚀 Google Gemini Live API 테스트 시작 (Vertex AI)\n")
    project_id = "jwlee-argolis-202104"
    
    tester = GeminiLiveAPITestVertexAI(project_id=project_id)
    
    try:
        # 시나리오 1: 기본 대화
        await run_scenario(
            tester, 
            "1. Basic Conversation", 
            "You are a helpful assistant.", 
            "Hello! Who are you?"
        )
        
        # 시나리오 2: 페르소나 변경 (해적)
        await run_scenario(
            tester, 
            "2. Pirate Persona Update Test", 
            "You are now a pirate. Talk like one! Use 'Arrr' and 'Matey'.", 
            "What is your mission, captain?"
        )
        
        # 시나리오 3: 한국어 비서
        await run_scenario(
            tester, 
            "3. Korean Assistant Locale Test", 
            "당신은 이제 친절한 한국어 비서입니다. 한국어로 정중하게 답변하세요.", 
            "오늘 날씨에 대해 이야기해줘."
        )
        
    finally:
        tester.close()
        print("\n✅ 모든 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(main())
