#!/usr/bin/env python
"""Debug Agent SDK - Full error output"""

import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def debug_agent():
    """Debug agent with full error output"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-20241022")

    print(f"API Key: {api_key[:20]}...")
    print(f"Model: {model}")
    print()

    from app.services.agent_service import AgentService

    try:
        service = AgentService(api_key=api_key)
        print(f"✓ Service initialized")
        print(f"✓ Client type: {type(service.client)}")
        print(f"✓ Client: {service.client}")
        print()

        print("Testing query...")
        query_text = "こんにちは"

        chunk_count = 0
        async for chunk in service.query(query_text):
            chunk_count += 1
            print(f"\n--- Chunk {chunk_count} ---")
            print(f"Type: {type(chunk)}")
            print(f"Content: {json.dumps(chunk, indent=2, ensure_ascii=False)}")

        print(f"\nTotal chunks: {chunk_count}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_agent())
