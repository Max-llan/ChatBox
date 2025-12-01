// Estado de la aplicación
let conversationHistory = [];
let isProcessing = false;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// Elementos del DOM
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const chatMessages = document.getElementById('chatMessages');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearChat');
const charCount = document.getElementById('charCount');
const recordBtn = document.getElementById('recordBtn');
const micIcon = document.getElementById('micIcon');
const stopIcon = document.getElementById('stopIcon');
const recordingStatus = document.getElementById('recordingStatus');

// Configurar Marked.js
marked.setOptions({
    breaks: true,
    gfm: true,
    highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            try {
                return hljs.highlight(code, { language: lang }).value;
            } catch (err) {}
        }
        return hljs.highlightAuto(code).value;
    }
});

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    messageInput.focus();
    loadChatHistory();
    adjustTextareaHeight();
});

// Auto-resize del textarea
messageInput.addEventListener('input', () => {
    adjustTextareaHeight();
    updateCharCount();
});

function adjustTextareaHeight() {
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
}

function updateCharCount() {
    charCount.textContent = messageInput.value.length;
}

// Manejo de grabación de audio
recordBtn.addEventListener('click', async () => {
    if (!isRecording) {
        await startRecording();
    } else {
        await stopRecording();
    }
});

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            await transcribeAudio(audioBlob);
            
            // Detener el stream
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start();
        isRecording = true;
        
        // Actualizar UI
        recordBtn.classList.add('recording');
        micIcon.style.display = 'none';
        stopIcon.style.display = 'block';
        recordingStatus.style.display = 'flex';
        
    } catch (error) {
        console.error('Error al acceder al micrófono:', error);
        alert('No se pudo acceder al micrófono. Por favor, verifica los permisos.');
    }
}

async function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        isRecording = false;
        
        // Actualizar UI
        recordBtn.classList.remove('recording');
        micIcon.style.display = 'block';
        stopIcon.style.display = 'none';
        recordingStatus.style.display = 'none';
    }
}

async function transcribeAudio(audioBlob) {
    try {
        // Mostrar indicador de procesamiento
        const formData = new FormData();
        formData.append('audio', audioBlob, 'audio.webm');
        
        // Deshabilitar controles
        recordBtn.disabled = true;
        sendBtn.disabled = true;
        messageInput.placeholder = 'Transcribiendo audio...';
        
        const response = await fetch('/transcribe/', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Insertar transcripción en el textarea
            messageInput.value = data.transcription;
            adjustTextareaHeight();
            updateCharCount();
            messageInput.focus();
        } else {
            alert('Error al transcribir el audio: ' + data.error);
        }
        
    } catch (error) {
        console.error('Error al transcribir audio:', error);
        alert('Error al transcribir el audio. Intenta nuevamente.');
    } finally {
        // Rehabilitar controles
        recordBtn.disabled = false;
        sendBtn.disabled = false;
        messageInput.placeholder = 'Escribe tu mensaje aquí o graba un audio...';
    }
}

// Enviar mensaje
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message || isProcessing) return;
    
    // Limpiar input
    messageInput.value = '';
    adjustTextareaHeight();
    updateCharCount();
    
    // Agregar mensaje del usuario
    addMessage(message, 'user');
    
    // Mostrar indicador de escritura
    showTypingIndicator();
    
    // Deshabilitar envío
    isProcessing = true;
    sendBtn.disabled = true;
    
    try {
        // Enviar a la API
        const response = await fetch('/send/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: conversationHistory
            })
        });
        
        const data = await response.json();
        
        // Remover indicador
        removeTypingIndicator();
        
        if (data.success) {
            // Agregar respuesta del bot
            addMessage(data.response, 'bot');
            
            // Actualizar historial
            conversationHistory.push({
                role: 'user',
                content: message
            });
            conversationHistory.push({
                role: 'assistant',
                content: data.response
            });
            
            saveChatHistory();
        } else {
            addMessage('Lo siento, hubo un error: ' + data.error, 'bot');
        }
    } catch (error) {
        removeTypingIndicator();
        addMessage('Lo siento, no pude conectarme con el servidor. Intenta nuevamente.', 'bot');
        console.error('Error:', error);
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
});

// Agregar mensaje al chat
function addMessage(content, type) {
    // Remover mensaje de bienvenida si existe
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? '👤' : '🤖';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Renderizar Markdown para mensajes del bot
    if (type === 'bot') {
        const renderedContent = marked.parse(content);
        messageContent.innerHTML = renderedContent;
        
        // Resaltar código después de renderizar
        messageContent.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    } else {
        // Para mensajes del usuario, escapar HTML pero permitir saltos de línea
        messageContent.innerHTML = escapeHtml(content).replace(/\n/g, '<br>');
    }
    
    const messageWrapper = document.createElement('div');
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = getCurrentTime();
    
    messageWrapper.appendChild(messageContent);
    messageWrapper.appendChild(time);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageWrapper);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Función para escapar HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Mostrar indicador de escritura
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot typing';
    typingDiv.id = 'typingIndicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';
    
    const indicator = document.createElement('div');
    indicator.className = 'message-content';
    indicator.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
    
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(indicator);
    
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

// Remover indicador de escritura
function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// Scroll al final
function scrollToBottom() {
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

// Obtener hora actual
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

// Limpiar chat
clearBtn.addEventListener('click', () => {
    if (confirm('¿Estás seguro de que quieres limpiar el chat?')) {
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">👋</div>
                <h2>¡Bienvenido al ChatBox AI!</h2>
                <p>Estoy aquí para ayudarte. Puedes preguntarme lo que quieras.</p>
            </div>
        `;
        conversationHistory = [];
        localStorage.removeItem('chatHistory');
    }
});

// Guardar historial en localStorage
function saveChatHistory() {
    try {
        localStorage.setItem('chatHistory', JSON.stringify(conversationHistory));
    } catch (error) {
        console.error('Error al guardar historial:', error);
    }
}

// Cargar historial desde localStorage
function loadChatHistory() {
    try {
        const saved = localStorage.getItem('chatHistory');
        if (saved) {
            conversationHistory = JSON.parse(saved);
            
            // Restaurar mensajes en la interfaz
            if (conversationHistory.length > 0) {
                const welcomeMsg = chatMessages.querySelector('.welcome-message');
                if (welcomeMsg) welcomeMsg.remove();
                
                conversationHistory.forEach(msg => {
                    if (msg.role === 'user') {
                        addMessage(msg.content, 'user');
                    } else if (msg.role === 'assistant') {
                        addMessage(msg.content, 'bot');
                    }
                });
            }
        }
    } catch (error) {
        console.error('Error al cargar historial:', error);
    }
}

// Atajos de teclado
messageInput.addEventListener('keydown', (e) => {
    // Enviar con Ctrl+Enter
    if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});
