from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime

from src.models.access_control import (
    Invite, UserAccess, AccessRequest, AdminSettings,
    InviteStatus, UserStatus, AccessLevel
)
from src.models.user import User, db

logger = logging.getLogger(__name__)

access_control_bp = Blueprint('access_control', __name__)

# ==================== ROTAS DE CONVITES ====================

@access_control_bp.route('/invites/create', methods=['POST'])
@jwt_required()
def create_invite():
    """Cria novo convite (apenas admins)"""
    try:
        user_id = get_jwt_identity()
        user_access = UserAccess.query.filter_by(user_id=user_id).first()
        
        # Verifica se é admin
        if not user_access or user_access.access_level != AccessLevel.ADMIN:
            return jsonify({
                'success': False,
                'erro': 'Apenas administradores podem criar convites'
            }), 403
        
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({
                'success': False,
                'erro': 'Email é obrigatório'
            }), 400
        
        # Verifica se já existe convite pendente para este email
        existing_invite = Invite.query.filter_by(
            email=data['email'],
            status=InviteStatus.PENDING
        ).first()
        
        if existing_invite and existing_invite.is_valid():
            return jsonify({
                'success': False,
                'erro': 'Já existe um convite pendente para este email'
            }), 400
        
        # Cria novo convite
        invite = Invite(
            email=data['email'],
            invited_by=user_id,
            access_level=AccessLevel(data.get('access_level', 'basic')),
            expires_in_days=data.get('expires_in_days', 7),
            max_uses=data.get('max_uses', 1),
            invitation_message=data.get('message')
        )
        
        db.session.add(invite)
        db.session.commit()
        
        # TODO: Enviar email de convite
        
        return jsonify({
            'success': True,
            'message': 'Convite criado com sucesso',
            'invite': invite.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Erro ao criar convite: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

@access_control_bp.route('/invites', methods=['GET'])
@jwt_required()
def list_invites():
    """Lista convites (apenas admins)"""
    try:
        user_id = get_jwt_identity()
        user_access = UserAccess.query.filter_by(user_id=user_id).first()
        
        if not user_access or user_access.access_level != AccessLevel.ADMIN:
            return jsonify({
                'success': False,
                'erro': 'Acesso negado'
            }), 403
        
        # Parâmetros de filtro
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        query = Invite.query
        
        if status:
            query = query.filter(Invite.status == InviteStatus(status))
        
        invites = query.order_by(Invite.created_at.desc())\
                      .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'invites': [invite.to_dict() for invite in invites.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': invites.total,
                'pages': invites.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar convites: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

@access_control_bp.route('/invites/<invite_code>/revoke', methods=['POST'])
@jwt_required()
def revoke_invite(invite_code):
    """Revoga convite"""
    try:
        user_id = get_jwt_identity()
        user_access = UserAccess.query.filter_by(user_id=user_id).first()
        
        if not user_access or user_access.access_level != AccessLevel.ADMIN:
            return jsonify({
                'success': False,
                'erro': 'Acesso negado'
            }), 403
        
        invite = Invite.query.filter_by(code=invite_code).first()
        if not invite:
            return jsonify({
                'success': False,
                'erro': 'Convite não encontrado'
            }), 404
        
        invite.revoke()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Convite revogado com sucesso'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao revogar convite: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

@access_control_bp.route('/invites/<invite_code>/validate', methods=['GET'])
def validate_invite(invite_code):
    """Valida código de convite (público)"""
    try:
        invite = Invite.query.filter_by(code=invite_code).first()
        
        if not invite:
            return jsonify({
                'valid': False,
                'erro': 'Convite não encontrado'
            }), 404
        
        if not invite.is_valid():
            reason = 'expirado' if invite.expires_at < datetime.utcnow() else 'já utilizado'
            return jsonify({
                'valid': False,
                'erro': f'Convite {reason}'
            }), 400
        
        return jsonify({
            'valid': True,
            'invite': {
                'email': invite.email,
                'access_level': invite.access_level.value,
                'expires_at': invite.expires_at.isoformat(),
                'invitation_message': invite.invitation_message
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao validar convite: {e}")
        return jsonify({
            'valid': False,
            'erro': 'Erro interno do servidor'
        }), 500

# ==================== ROTAS DE SOLICITAÇÃO DE ACESSO ====================

@access_control_bp.route('/access-requests', methods=['POST'])
def request_access():
    """Solicita acesso ao sistema (público)"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'full_name', 'reason']):
            return jsonify({
                'success': False,
                'erro': 'Email, nome completo e motivo são obrigatórios'
            }), 400
        
        # Verifica se já existe solicitação pendente
        existing_request = AccessRequest.query.filter_by(
            email=data['email'],
            status='pending'
        ).first()
        
        if existing_request:
            return jsonify({
                'success': False,
                'erro': 'Já existe uma solicitação pendente para este email'
            }), 400
        
        # Cria nova solicitação
        access_request = AccessRequest(
            email=data['email'],
            full_name=data['full_name'],
            reason=data['reason'],
            use_case=data.get('use_case'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        db.session.add(access_request)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Solicitação enviada com sucesso. Você receberá uma resposta em breve.',
            'request_id': access_request.id
        }), 201
        
    except Exception as e:
        logger.error(f"Erro ao solicitar acesso: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

@access_control_bp.route('/access-requests', methods=['GET'])
@jwt_required()
def list_access_requests():
    """Lista solicitações de acesso (apenas admins)"""
    try:
        user_id = get_jwt_identity()
        user_access = UserAccess.query.filter_by(user_id=user_id).first()
        
        if not user_access or user_access.access_level != AccessLevel.ADMIN:
            return jsonify({
                'success': False,
                'erro': 'Acesso negado'
            }), 403
        
        status = request.args.get('status', 'pending')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        requests_query = AccessRequest.query.filter_by(status=status)\
                                          .order_by(AccessRequest.created_at.desc())\
                                          .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'requests': [req.to_dict() for req in requests_query.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': requests_query.total,
                'pages': requests_query.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar solicitações: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

@access_control_bp.route('/access-requests/<int:request_id>/approve', methods=['POST'])
@jwt_required()
def approve_access_request(request_id):
    """Aprova solicitação de acesso"""
    try:
        user_id = get_jwt_identity()
        user_access = UserAccess.query.filter_by(user_id=user_id).first()
        
        if not user_access or user_access.access_level != AccessLevel.ADMIN:
            return jsonify({
                'success': False,
                'erro': 'Acesso negado'
            }), 403
        
        access_request = AccessRequest.query.get(request_id)
        if not access_request:
            return jsonify({
                'success': False,
                'erro': 'Solicitação não encontrada'
            }), 404
        
        data = request.get_json() or {}
        
        # Aprova solicitação
        access_request.approve(user_id, data.get('response'))
        
        # Cria convite automaticamente
        invite = Invite(
            email=access_request.email,
            invited_by=user_id,
            access_level=AccessLevel(data.get('access_level', 'basic')),
            expires_in_days=data.get('expires_in_days', 7),
            invitation_message=data.get('invitation_message')
        )
        
        db.session.add(invite)
        db.session.commit()
        
        # TODO: Enviar email de aprovação com convite
        
        return jsonify({
            'success': True,
            'message': 'Solicitação aprovada e convite enviado',
            'invite_code': invite.code
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao aprovar solicitação: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

@access_control_bp.route('/access-requests/<int:request_id>/reject', methods=['POST'])
@jwt_required()
def reject_access_request(request_id):
    """Rejeita solicitação de acesso"""
    try:
        user_id = get_jwt_identity()
        user_access = UserAccess.query.filter_by(user_id=user_id).first()
        
        if not user_access or user_access.access_level != AccessLevel.ADMIN:
            return jsonify({
                'success': False,
                'erro': 'Acesso negado'
            }), 403
        
        access_request = AccessRequest.query.get(request_id)
        if not access_request:
            return jsonify({
                'success': False,
                'erro': 'Solicitação não encontrada'
            }), 404
        
        data = request.get_json() or {}
        access_request.reject(user_id, data.get('response'))
        db.session.commit()
        
        # TODO: Enviar email de rejeição
        
        return jsonify({
            'success': True,
            'message': 'Solicitação rejeitada'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao rejeitar solicitação: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

# ==================== ROTAS DE GERENCIAMENTO DE USUÁRIOS ====================

@access_control_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """Lista usuários com controle de acesso"""
    try:
        user_id = get_jwt_identity()
        user_access = UserAccess.query.filter_by(user_id=user_id).first()
        
        if not user_access or user_access.access_level != AccessLevel.ADMIN:
            return jsonify({
                'success': False,
                'erro': 'Acesso negado'
            }), 403
        
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        query = db.session.query(User, UserAccess)\
                         .join(UserAccess, User.id == UserAccess.user_id)
        
        if status:
            query = query.filter(UserAccess.status == UserStatus(status))
        
        users = query.order_by(UserAccess.created_at.desc())\
                    .paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for user, access in users.items:
            user_data = {
                'id': user.id,
                'email': user.email,
                'created_at': user.created_at.isoformat(),
                'access_control': access.to_dict()
            }
            result.append(user_data)
        
        return jsonify({
            'success': True,
            'users': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

@access_control_bp.route('/users/<int:target_user_id>/approve', methods=['POST'])
@jwt_required()
def approve_user(target_user_id):
    """Aprova usuário"""
    try:
        user_id = get_jwt_identity()
        user_access = UserAccess.query.filter_by(user_id=user_id).first()
        
        if not user_access or user_access.access_level != AccessLevel.ADMIN:
            return jsonify({
                'success': False,
                'erro': 'Acesso negado'
            }), 403
        
        target_access = UserAccess.query.filter_by(user_id=target_user_id).first()
        if not target_access:
            return jsonify({
                'success': False,
                'erro': 'Usuário não encontrado'
            }), 404
        
        data = request.get_json() or {}
        target_access.approve(user_id, data.get('reason'))
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuário aprovado com sucesso'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao aprovar usuário: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

@access_control_bp.route('/users/<int:target_user_id>/suspend', methods=['POST'])
@jwt_required()
def suspend_user(target_user_id):
    """Suspende usuário"""
    try:
        user_id = get_jwt_identity()
        user_access = UserAccess.query.filter_by(user_id=user_id).first()
        
        if not user_access or user_access.access_level != AccessLevel.ADMIN:
            return jsonify({
                'success': False,
                'erro': 'Acesso negado'
            }), 403
        
        target_access = UserAccess.query.filter_by(user_id=target_user_id).first()
        if not target_access:
            return jsonify({
                'success': False,
                'erro': 'Usuário não encontrado'
            }), 404
        
        data = request.get_json() or {}
        days = data.get('days', 7)
        reason = data.get('reason')
        
        target_access.suspend(days, reason)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Usuário suspenso por {days} dias'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao suspender usuário: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

@access_control_bp.route('/users/<int:target_user_id>/ban', methods=['POST'])
@jwt_required()
def ban_user(target_user_id):
    """Bane usuário permanentemente"""
    try:
        user_id = get_jwt_identity()
        user_access = UserAccess.query.filter_by(user_id=user_id).first()
        
        if not user_access or user_access.access_level != AccessLevel.ADMIN:
            return jsonify({
                'success': False,
                'erro': 'Acesso negado'
            }), 403
        
        target_access = UserAccess.query.filter_by(user_id=target_user_id).first()
        if not target_access:
            return jsonify({
                'success': False,
                'erro': 'Usuário não encontrado'
            }), 404
        
        data = request.get_json() or {}
        target_access.ban(data.get('reason'))
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuário banido permanentemente'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao banir usuário: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

# ==================== CONFIGURAÇÕES ADMINISTRATIVAS ====================

@access_control_bp.route('/admin/settings', methods=['GET'])
@jwt_required()
def get_admin_settings():
    """Obtém configurações administrativas"""
    try:
        user_id = get_jwt_identity()
        user_access = UserAccess.query.filter_by(user_id=user_id).first()
        
        if not user_access or user_access.access_level != AccessLevel.ADMIN:
            return jsonify({
                'success': False,
                'erro': 'Acesso negado'
            }), 403
        
        settings = AdminSettings.get_settings()
        
        return jsonify({
            'success': True,
            'settings': settings.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter configurações: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

@access_control_bp.route('/admin/settings', methods=['PUT'])
@jwt_required()
def update_admin_settings():
    """Atualiza configurações administrativas"""
    try:
        user_id = get_jwt_identity()
        user_access = UserAccess.query.filter_by(user_id=user_id).first()
        
        if not user_access or user_access.access_level != AccessLevel.ADMIN:
            return jsonify({
                'success': False,
                'erro': 'Acesso negado'
            }), 403
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'erro': 'Dados não fornecidos'
            }), 400
        
        settings = AdminSettings.get_settings()
        
        # Atualiza configurações
        if 'registration_mode' in data:
            settings.registration_mode = data['registration_mode']
        
        if 'auto_approve_invites' in data:
            settings.auto_approve_invites = data['auto_approve_invites']
        
        if 'require_admin_approval' in data:
            settings.require_admin_approval = data['require_admin_approval']
        
        if 'default_daily_limit' in data:
            settings.default_daily_limit = data['default_daily_limit']
        
        if 'default_monthly_limit' in data:
            settings.default_monthly_limit = data['default_monthly_limit']
        
        if 'invite_expiry_days' in data:
            settings.invite_expiry_days = data['invite_expiry_days']
        
        if 'welcome_message' in data:
            settings.welcome_message = data['welcome_message']
        
        if 'rejection_message' in data:
            settings.rejection_message = data['rejection_message']
        
        settings.updated_by = user_id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Configurações atualizadas com sucesso',
            'settings': settings.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao atualizar configurações: {e}")
        return jsonify({
            'success': False,
            'erro': 'Erro interno do servidor'
        }), 500

# ==================== MIDDLEWARE DE VERIFICAÇÃO ====================

@access_control_bp.route('/check-access', methods=['GET'])
@jwt_required()
def check_user_access():
    """Verifica acesso do usuário atual"""
    try:
        user_id = get_jwt_identity()
        user_access = UserAccess.query.filter_by(user_id=user_id).first()
        
        if not user_access:
            return jsonify({
                'has_access': False,
                'reason': 'Controle de acesso não configurado'
            }), 200
        
        can_access, reason = user_access.can_make_request()
        
        return jsonify({
            'has_access': can_access,
            'reason': reason,
            'access_info': user_access.to_dict() if can_access else None
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao verificar acesso: {e}")
        return jsonify({
            'has_access': False,
            'reason': 'Erro interno do servidor'
        }), 500

