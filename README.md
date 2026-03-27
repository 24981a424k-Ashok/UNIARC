---
title: Intelligence Ai News Agent
emoji: 📰
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# 📰 Intelligence AI News Agent

An automated AI intelligence agent that collects, verifies, and analyzes global news from multiple sources to deliver high-impact daily digests.

## Features
- **60-Second Brief**: Top 5 headlines for quick consumption.
- **Deep Analysis**: AI-powered context and impact scoring.
- **Personalized Retention**: Save articles and track reading history.
- **High Frequency**: Refreshes every 2 minutes.

## Deployment on Spaces
This app runs in a Docker container. Ensure the following **Secrets** are set in the Space settings:
- `OPENAI_API_KEY`
- `NEWS_API_KEY`
- `FIREBASE_API_KEY`
- `FIREBASE_SERVICE_ACCOUNT_JSON`
- `FIREBASE_AUTH_DOMAIN`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_STORAGE_BUCKET`
- `FIREBASE_MESSAGING_SENDER_ID`
- `FIREBASE_APP_ID`
- `VAPID_PUBLIC_KEY`
- `VAPID_PRIVATE_KEY`
- `DATABASE_URL` (Optional: set to `sqlite:////app/data/news.db`)

Build and served by [Hugging Face Spaces](https://huggingface.co/spaces).
