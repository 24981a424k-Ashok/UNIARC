import asyncio
import os
import sys

# Ensure src is in path
sys.path.append(os.getcwd())

from src.utils.translator import translate_text, translate_news_batch

async def test_translation():
    print("Testing Translation Utility...")
    
    # Test single translation
    test_text = "Breaking News: Major development in New Delhi today."
    print(f"Original: {test_text}")
    
    hindi_trans = await translate_text(test_text, "Hindi")
    print(f"Hindi: {hindi_trans}")
    
    telugu_trans = await translate_text(test_text, "Telugu")
    print(f"Telugu: {telugu_trans}")
    
    # Test batch translation
    news_items = [
        {
            "title": "New infrastructure project announced for Mumbai",
            "bullets": ["Cost is 500 crores", "Completion by 2026"],
            "affected": "Residents of Mumbai",
            "why": "To reduce traffic congestion"
        }
    ]
    
    print("\nTesting Batch Translation (Hindi)...")
    translated = await translate_news_batch(news_items, "Hindi")
    print(f"Translated Item: {translated[0]}")

if __name__ == "__main__":
    asyncio.run(test_translation())
