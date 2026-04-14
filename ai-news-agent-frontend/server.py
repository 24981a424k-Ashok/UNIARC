import os
import sys
import uvicorn
import httpx
import logging
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UNI-ARC-FRONTEND")

# -------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------
FRONTEND_PORT = 3000
# Important: This points to your hosted Backend (or localhost for dev)
# For Firebase, update this to your firebase function/app URL
BACKEND_URL   = os.getenv("BACKEND_URL", "https://uniarcb-production.up.railway.app")

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR    = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app = FastAPI(title="UNI ARC - Standalone Frontend")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Serve static files locally
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(STATIC_DIR, "favicon.png"))

# -------------------------------------------------------
# API PROXY: For client-side Javascript calls (Listen, Chat, etc.)
# -------------------------------------------------------
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_api(request: Request, path: str):
    url = f"{BACKEND_URL}/api/{path}"
    if request.url.query:
        url += f"?{request.url.query}"
    
    headers = dict(request.headers)
    headers.pop("host", None)
    body = await request.body()
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            req = client.build_request(
                request.method, url, headers=headers, cookies=request.cookies, content=body
            )
            r = await client.send(req)
            from fastapi.responses import Response
            return Response(content=r.content, status_code=r.status_code, headers=dict(r.headers), media_type=r.headers.get("content-type"))
    except Exception as e:
        return {"error": f"Backend unreachable: {e}"}

# -------------------------------------------------------
# CORE RENDERING LOGIC: Fetch JSON data, Render HTML locally
# -------------------------------------------------------
async def get_backend_data(path: str, params: dict = None) -> dict:
    url = f"{BACKEND_URL}/api/v2/{path}"
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.get(url, params=params)
            if r.status_code == 200:
                return r.json()
            logger.error(f"Backend API error {r.status_code} at {url}")
    except Exception as e:
        logger.error(f"Failed to fetch data from {url}: {e}")
    return {}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Fetch base UI translations and config
    data = await get_backend_data("bootstrap", params={"lang": "english"})
    return templates.TemplateResponse("login.html", {
        "request": request,
        "firebase_config": data.get("firebase_config", {}),
        "ui": data.get("ui", {})
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, category: str = None, country: str = None, lang: str = 'english'):
    params = {"lang": lang}
    if category: params["category"] = category
    if country: params["country"] = country
    
    # FETCH ALL DATA FROM BACKEND API
    data = await get_backend_data("bootstrap", params=params)
    
    if not data or data.get("status") == "error":
        return HTMLResponse(content=f"<h1>Backend Sync Error</h1><p>{data.get('message', 'Unreachable')}</p>", status_code=503)

    # RENDER LOCAL TEMPLATE WITH REMOTE DATA
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "digest": data.get("digest", {}),
        "date": data.get("date", "Syncing..."),
        "firebase_config": data.get("firebase_config", {}),
        "left_ads": data.get("left_ads", []),
        "right_ads": data.get("right_ads", []),
        "mobile_ads": data.get("mobile_ads", []),
        "papers": data.get("papers", []),
        "categories": data.get("categories", []),
        "selected_category": category,
        "selected_country": country,
        "selected_lang": lang,
        "trending_title": data.get("trending_title", "Global News"),
        "ui": data.get("ui", {}),
        "vapid_public_key": data.get("vapid_public_key", ""),
        "admin_api_url": BACKEND_URL # Pass backend URL to client
    })

@app.get("/saved", response_class=HTMLResponse)
async def saved(request: Request):
    data = await get_backend_data("bootstrap")
    return templates.TemplateResponse("saved.html", {
        "request": request,
        "firebase_config": data.get("firebase_config", {}),
        "ui": data.get("ui", {})
    })

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    data = await get_backend_data("bootstrap")
    return templates.TemplateResponse("history.html", {
        "request": request,
        "firebase_config": data.get("firebase_config", {}),
        "ui": data.get("ui", {})
    })

@app.get("/mock-test", response_class=HTMLResponse)
async def mock_test(request: Request):
    data = await get_backend_data("bootstrap")
    return templates.TemplateResponse("mock_test.html", {
        "request": request,
        "firebase_config": data.get("firebase_config", {}),
        "ui": data.get("ui", {})
    })

@app.get("/universe", response_class=HTMLResponse)
async def universe(request: Request):
    data = await get_backend_data("bootstrap")
    return templates.TemplateResponse("universe.html", {
        "request": request,
        "firebase_config": data.get("firebase_config", {}),
        "ui": data.get("ui", {})
    })

@app.get("/student-news", response_class=HTMLResponse)
async def student_news(request: Request, category: str = "All Updates", country: str = "India", lang: str = "english"):
    # Unified Language Switcher: Ensure consistent lang handling
    params = {"lang": lang, "country": country}
    if category and category != "All Updates":
        params["category"] = category

    # 1. Fetch Page Metadata & UI (Bootstrap)
    bootstrap_data = await get_backend_data("bootstrap", params={"lang": lang, "country": country})
    ui = bootstrap_data.get("ui", {})
    
    # 2. Fetch Specialized Student News (New Backend Optimized API)
    student_payload = await get_backend_data("get-student-news", params=params)
    raw_articles = student_payload.get("articles", [])
    
    # 3. Map to View Format
    articles = []
    for s in raw_articles:
        articles.append({
            "id": s.get("id"),
            "title": s.get("title"),
            "summary": s.get("summary") or s.get("why") or "Intelligence report active.",
            "url": s.get("url"),
            "image_url": s.get("image_url"),
            "source_name": s.get("source_name", "Verified Portal"),
            "trend_score": 95,
            "urgency": s.get("urgency", "High"),
            "tags": s.get("tags", ["Student Intel"]),
            "authority": s.get("source_name", "Official Intelligence")
        })

    # Get trends if available
    trends = await get_backend_data("get-student-trends", params={"country": country})

    return templates.TemplateResponse("student_news.html", {
        "request": request,
        "firebase_config": bootstrap_data.get("firebase_config", {}),
        "ui": ui,
        "digest": bootstrap_data.get("digest", {}),
        "articles": articles[:50],
        "trends": trends.get("trends", {}),
        "selected_category": category,
        "selected_country": country,
        "selected_lang": lang
    })

@app.get("/personal-agent", response_class=HTMLResponse)
async def personal_agent(request: Request, lang: str = "english"):
    data = await get_backend_data("bootstrap", params={"lang": lang})
    # Provide default interests for the selector
    available_interests = [
        "Artificial Intelligence", "Blockchain", "OpenAI", "Bitcoin", "EV Market", 
        "SpaceX", "Cybersecurity", "Climate Change", "Stock Market", "Semiconductors"
    ]
    return templates.TemplateResponse("personal_agent.html", {
        "request": request,
        "firebase_config": data.get("firebase_config", {}),
        "ui": data.get("ui", {}),
        "lang": lang,
        "available_interests": available_interests
    })

@app.get("/business-intelligence", response_class=HTMLResponse)
async def business_intel(request: Request, lang: str = "english"):
    data = await get_backend_data("bootstrap", params={"lang": lang})
    return templates.TemplateResponse("business_intel.html", {
        "request": request,
        "firebase_config": data.get("firebase_config", {}),
        "ui": data.get("ui", {}),
        "premium_intel": data.get("digest", {}).get("premium_intel", []),
        "lang": lang
    })

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"  UNI ARC — Standalone Frontend Server (DECOUPLED)")
    print(f"{'='*60}")
    print(f"  UI URL      : http://127.0.0.1:{FRONTEND_PORT}")
    print(f"  API Backend : {BACKEND_URL}")
    print(f"{'='*60}\n")
    uvicorn.run("server:app", host="0.0.0.0", port=FRONTEND_PORT, reload=True)
