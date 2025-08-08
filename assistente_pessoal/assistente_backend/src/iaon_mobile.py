#!/usr/bin/env python3
"""
IAON Mobile App - Versão nativa para iPhone/Android
Sistema otimizado para dispositivos móveis com melhor reconhecimento de voz
"""

from flask import Flask, render_template_string, request, jsonify, session, redirect
from flask_cors import CORS
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.secret_key = 'iaon-mobile-2025-secret-key'
CORS(app)

def init_mobile_db():
    """Inicializar banco de dados mobile"""
    conn = sqlite3.connect('iaon_mobile.db')
    cursor = conn.cursor()
    
    # Criar tabelas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password_hash TEXT,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_profiles (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            profile_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            message TEXT,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def home():
    """Página principal mobile"""
    if 'user_id' not in session:
        return render_template_string(MOBILE_LOGIN_HTML)
    
    return render_template_string(MOBILE_APP_HTML, 
                                user_name=session.get('user_name', 'Usuário'),
                                user_id=session['user_id'])

@app.route('/api/login', methods=['POST'])
def login():
    """Login mobile"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    conn = sqlite3.connect('iaon_mobile.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, password_hash, name FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        session['user_name'] = user[2]
        return jsonify({'success': True, 'redirect': '/'})
    
    return jsonify({'error': 'Credenciais inválidas'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    """Registro mobile"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not all([email, password, name]):
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
    
    user_id = str(uuid.uuid4())
    password_hash = generate_password_hash(password)
    
    try:
        conn = sqlite3.connect('iaon_mobile.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (id, email, password_hash, name) 
            VALUES (?, ?, ?, ?)
        ''', (user_id, email, password_hash, name))
        
        conn.commit()
        conn.close()
        
        session['user_id'] = user_id
        session['user_name'] = name
        
        return jsonify({'success': True, 'redirect': '/'})
    
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email já cadastrado'}), 400

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat com IA"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'Mensagem vazia'}), 400
    
    # Resposta simples da IA
    response = generate_ai_response(message)
    
    # Salvar conversa
    conversation_id = str(uuid.uuid4())
    conn = sqlite3.connect('iaon_mobile.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO conversations (id, user_id, message, response)
        VALUES (?, ?, ?, ?)
    ''', (conversation_id, session['user_id'], message, response))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'response': response,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/voice-profile', methods=['POST'])
def save_voice_profile():
    """Salvar perfil de voz"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.get_json()
    profile_data = json.dumps(data.get('profile', {}))
    
    profile_id = str(uuid.uuid4())
    conn = sqlite3.connect('iaon_mobile.db')
    cursor = conn.cursor()
    
    # Deletar perfil anterior se existir
    cursor.execute('DELETE FROM voice_profiles WHERE user_id = ?', (session['user_id'],))
    
    # Inserir novo perfil
    cursor.execute('''
        INSERT INTO voice_profiles (id, user_id, profile_data)
        VALUES (?, ?, ?)
    ''', (profile_id, session['user_id'], profile_data))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/voice-profile', methods=['GET'])
def get_voice_profile():
    """Obter perfil de voz"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    conn = sqlite3.connect('iaon_mobile.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT profile_data FROM voice_profiles WHERE user_id = ?', (session['user_id'],))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({'profile': json.loads(result[0])})
    
    return jsonify({'profile': None})

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout"""
    session.clear()
    return jsonify({'success': True})

def generate_ai_response(message):
    """Gerar resposta da IA"""
    message_lower = message.lower()
    
    responses = {
        'oi': 'Olá! Como posso ajudá-lo hoje?',
        'ola': 'Olá! Como posso ajudá-lo hoje?',
        'como voce esta': 'Estou muito bem, obrigado por perguntar! Como você está?',
        'que horas': f'Agora são {datetime.now().strftime("%H:%M")}.',
        'que dia': f'Hoje é {datetime.now().strftime("%d/%m/%Y")}.',
        'ajuda': 'Posso ajudá-lo com várias tarefas! Você pode me perguntar sobre horários, datas, ou apenas conversar comigo.',
        'obrigado': 'De nada! Fico feliz em ajudar.',
        'tchau': 'Até logo! Foi um prazer conversar com você.',
        'tempo': 'Não tenho acesso a informações meteorológicas no momento, mas posso ajudá-lo com outras coisas!',
        'nome': 'Eu sou IAON, seu assistente pessoal inteligente!'
    }
    
    for key, response in responses.items():
        if key in message_lower:
            return response
    
    return f'Interessante pergunta sobre "{message}". Posso ajudá-lo com informações gerais, horários, datas e muito mais. O que gostaria de saber?'

# HTML Templates
MOBILE_LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>IAON Mobile</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            padding: 20px;
        }
        
        .login-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 40px 30px;
            width: 100%;
            max-width: 400px;
            text-align: center;
            box-shadow: 0 25px 45px rgba(0, 0, 0, 0.3);
        }
        
        .logo {
            font-size: 3rem;
            margin-bottom: 10px;
        }
        
        h1 {
            font-size: 2rem;
            margin-bottom: 30px;
            font-weight: 300;
        }
        
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
        }
        
        input {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 16px;
            backdrop-filter: blur(10px);
        }
        
        input::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(45deg, #ff6b6b, #feca57);
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 15px;
            transition: transform 0.2s;
        }
        
        .btn:active {
            transform: scale(0.98);
        }
        
        .switch-mode {
            color: rgba(255, 255, 255, 0.8);
            text-decoration: underline;
            cursor: pointer;
        }
        
        .demo-info {
            margin-top: 20px;
            padding: 15px;
            background: rgba(0, 255, 0, 0.1);
            border-radius: 10px;
            border: 1px solid rgba(0, 255, 0, 0.3);
        }
        
        .demo-info h3 {
            color: #4ade80;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">🤖</div>
        <h1>IAON Mobile</h1>
        
        <form id="authForm">
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" placeholder="seu@email.com" required>
            </div>
            
            <div class="form-group">
                <label for="password">Senha:</label>
                <input type="password" id="password" placeholder="Sua senha" required>
            </div>
            
            <div class="form-group" id="nameGroup" style="display: none;">
                <label for="name">Nome:</label>
                <input type="text" id="name" placeholder="Seu nome">
            </div>
            
            <button type="submit" class="btn" id="authBtn">Entrar</button>
            
            <div class="switch-mode" onclick="toggleMode()">
                <span id="switchText">Não tem conta? Registre-se</span>
            </div>
        </form>
        
        <div class="demo-info">
            <h3>🎯 Conta Demo</h3>
            <p>Email: admin@demo.com</p>
            <p>Senha: 123456</p>
        </div>
    </div>

    <script>
        let isLogin = true;
        
        function toggleMode() {
            isLogin = !isLogin;
            const nameGroup = document.getElementById('nameGroup');
            const authBtn = document.getElementById('authBtn');
            const switchText = document.getElementById('switchText');
            
            if (isLogin) {
                nameGroup.style.display = 'none';
                authBtn.textContent = 'Entrar';
                switchText.textContent = 'Não tem conta? Registre-se';
            } else {
                nameGroup.style.display = 'block';
                authBtn.textContent = 'Registrar';
                switchText.textContent = 'Já tem conta? Faça login';
            }
        }
        
        document.getElementById('authForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const name = document.getElementById('name').value;
            
            const data = { email, password };
            if (!isLogin) data.name = name;
            
            const endpoint = isLogin ? '/api/login' : '/api/register';
            
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    window.location.href = result.redirect;
                } else {
                    alert(result.error || 'Erro ao autenticar');
                }
            } catch (error) {
                alert('Erro de conexão: ' + error.message);
            }
        });
        
        // Preencher dados demo
        document.getElementById('email').value = 'admin@demo.com';
        document.getElementById('password').value = '123456';
    </script>
</body>
</html>
'''

MOBILE_APP_HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>IAON - {{ user_name }}</title>
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#667eea">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            overflow-x: hidden;
        }
        
        .header {
            padding: 20px;
            text-align: center;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
        }
        
        .logo {
            font-size: 2rem;
            margin-bottom: 5px;
        }
        
        .user-info {
            opacity: 0.8;
            font-size: 0.9rem;
        }
        
        .main-content {
            padding: 20px;
            height: calc(100vh - 100px);
            display: flex;
            flex-direction: column;
        }
        
        .voice-controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .voice-btn {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s;
            backdrop-filter: blur(10px);
        }
        
        .voice-btn.recording {
            background: linear-gradient(45deg, #ff4757, #ff6b7a);
            animation: pulse 1s infinite;
        }
        
        .voice-btn:not(.recording) {
            background: rgba(255, 255, 255, 0.2);
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        .chat-container {
            flex: 1;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            backdrop-filter: blur(20px);
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            padding-right: 10px;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .user-message {
            background: linear-gradient(45deg, #4facfe, #00f2fe);
            margin-left: auto;
            text-align: right;
        }
        
        .ai-message {
            background: rgba(255, 255, 255, 0.2);
            margin-right: auto;
        }
        
        .input-container {
            display: flex;
            gap: 10px;
        }
        
        .chat-input {
            flex: 1;
            padding: 15px;
            border: none;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 16px;
            backdrop-filter: blur(10px);
        }
        
        .chat-input::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        
        .send-btn {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(45deg, #ff6b6b, #feca57);
            color: white;
            font-size: 1.2rem;
            cursor: pointer;
        }
        
        .status {
            text-align: center;
            margin: 10px 0;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .status.listening {
            color: #4ade80;
            animation: pulse 1s infinite;
        }
        
        .logout-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 10px;
            border-radius: 50%;
            cursor: pointer;
            backdrop-filter: blur(10px);
        }
    </style>
</head>
<body>
    <button class="logout-btn" onclick="logout()">🚪</button>
    
    <div class="header">
        <div class="logo">🤖 IAON</div>
        <div class="user-info">Olá, {{ user_name }}!</div>
    </div>
    
    <div class="main-content">
        <div class="voice-controls">
            <button class="voice-btn" id="voiceBtn" onclick="toggleVoice()">🎤</button>
            <button class="voice-btn" onclick="resetVoice()">🔄</button>
        </div>
        
        <div class="status" id="status">Toque no microfone para ativar comandos de voz</div>
        
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="message ai-message">
                    Olá! Eu sou seu assistente IAON. Você pode digitar ou falar comigo! 
                    Tente dizer "IA, como você está?" 😊
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" class="chat-input" id="chatInput" placeholder="Digite sua mensagem...">
                <button class="send-btn" onclick="sendMessage()">📤</button>
            </div>
        </div>
    </div>

    <script>
        let isListening = false;
        let recognition = null;
        let voiceProfile = null;
        
        // Inicializar reconhecimento de voz
        function initVoiceRecognition() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                
                recognition.continuous = true;
                recognition.interimResults = false;
                recognition.lang = 'pt-BR';
                
                recognition.onstart = function() {
                    console.log('🎤 Reconhecimento iniciado');
                    updateStatus('Escutando... Diga "IA" seguido da sua pergunta', true);
                };
                
                recognition.onresult = function(event) {
                    let finalTranscript = '';
                    
                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        if (event.results[i].isFinal) {
                            finalTranscript += event.results[i][0].transcript;
                        }
                    }
                    
                    console.log('🗣️ Reconhecido:', finalTranscript);
                    
                    if (finalTranscript.toLowerCase().includes('ia')) {
                        handleVoiceCommand(finalTranscript);
                    }
                };
                
                recognition.onerror = function(event) {
                    console.error('❌ Erro no reconhecimento:', event.error);
                    if (event.error === 'not-allowed') {
                        updateStatus('❌ Permissão de microfone negada! Recarregue e permita o acesso.');
                    } else {
                        updateStatus('Erro no reconhecimento. Tente novamente.');
                    }
                };
                
                recognition.onend = function() {
                    if (isListening) {
                        setTimeout(() => recognition.start(), 100);
                    }
                };
                
                return true;
            } else {
                updateStatus('❌ Reconhecimento de voz não suportado neste navegador');
                return false;
            }
        }
        
        function toggleVoice() {
            if (!recognition && !initVoiceRecognition()) {
                return;
            }
            
            const voiceBtn = document.getElementById('voiceBtn');
            
            if (isListening) {
                recognition.stop();
                isListening = false;
                voiceBtn.classList.remove('recording');
                updateStatus('Reconhecimento de voz desativado');
            } else {
                recognition.start();
                isListening = true;
                voiceBtn.classList.add('recording');
            }
        }
        
        function handleVoiceCommand(command) {
            console.log('🤖 Processando comando:', command);
            updateStatus('Processando comando...');
            
            // Remover "IA" do início e enviar como mensagem
            const cleanCommand = command.replace(/^.*?ia\\s*/i, '').trim();
            if (cleanCommand) {
                sendMessage(cleanCommand);
            }
        }
        
        function resetVoice() {
            if (recognition) {
                recognition.stop();
                isListening = false;
                document.getElementById('voiceBtn').classList.remove('recording');
                updateStatus('Reconhecimento resetado. Toque no microfone para reativar.');
            }
        }
        
        function updateStatus(message, listening = false) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = listening ? 'status listening' : 'status';
        }
        
        async function sendMessage(text = null) {
            const input = document.getElementById('chatInput');
            const message = text || input.value.trim();
            
            if (!message) return;
            
            // Limpar input
            if (!text) input.value = '';
            
            // Adicionar mensagem do usuário
            addMessage(message, true);
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message })
                });
                
                const result = await response.json();
                
                if (result.response) {
                    addMessage(result.response, false);
                } else {
                    addMessage('Desculpe, ocorreu um erro. Tente novamente.', false);
                }
            } catch (error) {
                console.error('Erro:', error);
                addMessage('Erro de conexão. Verifique sua internet.', false);
            }
            
            updateStatus('Pronto para nova mensagem');
        }
        
        function addMessage(text, isUser) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
            messageDiv.textContent = text;
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        async function logout() {
            try {
                await fetch('/api/logout', { method: 'POST' });
                window.location.href = '/';
            } catch (error) {
                console.error('Erro no logout:', error);
                window.location.href = '/';
            }
        }
        
        // Event listeners
        document.getElementById('chatInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Inicializar quando a página carregar
        window.addEventListener('load', function() {
            updateStatus('Pronto! Toque no microfone para ativar comandos de voz');
            
            // Tentar inicializar reconhecimento de voz
            setTimeout(() => {
                if (initVoiceRecognition()) {
                    updateStatus('Reconhecimento de voz disponível. Toque no microfone para ativar.');
                }
            }, 1000);
        });
        
        console.log('🤖 IAON Mobile carregado');
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    init_mobile_db()
    
    # Criar usuário demo
    conn = sqlite3.connect('iaon_mobile.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM users WHERE email = ?', ('admin@demo.com',))
    if not cursor.fetchone():
        user_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO users (id, email, password_hash, name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, 'admin@demo.com', generate_password_hash('123456'), 'Admin Demo'))
        conn.commit()
    
    conn.close()
    
    print("📱 IAON MOBILE APP")
    print("🚀 Iniciando servidor mobile...")
    print("🌐 URL: http://localhost:5000")
    print("🌐 URL: http://192.168.15.36:5000")
    print("📱 Otimizado para iPhone/Android")
    print("👤 Login Demo: admin@demo.com / 123456")
    print("🔊 Reconhecimento de voz melhorado")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
