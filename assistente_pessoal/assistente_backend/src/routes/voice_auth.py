from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from src.services.voice_auth_service import VoiceAuthService
from src.models.voice_profile import VoiceProfile

logger = logging.getLogger(__name__)

voice_auth_bp = Blueprint('voice_auth', __name__)
voice_auth_service = VoiceAuthService()

@voice_auth_bp.route('/voice-profile/status', methods=['GET'])
@jwt_required()
def get_voice_profile_status():
    """Retorna status do perfil de voz do usuário"""
    try:
        user_id = get_jwt_identity()
        status = voice_auth_service.get_voice_profile_status(user_id)
        
        return jsonify({
            'success': True,
            'profile': status
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter status do perfil: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

@voice_auth_bp.route('/voice-profile/train', methods=['POST'])
@jwt_required()
def train_voice_profile():
    """Treina perfil de voz com amostras de áudio"""
    try:
        user_id = get_jwt_identity()
        
        # Verifica se há arquivos de áudio
        if 'audio_samples' not in request.files:
            return jsonify({
                'success': False,
                'erro': 'Nenhuma amostra de áudio fornecida'
            }), 400
        
        audio_files = request.files.getlist('audio_samples')
        
        if len(audio_files) < 3:
            return jsonify({
                'success': False,
                'erro': 'Mínimo de 3 amostras de áudio necessárias'
            }), 400
        
        # Processa amostras de áudio
        audio_samples = []
        for audio_file in audio_files:
            if audio_file.filename != '':
                audio_data = audio_file.read()
                audio_samples.append(audio_data)
        
        # Treina perfil
        result = voice_auth_service.train_voice_profile(user_id, audio_samples)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'samples_processed': result['samples_processed']
            }), 200
        else:
            return jsonify({
                'success': False,
                'erro': result['message'],
                'samples_processed': result.get('samples_processed', 0)
            }), 400
            
    except Exception as e:
        logger.error(f"Erro ao treinar perfil de voz: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

@voice_auth_bp.route('/voice-profile/authenticate', methods=['POST'])
@jwt_required()
def authenticate_voice():
    """Autentica usuário por voz"""
    try:
        user_id = get_jwt_identity()
        
        # Verifica se há arquivo de áudio
        if 'audio' not in request.files:
            return jsonify({
                'authenticated': False,
                'erro': 'Nenhum áudio fornecido'
            }), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({
                'authenticated': False,
                'erro': 'Arquivo de áudio inválido'
            }), 400
        
        audio_data = audio_file.read()
        
        # Autentica por voz
        result = voice_auth_service.authenticate_voice(user_id, audio_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erro na autenticação por voz: {e}")
        return jsonify({
            'authenticated': False,
            'erro': 'Erro interno do servidor'
        }), 500

@voice_auth_bp.route('/voice-profile/settings', methods=['PUT'])
@jwt_required()
def update_voice_settings():
    """Atualiza configurações do perfil de voz"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'erro': 'Dados não fornecidos'
            }), 400
        
        result = voice_auth_service.update_voice_profile_settings(user_id, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Erro ao atualizar configurações: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

@voice_auth_bp.route('/voice-profile/quick-auth', methods=['POST'])
def quick_voice_auth():
    """Autenticação rápida por voz (sem JWT) para wake word"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({
                'authenticated': False,
                'erro': 'Email não fornecido'
            }), 400
        
        # Busca usuário por email
        from src.models.user import User
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({
                'authenticated': False,
                'erro': 'Usuário não encontrado'
            }), 404
        
        # Verifica se há áudio em base64
        if 'audio_base64' not in data:
            return jsonify({
                'authenticated': False,
                'erro': 'Áudio não fornecido'
            }), 400
        
        import base64
        try:
            audio_data = base64.b64decode(data['audio_base64'])
        except Exception:
            return jsonify({
                'authenticated': False,
                'erro': 'Áudio inválido'
            }), 400
        
        # Autentica por voz
        result = voice_auth_service.authenticate_voice(user.id, audio_data)
        
        # Se autenticado, gera token JWT
        if result['authenticated']:
            from flask_jwt_extended import create_access_token
            access_token = create_access_token(identity=user.id)
            
            # Busca nome preferido
            voice_profile = VoiceProfile.query.filter_by(user_id=user.id).first()
            preferred_name = voice_profile.preferred_name if voice_profile else user.email.split('@')[0]
            
            return jsonify({
                'authenticated': True,
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'preferred_name': preferred_name
                },
                'confidence': result['confidence']
            }), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        logger.error(f"Erro na autenticação rápida por voz: {e}")
        return jsonify({
            'authenticated': False,
            'erro': 'Erro interno do servidor'
        }), 500

@voice_auth_bp.route('/voice-profile/wake-word-test', methods=['POST'])
@jwt_required()
def test_wake_word():
    """Testa detecção da palavra-chave 'IA'"""
    try:
        user_id = get_jwt_identity()
        
        if 'audio' not in request.files:
            return jsonify({
                'detected': False,
                'erro': 'Nenhum áudio fornecido'
            }), 400
        
        audio_file = request.files['audio']
        audio_data = audio_file.read()
        
        # Simula detecção de wake word (implementar com modelo específico)
        # Por enquanto, sempre retorna True para testes
        
        return jsonify({
            'detected': True,
            'confidence': 0.95,
            'message': 'Palavra-chave "IA" detectada'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no teste de wake word: {e}")
        return jsonify({
            'detected': False,
            'erro': 'Erro interno do servidor'
        }), 500

@voice_auth_bp.route('/voice-profile/setup-wizard', methods=['POST'])
@jwt_required()
def setup_wizard():
    """Wizard de configuração inicial do perfil de voz"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'erro': 'Dados não fornecidos'
            }), 400
        
        # Cria ou atualiza perfil de voz
        voice_profile = VoiceProfile.query.filter_by(user_id=user_id).first()
        if not voice_profile:
            voice_profile = VoiceProfile(user_id=user_id)
            from src.models.user import db
            db.session.add(voice_profile)
        
        # Configurações iniciais
        if 'preferred_name' in data:
            voice_profile.preferred_name = data['preferred_name']
        
        if 'voice_activation_enabled' in data:
            voice_profile.voice_activation_enabled = data['voice_activation_enabled']
        
        if 'confidence_threshold' in data:
            voice_profile.confidence_threshold = float(data['confidence_threshold'])
        
        if 'wake_word_sensitivity' in data:
            voice_profile.wake_word_sensitivity = float(data['wake_word_sensitivity'])
        
        from src.models.user import db
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Configuração inicial concluída',
            'profile': voice_profile.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no wizard de configuração: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

