#!/usr/bin/env python
"""Live integration test with actual Claude API

Tests the Agent service with real API calls to verify the implementation works.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_agent_service():
    """Test Agent service with real API calls"""
    print("=" * 60)
    print("🧪 Live Integration Test - Claude Agent SDK")
    print("=" * 60)

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("❌ Error: ANTHROPIC_API_KEY not set in .env file")
        return False

    print(f"✓ API Key configured: {api_key[:20]}...")
    print()

    # Import after env is loaded
    from app.services.agent_service import AgentService

    try:
        # Initialize service
        print("1️⃣ Initializing Agent Service...")
        service = AgentService(api_key=api_key)
        print(f"   ✓ Service initialized")
        print(f"   ✓ Client: {service.client}")
        print()

        # Test 1: Simple query
        print("2️⃣ Testing simple query...")
        query_text = "株式会社とは何ですか？簡潔に説明してください。"
        print(f"   Query: {query_text}")

        response_chunks = []
        async for chunk in service.query(query_text):
            response_chunks.append(chunk)
            if chunk.get("type") == "text":
                print(f"   📝 Response chunk: {chunk.get('content', '')[:100]}...")

        if response_chunks:
            print(f"   ✓ Received {len(response_chunks)} response chunks")
        else:
            print("   ⚠ No response chunks received")
        print()

        # Test 2: Session management
        print("3️⃣ Testing session management...")
        session_id = await service.create_session()
        print(f"   ✓ Session created: {session_id}")

        session_info = await service.get_session(session_id)
        print(f"   ✓ Session retrieved: {session_info['id']}")
        print()

        # Test 3: Chat with context
        print("4️⃣ Testing chat with context...")
        chat_message = "こんにちは、会社法について教えてください。"
        print(f"   Message: {chat_message}")

        chat_chunks = []
        async for chunk in service.chat(chat_message, session_id):
            chat_chunks.append(chunk)
            if chunk.get("type") == "text":
                print(f"   💬 Chat response: {chunk.get('content', '')[:100]}...")

        if chat_chunks:
            print(f"   ✓ Received {len(chat_chunks)} chat chunks")
        else:
            print("   ⚠ No chat chunks received")
        print()

        print("=" * 60)
        print("✅ All integration tests passed!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_endpoints():
    """Test API endpoints with actual requests"""
    print("\n" + "=" * 60)
    print("🌐 Testing API Endpoints")
    print("=" * 60)

    from httpx import AsyncClient, ASGITransport
    from app.main import app

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:

            # Test query endpoint
            print("\n1️⃣ Testing POST /api/v1/agent/query...")
            response = await client.post(
                "/api/v1/agent/query",
                json={"query": "会社法とは？"}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type')}")

            # Test session endpoint
            print("\n2️⃣ Testing POST /api/v1/agent/session...")
            response = await client.post("/api/v1/agent/session")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Session created: {data.get('session_id')}")
            else:
                print(f"   Status: {response.status_code}")

            print("\n✅ API endpoint tests completed!")

    except Exception as e:
        print(f"\n❌ Error testing endpoints: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting live integration tests...\n")

    # Run tests
    success = asyncio.run(test_agent_service())

    if success:
        asyncio.run(test_api_endpoints())

    print("\n✨ Testing complete!\n")
