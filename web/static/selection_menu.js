// Text Selection Menu - Monica AI-like functionality
// Provides context menu for selected text with AI features

class TextSelectionMenu {
    constructor() {
        this.menu = null;
        this.selectedText = '';
        this.init();
    }

    init() {
        // Create menu element
        this.createMenu();

        // Add event listeners
        document.addEventListener('mouseup', (e) => this.handleTextSelection(e));
        document.addEventListener('mousedown', (e) => this.handleClickOutside(e));

        // Hide menu on scroll
        window.addEventListener('scroll', () => this.hideMenu());
    }

    createMenu() {
        this.menu = document.createElement('div');
        this.menu.id = 'text-selection-menu';
        this.menu.className = 'selection-menu';
        this.menu.innerHTML = `
            <button class="menu-action" data-action="note" title="Create Note">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
                <span>Note</span>
            </button>
            <button class="menu-action" data-action="search" title="Google Search">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                </svg>
                <span>Search</span>
            </button>
            <button class="menu-action" data-action="ai" title="Ask AI">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
                </svg>
                <span>Ask AI</span>
            </button>
            <button class="menu-action" data-action="copy" title="Copy">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
                <span>Copy</span>
            </button>
            <button class="menu-action" data-action="share" title="Share">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="18" cy="5" r="3"></circle>
                    <circle cx="6" cy="12" r="3"></circle>
                    <circle cx="18" cy="19" r="3"></circle>
                    <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                    <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
                </svg>
                <span>Share</span>
            </button>
        `;

        document.body.appendChild(this.menu);

        // Add action listeners
        this.menu.querySelectorAll('.menu-action').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                this.handleAction(action);
            });
        });
    }

    handleTextSelection(e) {
        const selection = window.getSelection();
        const text = selection.toString().trim();

        if (text.length > 0) {
            this.selectedText = text;
            this.showMenu(e.pageX, e.pageY);
        } else {
            this.hideMenu();
        }
    }

    showMenu(x, y) {
        this.menu.style.display = 'flex';

        // Position menu near cursor
        const menuWidth = this.menu.offsetWidth;
        const menuHeight = this.menu.offsetHeight;
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;

        // Adjust position to keep menu in viewport
        let left = x - menuWidth / 2;
        let top = y - menuHeight - 10;

        if (left < 10) left = 10;
        if (left + menuWidth > windowWidth - 10) left = windowWidth - menuWidth - 10;
        if (top < 10) top = y + 20;

        this.menu.style.left = `${left}px`;
        this.menu.style.top = `${top}px`;

        // Animate in
        setTimeout(() => {
            this.menu.classList.add('visible');
        }, 10);
    }

    hideMenu() {
        this.menu.classList.remove('visible');
        setTimeout(() => {
            this.menu.style.display = 'none';
        }, 200);
    }

    handleClickOutside(e) {
        if (!this.menu.contains(e.target)) {
            this.hideMenu();
        }
    }

    async handleAction(action) {
        switch (action) {
            case 'note':
                this.createNote();
                break;
            case 'search':
                this.googleSearch();
                break;
            case 'ai':
                this.askAI();
                break;
            case 'copy':
                this.copyText();
                break;
            case 'share':
                this.shareText();
                break;
        }
        this.hideMenu();
    }

    createNote() {
        // Save note to localStorage
        const notes = JSON.parse(localStorage.getItem('newsNotes') || '[]');
        const note = {
            id: Date.now(),
            text: this.selectedText,
            timestamp: new Date().toISOString(),
            url: window.location.href
        };
        notes.unshift(note);
        localStorage.setItem('newsNotes', JSON.stringify(notes));

        // Show notification
        this.showNotification('📝 Note saved!');

        // Optional: Send to backend
        fetch('/api/save-note', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(note)
        }).catch(err => console.log('Note saved locally only'));
    }

    googleSearch() {
        const query = encodeURIComponent(this.selectedText);
        window.open(`https://www.google.com/search?q=${query}`, '_blank');
    }

    async askAI() {
        // Open chat widget and populate with query
        const chatWidget = document.getElementById('chat-widget');
        const chatInput = document.getElementById('chat-input');

        if (chatWidget && chatInput) {
            chatWidget.classList.remove('chat-closed');
            chatWidget.classList.add('chat-open');
            chatInput.value = `Explain: "${this.selectedText}"`;
            chatInput.focus();
        }
    }

    async copyText() {
        try {
            await navigator.clipboard.writeText(this.selectedText);
            this.showNotification('📋 Copied to clipboard!');
        } catch (err) {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = this.selectedText;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            this.showNotification('📋 Copied to clipboard!');
        }
    }

    async shareText() {
        const shareData = {
            title: 'News Intelligence',
            text: this.selectedText,
            url: window.location.href
        };

        if (navigator.share) {
            try {
                await navigator.share(shareData);
            } catch (err) {
                if (err.name !== 'AbortError') {
                    this.fallbackShare();
                }
            }
        } else {
            this.fallbackShare();
        }
    }

    fallbackShare() {
        // Copy link with selected text
        const shareUrl = `${window.location.href}#text=${encodeURIComponent(this.selectedText)}`;
        navigator.clipboard.writeText(shareUrl);
        this.showNotification('🔗 Share link copied!');
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'selection-notification';
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('visible');
        }, 10);

        setTimeout(() => {
            notification.classList.remove('visible');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 2000);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new TextSelectionMenu();
    });
} else {
    new TextSelectionMenu();
}
