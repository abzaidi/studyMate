class FlashMessageManager {
    constructor() {
        this.container = document.getElementById('flashMessageContainer');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'flashMessageContainer';
            this.container.className = 'flash-message-container';
            document.body.appendChild(this.container);
        }
        this.messageQueue = [];
        this.maxVisible = 3; // Maximum number of visible messages at once

        // Load Django messages on page load
        this.loadDjangoMessages();
    }

    // Load messages from Django's template
    loadDjangoMessages() {
        let messageContainer = document.getElementById("django-flash-messages");
        if (messageContainer) {
            let messages = messageContainer.querySelectorAll("div[data-type]");
            messages.forEach(msg => {
                let type = msg.getAttribute("data-type");
                let title = msg.getAttribute("data-title") || "Notification"; // Default title
                let text = msg.getAttribute("data-text");
                this.show(type, title, text);
            });
        }
    }
    // Create flash message element
    createMessage(type, title, message) {
        const messageId = 'flash-' + Date.now();
        const messageElement = document.createElement('div');
        messageElement.className = `flash-message flash-${type}`;
        messageElement.id = messageId;
        
        // Create icon based on type
        let iconSvg = '';
        switch(type) {
            case 'error':
                iconSvg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10-10-4.477 10-10 10zm-1-7v2h2v-2h-2zm0-8v6h2V7h-2z"/></svg>';
                break;
            case 'warning':
                iconSvg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm-1-7v2h2v-2h-2zm0-8v6h2V7h-2z"/></svg>';
                break;
            case 'info':
                iconSvg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10-10-4.477 10-10 10zm-1-11v6h2v-6h-2zm0-4v2h2V7h-2z"/></svg>';
                break;
            case 'success':
                iconSvg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm-1.177-7.86l-2.765-2.767L7 12.431l3.119 3.121a1 1 0 001.414 0l5.952-5.95-1.062-1.06-5.6 5.6z"/></svg>';
                break;
        }

        // Build message content
        messageElement.innerHTML = `
            <div class="flash-content">
                <div class="flash-icon">${iconSvg}</div>
                <div class="flash-text">
                    <strong>${title}</strong>
                    <div>${message}</div>
                </div>
            </div>
            <button class="flash-close" aria-label="Close">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
            </button>
        `;

        // Add close functionality
        const closeButton = messageElement.querySelector('.flash-close');
        closeButton.addEventListener('click', () => {
            this.closeMessage(messageId);
        });

        // Auto-dismiss after timeout (different by type)
        const timeouts = {
            error: 8000,
            warning: 6000,
            info: 5000,
            success: 5000
        };

        // Return the created message object
        return {
            element: messageElement,
            id: messageId,
            timeout: setTimeout(() => {
                this.closeMessage(messageId);
            }, timeouts[type] || 5000)
        };
    }

    // Show a message
    show(type, title, message) {
        const messageObj = this.createMessage(type, title, message);
        
        // Add to queue
        this.messageQueue.push(messageObj);
        
        // Update visible messages
        this.updateVisibleMessages();
        
        return messageObj.id;
    }

    // Update which messages are visible
    updateVisibleMessages() {
        // Display only the most recent messages up to maxVisible
        const visibleCount = Math.min(this.messageQueue.length, this.maxVisible);
        
        // Clear the container
        this.container.innerHTML = '';
        
        // Add the most recent messages
        for (let i = 0; i < visibleCount; i++) {
            this.container.appendChild(this.messageQueue[i].element);
        }
    }

    // Close a specific message
    closeMessage(id) {
        const index = this.messageQueue.findIndex(msg => msg.id === id);
        if (index !== -1) {
            const messageObj = this.messageQueue[index];
            
            // Add closing animation
            messageObj.element.classList.add('closing');
            
            // Clear timeout to prevent duplicate close calls
            clearTimeout(messageObj.timeout);
            
            // Remove after animation
            setTimeout(() => {
                // Remove from queue
                this.messageQueue.splice(index, 1);
                
                // Update visible messages
                this.updateVisibleMessages();
            }, 300); // Match the animation duration
        }
    }

    // Close all messages
    closeAll() {
        // Clear all timeouts
        this.messageQueue.forEach(msg => clearTimeout(msg.timeout));
        
        // Add closing animation to all messages
        const elements = document.querySelectorAll('.flash-message');
        elements.forEach(el => el.classList.add('closing'));
        
        // Clear after animation
        setTimeout(() => {
            this.messageQueue = [];
            this.container.innerHTML = '';
        }, 300);
    }
}

// Initialize the flash message manager
const flashManager = new FlashMessageManager();

// Function to show flash message manually
function showFlashMessage(type, title, message) {
    flashManager.show(type, title, message);
}
