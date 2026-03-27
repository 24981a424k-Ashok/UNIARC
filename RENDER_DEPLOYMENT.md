# 🚀 Deploying AI News Agent to Render

Render is a much better fit for this project than Vercel because it supports long-running background tasks (for news collection) and doesn't have the strict 250MB memory limit that Vercel has.

## Step 1: Create a Render Account
1. Go to [Render.com](https://render.com) and sign up (using GitHub is easiest).

## Step 2: Create a New Web Service
1. In your Render Dashboard, click **"New +"** and select **"Web Service"**.
2. Connect your GitHub account and select your repository: **Intelligence_agent**.

## Step 3: Configure Build & Start Commands
Fill in the following settings on the creation page:
- **Name**: `ai-news-intelligence`
- **Region**: Select the one closest to you (e.g., Singapore or US East).
- **Branch**: `master`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
## Step 5: (Optional but Recommended) Persistent Storage
Since the app uses SQLite, your news data will be lost every time the app restarts on the Free tier. To keep your data:
1. Go to the **"Disk"** tab in your Render service settings.
2. Click **"Add Disk"**.
3. **Name**: `news-data`
4. **Mount Path**: `/data`
5. **Size**: `1 GB` (usually sufficient).
6. Update your `DATABASE_URL` env var to: `sqlite:////data/news.db` (Note the 4 slashes).

---
## 💡 Troubleshooting
- **Build Fails**: If it says "Out of Memory," you might need to use a slightly higher plan ($7/mo) because the AI libraries (`torch`) are very heavy.
- **Port Error**: Render automatically sets the `$PORT` variable, so `uvicorn` will listen on the correct port automatically with the command provided in Step 3.

Once you click "Create Web Service," Render will build and deploy your app. You'll get a URL like `https://ai-news-intelligence.onrender.com`.
