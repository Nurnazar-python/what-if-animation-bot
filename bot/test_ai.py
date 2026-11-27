#!/usr/bin/env python
"""Test freelm AI integration."""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from bot.ai import get_client, ask_ai, ask_ai_with_provider, log_provider_health


def test_providers():
    """Test which providers are available."""
    print("=" * 60)
    print("Testing freelm provider health...")
    print("=" * 60)
    log_provider_health()


def test_basic_chat():
    """Test basic chat functionality."""
    print("\n" + "=" * 60)
    print("Testing basic chat...")
    print("=" * 60)
    
    prompt = "Say 'Hello from freelm!' in exactly 5 words."
    response = ask_ai(prompt)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")


def test_with_provider_info():
    """Test chat with provider info."""
    print("\n" + "=" * 60)
    print("Testing chat with provider tracking...")
    print("=" * 60)
    
    prompts = [
        "What is 2+2?",
        "Write a haiku about robots.",
        "Explain quantum computing in one sentence."
    ]
    
    for prompt in prompts:
        response, provider = ask_ai_with_provider(prompt)
        print(f"\nPrompt: {prompt}")
        print(f"Provider: {provider}")
        print(f"Response: {response}")


def test_system_prompt():
    """Test with system prompt."""
    print("\n" + "=" * 60)
    print("Testing with system prompt...")
    print("=" * 60)
    
    system = "You are a pirate. Answer everything in pirate speak."
    prompt = "How do I make a video?"
    response = ask_ai(prompt, system=system)
    print(f"System: {system}")
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")


if __name__ == "__main__":
    # Check for required env vars
    required = ["OPENROUTER_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY"]
    has_key = any(os.getenv(k) for k in required)
    
    if not has_key and os.getenv("FREELM_KEYLESS", "auto") == "never":
        print("⚠️  No API keys set and FREELM_KEYLESS=never")
        print("Set at least one key or export FREELM_KEYLESS=auto")
        sys.exit(1)
    
    print("Running freelm integration tests...\n")
    
    try:
        test_providers()
        test_basic_chat()
        test_with_provider_info()
        test_system_prompt()
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)