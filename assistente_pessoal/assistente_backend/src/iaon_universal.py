#!/usr/bin/env python3
"""
IAON UNIVERSAL - Funciona em TODOS os dispositivos
Progressive Web App com máxima compatibilidade
"""
from flask import Flask, render_template_string, request, jsonify, session, redirect, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import uuid
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
app.secret_key = 'iaon_universal_2025_mobile_key'
CORS(app)

def init_db():
    """Inicializar banco de dados"""
    conn = sqlite3.connect('iaon_universal.db')
    cursor = conn.cursor()
    
    # Tabela de organizações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            subdomain TEXT UNIQUE NOT NULL,
            plan TEXT DEFAULT 'free',
            expires_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            org_id TEXT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (org_id) REFERENCES organizations (id)
        )
    ''')
    
    # Tabela de conversas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            message TEXT,
            response TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def home():
    """Página principal universal"""
    return render_template_string("""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#2563eb">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="IAON">
    <meta name="mobile-web-app-capable" content="yes">
    <title>IAON Universal - Assistente IA</title>
    
    <!-- PWA Manifest -->
    <link rel="manifest" href="/manifest.json">
    <link rel="apple-touch-icon" href="/icon-192.png">
    <link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 100%;
            padding: 20px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px 0;
        }
        
        .logo {
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 10px;
            text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 20px;
        }
        
        .status-indicator {
            display: inline-block;
            padding: 8px 16px;
            background: rgba(16, 185, 129, 0.9);
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .chat-container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            min-height: 400px;
            display: flex;
            flex-direction: column;
        }
        
        .messages {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            padding-right: 10px;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 15px;
            max-width: 85%;
            word-wrap: break-word;
        }
        
        .user-message {
            background: rgba(37, 99, 235, 0.8);
            margin-left: auto;
            text-align: right;
        }
        
        .ai-message {
            background: rgba(16, 185, 129, 0.8);
            margin-right: auto;
        }
        
        .input-area {
            display: flex;
            gap: 10px;
            align-items: center;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .message-input {
            flex: 1;
            background: transparent;
            border: none;
            color: white;
            font-size: 16px;
            padding: 10px;
            outline: none;
        }
        
        .message-input::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 16px;
            min-width: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #3b82f6, #1d4ed8);
            color: white;
        }
        
        .btn-voice {
            background: linear-gradient(45deg, #ef4444, #dc2626);
            color: white;
            position: relative;
        }
        
        .btn-voice.active {
            background: linear-gradient(45deg, #10b981, #059669);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .device-info {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 0.9rem;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .loading.show {
            display: block;
        }
        
        /* Responsividade */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .logo {
                font-size: 2.5rem;
            }
            
            .chat-container {
                min-height: 350px;
                margin-bottom: 15px;
            }
            
            .controls {
                gap: 8px;
            }
            
            .btn {
                padding: 10px 16px;
                font-size: 14px;
            }
        }
        
        /* iOS Safari específico */
        @media screen and (-webkit-min-device-pixel-ratio: 2) {
            .btn {
                font-size: 16px; /* Previne zoom no iOS */
            }
            
            .message-input {
                font-size: 16px; /* Previne zoom no iOS */
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🤖 IAON</div>
            <div class="subtitle">Assistente IA Universal</div>
            <div class="status-indicator" id="status">
                🌐 Conectado - Funciona em qualquer dispositivo
            </div>
        </div>
        
        <div class="device-info" id="deviceInfo">
            📱 Detectando dispositivo...
        </div>
        
        <div class="controls">
            <button class="btn btn-voice" id="voiceBtn" onclick="toggleVoice()">
                🎤 Voz
            </button>
            <button class="btn btn-primary" onclick="clearChat()">
                🗑️ Limpar
            </button>
            <button class="btn btn-primary" onclick="testConnection()">
                🔧 Teste
            </button>
        </div>
        
        <div class="chat-container">
            <div class="messages" id="messages">
                <div class="ai-message message">
                    Olá! 👋 Eu sou o IAON, seu assistente IA universal. Funciono em qualquer dispositivo!<br><br>
                    📱 <strong>Como usar:</strong><br>
                    • Digite sua mensagem ou use o botão 🎤<br>
                    • Para comandos de voz, diga "IA" seguido da pergunta<br>
                    • Exemplo: "IA, como está o tempo?"<br><br>
                    💡 <strong>Compatibilidade total:</strong> iPhone, Android, Desktop, Tablet
                </div>
            </div>
            
            <div class="loading" id="loading">
                🤖 Processando...
            </div>
            
            <div class="input-area">
                <input type="text" 
                       class="message-input" 
                       id="messageInput" 
                       placeholder="Digite sua mensagem ou use o microfone..."
                       onkeypress="if(event.key==='Enter') sendMessage()">
                <button class="btn btn-primary" onclick="sendMessage()">
                    ➤
                </button>
            </div>
        </div>
    </div>

    <script>
        // Variáveis globais
        let isVoiceActive = false;
        let recognition = null;
        let isListening = false;
        
        // Detectar dispositivo
        function detectDevice() {
            const userAgent = navigator.userAgent;
            let device = "Desktop";
            let browser = "Desconhecido";
            let features = [];
            
            // Detectar dispositivo
            if (/iPhone/i.test(userAgent)) {
                device = "iPhone";
            } else if (/iPad/i.test(userAgent)) {
                device = "iPad";
            } else if (/Android/i.test(userAgent)) {
                device = "Android";
            } else if (/Windows Phone/i.test(userAgent)) {
                device = "Windows Phone";
            }
            
            // Detectar navegador
            if (/Safari/i.test(userAgent) && !/Chrome/i.test(userAgent)) {
                browser = "Safari";
            } else if (/Chrome/i.test(userAgent)) {
                browser = "Chrome";
            } else if (/Firefox/i.test(userAgent)) {
                browser = "Firefox";
            } else if (/Edge/i.test(userAgent)) {
                browser = "Edge";
            }
            
            // Verificar recursos
            if ('speechRecognition' in window || 'webkitSpeechRecognition' in window) {
                features.push("🎤 Voz");
            }
            if ('serviceWorker' in navigator) {
                features.push("📱 PWA");
            }
            if ('geolocation' in navigator) {
                features.push("📍 GPS");
            }
            if ('vibrate' in navigator) {
                features.push("📳 Vibração");
            }
            
            const info = `${device} | ${browser} | ${features.join(" ")}`;
            document.getElementById('deviceInfo').innerHTML = `📱 ${info}`;
            
            return { device, browser, features };
        }
        
        // Inicializar reconhecimento de voz universal
        function initVoiceRecognition() {
            if ('speechRecognition' in window || 'webkitSpeechRecognition' in window) {
                recognition = new (window.speechRecognition || window.webkitSpeechRecognition)();
                
                recognition.continuous = true;
                recognition.interimResults = false;
                recognition.lang = 'pt-BR';
                
                recognition.onstart = function() {
                    isListening = true;
                    document.getElementById('voiceBtn').classList.add('active');
                    updateStatus('🎤 Escutando... (Diga "IA" + sua pergunta)');
                };
                
                recognition.onend = function() {
                    isListening = false;
                    document.getElementById('voiceBtn').classList.remove('active');
                    updateStatus('🌐 Conectado - Pronto para ouvir');
                    
                    // Reiniciar automaticamente se ainda ativo
                    if (isVoiceActive) {
                        setTimeout(() => {
                            if (isVoiceActive) {
                                try {
                                    recognition.start();
                                } catch (e) {
                                    console.log('Reconhecimento já ativo ou erro:', e);
                                }
                            }
                        }, 1000);
                    }
                };
                
                recognition.onresult = function(event) {
                    const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();
                    console.log('Comando de voz detectado:', transcript);
                    
                    // Verificar se contém "ia" no início
                    if (transcript.includes('ia') || transcript.includes('hey') || transcript.includes('olá')) {
                        const command = transcript.replace(/^(ia|hey|olá)\\s*/i, '');
                        if (command.length > 0) {
                            addMessage(transcript, 'user');
                            processMessage(command);
                        }
                    }
                };
                
                recognition.onerror = function(event) {
                    console.log('Erro no reconhecimento:', event.error);
                    
                    if (event.error === 'not-allowed') {
                        updateStatus('❌ Microfone negado. Permita o acesso!');
                        isVoiceActive = false;
                        document.getElementById('voiceBtn').classList.remove('active');
                    } else {
                        updateStatus('⚠️ Erro na voz. Tentando novamente...');
                    }
                };
                
                return true;
            } else {
                updateStatus('❌ Voz não suportada neste navegador');
                return false;
            }
        }
        
        // Alternar reconhecimento de voz
        function toggleVoice() {
            if (!recognition) {
                if (!initVoiceRecognition()) {
                    alert('❌ Reconhecimento de voz não suportado neste dispositivo.\\n\\nUse o chat por texto!');
                    return;
                }
            }
            
            if (isVoiceActive) {
                // Parar voz
                isVoiceActive = false;
                try {
                    recognition.stop();
                } catch (e) {
                    console.log('Erro ao parar reconhecimento:', e);
                }
                document.getElementById('voiceBtn').classList.remove('active');
                updateStatus('🌐 Conectado - Voz desativada');
            } else {
                // Iniciar voz
                isVoiceActive = true;
                try {
                    recognition.start();
                    updateStatus('🎤 Iniciando reconhecimento...');
                } catch (e) {
                    console.log('Erro ao iniciar reconhecimento:', e);
                    updateStatus('⚠️ Erro ao iniciar voz. Tente novamente.');
                    isVoiceActive = false;
                }
            }
        }
        
        // Atualizar status
        function updateStatus(message) {
            document.getElementById('status').innerHTML = message;
        }
        
        // Adicionar mensagem ao chat
        function addMessage(message, sender = 'ai') {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.innerHTML = message;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        // Enviar mensagem
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (message) {
                addMessage(message, 'user');
                input.value = '';
                processMessage(message);
            }
        }
        
        // Processar mensagem
        async function processMessage(message) {
            const loading = document.getElementById('loading');
            loading.classList.add('show');
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    addMessage(data.response, 'ai');
                } else {
                    throw new Error('Erro na comunicação');
                }
            } catch (error) {
                console.error('Erro:', error);
                addMessage('❌ Desculpe, houve um erro. Tente novamente!', 'ai');
            } finally {
                loading.classList.remove('show');
            }
        }
        
        // Limpar chat
        function clearChat() {
            const messages = document.getElementById('messages');
            messages.innerHTML = `
                <div class="ai-message message">
                    Chat limpo! 🧹<br>
                    Como posso ajudar você agora?
                </div>
            `;
        }
        
        // Testar conexão
        function testConnection() {
            updateStatus('🔧 Testando conexão...');
            
            fetch('/api/test')
                .then(response => response.json())
                .then(data => {
                    addMessage(`✅ Teste OK! ${data.message}`, 'ai');
                    updateStatus('🌐 Conectado - Tudo funcionando!');
                })
                .catch(error => {
                    addMessage('❌ Erro de conexão. Verifique sua internet.', 'ai');
                    updateStatus('❌ Erro de conexão');
                });
        }
        
        // Inicialização
        document.addEventListener('DOMContentLoaded', function() {
            detectDevice();
            
            // Registrar Service Worker para PWA
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => console.log('SW registrado'))
                    .catch(error => console.log('SW falhou:', error));
            }
            
            // Detectar se é PWA
            let displayMode = 'browser';
            if (window.matchMedia('(display-mode: standalone)').matches) {
                displayMode = 'standalone';
                updateStatus('📱 Executando como App (PWA)');
            }
            
            console.log('IAON Universal carregado');
        });
        
        // Prevenir zoom no iOS
        document.addEventListener('gesturestart', function (e) {
            e.preventDefault();
        });
    </script>
</body>
</html>
    """)

@app.route('/api/chat', methods=['POST'])
def chat():
    """API de chat universal"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        # IA simples mas efetiva
        responses = {
            'oi': 'Olá! 👋 Como posso ajudar você hoje?',
            'olá': 'Oi! 😊 Em que posso ser útil?',
            'como você está': 'Estou ótimo e pronto para ajudar! 🤖✨',
            'tempo': 'Para informações do tempo, você pode consultar um app de meteorologia. Posso ajudar com outras coisas! 🌤️',
            'ajuda': 'Claro! Eu posso:\n• Responder perguntas\n• Conversar sobre diversos assuntos\n• Ajudar com tarefas simples\n• Funcionar em qualquer dispositivo! 💪',
            'obrigado': 'De nada! 😊 Sempre à disposição!',
            'tchau': 'Até logo! 👋 Volte sempre que precisar!',
        }
        
        # Buscar resposta
        message_lower = message.lower()
        response = None
        
        for key in responses:
            if key in message_lower:
                response = responses[key]
                break
        
        if not response:
            if '?' in message:
                response = f'Interessante pergunta! 🤔 Sobre "{message}", posso dizer que é um tópico fascinante. Como posso ajudar especificamente?'
            else:
                response = f'Entendi! Você disse: "{message}". Como posso ajudar você com isso? 💡'
        
        # Salvar conversa se tiver usuário logado
        if 'user_id' in session:
            conn = sqlite3.connect('iaon_universal.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (id, user_id, message, response)
                VALUES (?, ?, ?, ?)
            ''', (str(uuid.uuid4()), session['user_id'], message, response))
            conn.commit()
            conn.close()
        
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"Erro no chat: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/api/test')
def test():
    """Endpoint de teste"""
    return jsonify({
        'status': 'ok',
        'message': 'IAON Universal funcionando perfeitamente!',
        'timestamp': datetime.now().isoformat(),
        'device_support': 'iPhone, Android, Desktop, Tablet'
    })

@app.route('/manifest.json')
def manifest():
    """Manifest PWA"""
    return jsonify({
        "name": "IAON Universal",
        "short_name": "IAON",
        "description": "Assistente IA que funciona em qualquer dispositivo",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#667eea",
        "theme_color": "#2563eb",
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": "/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "/icon-512.png", 
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ],
        "categories": ["productivity", "utilities"],
        "lang": "pt-BR"
    })

@app.route('/sw.js')
def service_worker():
    """Service Worker para PWA"""
    return f"""
const CACHE_NAME = 'iaon-universal-v1';
const urlsToCache = [
    '/',
    '/manifest.json'
];

self.addEventListener('install', function(event) {{
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {{
                return cache.addAll(urlsToCache);
            }})
    );
}});

self.addEventListener('fetch', function(event) {{
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {{
                if (response) {{
                    return response;
                }}
                return fetch(event.request);
            }}
        )
    );
}});
""", 200, {'Content-Type': 'application/javascript'}

@app.route('/icon-192.png')
def icon_192():
    """Ícone 192x192"""
    # Retorna um ícone simples base64
    return send_from_directory('.', 'icon-192.png') if os.path.exists('icon-192.png') else ('', 404)

@app.route('/icon-512.png') 
def icon_512():
    """Ícone 512x512"""
    return send_from_directory('.', 'icon-512.png') if os.path.exists('icon-512.png') else ('', 404)

if __name__ == '__main__':
    init_db()
    
    # Criar dados demo
    conn = sqlite3.connect('iaon_universal.db')
    cursor = conn.cursor()
    
    # Verificar se já existe organização demo
    cursor.execute('SELECT id FROM organizations WHERE subdomain = ?', ('demo',))
    if not cursor.fetchone():
        org_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO organizations (id, name, subdomain, plan, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (org_id, 'Demo Universal', 'demo', 'premium', datetime.now() + timedelta(days=365)))
        
        cursor.execute('''
            INSERT INTO users (id, org_id, email, password_hash, name, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, org_id, 'admin@demo.com', generate_password_hash('123456'), 'Admin Universal', 'admin'))
        
        conn.commit()
    
    conn.close()
    
    print("🚀 IAON UNIVERSAL - FUNCIONANDO EM TODOS OS DISPOSITIVOS!")
    print("=" * 60)
    print("🌐 URL: http://localhost:5000")
    print("🌐 URL: http://192.168.15.36:5000") 
    print("📱 iPhone: Abra no Safari e adicione à tela inicial")
    print("🤖 Android: Abra no Chrome e instale como PWA")
    print("💻 Desktop: Funciona em qualquer navegador")
    print("📟 Tablet: Interface responsiva automática")
    print("=" * 60)
    print("✅ Recursos universais:")
    print("  🎤 Reconhecimento de voz (se suportado)")
    print("  💬 Chat por texto (sempre funciona)")
    print("  📱 PWA instalável")
    print("  🔄 Funciona offline (básico)")
    print("  🎯 Detecção automática do dispositivo")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
