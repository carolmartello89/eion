import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.reuniao import reuniao_bp
from src.routes.compromisso import compromisso_bp
from src.routes.contato import contato_bp
from src.routes.assistente import assistente_bp
from src.routes.assistente_advanced import assistente_advanced_bp
from src.routes.meetings_advanced import meetings_advanced_bp
from src.routes.analytics import analytics_bp
from src.routes.automation import automation_bp
from src.routes.memoria import memoria_bp
from src.routes.financeiro import financeiro_bp
from src.routes.voice_auth import voice_auth_bp
from src.routes.access_control import access_control_bp
from src.routes.subscription import subscription_bp
from src.routes.secretaria_executiva import secretaria_bp
from src.routes.health_monitoring import health_bp
from src.routes.sistema_medico_completo import medico_bp
from src.routes.financeiro_completo import financeiro_completo_bp
from src.utils.init_auth import init_auth_user
from src.utils.init_commercial import inicializar_sistema_comercial

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensões
CORS(app, origins="*")
jwt = JWTManager(app)
db.init_app(app)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(reuniao_bp, url_prefix='/api/reunioes')
app.register_blueprint(compromisso_bp, url_prefix='/api/compromissos')
app.register_blueprint(contato_bp, url_prefix='/api/contatos')
app.register_blueprint(assistente_bp, url_prefix='/api/assistente')
app.register_blueprint(assistente_advanced_bp, url_prefix='/api/assistente-advanced')
app.register_blueprint(meetings_advanced_bp, url_prefix='/api/meetings-advanced')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(automation_bp, url_prefix='/api/automation')
app.register_blueprint(memoria_bp, url_prefix='/api/memoria')
app.register_blueprint(financeiro_bp, url_prefix='/api/financeiro')
app.register_blueprint(voice_auth_bp, url_prefix='/api/voice-auth')
app.register_blueprint(access_control_bp, url_prefix='/api/access-control')
app.register_blueprint(subscription_bp, url_prefix='/api/subscription')
app.register_blueprint(secretaria_bp, url_prefix='/api/secretaria')
app.register_blueprint(health_bp, url_prefix='/api/health')
app.register_blueprint(medico_bp, url_prefix='/api/medico')
app.register_blueprint(financeiro_completo_bp, url_prefix='/api/financeiro')

# Inicializar banco de dados
with app.app_context():
    # Criar diretório do banco se não existir
    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    db.create_all()
    # Inicializa usuário de autenticação
    init_auth_user()
    # Inicializa sistema comercial
    inicializar_sistema_comercial()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve arquivos estáticos do frontend"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health')
def health_check():
    """Endpoint de verificação de saúde"""
    return {'status': 'ok', 'message': 'IA Backend funcionando!'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

