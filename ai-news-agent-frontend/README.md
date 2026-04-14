# AI News Agent - Frontend

This folder contains **all HTML templates, CSS, JavaScript and static assets** for the platform.

The frontend is **served by the backend** (`ai-news-agent-backend`), which reads templates from
this folder. You do NOT need to run a separate server for the frontend.

## Structure

```
ai-news-agent-frontend/
├── templates/          # All HTML templates (dashboard.html, login.html, etc.)
│   ├── dashboard.html
│   ├── login.html
│   ├── saved.html
│   ├── history.html
│   ├── mock_test.html
│   ├── student_news.html
│   └── ...
└── static/             # All static assets
    ├── style.css
    ├── dashboard.js
    ├── favicon.png
    └── ...
```

## How to Edit

- **Design changes**: Edit files in `templates/` or `static/`
- **Changes take effect immediately** — no build step required
- The backend at `ai-news-agent-backend/` automatically serves these files

## How to Start the Full Platform

```bash
# Run from the ai-news-agent-backend/ directory:
cd ai-news-agent-backend
python main.py
```

Then open: **http://127.0.0.1:8000**
