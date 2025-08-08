from flask import Blueprint, request, jsonify, current_app
from src.models.user import db
from src.models.auth import AuthUser
from functools import wraps
import jwt

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    """Decorator para proteger rotas que requerem autenticação"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verifica se o token está no header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'erro': 'Token inválido'}), 401
        
        if not token:
            return jsonify({'erro': 'Token de acesso necessário'}), 401
        
        try:
            # Verifica o token
            payload = AuthUser.verify_token(token, current_app.config['SECRET_KEY'])
            if payload is None:
                return jsonify({'erro': 'Token inválido ou expirado'}), 401
            
            # Busca o usuário
            current_user = AuthUser.query.filter_by(id=payload['user_id']).first()
            if not current_user or not current_user.is_active:
                return jsonify({'erro': 'Usuário não encontrado ou inativo'}), 401
            
        except Exception as e:
            return jsonify({'erro': 'Token inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para fazer login"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'erro': 'Email e senha são obrigatórios'}), 400
        
        email = data.get('email').lower().strip()
        password = data.get('password')
        
        # Busca o usuário
        user = AuthUser.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'erro': 'Email ou senha incorretos'}), 401
        
        if not user.is_active:
            return jsonify({'erro': 'Conta desativada'}), 401
        
        # Gera token
        token = user.generate_token(current_app.config['SECRET_KEY'])
        
        # Atualiza último login
        user.update_last_login()
        
        return jsonify({
            'token': token,
            'user': user.to_dict(),
            'mensagem': 'Login realizado com sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token_route(current_user):
    """Endpoint para verificar se o token é válido"""
    return jsonify({
        'valid': True,
        'user': current_user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Endpoint para fazer logout (apenas confirma que o token é válido)"""
    return jsonify({'mensagem': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """Endpoint para alterar senha"""
    try:
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({'erro': 'Senha atual e nova senha são obrigatórias'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # Verifica senha atual
        if not current_user.check_password(current_password):
            return jsonify({'erro': 'Senha atual incorreta'}), 401
        
        # Valida nova senha
        if len(new_password) < 6:
            return jsonify({'erro': 'Nova senha deve ter pelo menos 6 caracteres'}), 400
        
        # Atualiza senha
        current_user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'mensagem': 'Senha alterada com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Endpoint para obter perfil do usuário"""
    return jsonify({
        'user': current_user.to_dict()
    }), 200

