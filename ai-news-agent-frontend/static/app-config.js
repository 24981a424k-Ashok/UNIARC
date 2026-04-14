/**
 * app-config.js — Frontend API Configuration for Android (.aab) & Web
 * 
 * Instructions for Android Studio (.aab) packaging:
 * 1. When you host the Backend on Firebase, change PRODUCTION_BACKEND_URL to that URL.
 * 2. Example: const PRODUCTION_BACKEND_URL = "https://your-firebase-api.com";
 * 
 * If you are running locally on your computer with `server.py`, the system 
 * will automatically route through the local proxy.
 */

(function () {
    // CHANGE THIS TO YOUR FIREBASE URL BEFORE MAKING THE .AAB FILE
    const PRODUCTION_BACKEND_URL = "https://uniarcb-production.up.railway.app"; 
    
    const currentPort = window.location.port;
    const protocol = window.location.protocol;
    
    // Auto-detect environment
    if (protocol === 'file:' || protocol === 'android-app:') {
        // We are inside an Android App native WebView (.aab)
        // Must use absolute URLs to cross origin
        window.API_BASE = PRODUCTION_BACKEND_URL;
    } else if (currentPort === '3000' || currentPort === '5000') {
        // We are on the local decoupled testing proxy (server.py)
        // Requests go to /api/ which forwards securely to 8000
        window.API_BASE = '';
    } else {
        // Fallback for Vercel or other hosted setups
        window.API_BASE = window.ENV?.BACKEND_URL || PRODUCTION_BACKEND_URL;
    }

    // Helper: Build a full API URL dynamically
    window.apiUrl = function (path) {
        let base = window.API_BASE;
        return base + path;
    };

    console.log('[UNI ARC] Intelligence API Linked:', window.API_BASE || '(Proxy Relay)');
})();
