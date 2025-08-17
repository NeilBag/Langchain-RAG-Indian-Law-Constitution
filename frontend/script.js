const API_BASE_URL = window.location.origin;

// Global variables for context management
let currentSessionId = null;
let conversationHistory = [];

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('fileInput').addEventListener('change', handleFileUpload);
    document.getElementById('messageInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Start a new conversation session
    startNewConversation();
});

// Handle file upload
async function handleFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    
    if (files.length === 0) return;
    
    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }
    
    showUploadStatus('Uploading and processing documents...', 'info');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/upload-documents`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showUploadStatus(`✅ ${result.message}`, 'success');
            addMessage('system', `Documents processed successfully: ${result.files_processed.join(', ')}`);
        } else {
            showUploadStatus(`❌ Error: ${result.error}`, 'error');
        }
    } catch (error) {
        showUploadStatus(`❌ Upload failed: ${error.message}`, 'error');
    }
    
    // Clear file input
    fileInput.value = '';
}

// Initialize with existing PDFs
async function initializeWithExistingPDFs() {
    showUploadStatus('Initializing with existing PDF files...', 'info');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/initialize-with-existing-pdfs`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showUploadStatus(`✅ ${result.message}`, 'success');
            if (result.files_processed && result.files_processed.length > 0) {
                addMessage('system', `Initialized with documents: ${result.files_processed.join(', ')}`);
            }
        } else {
            showUploadStatus(`❌ Error: ${result.error}`, 'error');
        }
    } catch (error) {
        showUploadStatus(`❌ Initialization failed: ${error.message}`, 'error');
    }
}

// Start new conversation
async function startNewConversation() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/new-conversation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            currentSessionId = result.session_id;
            conversationHistory = [];
            console.log('Started new conversation:', currentSessionId);
        }
    } catch (error) {
        console.error('Error starting new conversation:', error);
    }
}

// Send message with context awareness
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessage('user', message);
    messageInput.value = '';
    
    // Show typing indicator
    showTypingIndicator(true);
    
    try {
        const requestBody = { 
            question: message,
            session_id: currentSessionId
        };
        
        const response = await fetch(`${API_BASE_URL}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Update session ID if returned
            if (result.session_id) {
                currentSessionId = result.session_id;
            }
            
            // Add context indicator for follow-up questions
            let contextIndicator = '';
            if (result.is_follow_up) {
                contextIndicator = '<div class="text-xs text-blue-600 italic mb-2">💬 Building on our previous conversation...</div>';
            }
            
            addMessage('assistant', contextIndicator + result.answer, result.sources);
            
            // Store in local conversation history
            conversationHistory.push({
                question: message,
                answer: result.answer,
                timestamp: new Date().toISOString()
            });
        } else {
            addMessage('assistant', `I apologize, but I encountered an error: ${result.error}`);
        }
    } catch (error) {
        addMessage('assistant', `I'm sorry, but I'm having trouble connecting to the server. Please try again later.`);
    } finally {
        showTypingIndicator(false);
    }
}

// Add message to chat
function addMessage(sender, content, sources = []) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-bubble';
    
    if (sender === 'user') {
        messageDiv.innerHTML = `
            <div class="flex justify-end">
                <div class="bg-blue-600 text-white p-4 rounded-lg max-w-3xl">
                    <div class="flex items-start">
                        <div class="flex-1">
                            <p>${content}</p>
                        </div>
                        <i class="fas fa-user ml-3 mt-1"></i>
                    </div>
                </div>
            </div>
        `;
    } else if (sender === 'assistant') {
        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            sourcesHtml = `
                <div class="mt-4 pt-3 border-t border-gray-200">
                    <p class="text-sm font-semibold text-gray-600 mb-2">📚 Sources:</p>
                    <div class="space-y-1">
                        ${sources.slice(0, 3).map((source, index) => `
                            <div class="text-xs bg-blue-50 p-2 rounded border-l-2 border-blue-400">
                                <p class="font-medium text-blue-800">${source.metadata.document_type || 'Document'} - Page ${source.metadata.page_number || 'N/A'}</p>
                                <p class="text-gray-600 mt-1 text-xs">${escapeHtml(source.content)}</p>
                            </div>
                        `).join('')}
                        ${sources.length > 3 ? `<p class="text-xs text-gray-500 italic">+ ${sources.length - 3} more sources</p>` : ''}
                    </div>
                </div>
            `;
        }
        
        messageDiv.innerHTML = `
            <div class="bg-gray-100 p-4 rounded-lg">
                <div class="flex items-start">
                    <i class="fas fa-robot text-blue-600 mr-3 mt-1"></i>
                    <div class="flex-1">
                        <div class="prose prose-sm max-w-none">
                            ${formatMessage(content)}
                        </div>
                        ${sourcesHtml}
                    </div>
                </div>
            </div>
        `;
    } else if (sender === 'system') {
        messageDiv.innerHTML = `
            <div class="bg-yellow-100 border-l-4 border-yellow-400 p-4 rounded">
                <div class="flex items-start">
                    <i class="fas fa-info-circle text-yellow-600 mr-3 mt-1"></i>
                    <p class="text-yellow-800">${escapeHtml(content)}</p>
                </div>
            </div>
        `;
    }
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Format message content with story-like structure
function formatMessage(content) {
    // Convert markdown-style formatting to HTML
    content = content.replace(/\*\*(.*?)\*\*/g, '<strong class="text-gray-800 font-semibold">$1</strong>');
    
    // Format story sections with enhanced styling
    content = content.replace(/^(🎯)\s*([^:]+):/gm, '<div class="mt-4 mb-3 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border-l-4 border-blue-400"><span class="text-xl">$1</span> <strong class="text-blue-800 font-bold text-lg">$2:</strong></div>');
    content = content.replace(/^(⚖️)\s*([^:]+):/gm, '<div class="mt-4 mb-2 p-2 bg-green-50 rounded-lg border-l-3 border-green-400"><span class="text-lg">$1</span> <strong class="text-green-700 font-semibold">$2:</strong></div>');
    content = content.replace(/^(📖)\s*([^:]+):/gm, '<div class="mt-4 mb-2 p-2 bg-yellow-50 rounded-lg border-l-3 border-yellow-400"><span class="text-lg">$1</span> <strong class="text-yellow-700 font-semibold">$2:</strong></div>');
    content = content.replace(/^(⚠️)\s*([^:]+):/gm, '<div class="mt-4 mb-2 p-2 bg-red-50 rounded-lg border-l-3 border-red-400"><span class="text-lg">$1</span> <strong class="text-red-700 font-semibold">$2:</strong></div>');
    content = content.replace(/^(💡)\s*([^:]+):/gm, '<div class="mt-4 mb-2 p-2 bg-purple-50 rounded-lg border-l-3 border-purple-400"><span class="text-lg">$1</span> <strong class="text-purple-700 font-semibold">$2:</strong></div>');
    
    // Format bullet points with better spacing
    content = content.replace(/^•\s*(.+)$/gm, '<div class="ml-6 mb-2 text-gray-700 leading-relaxed">• $1</div>');
    
    // Format section/article references (be more specific to avoid conflicts)
    content = content.replace(/\b(Article\s+\d+[A-Z]*|Section\s+\d+[A-Z]*)\b/gi, '<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-medium">$1</span>');
    
    // Format specific tax sections
    content = content.replace(/\b(Section\s+80[A-Z]+|Section\s+194[A-Z]*|Section\s+24|Section\s+17|Section\s+28|Section\s+37|Section\s+54[A-Z]*)\b/gi, '<span class="bg-purple-100 text-purple-800 px-2 py-1 rounded text-sm font-medium">$1</span>');
    
    // Format legal document names
    content = content.replace(/\b(Constitution|Bharatiya Nyaya Sanhita|BNS|IPC|Income Tax Act|Finance Act|Tax Rules)\b/gi, '<span class="text-green-700 font-medium bg-green-100 px-2 py-1 rounded">$1</span>');
    
    // Format tax-specific terms
    content = content.replace(/\b(TDS|Assessment Year|Financial Year|PAN|Advance Tax|PPF|EPF|ELSS|NPS|HUF)\b/gi, '<span class="text-purple-700 font-medium bg-purple-100 px-2 py-1 rounded">$1</span>');
    
    // Format engaging phrases (be more specific)
    content = content.replace(/\b(Here's what happens when|The law steps in by|In practical terms|What makes this law special|The real impact|For ordinary citizens|Here's the interesting part|What's fascinating is|The law works like this)\b/gi, '<span class="text-indigo-600 font-medium italic">$1</span>');
    
    // Format monetary amounts
    content = content.replace(/\b(₹[\d,]+|Rs\.?\s*[\d,]+)\b/gi, '<span class="text-orange-600 font-semibold">$1</span>');
    
    // Format time periods (years, months)
    content = content.replace(/\b(\d+\s*years?|\d+\s*months?)\b/gi, '<span class="text-red-600 font-medium">$1</span>');
    
    // Format line breaks with better spacing
    content = content.replace(/\n/g, '<br>');
    
    return content;
}

// Show upload status
function showUploadStatus(message, type) {
    const statusDiv = document.getElementById('uploadStatus');
    const colors = {
        info: 'text-blue-600',
        success: 'text-green-600',
        error: 'text-red-600'
    };
    
    statusDiv.className = `mt-4 text-sm ${colors[type] || 'text-gray-600'}`;
    statusDiv.textContent = message;
    
    // Clear status after 5 seconds for success/error messages
    if (type !== 'info') {
        setTimeout(() => {
            statusDiv.textContent = '';
        }, 5000);
    }
}

// Show/hide typing indicator
function showTypingIndicator(show) {
    const indicator = document.getElementById('typingIndicator');
    const chatContainer = document.getElementById('chatContainer');
    
    if (show) {
        indicator.classList.add('show');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    } else {
        indicator.classList.remove('show');
    }
}

// Show recent sessions
async function showRecentSessions() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/recent-sessions`);
        const result = await response.json();
        
        if (response.ok && result.sessions.length > 0) {
            let sessionsHtml = '<div class="mt-4"><h4 class="font-semibold mb-2">Recent Conversations:</h4>';
            
            result.sessions.forEach(session => {
                const date = new Date(session.created_at).toLocaleDateString();
                sessionsHtml += `
                    <div class="bg-gray-50 p-2 rounded mb-2 cursor-pointer hover:bg-gray-100" 
                         onclick="loadSession('${session.session_id}')">
                        <div class="text-sm font-medium">${session.preview}</div>
                        <div class="text-xs text-gray-600">${date} • ${session.total_exchanges} exchanges</div>
                    </div>
                `;
            });
            
            sessionsHtml += '</div>';
            
            // Show in a modal or update a section
            addMessage('system', sessionsHtml);
        } else {
            addMessage('system', 'No recent conversations found.');
        }
    } catch (error) {
        console.error('Error loading recent sessions:', error);
        addMessage('system', 'Error loading conversation history.');
    }
}

// Load a specific session
async function loadSession(sessionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/conversation-history/${sessionId}`);
        const result = await response.json();
        
        if (response.ok) {
            currentSessionId = sessionId;
            
            // Clear current chat
            const chatContainer = document.getElementById('chatContainer');
            chatContainer.innerHTML = '';
            
            // Load conversation history
            result.history.forEach(exchange => {
                addMessage('user', exchange.user_question);
                addMessage('assistant', exchange.assistant_response, exchange.sources);
            });
            
            // Update session info
            document.getElementById('sessionInfo').textContent = `Loaded conversation from ${new Date(result.history[0]?.timestamp).toLocaleDateString()}`;
            
            addMessage('system', `✅ Loaded conversation with ${result.history.length} previous exchanges. You can continue the conversation with context awareness.`);
        } else {
            addMessage('system', '❌ Error loading conversation.');
        }
    } catch (error) {
        console.error('Error loading session:', error);
        addMessage('system', '❌ Error loading conversation.');
    }
}

// Enhanced start new conversation
async function startNewConversation() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/new-conversation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            currentSessionId = result.session_id;
            conversationHistory = [];
            
            // Clear chat
            const chatContainer = document.getElementById('chatContainer');
            chatContainer.innerHTML = '';
            
            // Add welcome message
            addMessage('assistant', `
                <div class="bg-blue-100 p-4 rounded-lg">
                    <div class="flex items-start">
                        <i class="fas fa-robot text-blue-600 mr-3 mt-1"></i>
                        <div>
                            <p class="text-gray-800">Hello! I'm your Indian Legal Assistant with context awareness. I can help you with questions about:</p>
                            <ul class="mt-2 text-sm text-gray-600 list-disc list-inside">
                                <li>Indian Constitution - Articles, Fundamental Rights, Directive Principles</li>
                                <li>Bharatiya Nyaya Sanhita - Criminal law provisions and sections</li>
                                <li>Income Tax Laws - Tax deductions, TDS, Assessment, Compliance</li>
                            </ul>
                            <p class="mt-2 text-sm text-blue-600 font-medium">💬 I remember our conversation context, so feel free to ask follow-up questions!</p>
                        </div>
                    </div>
                </div>
            `);
            
            // Update session info
            document.getElementById('sessionInfo').textContent = 'New context-aware conversation started';
            
            console.log('Started new conversation:', currentSessionId);
        }
    } catch (error) {
        console.error('Error starting new conversation:', error);
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}