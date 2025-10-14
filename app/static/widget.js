(function() {
    'use strict';

    // Get bot ID from script tag
    const currentScript = document.currentScript;
    const botId = currentScript.getAttribute('data-bot-id');
    const apiBase = currentScript.src.replace('/static/widget.js', '');

    if (!botId) {
        console.error('AI Bot Widget: data-bot-id attribute is required');
        return;
    }

    // Create widget HTML
    const widgetHTML = `
        <div id="ai-bot-widget" style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        ">
            <div id="ai-bot-chat-window" style="
                display: none;
                position: absolute;
                bottom: 70px;
                right: 0;
                width: 380px;
                height: 600px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                flex-direction: column;
                overflow: hidden;
            ">
                <iframe
                    src="${apiBase}/chat/${botId}"
                    style="width: 100%; height: 100%; border: none;"
                ></iframe>
            </div>

            <button id="ai-bot-toggle" style="
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: var(--bot-color, #0066CC);
                border: none;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.2s, box-shadow 0.2s;
            ">
                <svg id="ai-bot-icon-chat" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <svg id="ai-bot-icon-close" style="display: none;" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        </div>
    `;

    // Inject widget into page
    document.addEventListener('DOMContentLoaded', function() {
        document.body.insertAdjacentHTML('beforeend', widgetHTML);

        const toggle = document.getElementById('ai-bot-toggle');
        const chatWindow = document.getElementById('ai-bot-chat-window');
        const iconChat = document.getElementById('ai-bot-icon-chat');
        const iconClose = document.getElementById('ai-bot-icon-close');

        // Load bot color
        fetch(`${apiBase}/api/bots/${botId}`)
            .then(res => res.json())
            .then(bot => {
                if (bot.widget_color) {
                    toggle.style.background = bot.widget_color;
                }
            })
            .catch(err => console.error('Failed to load bot config:', err));

        // Toggle chat window
        toggle.addEventListener('click', function() {
            const isOpen = chatWindow.style.display !== 'none';

            if (isOpen) {
                chatWindow.style.display = 'none';
                iconChat.style.display = 'block';
                iconClose.style.display = 'none';
            } else {
                chatWindow.style.display = 'flex';
                iconChat.style.display = 'none';
                iconClose.style.display = 'block';
            }
        });

        // Hover effect
        toggle.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
            this.style.boxShadow = '0 6px 16px rgba(0,0,0,0.2)';
        });

        toggle.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        });
    });
})();
