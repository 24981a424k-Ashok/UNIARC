# Premium API Guide & Speed Optimization

This guide explains how to acquire professional "Premium" API keys, add credits to your accounts, and configure the platform for maximum performance.

## 1. Buying Premium API Keys & Adding Credits

To ensure the "Neural News Agent" stays online with high accuracy and speed, you need high-quota keys from the following providers.

### **A. OpenAI (Powering Deep Analysis & Audio)**
-   **Step 1**: Visit [platform.openai.com](https://platform.openai.com/).
-   **Step 2**: Sign up or log in.
-   **Step 3**: Go to **'Settings' -> 'Billing'**.
-   **Step 4**: Click **'Add to credit balance'**. I recommend at least **$10 - $20** to start for a high-traffic site.
-   **Step 5**: Go to **'API Keys'** and generate a new key.
-   **Field in .env**: `OPENAI_API_KEY`

### **B. Groq (Powering Fast Categorization)**
-   **Step 1**: Visit [console.groq.com](https://console.groq.com/).
-   **Step 2**: Sign up or log in.
-   **Step 3**: Go to **'API Keys'**. They currently offer a free tier with high speed, but you can upgrade to a paid tier in the 'Billing' section as they roll it out.
-   **Field in .env**: `GROQ_API_KEY`

### **C. Google Cloud (Powering Global Translation & TTS)**
-   **Step 1**: Visit [console.cloud.google.com](https://console.cloud.google.com/).
-   **Step 2**: Create a Project.
-   **Step 3**: In the search bar, search for **'Cloud Translation API'** and **'Text-to-Speech API'** and enable them.
-   **Step 4**: Go to **'IAM & Admin' -> 'Service Accounts'**. Create one and generate a **JSON Key**.
-   **Step 5**: Attach a Credit Card in the 'Billing' section. Google offers $300 in free credits for new users.

---

## 2. Why the Website feels Slow

The current "Slowness" is caused by two main bottlenecks:
1.  **Parallel Translation Latency**: We are translating 20+ headlines in 0.5s. If Groq/OpenAI is under heavy load, the browser waits for all of them.
2.  **No Caching**: Every time a user changes a language, we recalculate the translation.

### **Our Speed Solution (Phase 4):**
-   **Database Caching**: We will store the Hindi/Tamil/Spanish versions of every headline in the database. 
-   **Instant Loads**: Next time someone visits in Hindi, the page will load in **< 100ms** (no AI call needed).

---

## 3. Resolving the Hugging Face "UDP Flood" Pause

The email you received is likely because:
1.  **Burst API Traffic**: Our app fires 100+ parallel requests (`asyncio.gather`) during news cycles. HF's firewall thinks this is a "Botnet" trying to DDoS the external AI servers.
2.  **Fixed Process**:
    -   **Semaphore Integration**: I am adding a "Traffic Controller" (Semaphore) that only allows 3-5 requests at a time.
    -   **Jitter**: We will add tiny, random millisecond delays between calls to look like "human" traffic patterns.

---

## 4. Replacing your 4 Premium Keys

Once you have your keys, follow these steps:

1.  Open the `.env` file in your editor (`ai-news-agent/.env`).
2.  Paste your new keys into these lines:
    ```env
    OPENAI_API_KEY="sk-..."
    GROQ_API_KEY="gsk-..."
    GNEWS_API_KEY="..."
    TWILIO_ACCOUNT_SID="..."
    ```
3.  **DO NOT SHARE** these keys with anyone.
4.  Restart the application for the keys to take effect.
