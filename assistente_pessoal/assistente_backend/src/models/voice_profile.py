from src.models.user import db
from datetime import datetime
import json

class VoiceProfile(db.Model):
    __tablename__ = 'voice_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Dados do perfil de voz
    voice_embeddings = db.Column(db.Text)  # Embeddings da voz em JSON
    voice_samples_count = db.Column(db.Integer, default=0)
    confidence_threshold = db.Column(db.Float, default=0.75)
    
    # Personalização
    preferred_name = db.Column(db.String(100))  # Como o usuário quer ser chamado
    voice_activation_enabled = db.Column(db.Boolean, default=True)
    wake_word_sensitivity = db.Column(db.Float, default=0.8)
    
    # Configurações de segurança
    voice_auth_enabled = db.Column(db.Boolean, default=True)
    max_failed_attempts = db.Column(db.Integer, default=3)
    lockout_duration = db.Column(db.Integer, default=300)  # 5 minutos
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_training = db.Column(db.DateTime)
    is_trained = db.Column(db.Boolean, default=False)
    
    # Relacionamento
    user = db.relationship('User', backref=db.backref('voice_profile', uselist=False))
    
    def set_embeddings(self, embeddings_list):
        """Salva os embeddings da voz como JSON"""
        self.voice_embeddings = json.dumps(embeddings_list)
        self.updated_at = datetime.utcnow()
    
    def get_embeddings(self):
        """Recupera os embeddings da voz"""
        if self.voice_embeddings:
            return json.loads(self.voice_embeddings)
        return []
    
    def add_voice_sample(self, embedding):
        """Adiciona uma nova amostra de voz"""
        embeddings = self.get_embeddings()
        embeddings.append(embedding)
        self.set_embeddings(embeddings)
        self.voice_samples_count += 1
        
        # Marca como treinado se tiver pelo menos 3 amostras
        if self.voice_samples_count >= 3:
            self.is_trained = True
            self.last_training = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'preferred_name': self.preferred_name,
            'voice_samples_count': self.voice_samples_count,
            'confidence_threshold': self.confidence_threshold,
            'voice_activation_enabled': self.voice_activation_enabled,
            'wake_word_sensitivity': self.wake_word_sensitivity,
            'voice_auth_enabled': self.voice_auth_enabled,
            'is_trained': self.is_trained,
            'last_training': self.last_training.isoformat() if self.last_training else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class VoiceAuthAttempt(db.Model):
    __tablename__ = 'voice_auth_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Dados da tentativa
    confidence_score = db.Column(db.Float)
    is_successful = db.Column(db.Boolean, default=False)
    failure_reason = db.Column(db.String(200))
    
    # Metadados
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento
    user = db.relationship('User', backref='voice_auth_attempts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'confidence_score': self.confidence_score,
            'is_successful': self.is_successful,
            'failure_reason': self.failure_reason,
            'timestamp': self.timestamp.isoformat()
        }

