import logging
import random
import json
import asyncio
from typing import List, Dict, Any, Union
from openai import AsyncOpenAI
from src.config import settings

logger = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"

class NewsTranslator:
    def __init__(self):
        # Support multiple Groq API keys for rotation to avoid rate limits
        self.groq_keys = getattr(settings, 'GROQ_API_KEYS', [])
        if not self.groq_keys:
            # Fall back to single key
            single = getattr(settings, 'GROQ_API_KEY', '')
            if single:
                self.groq_keys = [single]
        
        if not self.groq_keys:
            logger.warning("No GROQ API keys found. Translation will be skipped.")
        else:
            logger.info(f"NewsTranslator initialized with {len(self.groq_keys)} Groq API key(s) for rotation.")
        
        # Cache one client per key
        self._clients: Dict[str, AsyncOpenAI] = {}

    def _get_client(self, target_lang: str = None) -> tuple:
        """Return (AsyncOpenAI client, key_info) using a specialized or randomly selected Groq key."""
        # 1. Check for specialized keys first
        if target_lang:
            lang_key = None
            lang_name = target_lang.lower().strip()
            if "telugu" in lang_name:
                lang_key = getattr(settings, 'GROQ_KEY_TELUGU', None)
            elif "hindi" in lang_name:
                lang_key = getattr(settings, 'GROQ_KEY_HINDI', None)
            elif "malayalam" in lang_name:
                lang_key = getattr(settings, 'GROQ_KEY_MALAYALAM', None)
            elif "tamil" in lang_name:
                lang_key = getattr(settings, 'GROQ_KEY_TAMIL', None)

            if lang_key:
                if lang_key not in self._clients:
                    self._clients[lang_key] = AsyncOpenAI(api_key=lang_key, base_url=GROQ_BASE_URL)
                return self._clients[lang_key], f"Specialized ({target_lang})"

        # 2. Fall back to rotation
        if not self.groq_keys:
            return None, "None"
        
        idx = random.randint(0, len(self.groq_keys) - 1)
        key = self.groq_keys[idx]
        if key not in self._clients:
            self._clients[key] = AsyncOpenAI(api_key=key, base_url=GROQ_BASE_URL)
        return self._clients[key], f"Key#{idx + 1}"

    async def translate_text(self, text: str, target_lang: str) -> str:
        """Translate a single piece of text to target_lang using Groq (Async)."""
        if not text or not target_lang or target_lang.lower() == 'english':
            return text
        
        client, key_info = self._get_client(target_lang)
        if not client:
            return text

        try:
            response = await client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional news translator. Translate the following news text into {target_lang}. Return ONLY the translated text."
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0.2,
                timeout=20
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if "rate_limit" in str(e).lower():
                logger.warning(f"Rate limit hit on {key_info} during translation of '{text[:30]}...'. Trying another key next time.")
            else:
                logger.error(f"Translation failed on {key_info}: {e}")
            return text

    async def translate_stories(self, stories: List[Dict[str, Any]], target_lang: str) -> List[Dict[str, Any]]:
        """Translate key fields of multiple stories to target_lang (Async)."""
        if not stories or not target_lang or target_lang.lower() == 'english':
            return stories

        translated_stories = json.loads(json.dumps(stories))
        
        # Parallelize translation of stories for better performance
        async def translate_single_story(story):
            # Translate bullet lists
            if 'bullets' in story and story['bullets']:
                story['bullets'] = await asyncio.gather(*[self.translate_text(b, target_lang) for b in story['bullets']])
            
            # Translate key text fields
            fields_to_translate = ['title', 'why', 'affected', 'headline']
            for field in fields_to_translate:
                if field in story and story[field]:
                    story[field] = await self.translate_text(story[field], target_lang)
            return story

        # Process stories in small groups to distribute across keys and avoid bursts
        results = []
        batch_size = 3
        for i in range(0, len(translated_stories), batch_size):
            batch = translated_stories[i:i+batch_size]
            results.extend(await asyncio.gather(*[translate_single_story(s) for s in batch]))
            if i + batch_size < len(translated_stories):
                await asyncio.sleep(0.3)  # Small breath between batches

        return results

    async def translate_node_bulk(self, node_data: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
        """Translate an entire node dashboard in one bulk Groq call (Async)."""
        if not target_lang or target_lang.lower() == 'english':
            return node_data

        client, key_info = self._get_client(target_lang)

        articles_text = ""
        stories = node_data.get("stories", [])
        for idx, story in enumerate(stories, 1):
            bullets = story.get("bullets", [])
            bullet_str = "\n".join(f"- {b}" for b in bullets)
            articles_text += (
                f"ARTICLE {idx}\n\n"
                f"HEADLINE:\n{story.get('title') or story.get('headline', '')}\n\n"
                f"CORE DEVELOPMENT:\n{bullet_str}\n\n"
                f"WHO IS AFFECTED:\n{story.get('affected') or story.get('who_is_affected', 'N/A')}\n\n"
                f"WHY IT MATTERS:\n{story.get('why') or story.get('why_it_matters', 'N/A')}\n\n"
                f"----------------------------------------\n\n"
            )

        prompt = f"""Translate these items into {target_lang}. Return ONLY a JSON object.
Input:
NODE TITLE: {node_data.get('node_title', '')}
NODE DESCRIPTION: {node_data.get('node_description', '')}
ARTICLES:
{articles_text}

JSON Format:
{{
  "node_title": "...",
  "node_description": "...",
  "articles": [ {{ "headline": "...", "bullets": ["...", "..."], "who_is_affected": "...", "why_it_matters": "..." }} ]
}}"""

        try:
            response = await client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            raw = response.choices[0].message.content.strip()
            return json.loads(raw)
        except Exception as e:
            logger.error(f"Bulk node translation failed: {e}")
            return node_data
