# 🚀 Free Deployment Guide: Hugging Face Spaces

Since this project uses heavy AI libraries (`torch`, `sentence-transformers`), standard free tiers like Render or Koyeb (512MB RAM) will likely crash. 

**Hugging Face Spaces** is the best FREE option because it provides **16GB of RAM** and **2 CPU cores** for free.

## Step 1: Create a Hugging Face Account
1. Go to [huggingface.co](https://huggingface.co) and sign up.

## Step 2: Create a New Space
1. Click on your profile picture (top right) and select **"New Space"**.
2. **Space Name**: `ai-news-intelligence`
3. **License**: `apache-2.0` (or your choice).
4. **Select the Space SDK**: Select **Docker**.
5. **Choose Docker Template**: Select **"Blank"**.
6. **Space Hardware**: Keep it on **"CPU Basic • 16GB • FREE"**.
7. **Visibility**: Select **Public** (recommended for testing) or **Private**.
8. Click **"Create Space"**.

## Step 3: Connect your GitHub Repo
Instead of uploading files manually, you can sync your GitHub repo:
1. In your new Space, go to the **"Settings"** tab.
2. Scroll to **"Connected GitHub Repository"**.
3. Link your GitHub account and select your repository: `Intelligence_agent`.

## Step 4: Add Secrets (Environment Variables)
Hugging Face calls environment variables "Secrets".
1. In the **"Settings"** tab of your Space, find the **"Variables and secrets"** section.
2. Click **"New secret"** for each item in your `.env` file:
   - `OPENAI_API_KEY`
   - `NEWS_API_KEY`
   - `FIREBASE_API_KEY`
   - `FIREBASE_SERVICE_ACCOUNT_JSON` (Paste the entire content of your JSON file here)
   - *Add any other variables from your .env...*

## Step 5: Wait for Build
Hugging Face will automatically see the `Dockerfile` I created and start building. Once finished, you will see your Dashboard live in the Space!

---

### 💡 Why this is better than Render:
- **16GB RAM**: No more "Out of Memory" errors.
- **No Credit Card**: They don't usually ask for a card for the basic free tier.
- **24/7 Running**: Your background tasks (2-minute refresh) will continue to run as long as the Space is awake.

> [!NOTE]
> Hugging Face Spaces "sleep" after 48 hours of inactivity. To keep it running forever, you might need to visit the URL once every 2 days, or set up a simple pinging service.
