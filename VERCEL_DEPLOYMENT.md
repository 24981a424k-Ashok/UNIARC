# Vercel Deployment Guide

## Prerequisites
1. Install Vercel CLI: `npm install -g vercel`
2. Create a Vercel account at https://vercel.com

## Deployment Steps

### 1. Login to Vercel
```bash
vercel login
```

### 2. Deploy the Application
```bash
cd c:\Users\CH ASHOK REDDY\OneDrive\Desktop\VibeCoding\ai-news-agent
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? Choose your account
- Link to existing project? **N**
- Project name? `ai-news-agent` (or your preferred name)
- Directory? `./`
- Override settings? **N**

### 3. Set Environment Variables
After deployment, add your environment variables:

```bash
vercel env add NEWS_API_KEY
vercel env add OPENAI_API_KEY
vercel env add FIREBASE_SERVICE_ACCOUNT_PATH
```

Or set them in the Vercel dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add:
   - `NEWS_API_KEY`: Your NewsAPI key
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `DATABASE_URL`: SQLite won't work on Vercel (use PostgreSQL or external DB)

### 4. Redeploy with Environment Variables
```bash
vercel --prod
```

## Important Notes

⚠️ **Database Limitation**: Vercel serverless functions are stateless. You'll need to:
- Use an external database (PostgreSQL on Supabase, Neon, or Railway)
- Update `DATABASE_URL` in environment variables
- Consider using Vercel's Postgres or external service

⚠️ **Scheduler Limitation**: APScheduler won't work on serverless.
- We have implemented **Vercel Cron Jobs** in `vercel.json`.
- The endpoint `/api/cron/process-news` is called automatically by Vercel.
- The schedule is currently set to:
    - Every hour (`0 * * * *`)
    - Daily at 6:30 AM (`30 6 * * *`)

## Alternative: Use Render Instead

Since this app has:
- Background scheduler
- SQLite database
- Long-running processes

**Render** would be a better fit. Would you like me to set that up instead?
