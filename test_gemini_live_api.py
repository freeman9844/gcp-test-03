"""
Google Gemini Live API 테스트 샘플 코드 (Google AI Studio 버전)
google-genai SDK를 사용하여 실시간으로 시스템 인스트럭션을 업데이트하는 예제입니다.
"""

import asyncio
import os
from google import genai
from google.genai import types


class GeminiLiveAPITest:
    """Gemini Live API 테스트 클래스 (Google AI Studio)"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Args:
            api_key: Google AI API 키
            model_name: 사용할 모델 이름 (기본값: gemini-2.0-flash-exp)
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.session = None
    
    async def connect(self, initial_instruction: str = "You are a helpful assistant."):
        """
        Live API 세션을 생성하고 연결을 반환합니다.
        
        Args:
            initial_instruction: 초기 시스템 인스트럭션
        """
        print(f"📡 Connecting to Live API (Model: {self.model_name})")
        
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
        """
        if not self.session:
            raise RuntimeError("Session not connected.")
        
        print(f"\n💬 Sending user message: {text}")
        
        # send_client_content를 사용하여 타입 안전하게 전송
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
        """
        if not self.session:
            raise RuntimeError("Session not connected.")
        
        print(f"\n🔄 Updating system instruction...")
        print(f"   New: {new_instruction[:50]}...")
        
        # 'system' 역할을 가진 turn을 전송하여 업데이트 (최신 SDK 권장 방식)
        await self.session.send_client_content(
            turns=[
                types.Content(
                    role="system",
                    parts=[types.Part(text=new_instruction)]
                )
            ],
            turn_complete=False
        )
        print("✅ System instruction update sent.")


async def test_all_scenarios(api_key: str):
    """모든 시나리오 테스트"""
    tester = GeminiLiveAPITest(api_key=api_key)
    
    async def run_scenario():
        async with await tester.connect(initial_instruction="You are a helpful assistant.") as session:
            tester.session = session
            listener = asyncio.create_task(tester.handle_session_events())
            
            # 1. 기본 대화
            await tester.send_text("Hello! Who are you?")
            await asyncio.sleep(8)
            
            # 2. 페르소나 업데이트
            await tester.update_instruction("You are now a pirate. Talk like one!")
            await asyncio.sleep(2)
            await tester.send_text("What is your mission?")
            await asyncio.sleep(8)
            
            # 3. 로케일/언어 업데이트
            await tester.update_instruction("당신은 이제 친절한 한국어 비서입니다. 한국어로 답변하세요.")
            await asyncio.sleep(2)
            await tester.send_text("자기소개 부탁드려요.")
            await asyncio.sleep(8)
            
            listener.cancel()
            await asyncio.gather(listener, return_exceptions=True)

    await run_scenario()


async def main():
    """메인 함수"""
    print("\n🚀 Google Gemini Live API 테스트 시작 (AI Studio)\n")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.")
        return
        
    await test_all_scenarios(api_key)
    print("\n✅ 모든 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(main())
