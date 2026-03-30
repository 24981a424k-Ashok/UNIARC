import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.utils.translator import NewsTranslator
import logging

logging.basicConfig(level=logging.INFO)

def test_translation():
    translator = NewsTranslator()
    
    test_text = "Breaking News: Major development in New Delhi today regarding economic policy."
    target_lang = "Hindi"
    
    print(f"Original: {test_text}")
    print(f"Target Language: {target_lang}")
    
    translated = translator.translate_text(test_text, target_lang)
    print(f"Translated: {translated}")
    
    # Test JSON structure
    stories = [
        {
            "title": "Stock Market Update",
            "why": "Investors are optimistic about the new budget.",
            "bullets": ["Record highs reached", "Tech stocks leading"]
        }
    ]
    
    print("\nTesting Story Translation JSOn:")
    translated_stories = translator.translate_stories(stories, "Spanish")
    import json
    print(json.dumps(translated_stories, indent=2))

if __name__ == "__main__":
    test_translation()
