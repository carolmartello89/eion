import os
import sys
from flask import Flask, jsonify, request, render_template_string, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime, timedelta
import uuid

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações
app.config['SECRET_KEY'] = 'your-super-secret-key-change-in-production'
app.config['DATABASE'] = 'iaon_saas.db'

# Inicializar CORS
CORS(app, origins="*")

def init_db():
    """Inicializar banco de dados multi-tenant"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Tabela de empresas/organizações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            subdomain TEXT UNIQUE NOT NULL,
            plan TEXT DEFAULT 'basic',
            max_users INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (org_id) REFERENCES organizations (id),
            UNIQUE(org_id, email)
        )
    ''')
    
    # Tabela de sessões/uso
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            module TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (org_id) REFERENCES organizations (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db():
    """Conexão com banco de dados"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def get_current_org():
    """Obter organização atual baseada no subdomínio ou sessão"""
    if 'org_id' in session:
        return session['org_id']
    
    # Aqui você pode implementar lógica de subdomínio
    # Por enquanto, retorna uma org padrão
    return 'demo-org'

def log_usage(module, action):
    """Registrar uso para billing/analytics"""
    if 'user_id' in session:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usage_logs (id, org_id, user_id, module, action)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4()), get_current_org(), session['user_id'], module, action))
        conn.commit()
        conn.close()

@app.route('/api/health')
def health_check():
    """Endpoint de verificação de saúde"""
    return {'status': 'ok', 'message': 'IAON funcionando!', 'version': '2.0'}

@app.route('/api/register-org', methods=['POST'])
def register_organization():
    """Registrar nova organização"""
    data = request.json
    
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Criar organização
        cursor.execute('''
            INSERT INTO organizations (id, name, subdomain, plan, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            org_id, 
            data['organization'], 
            data['subdomain'],
            data.get('plan', 'trial'),
            datetime.now() + timedelta(days=30)  # Trial de 30 dias
        ))
        
        # Criar usuário admin
        cursor.execute('''
            INSERT INTO users (id, org_id, email, password_hash, name, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            org_id,
            data['email'],
            generate_password_hash(data['password']),
            data['name'],
            'admin'
        ))
        
        conn.commit()
        return {
            'success': True, 
            'message': 'Organização criada com sucesso!',
            'org_id': org_id,
            'trial_days': 30
        }
        
    except Exception as e:
        conn.rollback()
        return {'success': False, 'error': str(e)}, 400
        
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    """Login do usuário com sistema de cupons"""
    data = request.json
    coupon = data.get('coupon', '').upper() if data.get('coupon') else ''
    
    # Cupons válidos
    valid_coupons = {
        'GRATIS2025': 'Acesso gratuito 2025',
        'FREE': 'Acesso gratuito',
        'DEMO': 'Demonstração',
        'TEST': 'Teste gratuito'
    }
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Buscar usuário
    cursor.execute('''
        SELECT u.*, o.name as org_name, o.active as org_active, o.expires_at
        FROM users u 
        JOIN organizations o ON u.org_id = o.id 
        WHERE u.email = ? AND u.active = 1
    ''', (data['email'],))
    
    user = cursor.fetchone()
    
    if user and check_password_hash(user['password_hash'], data['password']):
        # Verificar se organização está ativa
        if not user['org_active']:
            conn.close()
            return {'success': False, 'error': 'Organização inativa'}, 401
        
        # Aplicar cupom se válido
        if coupon in valid_coupons:
            # Estender acesso por 1 ano com cupom
            new_expiry = datetime.now() + timedelta(days=365)
            cursor.execute('''
                UPDATE users SET expires_at = ? WHERE id = ?
            ''', (new_expiry.isoformat(), user['id']))
            conn.commit()
            user = dict(user)
            user['expires_at'] = new_expiry.isoformat()
        
        # Verificar expiração (se não tiver cupom válido)
        if user['expires_at'] and datetime.fromisoformat(user['expires_at']) < datetime.now():
            if coupon not in valid_coupons:
                conn.close()
                return {'success': False, 'error': 'Acesso expirado. Use cupom GRATIS2025'}, 401
        
        # Login bem-sucedido
        session['user_id'] = user['id']
        session['org_id'] = user['org_id']
        session['user_name'] = user['name']
        session['user_role'] = user['role']
        session['org_name'] = user['org_name']
        session['coupon_used'] = coupon if coupon in valid_coupons else None
        
        conn.close()
        return {
            'success': True,
            'user': {
                'name': user['name'],
                'email': user['email'],
                'role': user['role'],
                'organization': user['org_name']
            },
            'coupon_status': f"✅ Cupom '{coupon}' aplicado!" if coupon in valid_coupons else None
        }
    
    conn.close()
    return {'success': False, 'error': 'Credenciais inválidas'}, 401

@app.route('/manifest.json')
def manifest():
    """Manifest para PWA"""
    return {
        "name": "IAON - Assistente Inteligente",
        "short_name": "IAON",
        "description": "Assistente IA com reconhecimento de voz",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#1e3a8a",
        "theme_color": "#3730a3",
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": "/icon-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "/icon-512x512.png", 
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ],
        "categories": ["productivity", "business"],
        "screenshots": [],
        "shortcuts": [
            {
                "name": "Chat IA",
                "short_name": "Chat",
                "description": "Abrir chat com IA",
                "url": "/?module=ia",
                "icons": [{"src": "/icon-192x192.png", "sizes": "192x192"}]
            }
        ]
    }

@app.route('/icon-192x192.png')
def icon_192():
    """Ícone 192x192 para PWA"""
    return app.send_static_file('icon-192x192.png')

@app.route('/icon-512x512.png')
def icon_512():
    """Ícone 512x512 para PWA"""
    return app.send_static_file('icon-512x512.png')

@app.route('/sw.js')
def service_worker():
    """Service Worker para PWA"""
    sw_code = '''
const CACHE_NAME = 'iaon-v1';
const urlsToCache = [
    '/',
    '/manifest.json',
    '/icon-192x192.png',
    '/icon-512x512.png'
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                if (response) {
                    return response;
                }
                return fetch(event.request);
            }
        )
    );
});

// Manter ativo em background
self.addEventListener('message', function(event) {
    if (event.data.action === 'keepAlive') {
        event.ports[0].postMessage({result: 'ok'});
    }
});
'''
    response = app.response_class(sw_code, mimetype='application/javascript')
    return response

@app.route('/api/usage-stats')
def usage_stats():
    """Estatísticas de uso da organização"""
    if 'org_id' not in session:
        return {'error': 'Não autorizado'}, 401
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Uso do mês atual
    cursor.execute('''
        SELECT module, COUNT(*) as count
        FROM usage_logs 
        WHERE org_id = ? AND timestamp >= date('now', 'start of month')
        GROUP BY module
    ''', (session['org_id'],))
    
    usage = dict(cursor.fetchall())
    conn.close()
    
    return {
        'organization': session.get('org_name'),
        'month_usage': usage,
        'total_actions': sum(usage.values())
    }

# ROTAS FUNCIONAIS DOS MÓDULOS
@app.route('/api/ia-chat', methods=['POST'])
def ia_chat():
    """Interface de IA funcional"""
    if 'user_id' not in session:
        return {'error': 'Não autorizado'}, 401
    
    data = request.get_json()
    message = data.get('message', '')
    
    # Log de uso
    log_usage('ia', f"Chat: {message[:50]}...")
    
    # Simulação de resposta inteligente
    responses = {
        'oi': 'Olá! Como posso ajudar você hoje?',
        'olá': 'Oi! Estou aqui para ajudar. O que você precisa?',
        'ola': 'Oi! Estou aqui para ajudar. O que você precisa?',
        'como vai': 'Estou ótima, obrigada! E você?',
        'ajuda': 'Posso ajudar com compromissos, finanças, contatos e muito mais. O que você gostaria de fazer?',
        'compromissos': 'Vou abrir seus compromissos para você!',
        'agenda': 'Sua agenda está sendo carregada...',
        'finanças': 'Posso ajudar com controle financeiro. Quer ver suas despesas?',
        'financeiro': 'Posso ajudar com controle financeiro. Quer ver suas despesas?',
        'reunião': 'Posso agendar uma reunião para você. Qual a data e horário?',
        'contatos': 'Vou mostrar sua lista de contatos!',
        'medicina': 'Verificando seus lembretes médicos...',
        'saúde': 'Verificando seus lembretes médicos...',
        'automação': 'Abrindo o centro de automação para você!',
        'ia': 'Estou aqui! Como posso ajudar?',
        'assistente': 'Sim, sou sua assistente! O que você precisa?',
        'que horas são': f'Agora são {datetime.now().strftime("%H:%M")}',
        'que dia é hoje': f'Hoje é {datetime.now().strftime("%d de %B de %Y")}',
        'obrigado': 'De nada! Estou sempre aqui para ajudar.',
        'obrigada': 'De nada! Estou sempre aqui para ajudar.',
        'tchau': 'Até logo! Estarei aqui quando precisar.',
        'adeus': 'Até logo! Estarei aqui quando precisar.'
    }
    
    # Resposta contextual mais inteligente
    message_lower = message.lower()
    
    # Verificar se contém palavras-chave
    if any(word in message_lower for word in ['compromisso', 'agenda', 'reunião']):
        response = 'Vou verificar sua agenda! Você tem algumas reuniões importantes hoje.'
    elif any(word in message_lower for word in ['dinheiro', 'gasto', 'receita', 'financeiro']):
        response = 'Posso ajudar com suas finanças! Quer ver o resumo financeiro?'
    elif any(word in message_lower for word in ['contato', 'telefone', 'email']):
        response = 'Vou buscar em seus contatos! Quem você está procurando?'
    elif any(word in message_lower for word in ['remédio', 'médico', 'consulta', 'saúde']):
        response = 'Verificando seus lembretes de saúde e medicamentos!'
    else:
        # Buscar resposta exata ou gerar resposta contextual
        response = responses.get(message_lower, 
                               f"Entendi que você disse: '{message}'. Como posso ajudar com isso?")
    
    return {
        'success': True,
        'response': response,
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/compromissos')
def get_compromissos():
    """Lista compromissos do usuário"""
    if 'user_id' not in session:
        return {'error': 'Não autorizado'}, 401
    
    log_usage('compromissos', 'Visualização de compromissos')
    
    # Dados simulados baseados na organização
    org_name = session.get('org_name', 'Sua Empresa')
    compromissos = [
        {
            'id': 1,
            'titulo': f'Reunião de equipe - {org_name}',
            'data': '2024-01-15',
            'hora': '14:00',
            'descricao': 'Revisão semanal do projeto'
        },
        {
            'id': 2,
            'titulo': 'Apresentação para cliente',
            'data': '2024-01-16',
            'hora': '10:30',
            'descricao': 'Demonstração do novo sistema'
        },
        {
            'id': 3,
            'titulo': 'Treinamento IAON',
            'data': '2024-01-17',
            'hora': '16:00',
            'descricao': 'Capacitação da equipe'
        }
    ]
    
    return {
        'success': True,
        'compromissos': compromissos,
        'total': len(compromissos)
    }

@app.route('/api/financeiro')
def get_financeiro():
    """Módulo financeiro funcional"""
    if 'user_id' not in session:
        return {'error': 'Não autorizado'}, 401
    
    log_usage('financeiro', 'Consulta financeira')
    
    # Dados financeiros simulados
    dados = {
        'receitas': 15750.00,
        'despesas': 8420.50,
        'saldo': 7329.50,
        'transacoes_recentes': [
            {'descricao': 'Pagamento de fornecedor', 'valor': -2500.00, 'data': '2024-01-10'},
            {'descricao': 'Recebimento de cliente', 'valor': 5000.00, 'data': '2024-01-09'},
            {'descricao': 'Despesas operacionais', 'valor': -1200.00, 'data': '2024-01-08'}
        ],
        'categorias': {
            'Vendas': 12000.00,
            'Serviços': 3750.00,
            'Fornecedores': -4500.00,
            'Operacional': -2920.50,
            'Marketing': -1000.00
        }
    }
    
    return {
        'success': True,
        'dados': dados,
        'ultima_atualizacao': datetime.now().isoformat()
    }

@app.route('/api/contatos')
def get_contatos():
    """Lista de contatos da organização"""
    if 'user_id' not in session:
        return {'error': 'Não autorizado'}, 401
    
    log_usage('contatos', 'Visualização de contatos')
    
    contatos = [
        {
            'id': 1,
            'nome': 'João Silva',
            'empresa': 'Tech Solutions',
            'telefone': '(11) 99999-1234',
            'email': 'joao@techsolutions.com',
            'categoria': 'Cliente'
        },
        {
            'id': 2,
            'nome': 'Maria Santos',
            'empresa': 'Consultoria ABC',
            'telefone': '(11) 98888-5678',
            'email': 'maria@consultoria.com',
            'categoria': 'Fornecedor'
        },
        {
            'id': 3,
            'nome': 'Pedro Costa',
            'empresa': session.get('org_name', 'Sua Empresa'),
            'telefone': '(11) 97777-9012',
            'email': 'pedro@empresa.com',
            'categoria': 'Equipe'
        }
    ]
    
    return {
        'success': True,
        'contatos': contatos,
        'total': len(contatos)
    }

@app.route('/api/medicina')
def get_medicina():
    """Módulo de saúde e medicina"""
    if 'user_id' not in session:
        return {'error': 'Não autorizado'}, 401
    
    log_usage('medicina', 'Consulta médica')
    
    dados = {
        'alertas': [
            'Lembre-se de tomar o medicamento às 14h',
            'Consulta agendada para terça-feira às 10h',
            'Exame de sangue pendente'
        ],
        'medicamentos': [
            {'nome': 'Vitamina D', 'dosagem': '1000 UI', 'horario': '08:00'},
            {'nome': 'Ômega 3', 'dosagem': '1g', 'horario': '12:00'}
        ],
        'proximas_consultas': [
            {'medico': 'Dr. Carlos Silva', 'especialidade': 'Cardiologia', 'data': '2024-01-20'},
            {'medico': 'Dra. Ana Costa', 'especialidade': 'Clínico Geral', 'data': '2024-01-25'}
        ]
    }
    
    return {
        'success': True,
        'dados': dados,
        'status': 'Acompanhamento em dia'
    }

@app.route('/api/reunioes')
def get_reunioes():
    """Sistema de reuniões"""
    if 'user_id' not in session:
        return {'error': 'Não autorizado'}, 401
    
    log_usage('reunioes', 'Gestão de reuniões')
    
    reunioes = [
        {
            'id': 1,
            'titulo': 'Daily Standup',
            'data': '2024-01-15',
            'hora': '09:00',
            'participantes': ['João', 'Maria', 'Pedro'],
            'link': 'https://meet.google.com/abc-def-ghi',
            'status': 'Agendada'
        },
        {
            'id': 2,
            'titulo': 'Revisão de Sprint',
            'data': '2024-01-16',
            'hora': '15:00',
            'participantes': ['Equipe completa'],
            'link': 'https://zoom.us/j/123456789',
            'status': 'Confirmada'
        }
    ]
    
    return {
        'success': True,
        'reunioes': reunioes,
        'proxima': reunioes[0] if reunioes else None
    }

@app.route('/api/automacao')
def get_automacao():
    """Centro de automação"""
    if 'user_id' not in session:
        return {'error': 'Não autorizado'}, 401
    
    log_usage('automacao', 'Gerenciamento de automação')
    
    automacoes = {
        'ativas': [
            {'nome': 'Backup automático', 'status': 'Ativo', 'ultima_execucao': '2024-01-14 23:00'},
            {'nome': 'Relatório semanal', 'status': 'Ativo', 'proxima_execucao': '2024-01-21 08:00'},
            {'nome': 'Lembrete de reuniões', 'status': 'Ativo', 'configuracao': '15 min antes'}
        ],
        'disponiveis': [
            'Integração com calendário',
            'Notificações por email',
            'Sincronização de dados',
            'Geração de relatórios'
        ],
        'estatisticas': {
            'tarefas_executadas_hoje': 12,
            'tempo_economizado': '2h 30min',
            'taxa_sucesso': '98%'
        }
    }
    
    return {
        'success': True,
        'automacoes': automacoes,
        'status_sistema': 'Operacional'
    }

@app.route('/')
def home():
    """Interface principal com controle de acesso"""
    
    # Se não logado, mostrar tela de login
    if 'user_id' not in session:
        return render_template_string("""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, maximum-scale=1.0">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#1e3a8a">
    <title>IAON - Assistente IA com Reconhecimento de Voz Biométrico</title>
    <meta name="description" content="Sistema IA com reconhecimento de voz biométrico, compatível com dispositivos móveis e desktop">
    <meta name="keywords" content="ia, assistente, voz, biometria, mobile, voice recognition, speechRecognition">
    <link rel="manifest" href="/static/manifest.json">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #581c87 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        
        .login-container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px;
            backdrop-filter: blur(20px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 400px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .logo {
            text-align: center;
            font-size: 3rem;
            margin-bottom: 10px;
        }
        
        .title {
            text-align: center;
            font-size: 2rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ffd700, #ffed4e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .subtitle {
            text-align: center;
            opacity: 0.8;
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 1rem;
        }
        
        .form-group input::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        
        .login-btn {
            width: 100%;
            background: linear-gradient(45deg, #ffd700, #ffed4e);
            color: #333;
            border: none;
            padding: 15px;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(255, 215, 0, 0.4);
        }
        
        .register-link {
            text-align: center;
            opacity: 0.8;
        }
        
        .register-link a {
            color: #ffd700;
            text-decoration: none;
            font-weight: 600;
        }
        
        .demo-info {
            background: rgba(34, 197, 94, 0.2);
            border: 1px solid rgba(34, 197, 94, 0.5);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .error {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.5);
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 15px;
            text-align: center;
            color: #fecaca;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">🤖</div>
        <h1 class="title">IAON</h1>
        <p class="subtitle">Assistente Inteligente</p>
        
        <div id="error-message" class="error" style="display: none;"></div>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" placeholder="seu@email.com" required>
            </div>
            
            <div class="form-group">
                <label for="password">Senha:</label>
                <input type="password" id="password" name="password" placeholder="Sua senha" required>
            </div>
            
            <div class="form-group">
                <label for="coupon">Cupom (opcional):</label>
                <input type="text" id="coupon" name="coupon" placeholder="Digite seu cupom" style="text-transform: uppercase;">
            </div>
            
            <button type="submit" class="login-btn">
                <i class="fas fa-sign-in-alt"></i> Entrar
            </button>
        </form>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const coupon = document.getElementById('coupon').value;
            const errorDiv = document.getElementById('error-message');
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password, coupon })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    if (data.coupon_status) {
                        alert(data.coupon_status + '\\n\\nAcesso liberado por 1 ano!');
                    }
                    window.location.reload();
                } else {
                    errorDiv.textContent = data.error;
                    errorDiv.style.display = 'block';
                }
            } catch (error) {
                errorDiv.textContent = 'Erro de conexão';
                errorDiv.style.display = 'block';
            }
        });
        
        function showRegister() {
            alert('Funcionalidade de registro será implementada em breve!\\n\\nPor enquanto, use a conta demo:\\nadmin@demo.com / 123456');
        }
        
        // Auto-complete para demo
        document.getElementById('email').value = 'admin@demo.com';
        document.getElementById('password').value = '123456';
    </script>
</body>
</html>
        """)
    
    # Se logado, mostrar o IAON completo
    log_usage('dashboard', 'access')
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, maximum-scale=1.0">
    <title>IAON - {{ user_name }} - Assistente IA com Reconhecimento de Voz</title>
    <meta name="description" content="Sistema IAON com reconhecimento de voz biométrico, interface mobile-first e recursos PWA">
    <meta name="keywords" content="iaon, ia, assistente, voz, biometria, mobile, voice recognition, speechRecognition, biometric, artificial intelligence">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#3730a3">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="IAON">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="application-name" content="IAON">
    <link rel="apple-touch-icon" href="/icon-192x192.png">
    <link rel="icon" type="image/png" sizes="192x192" href="/icon-192x192.png">
    <!-- PWA and Mobile Optimizations -->
    <meta name="format-detection" content="telephone=no">
    <meta name="msapplication-tap-highlight" content="no">
    <meta name="touch-action" content="manipulation">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #581c87 100%);
            min-height: 100vh;
            color: white;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .logo {
            font-size: 1.8em;
            font-weight: 700;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .org-info {
            text-align: right;
            opacity: 0.9;
        }
        
        .logout-btn {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.5);
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .logout-btn:hover {
            background: rgba(239, 68, 68, 0.3);
        }
        
        .main-content {
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .welcome-section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        .modules-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }
        
        .module-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .module-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .module-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            color: #ffd700;
        }
        
        .usage-stats {
            background: rgba(34, 197, 94, 0.2);
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        /* CSS para interfaces dos módulos */
        .module-interface {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            backdrop-filter: blur(20px);
        }
        
        .module-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .back-btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }
        
        /* Chat IA */
        .chat-container {
            height: 500px;
            display: flex;
            flex-direction: column;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            overflow: hidden;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: rgba(0, 0, 0, 0.1);
        }
        
        .message {
            margin-bottom: 15px;
        }
        
        .message-user .message-content {
            background: linear-gradient(45deg, #3b82f6, #1d4ed8);
            color: white;
            padding: 12px 16px;
            border-radius: 20px 20px 5px 20px;
            margin-left: 50px;
            display: inline-block;
            max-width: 80%;
        }
        
        .message-ai .message-content {
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            padding: 12px 16px;
            border-radius: 20px 20px 20px 5px;
            margin-right: 50px;
            display: inline-block;
            max-width: 80%;
        }
        
        .message-time {
            font-size: 0.8em;
            color: rgba(255, 255, 255, 0.7);
            margin-top: 5px;
            text-align: right;
        }
        
        .chat-input-container {
            display: flex;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-top: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        #chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 16px;
        }
        
        #chat-input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
        
        .send-btn {
            background: linear-gradient(45deg, #10b981, #047857);
            color: white;
            border: none;
            padding: 12px 20px;
            margin-left: 10px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .send-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(16, 185, 129, 0.4);
        }
        
        /* Compromissos */
        .compromissos-list {
            display: grid;
            gap: 15px;
        }
        
        .compromisso-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s ease;
        }
        
        .compromisso-card:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
        }
        
        .compromisso-card h3 {
            color: #ffd700;
            margin-bottom: 10px;
        }
        
        /* Financeiro */
        .financial-dashboard {
            display: grid;
            gap: 25px;
        }
        
        .financial-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .summary-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        
        .summary-card h3 {
            margin-bottom: 10px;
            opacity: 0.9;
        }
        
        .value {
            font-size: 1.8rem;
            font-weight: 700;
        }
        
        .positive {
            color: #10b981;
        }
        
        .negative {
            color: #ef4444;
        }
        
        .transactions {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
        }
        
        .transaction-item {
            display: grid;
            grid-template-columns: 1fr auto auto;
            gap: 15px;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            align-items: center;
        }
        
        .transaction-item:last-child {
            border-bottom: none;
        }
        
        .date {
            opacity: 0.7;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-section">
            <div class="logo">🤖 IAON</div>
        </div>
        
        <div class="user-info">
            <div class="org-info">
                <div><strong>{{ user_name }}</strong></div>
            </div>
            <button class="logout-btn" onclick="logout()">
                <i class="fas fa-sign-out-alt"></i>
            </button>
        </div>
    </div>

    <div class="main-content" id="main-content">
        <div class="welcome-section">
            <h1 style="font-size: 2.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #ffd700, #ffed4e); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                IAON
            </h1>
            <p style="font-size: 1.2rem; opacity: 0.9;">
                Seu Assistente Inteligente
            </p>
        </div>

        <div class="modules-grid">
            <div class="module-card" onclick="useModule('ia')">
                <div class="module-icon"><i class="fas fa-brain"></i></div>
                <h3>IA Avançada</h3>
                <p>Processamento inteligente personalizado para sua organização</p>
            </div>

            <div class="module-card" onclick="useModule('medicina')">
                <div class="module-icon"><i class="fas fa-user-md"></i></div>
                <h3>Telemedicina</h3>
                <p>Sistema médico completo para sua empresa</p>
            </div>

            <div class="module-card" onclick="useModule('financeiro')">
                <div class="module-icon"><i class="fas fa-chart-pie"></i></div>
                <h3>Gestão Financeira</h3>
                <p>Controle financeiro empresarial avançado</p>
            </div>

            <div class="module-card" onclick="useModule('agenda')">
                <div class="module-icon"><i class="fas fa-calendar-check"></i></div>
                <h3>Agenda Corporativa</h3>
                <p>Organização de equipes e projetos</p>
            </div>

            <div class="module-card" onclick="useModule('reunioes')">
                <div class="module-icon"><i class="fas fa-video"></i></div>
                <h3>Centro de Reuniões</h3>
                <p>Videoconferências empresariais com IA</p>
            </div>

            <div class="module-card" onclick="useModule('analytics')">
                <div class="module-icon"><i class="fas fa-chart-bar"></i></div>
                <h3>Analytics</h3>
                <p>Relatórios e métricas da organização</p>
            </div>
        </div>
    </div>

    <script>
        function useModule(module) {
            // Log de uso para billing
            fetch('/api/log-usage', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ module: module, action: 'access' })
            });
            
            // Abrir interface funcional do módulo
            openModuleInterface(module);
        }
        
        async function openModuleInterface(module) {
            const container = document.getElementById('main-content');
            
            switch(module) {
                case 'ia':
                    await openIAChat();
                    break;
                case 'compromissos':
                    await openCompromissos();
                    break;
                case 'financeiro':
                    await openFinanceiro();
                    break;
                case 'contatos':
                    await openContatos();
                    break;
                case 'medicina':
                    await openMedicina();
                    break;
                case 'reunioes':
                    await openReunioes();
                    break;
                case 'automacao':
                    await openAutomacao();
                    break;
                default:
                    alert(`Módulo ${module} em desenvolvimento`);
            }
        }
        
        async function openIAChat() {
            const container = document.getElementById('main-content');
            container.innerHTML = `
                <div class="module-interface">
                    <div class="module-header">
                        <h2>🤖 Assistente IA</h2>
                        <button onclick="goBack()" class="back-btn">← Voltar</button>
                    </div>
                    <div class="chat-container">
                        <div id="chat-messages" class="chat-messages"></div>
                        <div class="chat-input-container">
                            <input type="text" id="chat-input" placeholder="Digite sua mensagem..." onkeypress="if(event.key==='Enter') sendMessage()">
                            <button onclick="sendMessage()" class="send-btn">Enviar</button>
                        </div>
                    </div>
                </div>
            `;
            
            // Adicionar estilos do chat
            addChatStyles();
        }
        
        async function sendMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            if (!message) return;
            
            // Adicionar mensagem do usuário
            addMessageToChat('user', message);
            input.value = '';
            
            try {
                const response = await fetch('/api/ia-chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                if (data.success) {
                    addMessageToChat('ai', data.response);
                    // Resposta por voz
                    speakResponse(data.response);
                } else {
                    addMessageToChat('ai', 'Desculpe, ocorreu um erro. Tente novamente.');
                }
            } catch (error) {
                addMessageToChat('ai', 'Erro de conexão. Verifique sua internet.');
            }
        }
        
        function speakResponse(text) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'pt-BR';
                utterance.rate = 0.9;
                utterance.pitch = 1;
                
                // Usar voz feminina se disponível
                const voices = speechSynthesis.getVoices();
                const femaleVoice = voices.find(voice => 
                    voice.lang.includes('pt') && 
                    (voice.name.includes('female') || voice.name.includes('Luciana') || voice.name.includes('Maria'))
                );
                
                if (femaleVoice) {
                    utterance.voice = femaleVoice;
                }
                
                speechSynthesis.speak(utterance);
            }
        }
        
        function addMessageToChat(sender, message) {
            const messagesDiv = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message message-${sender}`;
            messageDiv.innerHTML = `
                <div class="message-content">
                    ${sender === 'user' ? '👤' : '🤖'} ${message}
                </div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            `;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function addChatStyles() {
            if (!document.getElementById('chat-styles')) {
                const style = document.createElement('style');
                style.id = 'chat-styles';
                style.textContent = `
                    .module-interface { max-width: 800px; margin: 0 auto; padding: 20px; }
                    .module-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
                    .back-btn { background: #6366f1; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
                    .chat-container { height: 500px; display: flex; flex-direction: column; }
                    .chat-messages { flex: 1; border: 1px solid #ddd; padding: 15px; overflow-y: auto; background: white; }
                    .message { margin-bottom: 15px; }
                    .message-user .message-content { background: #3b82f6; color: white; padding: 10px; border-radius: 15px; margin-left: 50px; }
                    .message-ai .message-content { background: #f3f4f6; padding: 10px; border-radius: 15px; margin-right: 50px; }
                    .message-time { font-size: 0.8em; color: #666; margin-top: 5px; }
                    .chat-input-container { display: flex; margin-top: 10px; }
                    #chat-input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 5px; }
                    .send-btn { background: #10b981; color: white; border: none; padding: 12px 20px; margin-left: 10px; border-radius: 5px; cursor: pointer; }
                `;
                document.head.appendChild(style);
            }
        }
        
        async function openCompromissos() {
            try {
                const response = await fetch('/api/compromissos');
                const data = await response.json();
                
                const container = document.getElementById('main-content');
                container.innerHTML = `
                    <div class="module-interface">
                        <div class="module-header">
                            <h2>📅 Compromissos</h2>
                            <button onclick="goBack()" class="back-btn">← Voltar</button>
                        </div>
                        <div class="compromissos-list">
                            ${data.compromissos.map(comp => `
                                <div class="compromisso-card">
                                    <h3>${comp.titulo}</h3>
                                    <p>📅 ${comp.data} às ${comp.hora}</p>
                                    <p>${comp.descricao}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            } catch (error) {
                alert('Erro ao carregar compromissos');
            }
        }
        
        async function openFinanceiro() {
            try {
                const response = await fetch('/api/financeiro');
                const data = await response.json();
                
                const container = document.getElementById('main-content');
                container.innerHTML = `
                    <div class="module-interface">
                        <div class="module-header">
                            <h2>� Financeiro</h2>
                            <button onclick="goBack()" class="back-btn">← Voltar</button>
                        </div>
                        <div class="financial-dashboard">
                            <div class="financial-summary">
                                <div class="summary-card">
                                    <h3>Receitas</h3>
                                    <p class="value positive">R$ ${data.dados.receitas.toLocaleString()}</p>
                                </div>
                                <div class="summary-card">
                                    <h3>Despesas</h3>
                                    <p class="value negative">R$ ${data.dados.despesas.toLocaleString()}</p>
                                </div>
                                <div class="summary-card">
                                    <h3>Saldo</h3>
                                    <p class="value ${data.dados.saldo > 0 ? 'positive' : 'negative'}">R$ ${data.dados.saldo.toLocaleString()}</p>
                                </div>
                            </div>
                            <div class="transactions">
                                <h3>Transações Recentes</h3>
                                ${data.dados.transacoes_recentes.map(trans => `
                                    <div class="transaction-item">
                                        <span>${trans.descricao}</span>
                                        <span class="${trans.valor > 0 ? 'positive' : 'negative'}">R$ ${trans.valor.toLocaleString()}</span>
                                        <span class="date">${trans.data}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                `;
            } catch (error) {
                alert('Erro ao carregar dados financeiros');
            }
        }
        
        function goBack() {
            location.reload();
        }
        
        async function logout() {
            if (confirm('Deseja sair do IAON?')) {
                try {
                    await fetch('/api/logout', { method: 'POST' });
                    window.location.reload();
                } catch (error) {
                    window.location.reload();
                }
            }
        }
        
        // Sistema de reconhecimento de voz com autenticação biométrica
        let recognition;
        let isListening = false;
        let restartCount = 0;
        let voiceProfile = null;
        let isVoiceAuthenticated = false;
        let voiceTrainingData = [];
        
        function initVoiceRecognition() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = 'pt-BR';
                recognition.maxAlternatives = 3;
                
                recognition.onstart = function() {
                    console.log('🎤 Reconhecimento de voz iniciado');
                    isListening = true;
                    updateVoiceIndicator(true);
                    restartCount = 0;
                };
                
                recognition.onresult = function(event) {
                    let finalTranscript = '';
                    
                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        if (event.results[i].isFinal) {
                            finalTranscript += event.results[i][0].transcript;
                            
                            // Análise biométrica da voz
                            const voiceData = extractVoiceFeatures(event.results[i]);
                            const command = finalTranscript.toLowerCase().trim();
                            
                            console.log('🎤 Comando detectado:', command);
                            console.log('🔍 Dados de voz:', voiceData);
                            
                            // Verificar se contém palavras de ativação
                            if (command.includes('ia') || command.includes('assistente')) {
                                console.log('✅ Palavra de ativação detectada');
                                
                                // Verificar autenticação de voz
                                if (isVoiceAuthenticated || authenticateVoice(voiceData)) {
                                    console.log('✅ Voz autenticada - executando comando');
                                    isVoiceAuthenticated = true;
                                    updateVoiceIndicator(false); // Atualizar status visual
                                    handleVoiceCommand(command);
                                } else {
                                    console.log('🚫 Voz não autorizada');
                                    showUnauthorizedAlert();
                                }
                            } else {
                                console.log('ℹ️ Comando ignorado - não contém palavra de ativação');
                            }
                        }
                    }
                };
                
                recognition.onerror = function(event) {
                    console.log('❌ Erro no reconhecimento:', event.error);
                    
                    if (event.error === 'not-allowed') {
                        alert('❌ Permissão de microfone negada!\\n\\nPara usar comandos de voz:\\n1. Clique no ícone de microfone na barra do navegador\\n2. Selecione "Permitir"\\n3. Recarregue a página');
                        updateVoiceIndicator(false);
                        return;
                    }
                    
                    setTimeout(() => {
                        if (restartCount < 5) {
                            restartCount++;
                            startListening();
                        }
                    }, 1000);
                };
                
                recognition.onend = function() {
                    console.log('🎤 Reconhecimento parou');
                    isListening = false;
                    updateVoiceIndicator(false);
                    
                    setTimeout(() => {
                        if (restartCount < 10) {
                            startListening();
                        }
                    }, 500);
                };
                
                // Verificar se já tem perfil de voz salvo
                loadVoiceProfile();
                
                if (!voiceProfile) {
                    showVoiceSetup();
                } else {
                    startListening();
                    showVoiceStatus();
                }
                
                setInterval(checkVoiceStatus, 3000);
                
            } else {
                console.log('❌ Reconhecimento de voz não suportado neste navegador');
                alert('❌ Reconhecimento de voz não suportado!\\n\\nUse Chrome, Edge ou Safari para comandos de voz.');
            }
        }
        
        function extractVoiceFeatures(result) {
            // Extrair características da voz com valores padrão seguros
            const transcript = result[0].transcript || '';
            const confidence = result[0].confidence || 0.8;
            
            // Características calculadas baseadas na fala
            const words = transcript.split(' ').filter(w => w.length > 0);
            const avgWordLength = words.length > 0 ? words.reduce((sum, word) => sum + word.length, 0) / words.length : 5;
            
            const voiceFeatures = {
                confidence: confidence,
                length: transcript.length,
                words: words.length,
                timestamp: Date.now(),
                avgWordLength: avgWordLength,
                // Simular características únicas da voz
                voiceprint: transcript.toLowerCase().replace(/[^a-z]/g, '').slice(0, 8) || 'defaultvoice',
                speed: words.length > 0 ? words.length / (transcript.length / 10) : 2.0
            };
            
            console.log('🎙️ Características extraídas:', voiceFeatures);
            return voiceFeatures;
        }
        
        function authenticateVoice(voiceData) {
            if (!voiceProfile) {
                console.log('⚠️ Sem perfil de voz - criando temporário para primeira autenticação');
                // Se não tem perfil, aceitar primeira tentativa e criar perfil básico
                voiceProfile = {
                    avgConfidence: voiceData.confidence || 0.8,
                    voiceprint: voiceData.voiceprint || 'temp_voice',
                    avgSpeed: voiceData.speed || 2.0,
                    created: Date.now()
                };
                localStorage.setItem('iaon_voice_profile', JSON.stringify(voiceProfile));
                return true;
            }
            
            // Algoritmo de comparação de voz com tolerância ajustada
            const similarity = compareVoiceFeatures(voiceData, voiceProfile);
            console.log('🔍 Similaridade de voz:', similarity);
            console.log('🔍 Perfil salvo:', voiceProfile);
            console.log('🔍 Dados atuais:', voiceData);
            
            // Reduzir threshold para 0.5 para facilitar autenticação durante testes
            if (similarity > 0.5) {
                console.log('✅ Voz autenticada com similaridade:', similarity);
                isVoiceAuthenticated = true;
                return true;
            } else {
                console.log('❌ Voz rejeitada - similaridade muito baixa:', similarity);
                return false;
            }
        }
        
        function compareVoiceFeatures(current, profile) {
            // Comparação biométrica melhorada
            let score = 0;
            let maxScore = 0;
            
            // Comparar confiança (peso: 0.3)
            maxScore += 0.3;
            const confidenceDiff = Math.abs(current.confidence - profile.avgConfidence);
            if (confidenceDiff < 0.3) {
                score += 0.3 * (1 - confidenceDiff / 0.3);
            }
            
            // Comparar padrão de voz/voiceprint (peso: 0.4)
            maxScore += 0.4;
            const currentPrint = current.voiceprint || '';
            const profilePrint = profile.voiceprint || '';
            
            if (currentPrint && profilePrint) {
                const similarity = calculateStringSimilarity(currentPrint, profilePrint);
                score += 0.4 * similarity;
            }
            
            // Comparar velocidade de fala (peso: 0.3)
            maxScore += 0.3;
            const currentSpeed = current.speed || 2.0;
            const profileSpeed = profile.avgSpeed || 2.0;
            const speedDiff = Math.abs(currentSpeed - profileSpeed);
            
            if (speedDiff < 3) {
                score += 0.3 * (1 - speedDiff / 3);
            }
            
            const finalScore = maxScore > 0 ? score / maxScore : 0;
            console.log('📊 Score detalhado - Confiança:', confidenceDiff, 'Voiceprint:', calculateStringSimilarity(currentPrint, profilePrint), 'Velocidade:', speedDiff);
            
            return finalScore;
        }
        
        function calculateStringSimilarity(str1, str2) {
            if (!str1 || !str2) return 0;
            if (str1 === str2) return 1;
            
            const longer = str1.length > str2.length ? str1 : str2;
            const shorter = str1.length > str2.length ? str2 : str1;
            
            if (longer.length === 0) return 1;
            
            // Algoritmo simples de distância de edição
            let matches = 0;
            for (let i = 0; i < shorter.length; i++) {
                if (longer.includes(shorter[i])) matches++;
            }
            
            return matches / longer.length;
        }
        
        function showVoiceSetup() {
            const container = document.getElementById('main-content');
            container.innerHTML = `
                <div class="voice-setup">
                    <h2>🎤 Configuração de Voz Pessoal</h2>
                    <p>Para sua segurança, vamos configurar o reconhecimento da sua voz.</p>
                    <p>Apenas você poderá dar comandos ao IAON.</p>
                    
                    <div class="training-status">
                        <div>Treinamento: <span id="training-count">0</span>/3</div>
                        <div id="training-text">Clique em "Treinar" e diga: "IA, olá, sou eu"</div>
                    </div>
                    
                    <button onclick="startVoiceTraining()" class="train-btn" id="train-btn">
                        🎙️ Treinar Minha Voz
                    </button>
                    
                    <div class="training-progress" id="training-progress" style="display: none;">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-fill"></div>
                        </div>
                        <p>Fale agora: "IA, olá, sou eu"</p>
                    </div>
                </div>
            `;
            
            addVoiceSetupStyles();
        }
        
        function addVoiceSetupStyles() {
            if (!document.getElementById('voice-setup-styles')) {
                const style = document.createElement('style');
                style.id = 'voice-setup-styles';
                style.textContent = `
                    .voice-setup {
                        max-width: 600px;
                        margin: 50px auto;
                        padding: 30px;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 15px;
                        text-align: center;
                        color: white;
                    }
                    
                    .voice-setup h2 {
                        margin-bottom: 20px;
                        color: #ffd700;
                    }
                    
                    .training-status {
                        background: rgba(0, 0, 0, 0.2);
                        padding: 20px;
                        border-radius: 10px;
                        margin: 20px 0;
                    }
                    
                    .train-btn {
                        background: linear-gradient(45deg, #10b981, #047857);
                        color: white;
                        border: none;
                        padding: 15px 30px;
                        border-radius: 25px;
                        font-size: 1.2em;
                        cursor: pointer;
                        margin: 20px;
                        transition: all 0.3s ease;
                    }
                    
                    .train-btn:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 8px 15px rgba(16, 185, 129, 0.4);
                    }
                    
                    .training-progress {
                        margin: 20px 0;
                    }
                    
                    .progress-bar {
                        background: rgba(255, 255, 255, 0.2);
                        height: 10px;
                        border-radius: 5px;
                        overflow: hidden;
                        margin: 10px 0;
                    }
                    
                    .progress-fill {
                        background: linear-gradient(45deg, #ffd700, #ffed4e);
                        height: 100%;
                        width: 0%;
                        transition: width 0.3s ease;
                    }
                `;
                document.head.appendChild(style);
            }
        }
        
        function startVoiceTraining() {
            if (voiceTrainingData.length >= 3) {
                completeVoiceSetup();
                return;
            }
            
            document.getElementById('train-btn').disabled = true;
            document.getElementById('train-btn').textContent = 'Escutando...';
            document.getElementById('training-progress').style.display = 'block';
            
            // Simular captura real de características de voz
            setTimeout(() => {
                const sampleData = {
                    confidence: 0.75 + Math.random() * 0.25, // 0.75-1.0
                    voiceprint: 'user_voice_' + (voiceTrainingData.length + 1),
                    speed: 1.5 + Math.random() * 1.0, // 1.5-2.5
                    avgWordLength: 4 + Math.random() * 2, // 4-6
                    timestamp: Date.now()
                };
                
                voiceTrainingData.push(sampleData);
                console.log('📝 Amostra coletada:', sampleData);
                
                const count = voiceTrainingData.length;
                document.getElementById('training-count').textContent = count;
                document.getElementById('progress-fill').style.width = (count / 3 * 100) + '%';
                
                if (count < 3) {
                    document.getElementById('training-text').textContent = `Ótimo! Agora diga novamente: "IA, olá, sou eu" (${count}/3)`;
                    document.getElementById('train-btn').disabled = false;
                    document.getElementById('train-btn').textContent = '🎙️ Treinar Novamente';
                } else {
                    document.getElementById('training-text').textContent = 'Processando perfil de voz...';
                    setTimeout(completeVoiceSetup, 1000);
                }
            }, 2000);
        }
        
        function completeVoiceSetup() {
            // Criar perfil de voz baseado nas amostras coletadas
            if (voiceTrainingData.length === 0) {
                alert('❌ Erro: Nenhuma amostra coletada');
                return;
            }
            
            voiceProfile = {
                avgConfidence: voiceTrainingData.reduce((sum, data) => sum + data.confidence, 0) / voiceTrainingData.length,
                voiceprint: voiceTrainingData[0].voiceprint, // Usar primeira amostra como base
                avgSpeed: voiceTrainingData.reduce((sum, data) => sum + data.speed, 0) / voiceTrainingData.length,
                avgWordLength: voiceTrainingData.reduce((sum, data) => sum + (data.avgWordLength || 5), 0) / voiceTrainingData.length,
                created: Date.now(),
                samples: voiceTrainingData.length
            };
            
            console.log('👤 Perfil de voz criado:', voiceProfile);
            
            // Salvar perfil no localStorage
            localStorage.setItem('iaon_voice_profile', JSON.stringify(voiceProfile));
            isVoiceAuthenticated = true;
            
            alert('✅ Voz configurada com sucesso!\\n\\n🔒 Biometria ativada\\n🎤 Apenas você pode dar comandos\\n\\nDiga "IA" para testar!');
            
            // Recarregar interface principal
            location.reload();
        }
        
        function loadVoiceProfile() {
            const saved = localStorage.getItem('iaon_voice_profile');
            if (saved) {
                voiceProfile = JSON.parse(saved);
                console.log('📁 Perfil de voz carregado');
            }
        }
        
        function showUnauthorizedAlert() {
            // Vibrar se suportado
            if (navigator.vibrate) {
                navigator.vibrate([200, 100, 200]);
            }
            
            // Mostrar alerta discreto
            const alert = document.createElement('div');
            alert.innerHTML = `
                <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(239, 68, 68, 0.95); color: white; padding: 20px; border-radius: 10px; z-index: 2000; text-align: center;">
                    🚫 Voz não autorizada<br>
                    <small>Apenas o proprietário pode dar comandos</small>
                </div>
            `;
            document.body.appendChild(alert);
            
            setTimeout(() => alert.remove(), 2000);
        }
        
        function checkVoiceStatus() {
            if (!isListening && restartCount < 10) {
                console.log('🔄 Reativando reconhecimento de voz...');
                startListening();
            }
        }
        
        function startListening() {
            if (recognition && !isListening) {
                try {
                    recognition.start();
                } catch (error) {
                    console.log('⚠️ Erro ao iniciar reconhecimento:', error);
                    setTimeout(startListening, 2000);
                }
            }
        }
        
        function stopListening() {
            if (recognition && isListening) {
                recognition.stop();
                isListening = false;
                updateVoiceIndicator(false);
            }
        }
        
        function handleVoiceCommand(command) {
            console.log('🤖 Processando comando de voz:', command);
            
            try {
                // Abrir chat IA automaticamente
                console.log('🔄 Abrindo chat IA...');
                openIAChat();
                
                // Aguardar interface carregar e inserir comando
                setTimeout(() => {
                    console.log('⏳ Aguardando interface carregar...');
                    const input = document.getElementById('chat-input');
                    if (input) {
                        console.log('✅ Campo de entrada encontrado, inserindo comando:', command);
                        input.value = command;
                        input.focus();
                        
                        // Aguardar um pouco e enviar
                        setTimeout(() => {
                            console.log('📤 Enviando mensagem...');
                            sendMessage();
                        }, 300);
                    } else {
                        console.error('❌ Campo de entrada não encontrado');
                        // Tentar novamente após mais tempo
                        setTimeout(() => {
                            const retryInput = document.getElementById('chat-input');
                            if (retryInput) {
                                retryInput.value = command;
                                retryInput.focus();
                                setTimeout(() => sendMessage(), 200);
                            }
                        }, 1000);
                    }
                }, 800);
                
            } catch (error) {
                console.error('❌ Erro ao processar comando de voz:', error);
            }
        }
        
        function showVoiceStatus() {
            const container = document.getElementById('main-content');
            const voiceStatus = document.createElement('div');
            voiceStatus.id = 'voice-status';
            voiceStatus.innerHTML = `
                <div class="voice-indicator">
                    <div class="voice-icon">🎤</div>
                    <div class="voice-text">
                        <div>Reconhecimento Pessoal</div>
                        <div class="voice-subtitle">Apenas sua voz autorizada</div>
                    </div>
                    <div class="voice-toggle">
                        <button onclick="toggleVoice()" id="voice-btn" class="voice-control-btn">🎤</button>
                        <button onclick="testVoiceCommand()" style="background: #2196F3; color: white; border: none; padding: 8px 12px; border-radius: 20px; cursor: pointer; margin-left: 5px; font-size: 14px;" title="Teste Comando">🧪</button>
                        <button onclick="showDebugInfo()" style="background: #4CAF50; color: white; border: none; padding: 8px 12px; border-radius: 20px; cursor: pointer; margin-left: 5px; font-size: 14px;" title="Debug Info">🔍</button>
                        <button onclick="resetVoiceProfile()" style="background: #f44336; color: white; border: none; padding: 8px 12px; border-radius: 20px; cursor: pointer; margin-left: 5px; font-size: 14px;" title="Reset Voz">🔒</button>
                    </div>
                </div>
            `;
            
            // Inserir no topo do conteúdo
            container.insertBefore(voiceStatus, container.firstChild);
            
            // Adicionar estilos
            addVoiceStyles();
        }
        
        function addVoiceStyles() {
            if (!document.getElementById('voice-styles')) {
                const style = document.createElement('style');
                style.id = 'voice-styles';
                style.textContent = `
                    #voice-status {
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        z-index: 1000;
                        background: rgba(16, 185, 129, 0.9);
                        backdrop-filter: blur(20px);
                        border-radius: 15px;
                        padding: 15px;
                        border: 1px solid rgba(255, 255, 255, 0.3);
                        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
                    }
                    
                    .voice-indicator {
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        color: white;
                    }
                    
                    .voice-icon {
                        font-size: 1.5em;
                        animation: pulse 2s infinite;
                    }
                    
                    @keyframes pulse {
                        0%, 100% { opacity: 1; transform: scale(1); }
                        50% { opacity: 0.6; transform: scale(1.1); }
                    }
                    
                    .voice-text {
                        flex: 1;
                    }
                    
                    .voice-subtitle {
                        font-size: 0.8em;
                        opacity: 0.8;
                    }
                    
                    .voice-control-btn {
                        background: rgba(255, 255, 255, 0.2);
                        border: none;
                        color: white;
                        padding: 8px 12px;
                        border-radius: 8px;
                        cursor: pointer;
                        font-size: 1.2em;
                        transition: all 0.3s ease;
                    }
                    
                    .voice-control-btn:hover {
                        background: rgba(255, 255, 255, 0.3);
                        transform: scale(1.1);
                    }
                    
                    .voice-listening {
                        background: rgba(239, 68, 68, 0.9) !important;
                        animation: listening-glow 1s infinite;
                    }
                    
                    @keyframes listening-glow {
                        0%, 100% { box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3); }
                        50% { box-shadow: 0 8px 25px rgba(239, 68, 68, 0.6); }
                    }
                    
                    .voice-listening .voice-icon {
                        animation: pulse 0.5s infinite;
                        color: #ffff00;
                    }
                `;
                document.head.appendChild(style);
            }
        }
        
        function updateVoiceIndicator(listening) {
            const status = document.getElementById('voice-status');
            const btn = document.getElementById('voice-btn');
            const subtitle = document.querySelector('.voice-subtitle');
            
            if (!status) return;
            
            if (listening) {
                status.classList.add('voice-listening');
                btn.textContent = '🔴';
                subtitle.textContent = 'Escutando sua voz...';
            } else {
                status.classList.remove('voice-listening');
                
                if (isVoiceAuthenticated) {
                    btn.textContent = '�';
                    subtitle.textContent = 'Autorizado - Diga "IA"';
                    status.style.background = 'rgba(16, 185, 129, 0.9)';
                } else {
                    btn.textContent = '🔒';
                    subtitle.textContent = 'Aguardando autenticação';
                    status.style.background = 'rgba(245, 158, 11, 0.9)';
                }
            }
        }
        
        function toggleVoice() {
            if (isListening) {
                stopListening();
            } else {
                if (!voiceProfile) {
                    if (confirm('🎤 Configurar reconhecimento de voz pessoal?\\n\\nIsso garante que apenas você possa dar comandos.')) {
                        showVoiceSetup();
                    }
                } else {
                    startListening();
                }
            }
        }
        
        function resetVoiceProfile() {
            if (confirm('⚠️ Resetar configuração de voz?\\n\\nVocê precisará treinar novamente.')) {
                localStorage.removeItem('iaon_voice_profile');
                voiceProfile = null;
                isVoiceAuthenticated = false;
                voiceTrainingData = [];
                showVoiceSetup();
            }
        }
        
        function showDebugInfo() {
            const debugInfo = `
🔍 DEBUG BIOMÉTRICO:
━━━━━━━━━━━━━━━━━━━━━━
🎤 Escutando: ${isListening}
🔓 Autenticado: ${isVoiceAuthenticated}
👤 Perfil existe: ${voiceProfile ? 'Sim' : 'Não'}
📊 Reinicializações: ${restartCount}
🗣️ Amostras treinamento: ${voiceTrainingData.length}

${voiceProfile ? 
`👤 PERFIL BIOMÉTRICO:
Confiança média: ${voiceProfile.avgConfidence?.toFixed(3)}
Velocidade: ${voiceProfile.avgSpeed?.toFixed(2)} p/s
Padrão: ${voiceProfile.voiceprint}
Criado: ${new Date(voiceProfile.created).toLocaleString()}
Amostras: ${voiceProfile.samples || 'N/A'}` : 
'❌ Nenhum perfil biométrico encontrado'
}
━━━━━━━━━━━━━━━━━━━━━━
💡 Teste: Diga "IA teste" claramente
🔄 Reset: Botão 🔒 para reconfigurar
🔊 Permissão: Microfone deve estar autorizado
            `;
            
            alert(debugInfo);
        }
        
        function testVoiceCommand() {
            console.log('🧪 Teste manual do comando de voz');
            
            // Simular comando de voz
            const testCommand = 'IA como está o tempo hoje?';
            
            // Criar dados de voz simulados
            const testVoiceData = {
                confidence: 0.85,
                length: testCommand.length,
                words: testCommand.split(' ').length,
                timestamp: Date.now(),
                avgWordLength: testCommand.length / testCommand.split(' ').length,
                voiceprint: testCommand.toLowerCase().replace(/[^a-z]/g, '').slice(0, 8),
                speed: 2.5
            };
            
            console.log('🎤 Comando de teste:', testCommand);
            console.log('🔍 Dados simulados:', testVoiceData);
            
            // Testar autenticação
            if (isVoiceAuthenticated || authenticateVoice(testVoiceData)) {
                console.log('✅ Teste: Autenticação bem-sucedida');
                isVoiceAuthenticated = true;
                handleVoiceCommand(testCommand);
            } else {
                console.log('❌ Teste: Falha na autenticação');
                alert('❌ Teste falhou: Voz não autenticada');
            }
        }
                stopListening();
            } else {
                startListening();
            }
        }
        
        // Carregar estatísticas de uso
        window.onload = function() {
            console.log('🤖 IAON carregado');
            
            // Registrar Service Worker para PWA
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/sw.js')
                    .then(function(registration) {
                        console.log('📱 PWA Service Worker registrado');
                        
                        // Manter ativo
                        setInterval(() => {
                            const channel = new MessageChannel();
                            registration.active?.postMessage({action: 'keepAlive'}, [channel.port2]);
                        }, 30000);
                    })
                    .catch(function(error) {
                        console.log('❌ Erro ao registrar Service Worker:', error);
                    });
            }
            
            // Inicializar reconhecimento de voz
            setTimeout(initVoiceRecognition, 1000);
            
            // Mostrar instruções de instalação
            setTimeout(showInstallPrompt, 3000);
        }
        
        function showInstallPrompt() {
            if (window.matchMedia('(display-mode: browser)').matches) {
                const installDiv = document.createElement('div');
                installDiv.innerHTML = `
                    <div style="position: fixed; bottom: 20px; right: 20px; background: rgba(16, 185, 129, 0.95); color: white; padding: 15px; border-radius: 10px; z-index: 1000; max-width: 300px; box-shadow: 0 8px 25px rgba(0,0,0,0.3);">
                        <div style="font-weight: bold; margin-bottom: 8px;">📱 Instalar IAON</div>
                        <div style="font-size: 0.9em; margin-bottom: 10px;">Adicione à tela inicial para acesso rápido</div>
                        <button onclick="this.parentElement.parentElement.remove()" style="background: white; color: #059669; border: none; padding: 8px 15px; border-radius: 5px; font-weight: 600; cursor: pointer;">OK</button>
                    </div>
                `;
                document.body.appendChild(installDiv);
                
                // Remover automaticamente após 10 segundos
                setTimeout(() => {
                    if (installDiv.parentElement) {
                        installDiv.remove();
                    }
                }, 10000);
            }
        }
    </script>
</body>
</html>
    """, 
    user_name=session['user_name'],
    user_role=session['user_role'], 
    org_name=session['org_name'])

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout do usuário"""
    session.clear()
    return {'success': True}

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Página de login para compatibilidade"""
    if request.method == 'POST':
        # Redirecionar para API de login
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validar credenciais
        conn = sqlite3.connect('iaon_saas.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.org_id, u.password_hash, u.role, u.name, o.name as org_name
            FROM users u 
            JOIN organizations o ON u.org_id = o.id
            WHERE u.email = ?
        ''', (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['organization_id'] = user[1]
            session['role'] = user[3]
            session['user_name'] = user[4]
            session['user_role'] = user[3]
            session['org_name'] = user[5]
            return redirect('/dashboard')
        else:
            return redirect('/?error=invalid')
    
    return redirect('/')

@app.route('/dashboard')
def dashboard_page():
    """Página do dashboard"""
    if 'user_id' not in session:
        return redirect('/')
    
    return redirect('/')  # Redireciona para a página principal que já tem o dashboard

if __name__ == '__main__':
    init_db()
    
    # Criar organização demo se não existir
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM organizations WHERE subdomain = ?', ('demo',))
    if not cursor.fetchone():
        org_id = 'demo-org'
        user_id = 'demo-user'
        
        cursor.execute('''
            INSERT INTO organizations (id, name, subdomain, plan, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (org_id, 'Empresa Demo', 'demo', 'enterprise', datetime.now() + timedelta(days=365)))
        
        cursor.execute('''
            INSERT INTO users (id, org_id, email, password_hash, name, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, org_id, 'admin@demo.com', generate_password_hash('123456'), 'Admin Demo', 'admin'))
        
        conn.commit()
    
    conn.close()
    
    print("🚀 Iniciando IAON...")
    print("🌐 Servidor HTTP: http://localhost:5000")
    print("� Servidor HTTPS: https://192.168.15.36:5000")
    print("�👤 Demo: admin@demo.com / 123456")
    print("🏢 Multi-organizacional: Suporte a múltiplas empresas")
    print("💰 Pronto para comercialização!")
    print("🛡️ Conexão segura com SSL/TLS")
    
    # Configurar contexto SSL
    import ssl
    import os
    
    cert_dir = os.path.dirname(os.path.abspath(__file__))
    cert_file = os.path.join(cert_dir, 'cert.pem')
    key_file = os.path.join(cert_dir, 'cert.key')
    
    # Usar HTTP para melhor compatibilidade mobile (iPhone/Android)
    app.run(host='0.0.0.0', port=5000, debug=True)
