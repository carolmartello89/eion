from src.models.user import db
from datetime import datetime
import uuid

class Contato(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    empresa = db.Column(db.String(100))
    cargo = db.Column(db.String(100))
    categoria = db.Column(db.String(50), default='geral')  # trabalho, pessoal, familia, etc
    favorito = db.Column(db.Boolean, default=False)
    notas = db.Column(db.Text)
    foto_url = db.Column(db.String(500))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Contato {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'email': self.email,
            'empresa': self.empresa,
            'cargo': self.cargo,
            'categoria': self.categoria,
            'favorito': self.favorito,
            'notas': self.notas,
            'foto_url': self.foto_url,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }

