"""
google-genai SDK 타입 인트로스펙션 3
LiveServerMessage 필드를 확인합니다.
"""
from google.genai import types

def print_fields(cls):
    print(f"\n🔍 Fields for {cls.__name__}:")
    try:
        for field_name, field in cls.model_fields.items():
            print(f"  - {field_name}: {field.annotation}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

async def main():
    print_fields(types.LiveServerMessage)
    print_fields(types.LiveServerContent)
    print_fields(types.LiveServerSetupComplete)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
