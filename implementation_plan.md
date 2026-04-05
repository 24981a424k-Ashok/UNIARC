# Architecture Update: Decoupled Frontend/Backend & API Key Rotation

This plan outlines the steps to separate the current monolithic FastAPI application into a decoupled architecture and implement a robust API key rotation system.

## User Review Required

> [!IMPORTANT]
> **Deployment Changes:** You will need to set up two separate projects: one on Vercel for the frontend and one on Render for the backend.
> **Environment Variables:** You will need to move your Firebase and API configurations to the respective platforms (Frontend vars to Vercel, Backend vars to Render).
> **CORS Security:** We will need to whitelist your Vercel domain in the Render backend to allow communication.

## Proposed Changes

### 1. Backend Decoupling (Render)

#### [MODIFY] [main.py](file:///c:/Users/CH%20ASHOK%20REDDY/OneDrive/Desktop/VibeCoding/ai-news-agent/main.py)
- Add `CORSMiddleware` to allow requests from the Vercel frontend domain.
- Remove static file mounting if no longer needed for development.

#### [MODIFY] [web_dashboard.py](file:///c:/Users/CH%20ASHOK%20REDDY/OneDrive/Desktop/VibeCoding/ai-news-agent/src/delivery/web_dashboard.py)
- Refactor routes (e.g., `/dashboard`, `/student-news`) to return JSON data instead of `Jinja2Templates.TemplateResponse`.
- Ensure all logic (filtering, translation, etc.) remains intact but outputs as a standardized JSON structure.

---

### 2. Frontend Separation (Vercel)

#### [NEW] `frontend/` (Directory)
- Create a dedicated folder for the standalone frontend.
- Move all HTML files from `web/templates/` to `frontend/public/` (or root).
- **Update JS Logic:** 
    - Create a `config.js` to define `BACKEND_URL`.
    - Replace all relative fetch calls (e.g., `fetch('/api/login')`) with absolute calls (e.g., `fetch(`${BACKEND_URL}/api/login`)`).
    - Handle navigation by linking directly to `.html` files (e.g., `href="dashboard.html"`).

---

### 3. API Key Rotation System

#### [MODIFY] [settings.py](file:///c:/Users/CH%20ASHOK%20REDDY/OneDrive/Desktop/VibeCoding/ai-news-agent/src/config/settings.py)
- Update to load multiple keys from `.env` (e.g., `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2`, etc.).
- Create lists for `OPENAI_KEYS` and `GROQ_KEYS`.

#### [NEW] [key_manager.py](file:///c:/Users/CH%20ASHOK%20REDDY/OneDrive/Desktop/VibeCoding/ai-news-agent/src/utils/key_manager.py)
- Implement a `KeyManager` class with a `get_next_openai_key()` method.
- Add "Round Robin" rotation logic.
- **Error Handling:** If a key returns a `429` (Rate Limit) or `Insufficient Funds` error, automatically rotate to the next key and mark the failed one as "Coalescing" for a period of time.

#### [MODIFY] [llm_analyzer.py](file:///c:/Users/CH%20ASHOK%20REDDY/OneDrive/Desktop/VibeCoding/ai-news-agent/src/analysis/llm_analyzer.py)
- Refactor the `__init__` and `analyze_batch` methods to fetch keys dynamically from the `KeyManager` instead of a static setting.

---

## Open Questions

1. **Frontend Framework:** Would you like to keep the frontend as plain HTML/JS files (easiest migration), or would you prefer me to wrap them in a simple Vite/React structure for better management?
2. **Key Count:** How many premium keys do you plan to use for each (OpenAI vs. Groq)? I will pre-configure the system to handle up to 10 for each.
3. **Domain Name:** Do you have a custom domain for the frontend, or will you use the default `.vercel.app`? (Needed for CORS setup).

## Verification Plan

### Automated Tests
- `python test_keys.py`: A script to simulate multiple LLM calls and verify that keys are rotating correctly.
- `api_test.py`: Verify that all backend routes return valid JSON and correctly handle CORS headers.

### Manual Verification
1. Deploy backend to a "Staging" Render environment.
2. Run frontend locally and attempt to sign in and fetch news from the remote backend.
3. Verify that translation and AI chat still work using the rotated keys.
