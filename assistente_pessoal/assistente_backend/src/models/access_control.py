from src.models.user import db
from datetime import datetime, timedelta
import secrets
import string
from enum import Enum

class InviteStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"

class UserStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SUSPENDED = "suspended"
    BANNED = "banned"

class AccessLevel(Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ADMIN = "admin"

class Invite(db.Model):
    __tablename__ = 'invites'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dados do convite
    code = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    invited_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Status e configurações
    status = db.Column(db.Enum(InviteStatus), default=InviteStatus.PENDING)
    access_level = db.Column(db.Enum(AccessLevel), default=AccessLevel.BASIC)
    max_uses = db.Column(db.Integer, default=1)
    uses_count = db.Column(db.Integer, default=0)
    
    # Datas
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime)
    
    # Metadados
    invitation_message = db.Column(db.Text)
    restrictions = db.Column(db.JSON)  # Restrições específicas
    
    # Relacionamentos
    inviter = db.relationship('User', foreign_keys=[invited_by], backref='sent_invites')
    
    def __init__(self, email, invited_by, access_level=AccessLevel.BASIC, 
                 expires_in_days=7, max_uses=1, invitation_message=None):
        self.email = email
        self.invited_by = invited_by
        self.access_level = access_level
        self.max_uses = max_uses
        self.invitation_message = invitation_message
        self.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        self.code = self.generate_invite_code()
    
    @staticmethod
    def generate_invite_code():
        """Gera código único de convite"""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
    
    def is_valid(self):
        """Verifica se o convite é válido"""
        return (
            self.status == InviteStatus.PENDING and
            self.expires_at > datetime.utcnow() and
            self.uses_count < self.max_uses
        )
    
    def use_invite(self):
        """Marca convite como usado"""
        self.uses_count += 1
        self.used_at = datetime.utcnow()
        
        if self.uses_count >= self.max_uses:
            self.status = InviteStatus.ACCEPTED
    
    def revoke(self):
        """Revoga o convite"""
        self.status = InviteStatus.REVOKED
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'email': self.email,
            'status': self.status.value,
            'access_level': self.access_level.value,
            'max_uses': self.max_uses,
            'uses_count': self.uses_count,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'invitation_message': self.invitation_message,
            'is_valid': self.is_valid()
        }

class UserAccess(db.Model):
    __tablename__ = 'user_access'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Status de acesso
    status = db.Column(db.Enum(UserStatus), default=UserStatus.PENDING)
    access_level = db.Column(db.Enum(AccessLevel), default=AccessLevel.BASIC)
    
    # Dados de aprovação
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    approval_reason = db.Column(db.Text)
    
    # Convite usado
    invite_code = db.Column(db.String(32), db.ForeignKey('invites.code'))
    
    # Limites e restrições
    daily_requests_limit = db.Column(db.Integer, default=100)
    monthly_requests_limit = db.Column(db.Integer, default=3000)
    features_enabled = db.Column(db.JSON, default=lambda: {
        'voice_recognition': True,
        'financial_management': True,
        'meeting_recording': True,
        'real_time_info': True,
        'automation': True
    })
    
    # Métricas de uso
    total_requests = db.Column(db.Integer, default=0)
    daily_requests = db.Column(db.Integer, default=0)
    monthly_requests = db.Column(db.Integer, default=0)
    last_request_date = db.Column(db.Date)
    last_reset_date = db.Column(db.Date, default=datetime.utcnow().date())
    
    # Datas importantes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    suspended_until = db.Column(db.DateTime)
    
    # Relacionamentos
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('access_control', uselist=False))
    approver = db.relationship('User', foreign_keys=[approved_by])
    invite = db.relationship('Invite', foreign_keys=[invite_code])
    
    def is_active(self):
        """Verifica se o usuário tem acesso ativo"""
        if self.status == UserStatus.BANNED:
            return False
        
        if self.status == UserStatus.SUSPENDED:
            if self.suspended_until and self.suspended_until > datetime.utcnow():
                return False
            else:
                # Remove suspensão expirada
                self.status = UserStatus.APPROVED
                self.suspended_until = None
        
        return self.status == UserStatus.APPROVED
    
    def can_make_request(self):
        """Verifica se pode fazer nova requisição"""
        if not self.is_active():
            return False, "Acesso negado"
        
        # Reset contadores se necessário
        today = datetime.utcnow().date()
        if self.last_reset_date != today:
            self.daily_requests = 0
            self.last_reset_date = today
            
            # Reset mensal
            if today.day == 1:
                self.monthly_requests = 0
        
        # Verifica limites
        if self.daily_requests >= self.daily_requests_limit:
            return False, "Limite diário de requisições excedido"
        
        if self.monthly_requests >= self.monthly_requests_limit:
            return False, "Limite mensal de requisições excedido"
        
        return True, "OK"
    
    def record_request(self):
        """Registra uma nova requisição"""
        self.total_requests += 1
        self.daily_requests += 1
        self.monthly_requests += 1
        self.last_activity = datetime.utcnow()
        self.last_request_date = datetime.utcnow().date()
    
    def approve(self, approved_by_id, reason=None):
        """Aprova acesso do usuário"""
        self.status = UserStatus.APPROVED
        self.approved_by = approved_by_id
        self.approved_at = datetime.utcnow()
        self.approval_reason = reason
    
    def suspend(self, days=7, reason=None):
        """Suspende usuário temporariamente"""
        self.status = UserStatus.SUSPENDED
        self.suspended_until = datetime.utcnow() + timedelta(days=days)
        self.approval_reason = reason
    
    def ban(self, reason=None):
        """Bane usuário permanentemente"""
        self.status = UserStatus.BANNED
        self.approval_reason = reason
    
    def has_feature(self, feature_name):
        """Verifica se usuário tem acesso a uma funcionalidade"""
        return self.features_enabled.get(feature_name, False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status.value,
            'access_level': self.access_level.value,
            'daily_requests_limit': self.daily_requests_limit,
            'monthly_requests_limit': self.monthly_requests_limit,
            'daily_requests': self.daily_requests,
            'monthly_requests': self.monthly_requests,
            'total_requests': self.total_requests,
            'features_enabled': self.features_enabled,
            'is_active': self.is_active(),
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'last_activity': self.last_activity.isoformat(),
            'suspended_until': self.suspended_until.isoformat() if self.suspended_until else None,
            'invite_code': self.invite_code
        }

class AccessRequest(db.Model):
    __tablename__ = 'access_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dados da solicitação
    email = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    use_case = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    
    # Resposta do admin
    admin_response = db.Column(db.Text)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    
    # Metadados
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    
    def approve(self, admin_id, response=None):
        """Aprova solicitação de acesso"""
        self.status = 'approved'
        self.reviewed_by = admin_id
        self.reviewed_at = datetime.utcnow()
        self.admin_response = response
    
    def reject(self, admin_id, response=None):
        """Rejeita solicitação de acesso"""
        self.status = 'rejected'
        self.reviewed_by = admin_id
        self.reviewed_at = datetime.utcnow()
        self.admin_response = response
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'reason': self.reason,
            'use_case': self.use_case,
            'status': self.status,
            'admin_response': self.admin_response,
            'created_at': self.created_at.isoformat(),
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }

class AdminSettings(db.Model):
    __tablename__ = 'admin_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Configurações de acesso
    registration_mode = db.Column(db.String(20), default='invite_only')  # open, invite_only, request_only, closed
    auto_approve_invites = db.Column(db.Boolean, default=True)
    require_admin_approval = db.Column(db.Boolean, default=True)
    
    # Limites padrão
    default_daily_limit = db.Column(db.Integer, default=100)
    default_monthly_limit = db.Column(db.Integer, default=3000)
    default_access_level = db.Column(db.Enum(AccessLevel), default=AccessLevel.BASIC)
    
    # Configurações de convite
    invite_expiry_days = db.Column(db.Integer, default=7)
    max_invites_per_user = db.Column(db.Integer, default=5)
    
    # Mensagens personalizadas
    welcome_message = db.Column(db.Text, default="Bem-vindo à IA! Sua conta foi aprovada.")
    rejection_message = db.Column(db.Text, default="Sua solicitação foi analisada, mas não podemos aprovar no momento.")
    
    # Metadados
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relacionamentos
    updater = db.relationship('User', foreign_keys=[updated_by])
    
    @classmethod
    def get_settings(cls):
        """Obtém configurações atuais ou cria padrão"""
        settings = cls.query.first()
        if not settings:
            settings = cls()
            db.session.add(settings)
            db.session.commit()
        return settings
    
    def to_dict(self):
        return {
            'registration_mode': self.registration_mode,
            'auto_approve_invites': self.auto_approve_invites,
            'require_admin_approval': self.require_admin_approval,
            'default_daily_limit': self.default_daily_limit,
            'default_monthly_limit': self.default_monthly_limit,
            'default_access_level': self.default_access_level.value,
            'invite_expiry_days': self.invite_expiry_days,
            'max_invites_per_user': self.max_invites_per_user,
            'welcome_message': self.welcome_message,
            'rejection_message': self.rejection_message,
            'updated_at': self.updated_at.isoformat()
        }

