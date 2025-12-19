"""
Google Gemini Live API 테스트 샘플 코드 (Vertex AI 버전)
google-genai SDK를 사용하여 Vertex AI로 실시간 시스템 인스트럭션을 업데이트하는 예제입니다.
"""

import asyncio
from google import genai
from google.genai import types


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
    
    async def connect(self, initial_instruction: str = "You are a helpful assistant."):
        """
        Live API 세션 연결을 반환합니다.
        
        Args:
            initial_instruction: 초기 시스템 인스트럭션
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
            
        print("\n👂 Listening for responses...")
        
        try:
            async for response in self.session.receive():
                # 서버로부터 받은 응답 처리
                if response.text:
                    print(f"\n🤖 Assistant: {response.text}")
                elif response.server_content and response.server_content.model_turn:
                    for part in response.server_content.model_turn.parts:
                        if part.text:
                            print(f"\n🤖 Assistant: {part.text}")
                elif response.tool_call:
                    print(f"\n🔧 Tool call: {response.tool_call}")
        except asyncio.CancelledError:
            print("\n🛑 Listening task cancelled.")
        except Exception as e:
            print(f"\n⚠️  Session ended or error occurred: {e}")
    
    async def send_text(self, text: str, end_of_turn: bool = True):
        """
        텍스트 메시지를 전송합니다.
        
        Args:
            text: 전송할 텍스트
            end_of_turn: 대화 턴 종료 여부
        """
        if not self.session:
            raise RuntimeError("Session not connected.")
        
        print(f"\n💬 Sending user message: {text}")
        
        # 인트로스펙션 결과: turns 인자를 사용해야 함
        await self.session.send_client_content(
            turns=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=text)]
                )
            ],
            turn_complete=end_of_turn
        )

    async def update_instruction(self, new_instruction: str):
        """
        시스템 인스트럭션을 실시간으로 업데이트합니다.
        
        Args:
            new_instruction: 새로운 시스템 인스트럭션
        """
        if not self.session:
            raise RuntimeError("Session not connected.")
        
        print(f"\n🔄 Updating system instruction...")
        print(f"   New: {new_instruction[:50]}...")
        
        # 최신 가이드: 'system' 역할을 가진 turn을 전송하여 업데이트
        await self.session.send_client_content(
            turns=[
                types.Content(
                    role="system",
                    parts=[types.Part(text=new_instruction)]
                )
            ],
            turn_complete=False
        )
        print("✅ System instruction update sent (via send_client_content with role='system').")


async def test_all_scenarios(project_id: str):
    """모든 시나리오를 하나의 세션에서 또는 순차적으로 테스트"""
    tester = GeminiLiveAPITestVertexAI(project_id=project_id)
    
    # 1. 기본 대화 테스트
    print("\n" + "=" * 60)
    print("SCENARIO 1: Basic Conversation")
    print("=" * 60)
    
    async with await tester.connect(initial_instruction="You are a helpful assistant.") as session:
        tester.session = session
        listener = asyncio.create_task(tester.handle_session_events())
        
        await tester.send_text("Hello! Who are you?")
        await asyncio.sleep(8)
        
        # 2. 인스트럭션 업데이트 테스트
        print("\n" + "=" * 60)
        print("SCENARIO 2: System Instruction Update")
        print("=" * 60)
        
        await tester.update_instruction("You are now a pirate. Talk like one!")
        await asyncio.sleep(2)
        
        await tester.send_text("What is your mission?")
        await asyncio.sleep(8)
        
        # 3. 로케일 변경 테스트
        print("\n" + "=" * 60)
        print("SCENARIO 3: Locale/Role Change")
        print("=" * 60)
        
        await tester.update_instruction("당신은 이제 친절한 한국어 비서입니다. 한국어로 답변하세요.")
        await asyncio.sleep(2)
        
        await tester.send_text("오늘 날씨에 대해 이야기해줘.")
        await asyncio.sleep(8)
        
        listener.cancel()
        await asyncio.gather(listener, return_exceptions=True)

    print("\n✅ 모든 테스트 완료!")


async def main():
    """메인 함수"""
    print("\n🚀 Google Gemini Live API 테스트 시작 (Vertex AI)\n")
    project_id = "jwlee-argolis-202104"
    await test_all_scenarios(project_id)


if __name__ == "__main__":
    asyncio.run(main())
