import os
import openai
from dotenv import load_dotenv

load_dotenv()

keys = [
    os.getenv('TRANSLATION_OPENAI_KEY_1'),
    os.getenv('TRANSLATION_OPENAI_KEY_2'),
    os.getenv('TRANSLATION_OPENAI_KEY_3')
]

with open('key_results.txt', 'w') as f:
    for i, k in enumerate(keys):
        f.write(f"Testing Key {i+1}...\n")
        if not k:
            f.write(f"Key {i+1} is missing!\n")
            continue
        
        try:
            client = openai.OpenAI(api_key=k)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=5
            )
            f.write(f"Key {i+1} works! Response: {response.choices[0].message.content}\n")
        except Exception as e:
            f.write(f"Key {i+1} failed: {e}\n")
        f.write("-" * 20 + "\n")

print("Done. Results in key_results.txt")
