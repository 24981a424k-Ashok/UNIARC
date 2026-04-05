/**
 * Dashboard Enhancement Script
 * Handles "See More" functionality, dark/light mode toggle, and breaking news display
 */

// Initialize UI_DICT from embedded JSON
try {
    const uiDataElement = document.getElementById('ui-data');
    if (uiDataElement) {
        window.UI_DICT = JSON.parse(uiDataElement.textContent);
    } else {
        window.UI_DICT = window.UI_DICT || {};
    }
} catch (e) {
    console.error("Failed to parse UI_DICT:", e);
    window.UI_DICT = window.UI_DICT || {};
}

// ===== IMAGE FALLBACK HELPER =====
function getCategoryFallback(category, seed = '', index = 0) {
    const images = {
        'business': [
            'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1507679799987-c73774573b8a?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1454165833767-027ffea9e77b?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1591608971362-f08b2a75731a?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1579532566591-953b1445c8f1?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1512428559087-560fa5ceab42?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1542222024-c39e2281f121?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=800&q=80'
        ],
        'technology': [
            'https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1531297484001-80022131f5a1?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1535223289827-42f1e9919769?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80'
        ],
        'sports': [
            'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1504450758481-7338eba7524a?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1471295253337-3ceaaedca401?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1517649763962-0c623066013b?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1541252260730-1111e70b147a?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1517927033932-b3d18e61fb3a?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1521412644187-c49fa0b3a2a2?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1531415074968-036ba1b575da?auto=format&fit=crop&w=800&q=80'
        ],
        'politics': [
            'https://images.unsplash.com/photo-1529101091760-6149d4c46fa7?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1541872703-74c5e443d1fe?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1444653356445-99af1073c152?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1523292562811-8fa7962a78c8?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1560174038-da43ac74f01b?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1520110120185-60b527830cb1?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1575908064841-987302c3ef31?auto=format&fit=crop&w=800&q=80'
        ],
        'science': [
            'https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1564325724739-bae0bd08762c?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1507668077129-599d0608460c?auto=format&fit=crop&w=800&q=80'
        ],
        'health': [
            'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1532938911079-1b06ac7ce40b?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1576091160550-217359f48f4c?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1527613426441-4da17471b66d?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1511174511547-e4797abb41b4?auto=format&fit=crop&w=800&q=80'
        ],
        'entertainment': [
            'https://images.unsplash.com/photo-1499364660878-4a3079524524?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1514525253361-b4408569e59d?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1485182708500-e8f1f318ba72?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80'
        ],
        'world': [
            'https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1521295121783-8a321d551ad2?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1489749798305-4fea3ae63d43?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&w=800&q=80'
        ],
        'india': [
            'https://images.unsplash.com/photo-1532375810709-75b1da00537c?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1524492459423-5ec9a799ed65?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1514222134-b57cbb8ce073?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1477505982272-ead89926a577?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1532151600810-70f90772718e?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1558434088-918448994d13?auto=format&fit=crop&w=800&q=80'
        ],
        'breaking': [
            // Generic News / World
            'https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1585829365234-78d2b5020164?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1495020689067-958852a7765e?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1503694967365-bb8956c5b056?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1566378246598-5b11a0d486cc?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1523995462485-3d171b5c8fa9?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1586339949916-3e9457bef6d3?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1529101091760-6149d4c46fa7?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1504198266287-1659872e6590?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1523995462485-3d171b5c8fa9?auto=format&fit=crop&w=800&q=80',

            // Politics / Government (Expanded)
            'https://images.unsplash.com/photo-1540910419868-474947ce5b27?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1555848962-6e79363ec58f?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1577563908411-5077b6dc7624?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1549637642-90187f64f420?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1529101091760-6149d4c46fa7?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1541872703-74c5e443d1fe?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1444653356445-99af1073c152?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1523292562811-8fa7962a78c8?auto=format&fit=crop&w=800&q=80',

            // Tech / Cyber
            'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=800&q=80',

            // Financial / Market
            'https://images.unsplash.com/photo-1611974765270-ca12586343bb?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1535320903710-d9cf5d3ebdb5?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=800&q=80',

            // Climate / Environment
            'https://images.unsplash.com/photo-1569000972087-8d48e0466bad?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80',

            // Urban / City
            'https://images.unsplash.com/photo-1444723121867-c61e74ebf60a?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=800&q=80',

            // Space / abstract
            'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=800&q=80',

            // Crowd / Protest / People
            'https://images.unsplash.com/photo-1531206715517-5c0ba140b2b8?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1572949645841-094f3a9c4c94?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1494178270175-e96de2971df9?auto=format&fit=crop&w=800&q=80',

            // Medical / Health
            'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1581091226033-d5c48150dbaa?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1584036561566-b93744918300?auto=format&fit=crop&w=800&q=80',

            // Education
            'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80',

            // Justice / Law
            'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1505664194779-8beaceb93744?auto=format&fit=crop&w=800&q=80',

            // World / International (Added)
            'https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1521295121783-8a321d551ad2?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1489749798305-4fea3ae63d43?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&w=800&q=80'
        ]
    };
    limit = 20;

    const normalize = (category || '').toLowerCase();
    let targetList = images['breaking']; // Default

    for (const key in images) {
        if (normalize.includes(key)) {
            targetList = images[key];
            break;
        }
    }

    // Use seed with index to ensure uniqueness per container
    if (!seed) return targetList[index % targetList.length];

    // Improved String Hashing (djb2-like) for better variance
    let hash = 5381;
    const combinedSeed = seed + index + (category || 'global'); // Mix in category for section isolation
    for (let i = 0; i < combinedSeed.length; i++) {
        hash = (hash * 33) ^ combinedSeed.charCodeAt(i);
    }

    const finalIndex = Math.abs(hash) % targetList.length;
    return targetList[finalIndex];
}

/**
 * Global image error handler called from HTML onerror attributes
 */
function handleImageError(img, type, seed, index) {
    if (img.dataset.failed) return; // Prevent infinite loops
    img.dataset.failed = "true";

    const fallback = getCategoryFallback(type, seed, index);
    console.log(`Fallback triggered for ${type}: ${seed} -> ${fallback}`);

    const parent = img.parentElement;
    if (parent && parent.classList.contains('breaking-img-top') || parent.classList.contains('mini-img') || parent.classList.contains('side-img')) {
        parent.style.backgroundImage = `url('${fallback}')`;
    } else {
        img.src = fallback;
    }
}
window.handleImageError = handleImageError;

// ===== SEE MORE FUNCTIONALITY (API INTEGRATED) =====
function initializeSeeMore() {
    window.toggleSeeMore = toggleSeeMore;
    window.getCategoryFallback = getCategoryFallback;
}

// API-Based "See More" Function
async function toggleSeeMore(btn, selector) {
    const container = btn.previousElementSibling;
    if (!container) return;

    // First, reveal local hidden items if any
    const hiddenItems = container.querySelectorAll('.hidden-item');
    if (hiddenItems.length > 0) {
        // Reveal a batch of 6 or all if fewer
        const batch = Array.from(hiddenItems).slice(0, 20);
        batch.forEach(item => {
            item.classList.remove('hidden-item');
            item.style.display = 'flex';
        });

        // If no more hidden items, let the button know it might need to fetch next time
        if (container.querySelectorAll('.hidden-item').length === 0) {
            // We don't return early if we want it to fetch immediately on next click
            // but for better UX, we reveal first, then fetch on NEXT click.
            btn.innerText = "See More";
            btn.disabled = false;
            return;
        }
        btn.innerText = "See More";
        btn.disabled = false;
        return;
    }

    // Determine category and country from main-content data attributes
    const mainContent = document.querySelector('.main-content');
    let category = mainContent.getAttribute('data-category') || 'top_stories';
    const country = mainContent.getAttribute('data-country') || '';

    // Override if clicking on breaking news specifically
    if (selector.includes('breaking')) category = "breaking_news";

    // UX: Loading state
    btn.innerText = "Loading...";
    btn.disabled = true;
    try {
        // Use the container immediately before the button as the default target
        let targetContainer = container;
        const isHeadlines = selector.includes('intel-card');

        // Calculate current items based on the selector
        const currentItems = container.querySelectorAll(selector).length;
        // Retrieve active language if available (via URL or default)
        const urlParams = new URLSearchParams(window.location.search);
        let langQuery = urlParams.get('lang') || 'english';

        let fetchUrl = `/api/more-stories/${encodeURIComponent(category)}/${currentItems}?lang=${langQuery}`;
        if (country) {
            fetchUrl += `&country=${country}`;
        }

        const response = await fetch(fetchUrl);

        if (!response.ok) throw new Error("API Failure");
        const data = await response.json();

        if (data.stories && data.stories.length > 0) {
            data.stories.forEach((story, idx) => {
                const div = document.createElement('div');

                if (isHeadlines) {
                    // Formatting for Headlines (intel-card)
                    div.className = 'intel-card fade-in';
                    div.setAttribute('data-url', story.url);
                    div.setAttribute('data-id', story.id);
                    div.onclick = function () { if (window.handleCardClick) window.handleCardClick(this); else window.open(story.url, '_blank'); };

                    div.innerHTML = `
            < div class="intel-card-image" style = "background: linear-gradient(135deg, #1e293b, #0f172a);" >
                <button class="save-btn" onclick="saveArticle(event, '${story.id}')">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                        <path d="M17 3H7c-1.1 0-2 .9-2 2v16l7-3 7 3V5c0-1.1-.9-2-2-2z" />
                    </svg>
                </button>
                    </div >
                    <div class="intel-header">
                        <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                            <span style="color:var(--accent-blue); font-size:0.8rem; font-weight:700;">${window.UI_DICT ? window.UI_DICT.verified || 'VERIFIED:' : 'VERIFIED:'} ${story.source_name}</span>
                            <span style="color:var(--text-secondary); font-size:0.8rem;">${story.bias === 'Neutral' ? (window.UI_DICT ? window.UI_DICT.neutral || 'Neutral' : 'Neutral') : (story.bias || (window.UI_DICT ? window.UI_DICT.neutral || 'Neutral' : 'Neutral'))}</span>
                        </div>
                        <h3 class="intel-title">${story.title}</h3>
                        <div style="display:flex; gap:0.5rem; flex-wrap:wrap; margin-bottom:1rem;">
                            ${(story.tags || []).slice(0, 3).map(tag => `<span style="background:rgba(255,255,255,0.1); color:white; padding:4px 10px; border-radius:4px; font-size:0.7rem; font-weight:700; text-transform:uppercase;">${tag}</span>`).join('')}
                        </div>
                    </div>
                    <div class="intel-section">
                        <ul>
                            ${(story.bullets || []).slice(0, 3).map(b => `<li>${b}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="intel-section" style="background:rgba(59, 130, 246, 0.05); border-left:3px solid var(--accent-blue);">
                        <h4 style="color:var(--accent-blue);">${window.UI_DICT ? window.UI_DICT.who_affected || '👥 Who is Affected' : '👥 Who is Affected'}</h4>
                        <p style="font-size:0.9rem; color:#cbd5e1;">${story.affected || 'General Public'}</p>
                    </div>
                    <div class="intel-section" style="background:rgba(251, 188, 4, 0.05); border-left:3px solid var(--accent-gold);">
                        <h4 style="color:var(--accent-gold);">${window.UI_DICT ? window.UI_DICT.why_matters || '⚡ Why It Matters' : '⚡ Why It Matters'}</h4>
                        <p style="font-size:0.9rem; color:#cbd5e1;">${story.why || 'Significant development.'}</p>
                    </div>
                    <div class="intel-footer">
                        <span style="font-size:0.8rem; color:var(--text-secondary);">${window.UI_DICT ? window.UI_DICT.ai_analysis || 'AI Analysis' : 'AI Analysis'} • ${story.time_ago || (window.UI_DICT ? window.UI_DICT.just_now || 'Just Now' : 'Just Now')}</span>
                    </div>
        `;
                } else {
                    // Formatting for Trending (trend-card)
                    div.className = 'trend-card fade-in';
                    div.setAttribute('data-url', story.url);
                    div.setAttribute('data-id', story.id);
                    div.onclick = function () { if (window.handleCardClick) window.handleCardClick(this); else window.open(story.url, '_blank'); };

                    div.innerHTML = `
                    <span class="trend-badge">${window.UI_DICT ? window.UI_DICT.more_intel || 'MORE INTEL' : 'MORE INTEL'}</span>
                    <h4 style="margin:0 0 0.5rem 0; font-size:1rem; color: var(--text-primary); font-weight: 600;">${story.title}</h4>
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-secondary); margin-top: 1rem;">
                        <span>${story.source_name}</span>
                        <span>${window.UI_DICT ? window.UI_DICT.analysis || 'ANALYSIS' : 'ANALYSIS'}</span>
                    </div>
        `;
                }
                targetContainer.appendChild(div);
            });

            // Update Button State
            if (data.has_more) {
                btn.innerText = "See More";
                btn.disabled = false;
            } else {
                btn.innerText = "No More Stories";
                btn.style.opacity = "0.5";
                btn.disabled = true;
            }
        } else {
            btn.innerText = "No More Stories";
            btn.style.opacity = "0.5";
            btn.disabled = true;
        }
    } catch (e) {
        console.error("Error fetching more stories", e);
        btn.innerText = "Error - Retry";
        btn.disabled = false;
    }
}

function expandBrief(btn) {
    const grid = document.getElementById('brief-grid');
    if (!grid) return;
    const hiddenItems = grid.querySelectorAll('.hidden-item');
    hiddenItems.forEach(item => {
        item.classList.remove('hidden-item');
        item.style.display = 'flex';
    });
    btn.style.display = 'none';
}
window.expandBrief = expandBrief;

// ===== DARK/LIGHT MODE TOGGLE =====
function initializeThemeToggle() {
    // Check for saved theme preference or default to dark
    const currentTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);

    // Guard: Don't add if already exists
    if (document.getElementById('theme-toggle')) return;

    // Create toggle button
    const themeToggle = document.createElement('button');
    themeToggle.id = 'theme-toggle';
    themeToggle.className = 'theme-toggle-btn';
    themeToggle.setAttribute('aria-label', 'Toggle theme');
    themeToggle.innerHTML = currentTheme === 'dark'
        ? `<svg viewBox = "0 0 24 24" width = "20" height = "20" fill = "currentColor" >
            <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
           </svg > `
        : `<svg viewBox = "0 0 24 24" width = "20" height = "20" fill = "currentColor" >
            <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
           </svg > `;

    themeToggle.onclick = function () {
        const theme = document.documentElement.getAttribute('data-theme');
        const newTheme = theme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        // Update icon
        themeToggle.innerHTML = newTheme === 'dark'
            ? `<svg viewBox = "0 0 24 24" width = "20" height = "20" fill = "currentColor" >
            <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
               </svg > `
            : `<svg viewBox = "0 0 24 24" width = "20" height = "20" fill = "currentColor" >
            <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
               </svg > `;
    };

    // Add to header-right
    const headerRight = document.querySelector('.header-right');
    if (headerRight) {
        headerRight.insertBefore(themeToggle, document.getElementById('mobile-menu-btn'));
    }
}

// ===== BREAKING NEWS AUTO-REFRESH =====
function initializeBreakingNewsRefresh() {
    // Refresh breaking news every 5 minutes
    setInterval(async () => {
        try {
            const mainContent = document.querySelector('.main-content');
            const country = mainContent ? mainContent.getAttribute('data-country') : '';
            const response = await fetch(`/api/breaking-news${country ? '?country=' + country : ''}`);
            if (response.ok) {
                const data = await response.json();
                updateBreakingNewsSection(data.breaking_news);
            }
        } catch (e) {
            console.error('Failed to refresh breaking news:', e);
        }
    }, 15 * 60 * 1000); // 15 minutes (Synced with news cycle)
}

function updateBreakingNewsSection(breakingNews) {
    const section = document.getElementById('breaking-news') || document.querySelector('.breaking-container');
    if (!section || !breakingNews || breakingNews.length === 0) return;

    const itemsContainer = section.querySelector('.breaking-items');
    if (!itemsContainer) return;

    // Build new HTML for breaking cards to match dashboard.html structure
    const newCardsHtml = breakingNews.slice(0, 100).map((item, index) => {
        const headline = item.headline || item.title || "";
        const fallback = getCategoryFallback('breaking', headline, index);
        const imgUrl = item.image_url || fallback;
        const isHidden = index >= 6 ? 'hidden-item' : '';
        const displayStyle = index >= 6 ? 'display: none;' : '';
        const safeHeadline = headline.replace(/'/g, "\\'");

        return `
            <div class="breaking-card-emergency ${isHidden}"
             onclick="window.open('${item.url || '#'}', '_blank')"
             style="${displayStyle}">
            <div class="breaking-badge">${window.UI_DICT ? window.UI_DICT.breaking_news || 'BREAKING NEWS' : 'BREAKING NEWS'}</div>
            
            <div class="breaking-img-top" style="background-image: url('${imgUrl}');">
                 <img src="${item.image_url || '#'}" style="display:none;" 
                      onerror="this.parentElement.style.backgroundImage = 'url(' + getCategoryFallback('breaking', '${safeHeadline}', ${index}) + ')'">
            </div>

            <h3 class="breaking-headline">${headline}</h3>
            <div class="breaking-section">
                <div class="breaking-subhead">${window.UI_DICT ? window.UI_DICT.what_happened || '📌 What Just Happened:' : '📌 What Just Happened:'}</div>
                <ul class="breaking-bullets">
                    <li>${item.summary || item.headline || item.title}</li>
                </ul>
            </div>

            <div class="breaking-impact-box">
                <div class="breaking-subhead" style="color:#b45309;">${window.UI_DICT ? window.UI_DICT.why_this_matters || '⚡ Why This Matters:' : '⚡ Why This Matters:'}</div>
                <p>${item.why || item.why_matters || (window.UI_DICT ? window.UI_DICT.significant_dev_req || "Significant development requiring immediate attention." : "Significant development requiring immediate attention.")}</p>
            </div>

            <div class="breaking-footer">
                <span>🔒 ${item.confidence || (window.UI_DICT ? window.UI_DICT.high_confidence || 'High Confidence' : 'High Confidence')}</span>
                <span>⏱ ${item.time_ago || (window.UI_DICT ? window.UI_DICT.just_now || 'Just now' : 'Just now')}</span>
            </div>
        </div >
            `}).join('');

    itemsContainer.innerHTML = newCardsHtml;
    console.log(`Live Update: ${breakingNews.length} breaking stories refreshed.`);
}

// ===== UTILITY FUNCTIONS =====
let currentModalArticleId = null;

async function handleCardClick(card) {
    const id = card.dataset.id;
    const url = card.dataset.url;
    if (!id || !url) return;

    // Track history in background
    trackHistory(id);

    // Redirect directly
    if (url && url !== '#') {
        window.open(url, '_blank');
    }
}

async function openArticleModal(id) {
    const modal = document.getElementById('article-modal');
    if (!modal) return;

    currentModalArticleId = id;

    // Show modal loading state
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    try {
        const res = await fetch(`/ api / article / ${id} `);
        if (!res.ok) throw new Error("Artifact not found");

        const data = await res.json();

        // Populate Modal
        document.getElementById('modal-title').innerText = data.title || window.UI_DICT.intelligence_artifact || "Intelligence Artifact";
        const heroImg = document.getElementById('modal-image');
        if (heroImg) heroImg.style.backgroundImage = `url('${data.image_url}')`;

        const sourceBadge = document.getElementById('modal-source');
        if (sourceBadge) sourceBadge.innerText = `${window.UI_DICT.verified || 'VERIFIED:'} ${data.source_name || window.UI_DICT.global_source || 'Global Source'} `;

        const timeText = document.getElementById('modal-time');
        if (timeText) timeText.innerText = data.time_ago || window.UI_DICT.recently || 'Recently';

        const biasBadge = document.getElementById('modal-bias');
        if (biasBadge) biasBadge.innerText = data.bias_rating || window.UI_DICT.neutral || 'Neutral';

        const affectedText = document.getElementById('modal-affected');
        if (affectedText) affectedText.innerText = data.who_is_affected || window.UI_DICT.analyzing_demo || 'Analyzing global implications...';

        const whyText = document.getElementById('modal-why');
        if (whyText) whyText.innerText = data.why_it_matters || window.UI_DICT.evaluating_strat || 'Evaluating strategic significance.';

        const sourceLink = document.getElementById('modal-source-link');
        if (sourceLink) sourceLink.href = data.url || '#';

        // Bullets
        const bulletList = document.getElementById('modal-bullets');
        if (bulletList) {
            bulletList.innerHTML = '';
            const bullets = data.summary_bullets;
            if (bullets && Array.isArray(bullets)) {
                bullets.forEach(bullet => {
                    const li = document.createElement('li');
                    li.innerText = bullet;
                    bulletList.appendChild(li);
                });
            } else if (typeof bullets === 'string' && bullets.startsWith('[')) {
                // Handle stringified JSON if needed
                try {
                    JSON.parse(bullets).forEach(bullet => {
                        const li = document.createElement('li');
                        li.innerText = bullet;
                        bulletList.appendChild(li);
                    });
                } catch (e) { }
            }
        }

        // Tags
        const tagContainer = document.getElementById('modal-tags');
        if (tagContainer) {
            tagContainer.innerHTML = '';
            const tags = data.impact_tags;
            if (tags && Array.isArray(tags)) {
                tags.forEach(tag => {
                    const span = document.createElement('span');
                    span.className = 'modal-tag-pill';
                    span.innerText = tag;
                    tagContainer.appendChild(span);
                });
            }
        }

    } catch (e) {
        console.error("Failed to load article details", e);
        // Fallback: If we fail to fetch, just open the URL if we can find it
        const card = document.querySelector(`.intel - card[data - id="${id}"]`);
        if (card && card.dataset.url && card.dataset.url !== '#') {
            window.open(card.dataset.url, '_blank');
        } else {
            alert("This intelligence artifact is currently being re-indexed. Please try again in a few moments.");
        }
        closeArticleModal();
    }
}

function closeArticleModal() {
    const modal = document.getElementById('article-modal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
    currentModalArticleId = null;
}

async function saveArticleModal() {
    if (!currentModalArticleId) return;

    const user = firebase.auth().currentUser;
    if (!user) {
        alert("Identification required. Please login to save intelligence.");
        return;
    }

    try {
        const res = await fetch('/api/retention/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                firebase_uid: user.uid,
                news_id: parseInt(currentModalArticleId)
            })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert("Intelligence artifact archived successfully.");
        } else {
            alert("Artifact already archived in your terminal.");
        }
    } catch (e) {
        console.error("Archive failure", e);
    }
}

async function trackHistory(newsId) {
    const uid = (firebase.auth().currentUser ? firebase.auth().currentUser.uid : null) || localStorage.getItem('user_uid');
    if (!uid || !newsId) return;

    try {
        await fetch('/api/retention/history', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                firebase_uid: uid,
                news_id: parseInt(newsId)
            })
        });
    } catch (e) {
        console.error("History track failed", e);
    }
}

async function shareArticle(event, id, title, url) {
    if (event) event.stopPropagation();
    const shareData = {
        title: decodeURIComponent(title),
        text: `Check out this intelligence artifact: ${decodeURIComponent(title)}`,
        url: url
    };

    if (navigator.share) {
        try {
            await navigator.share(shareData);
        } catch (err) {
            console.log('Share failed:', err);
            // Fallback to clipboard
            copyToClipboard(url);
        }
    } else {
        copyToClipboard(url);
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert("Link copied to clipboard!");
    }).catch(err => {
        console.error('Could not copy text: ', err);
    });
}

function closePhoneModal() {
    const modal = document.getElementById('phone-collection-modal');
    if (modal) modal.style.display = 'none';
    document.body.style.overflow = '';
}

async function trackTopic(event, newsId, title) {
    if (event) event.stopPropagation();
    
    let uid = null;
    const fbUser = firebase.auth().currentUser;
    if (fbUser) {
        uid = fbUser.uid;
    } else {
        uid = localStorage.getItem('user_uid');
    }

    if (!uid) {
        alert("Identification required to track intelligence. Please sign in.");
        return;
    }

    try {
        // 1. Check if user already has a phone number
        const statusRes = await fetch(`/api/user/status?firebase_uid=${uid}`);
        const statusData = await statusRes.json();
        
        // Assume backend returns user object or phone status
        // I'll update the /api/user/status endpoint to return 'phone' as well
        if (!statusData.phone) {
            // Show modal to collect phone
            const modal = document.getElementById('phone-collection-modal');
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
            
            const confirmBtn = document.getElementById('confirm-phone-btn');
            confirmBtn.onclick = async () => {
                const phoneInput = document.getElementById('tracking-phone-input').value;
                if (!phoneInput || !phoneInput.includes('+')) {
                    alert("Please enter a valid phone number with country code (e.g. +91...)");
                    return;
                }
                
                confirmBtn.innerText = "WAIT...";
                confirmBtn.disabled = true;
                
                try {
                    // Update phone first
                    await fetch('/api/user/update_phone', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ firebase_uid: uid, phone: phoneInput })
                    });
                    
                    // Then track topic
                    await executeTrackRequest(uid, newsId, title);
                    closePhoneModal();
                } catch (e) {
                    alert("Failed to update phone strategy.");
                } finally {
                    confirmBtn.innerText = "START TRACKING";
                    confirmBtn.disabled = false;
                }
            };
            return;
        }

        // Already has phone, just track
        await executeTrackRequest(uid, newsId, title);

    } catch (e) {
        console.error("Track failed", e);
    }
}

async function executeTrackRequest(uid, newsId, title) {
    const keywords = [decodeURIComponent(title)];
    // Extract keywords if title is long? Simple for now.
    
    const res = await fetch('/api/user/track_topic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            firebase_uid: uid,
            news_id: parseInt(newsId),
            keywords: keywords
        })
    });
    const data = await res.json();
    if (data.status === 'success') {
        alert("Topic tracking activated for 30 days. SMS alerts enabled!");
    }
}

window.closePhoneModal = closePhoneModal;

async function saveArticle(event, newsId) {
    event.stopPropagation(); // Prevent card click
    const user = firebase.auth().currentUser;
    if (!user) {
        alert("Please login to save articles.");
        return;
    }

    const btn = event.currentTarget;
    btn.classList.add('saving'); // Optional animation class

    try {
        const res = await fetch('/api/retention/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                firebase_uid: user.uid,
                news_id: parseInt(newsId)
            })
        });
        const data = await res.json();
        if (data.status === 'success') {
            alert("Article saved!");
            btn.style.color = 'var(--accent-gold)';
        } else if (data.status === 'already_saved') {
            alert("Already saved!");
        }
    } catch (e) {
        console.error("Save failed", e);
        alert("Failed to save.");
    }
}

// Export to window for inline onclicks
window.handleCardClick = handleCardClick;
window.saveArticleModal = saveArticleModal;
window.saveArticle = saveArticle;
window.shareArticle = shareArticle;
window.trackTopic = trackTopic;

// ===== INITIALIZE ON PAGE LOAD =====
document.addEventListener('DOMContentLoaded', function () {
    initializeSeeMore();
    initializeThemeToggle();
    initializeBreakingNewsRefresh();

    // Twilio Session Handling: Check for UID in URL from login redirect
    const urlParams = new URLSearchParams(window.location.search);
    const urlUid = urlParams.get('uid');
    if (urlUid) {
        localStorage.setItem('user_uid', urlUid);
        console.log("Twilio Session Activated for UID:", urlUid);
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    console.log('Dashboard enhancements initialized v4.2');
});


// ===== DUAL AUTO-SCROLL LOGIC =====

function initBreakingLayout() {
    initMainCarousel();
    initSideTicker();
}

// 1. Main Carousel (Items 0-6)
function initMainCarousel() {
    const slides = document.querySelectorAll('.breaking-slide');
    if (slides.length === 0) return;

    let currentIndex = 0;
    const intervalTime = 3000; // 3 seconds

    setInterval(() => {
        // Remove active from current
        slides[currentIndex].classList.remove('active');

        // Next index
        currentIndex = (currentIndex + 1) % slides.length;

        // Add active to next
        slides[currentIndex].classList.add('active');
    }, intervalTime);
}

// 2. Side Slider (Items 7-27) - Single View Auto-Cycle
function initSideTicker() {
    const slides = document.querySelectorAll('.side-slide-item');
    if (slides.length === 0) {
        console.warn('Side Slider: No slides found.');
        return;
    }
    console.log(`Side Slider: Found ${slides.length} slides.Starting cycle.`);

    let currentIndex = 0;

    // Cycle every 3 seconds
    setInterval(() => {
        // Remove active from current
        slides[currentIndex].classList.remove('active');

        // Next index
        currentIndex = (currentIndex + 1) % slides.length;

        // Add active to next
        slides[currentIndex].classList.add('active');
        // console.log('Side Slider: Switched to slide', currentIndex);
    }, 3000);
}

// 3. See More Expansion
function expandBreakingNews() {
    const grid = document.getElementById('breaking-expansion');
    const btn = document.getElementById('breaking-see-more');

    if (grid) {
        grid.style.display = 'grid'; // Show the grid
        // Trigger reflow for fade-in
        void grid.offsetWidth;

        // Add visible class to children for animation if needed
        const cards = grid.querySelectorAll('.breaking-mini-card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 50);
        });
    }

    if (btn) btn.style.display = 'none'; // Hide button after click
}

// ===== MARKET & WEATHER LOGIC =====
function initializeTicker() {
    const ticker = document.getElementById('market-ticker');
    if (!ticker) return;

    // Clone ticker items for seamless loop
    const items = ticker.innerHTML;
    ticker.innerHTML = items + items + items; // Triple for safety in wide screens
}

function initializeWeather() {
    const weatherTemp = document.getElementById('weather-temp');
    if (!weatherTemp) return;

    // Localized base temperatures
    const countryTemps = {
        'USA': 55, 'UK': 42, 'China': 48, 'Japan': 45, 'India': 82,
        'Russia': 12, 'Germany': 38, 'France': 46, 'Australia': 78, 'Global': 65
    };

    const loc = document.querySelector('.weather-loc').innerText || 'Global';
    const base = countryTemps[loc] || 65;
    const vari = Math.floor(Math.random() * 5) - 2;
    weatherTemp.innerText = `${base + vari}°F`;
}

// SIDEBAR DISMISSAL
function dismissSidebar(id) {
    const sidebar = document.getElementById(id);
    if (sidebar) {
        sidebar.style.transform = 'translateY(-50%) scale(0.9)';
        sidebar.style.opacity = '0';
        setTimeout(() => {
            sidebar.style.display = 'none';
        }, 300);
    }
}
window.dismissSidebar = dismissSidebar;

// MOBILE AD DISMISSAL
function dismissMobileAd() {
    const overlay = document.getElementById('mobile-ad-overlay');
    if (overlay) {
        overlay.style.opacity = '0';
        overlay.style.pointerEvents = 'none';
        setTimeout(() => {
            overlay.style.display = 'none';
        }, 300);
    }
}
window.dismissMobileAd = dismissMobileAd;

// Initialize on Load
document.addEventListener('DOMContentLoaded', () => {
    initBreakingLayout();
    initializeTicker();
    initializeWeather();
    if (window.initializeSeeMore) window.initializeSeeMore();

    // Click outside to close language menu
    document.addEventListener('click', (e) => {
        const langSwitcher = document.getElementById('global-lang-switcher');
        const searchInput = document.getElementById('header-lang-search');
        if (langSwitcher && !langSwitcher.contains(e.target)) {
            langSwitcher.classList.remove('active');
            if (searchInput) searchInput.value = '';
            filterHeaderLanguages();
        }
    });

    // Mobile nav overlay click outside
    document.addEventListener('click', (e) => {
        const mobileMenu = document.getElementById('mobile-nav-overlay');
        const trigger = document.getElementById('mobile-nav-trigger');
        if (mobileMenu && trigger && !mobileMenu.contains(e.target) && !trigger.contains(e.target)) {
            mobileMenu.classList.remove('active');
        }
    });
});

window.toggleHeaderLangMenu = function() {
    const switcher = document.getElementById('global-lang-switcher');
    if (switcher) switcher.classList.toggle('active');
};

window.filterHeaderLanguages = function() {
    const input = document.getElementById('header-lang-search');
    const filter = input ? input.value.toLowerCase() : '';
    const menuList = document.getElementById('header-lang-list');
    if (!menuList) return;
    const items = menuList.getElementsByTagName('a');
    for (let i = 0; i < items.length; i++) {
        const txtValue = items[i].getAttribute('data-name');
        if (txtValue && txtValue.indexOf(filter) > -1) {
            items[i].style.display = "";
        } else {
            items[i].style.display = "none";
        }
    }
};

window.changeLang = function(langStr) {
    const url = new URL(window.location.href);
    if (langStr && langStr !== 'english') {
        url.searchParams.set('lang', langStr);
    } else {
        url.searchParams.delete('lang');
    }
    window.location.href = url.toString();
};

window.toggleMobileMenu = function() {
    const nav = document.getElementById('mobile-nav-overlay');
    if (nav) nav.classList.toggle('active');
};

// ===== TOPIC TRACKING (SMS NOTIFICATIONS) =====
async function trackTopic(event, articleId, title) {
    if (event) event.stopPropagation();
    
    // Check if user is logged in
    const userUid = localStorage.getItem('user_uid');
    if (!userUid) {
        alert("Please login via Mobile/OTP first to enable SMS tracking.");
        return;
    }

    const btn = event.currentTarget;
    const originalContent = btn.innerHTML;
    btn.innerHTML = '<span class="spinner" style="display:inline-block; width:12px; height:12px; border:2px solid white; border-top-color:transparent; border-radius:50%; animation:spin 1s linear infinite;"></span>';
    btn.disabled = true;

    try {
        const response = await fetch('/api/track-topic', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                article_id: articleId,
                user_id: userUid,
                firebase_uid: userUid,
                language: 'english'
            })
        });

        const data = await response.json();
        if (data.status === 'success') {
            btn.style.background = '#10b981'; // Green
            btn.innerHTML = '✓ Tracked';
            alert("Topic Tracking Enabled! You'll receive SMS intel when related regional updates occur.");
        } else {
            throw new Error(data.message || "Tracking failed");
        }
    } catch (error) {
        console.error("Tracking failed:", error);
        if (btn) {
            btn.style.background = '#ef4444'; // Red
            btn.innerHTML = '! Error';
            setTimeout(() => {
                btn.innerHTML = originalContent;
                btn.style.background = '';
                btn.disabled = false;
            }, 3000);
        }
    }
}
window.trackTopic = trackTopic;

// ===== PROFILE & STREAK MANAGEMENT =====
function toggleProfileDropdown() {
    const menu = document.getElementById('profile-dropdown-menu');
    if (menu) {
        const isVisible = menu.style.display === 'block';
        menu.style.display = isVisible ? 'none' : 'block';
    }
}
window.toggleProfileDropdown = toggleProfileDropdown;

// Close dropdown on outside click
document.addEventListener('click', (e) => {
    const container = document.querySelector('.header-profile-container');
    const menu = document.getElementById('profile-dropdown-menu');
    if (container && menu && !container.contains(e.target)) {
        menu.style.display = 'none';
    }
});

async function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (file.size > 2 * 1024 * 1024) {
        alert("Image too large. Max 2MB allowed.");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    
    const user = firebase.auth().currentUser;
    if (!user) {
        alert("Please sign in to upload images.");
        return;
    }
    formData.append('firebase_uid', user.uid);

    try {
        const response = await fetch('/api/user/upload_profile_image', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.status === 'success') {
            updateProfileUI(data.image_url);
            alert("Profile image updated successfully!");
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error("Upload failed:", error);
        alert("Failed to upload image. Please try again.");
    }
}
window.handleImageUpload = handleImageUpload;

function updateProfileUI(imageUrl, displayName, email) {
    const headerImg = document.getElementById('header-profile-img');
    const dropdownImg = document.getElementById('dropdown-profile-img');
    const headerInitial = document.getElementById('header-profile-initial');
    const dropdownInitial = document.getElementById('dropdown-profile-initial');
    const nameDisplay = document.getElementById('user-display-name');
    const emailDisplay = document.getElementById('user-display-email');

    if (imageUrl) {
        if (headerImg) { headerImg.src = imageUrl; headerImg.style.display = 'block'; }
        if (dropdownImg) { dropdownImg.src = imageUrl; dropdownImg.style.display = 'block'; }
        if (headerInitial) headerInitial.style.display = 'none';
        if (dropdownInitial) dropdownInitial.style.display = 'none';
    } else if (displayName) {
        const initial = displayName.charAt(0).toUpperCase();
        if (headerInitial) { headerInitial.innerText = initial; headerInitial.style.display = 'flex'; }
        if (dropdownInitial) { dropdownInitial.innerText = initial; dropdownInitial.style.display = 'flex'; }
        if (headerImg) headerImg.style.display = 'none';
        if (dropdownImg) dropdownImg.style.display = 'none';
    }

    if (displayName && nameDisplay) nameDisplay.innerText = displayName;
    if (email && emailDisplay) emailDisplay.innerText = email;
}

// Sync Firebase Auth State with Profile UI
firebase.auth().onAuthStateChanged((user) => {
    if (user) {
        updateProfileUI(user.photoURL, user.displayName, user.email);
        localStorage.setItem('user_uid', user.uid);
        // Fetch streak from backend
        fetch(`/api/user/ping_streak`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ firebase_uid: user.uid })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                const badge = document.getElementById('streak-count-display');
                if (badge) badge.innerText = data.current_streak || 0;
            }
        }).catch(err => console.error("Streak sync error:", err));
    }
});

function handleSignOut() {
    firebase.auth().signOut().then(() => {
        localStorage.removeItem('user_uid');
        window.location.reload();
    });
}
window.handleSignOut = handleSignOut;

// ===== LANGUAGE SWITCHER HELPERS =====
function toggleHeaderLangMenu() {
    const switcher = document.getElementById('global-lang-switcher');
    if (switcher) {
        const menu = switcher.querySelector('.dropdown-menu');
        if (menu) {
            const isVisible = menu.style.display === 'block';
            menu.style.display = isVisible ? 'none' : 'block';
        }
    }
}
window.toggleHeaderLangMenu = toggleHeaderLangMenu;

function filterHeaderLanguages() {
    const input = document.getElementById('header-lang-search');
    const filter = input.value.toLowerCase();
    const items = document.querySelectorAll('#header-lang-list .lang-item');
    items.forEach(item => {
        const name = item.getAttribute('data-name');
        if (name.includes(filter)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}
window.filterHeaderLanguages = filterHeaderLanguages;

async function changeLang(lang) {
    console.log("Changing language to:", lang);
    const user = firebase.auth().currentUser;
    if (user) {
        try {
            await fetch('/api/user/language', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ firebase_uid: user.uid, language: lang })
            });
        } catch (e) { console.error("Lang save failed:", e); }
    }
    const url = new URL(window.location.href);
    url.searchParams.set('lang', lang);
    window.location.href = url.toString();
}
window.changeLang = changeLang;

// Close lang menu on outside click
document.addEventListener('click', (e) => {
    const switcher = document.getElementById('global-lang-switcher');
    if (switcher && !switcher.contains(e.target)) {
        const menu = switcher.querySelector('.dropdown-menu');
        if (menu) menu.style.display = 'none';
    }
});

// ===== CARD INTERACTION HELPERS =====
function openChatFromCard(event, articleId) {
    if (event) event.stopPropagation();
    const chatBtn = document.getElementById('ai-chat-btn');
    if (chatBtn) {
        chatBtn.click();
        window.currentChatContextId = articleId;
        console.log("Chat opened with context:", articleId);
    } else {
        alert("AI Chat module loading...");
    }
}
window.openChatFromCard = openChatFromCard;

async function requestUpdate(event, id) {
    if (event) event.stopPropagation();
    const btn = event.currentTarget || event.target;
    if (!btn) return;

    const originalContent = btn.innerHTML;
    btn.innerHTML = '<span class="spinner" style="display:inline-block; width:12px; height:12px; border:2px solid white; border-top-color:transparent; border-radius:50%; animation:spin 1s linear infinite;"></span>';
    btn.disabled = true;
    
    try {
        const res = await fetch(`/api/articles/${id}/update`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            btn.style.background = '#10b981';
            btn.innerHTML = '✓ Updated';
            setTimeout(() => { window.location.reload(); }, 1500);
        } else {
            throw new Error(data.error || "Update failed");
        }
    } catch (err) {
        console.error("Update request failed:", err);
        btn.style.background = '#ef4444';
        btn.innerHTML = 'Error';
        setTimeout(() => { btn.innerHTML = originalContent; btn.disabled = false; btn.style.background = ''; }, 3000);
    }
}
window.requestUpdate = requestUpdate;
