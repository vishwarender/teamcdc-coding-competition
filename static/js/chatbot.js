// Chatbot functionality for the Coding Competition website

document.addEventListener('DOMContentLoaded', function() {
    // Create chatbot elements if they don't exist
    if (!document.querySelector('.chat-container')) {
        createChatbotElements();
    }

    // Toggle chatbot visibility
    const chatToggle = document.querySelector('.chat-toggle');
    const chatContainer = document.querySelector('.chat-container');
    const closeChat = document.querySelector('.chat-close');

    if (chatToggle && chatContainer) {
        chatToggle.addEventListener('click', function() {
            chatContainer.classList.toggle('active');
            // Focus on input field when opened
            if (chatContainer.classList.contains('active')) {
                document.querySelector('.chat-input').focus();
            }
        });
    }

    if (closeChat) {
        closeChat.addEventListener('click', function() {
            chatContainer.classList.remove('active');
        });
    }

    // Handle sending messages
    const chatForm = document.querySelector('.chat-form');
    const chatInput = document.querySelector('.chat-input');
    const chatBody = document.querySelector('.chat-body');

    if (chatForm && chatInput && chatBody) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const message = chatInput.value.trim();
            if (message) {
                // Add user message to chat
                addMessage(message, 'user');
                chatInput.value = '';
                
                // Show typing indicator
                showTypingIndicator();
                
                // Send message to server
                sendMessage(message);
            }
        });
    }

    // Initialize with a welcome message
    setTimeout(function() {
        if (chatBody && chatBody.children.length === 0) {
            addMessage("👋 Hi there! I'm your coding competition assistant. How can I help you today?", 'bot');
        }
    }, 1000);
});

function createChatbotElements() {
    // Create chat toggle button
    const chatToggle = document.createElement('div');
    chatToggle.className = 'chat-toggle';
    chatToggle.innerHTML = '<i class="fas fa-comment-dots"></i>';
    
    // Create chat container
    const chatContainer = document.createElement('div');
    chatContainer.className = 'chat-container';
    chatContainer.innerHTML = `
        <div class="chat-header">
            <div>BCG Coding Competition Support</div>
            <button class="chat-close"><i class="fas fa-times"></i></button>
        </div>
        <div class="chat-body"></div>
        <div class="chat-footer">
            <form class="chat-form">
                <input type="text" class="chat-input" placeholder="Type your question here...">
                <button type="submit" class="chat-send"><i class="fas fa-paper-plane"></i></button>
            </form>
        </div>
    `;
    
    // Append to document
    document.body.appendChild(chatToggle);
    document.body.appendChild(chatContainer);
}

function addMessage(message, sender) {
    const chatBody = document.querySelector('.chat-body');
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${sender}`;
    messageElement.textContent = message;
    chatBody.appendChild(messageElement);
    
    // Scroll to bottom
    chatBody.scrollTop = chatBody.scrollHeight;
}

function showTypingIndicator() {
    const chatBody = document.querySelector('.chat-body');
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'chat-message bot typing-indicator';
    typingIndicator.innerHTML = '<span>.</span><span>.</span><span>.</span>';
    chatBody.appendChild(typingIndicator);
    
    // Scroll to bottom
    chatBody.scrollTop = chatBody.scrollHeight;
    
    return typingIndicator;
}

function removeTypingIndicator() {
    const typingIndicator = document.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function sendMessage(message) {
    // Get common responses based on keywords
    const responses = {
        'register': 'You can register for the competition by clicking the "Register" button in the navigation menu. Make sure to have your details ready!',
        'deadline': 'The submission deadline is December 31, 2025. Be sure to submit your project before then!',
        'rules': 'You can read the competition rules by clicking on the "Rules" button in the navigation menu.',
        'team': 'Teams can have 1-3 members depending on your grade level. Grades 6-8 can have up to 2 members, while grades 9-10 can have up to 3 members.',
        'submit': 'To submit your project, click on the "Submit Project" button in the navigation menu. You\'ll need to upload your code and optional presentation.',
        'prize': 'Winners will receive awards for 1st, 2nd, and 3rd places in each grade group. Special awards may also be given for Best UI Design or Best Innovation.',
        'help': 'I can help with registration, submission, rules clarification, and general information about the competition. Just ask me a question!'
    };

    // Simulate network delay
    setTimeout(function() {
        removeTypingIndicator();
        
        // Check for keyword matches
        let botResponse = 'I\'m not sure I understand. Could you try rephrasing your question? You can ask about registration, submission, rules, deadlines, or teams.';
        
        for (const [keyword, response] of Object.entries(responses)) {
            if (message.toLowerCase().includes(keyword)) {
                botResponse = response;
                break;
            }
        }
        
        // Add bot message to chat
        addMessage(botResponse, 'bot');
        
    }, 1500);
}