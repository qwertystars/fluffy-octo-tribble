/**
 * AI Code Generator - Frontend JavaScript
 * Handles WebSocket communication and UI interactions
 */

class CodeGeneratorApp {
    constructor() {
        this.ws = null;
        this.sessionId = this.generateSessionId();
        this.isConnected = false;
        this.messageQueue = [];

        // UI Elements
        this.chatContainer = document.getElementById('chatContainer');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendButton');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusText = document.getElementById('statusText');
        this.buttonText = document.getElementById('buttonText');
        this.buttonLoader = document.getElementById('buttonLoader');
        this.toolsCount = document.getElementById('toolsCount');

        this.initialize();
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    initialize() {
        // Load available tools
        this.loadTools();

        // Connect WebSocket
        this.connect();

        // Setup event listeners
        this.setupEventListeners();
    }

    async loadTools() {
        try {
            const response = await fetch('/api/tools');
            const data = await response.json();

            if (data.total) {
                this.toolsCount.textContent = `${data.total} tools available`;
            }
        } catch (error) {
            console.error('Failed to load tools:', error);
            this.toolsCount.textContent = 'Tools loading...';
        }
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.isConnected = true;
            this.updateConnectionStatus(true);
            this.showToast('Connected to AI Code Generator', 'success');

            // Send queued messages
            while (this.messageQueue.length > 0) {
                const message = this.messageQueue.shift();
                this.ws.send(JSON.stringify(message));
            }
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Failed to parse message:', error);
            }
        };

        this.ws.onclose = () => {
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.showToast('Disconnected. Reconnecting...', 'warning');

            // Attempt to reconnect after 2 seconds
            setTimeout(() => this.connect(), 2000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showToast('Connection error', 'error');
        };
    }

    updateConnectionStatus(connected) {
        if (connected) {
            this.statusIndicator.classList.add('connected');
            this.statusText.textContent = 'Connected';
        } else {
            this.statusIndicator.classList.remove('connected');
            this.statusText.textContent = 'Disconnected';
        }
    }

    setupEventListeners() {
        // Send button click
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Enter to send, Shift+Enter for new line
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        this.userInput.addEventListener('input', () => {
            this.userInput.style.height = 'auto';
            this.userInput.style.height = this.userInput.scrollHeight + 'px';
        });
    }

    sendMessage() {
        const message = this.userInput.value.trim();

        if (!message) {
            this.showToast('Please enter a message', 'warning');
            return;
        }

        // Display user message
        this.addMessage('user', message);

        // Send to server
        const payload = { message: message };

        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(payload));
        } else {
            this.messageQueue.push(payload);
            this.showToast('Message queued. Reconnecting...', 'warning');
        }

        // Clear input
        this.userInput.value = '';
        this.userInput.style.height = 'auto';

        // Show loading state
        this.setLoading(true);
    }

    handleMessage(data) {
        switch (data.type) {
            case 'response':
                this.addMessage('assistant', data.content);
                this.setLoading(false);
                break;

            case 'tool':
                this.addMessage('tool', data.content);
                break;

            case 'error':
                this.addMessage('error', data.content);
                this.setLoading(false);
                this.showToast('Error occurred', 'error');
                break;

            case 'system':
                this.addMessage('system', data.content);
                break;

            default:
                console.warn('Unknown message type:', data.type);
        }
    }

    addMessage(type, content) {
        // Remove welcome message if it exists
        const welcomeMessage = this.chatContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        // Add message header
        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';

        let icon = '';
        let label = '';

        switch (type) {
            case 'user':
                icon = '👤';
                label = 'You';
                break;
            case 'assistant':
                icon = '🤖';
                label = 'AI Assistant';
                break;
            case 'tool':
                icon = '🔧';
                label = 'Tool Execution';
                break;
            case 'error':
                icon = '❌';
                label = 'Error';
                break;
            case 'system':
                icon = 'ℹ️';
                label = 'System';
                break;
        }

        headerDiv.innerHTML = `<span>${icon}</span><span>${label}</span>`;

        // Add message content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;

        // Format code blocks (simple implementation)
        this.formatCodeBlocks(contentDiv);

        messageDiv.appendChild(headerDiv);
        messageDiv.appendChild(contentDiv);

        this.chatContainer.appendChild(messageDiv);

        // Scroll to bottom
        this.scrollToBottom();
    }

    formatCodeBlocks(contentDiv) {
        const content = contentDiv.textContent;

        // Simple code block detection
        const codeBlockPattern = /```(\w+)?\n([\s\S]*?)```/g;
        let match;
        let lastIndex = 0;
        const fragments = [];

        while ((match = codeBlockPattern.exec(content)) !== null) {
            // Add text before code block
            if (match.index > lastIndex) {
                fragments.push(document.createTextNode(content.substring(lastIndex, match.index)));
            }

            // Add code block
            const pre = document.createElement('pre');
            const code = document.createElement('code');
            code.textContent = match[2].trim();
            pre.appendChild(code);
            fragments.push(pre);

            lastIndex = match.index + match[0].length;
        }

        // Add remaining text
        if (lastIndex < content.length) {
            fragments.push(document.createTextNode(content.substring(lastIndex)));
        }

        // Replace content if we found code blocks
        if (fragments.length > 0) {
            contentDiv.textContent = '';
            fragments.forEach(fragment => contentDiv.appendChild(fragment));
        }
    }

    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    setLoading(loading) {
        if (loading) {
            this.sendButton.disabled = true;
            this.buttonText.classList.add('hidden');
            this.buttonLoader.classList.remove('hidden');
        } else {
            this.sendButton.disabled = false;
            this.buttonText.classList.remove('hidden');
            this.buttonLoader.classList.add('hidden');
        }
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        toastContainer.appendChild(toast);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'toastSlideIn 0.3s ease-out reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.app = new CodeGeneratorApp();
    });
} else {
    window.app = new CodeGeneratorApp();
}

// Expose sendMessage function for backward compatibility
function sendMessage() {
    if (window.app) {
        window.app.sendMessage();
    }
}
