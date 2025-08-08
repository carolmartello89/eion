from src.models.user import db
from datetime import datetime
import uuid

class Compromisso(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    data_hora = db.Column(db.DateTime, nullable=False)
    alerta_antecedencia = db.Column(db.Integer, default=30)  # minutos de antecedência
    tipo = db.Column(db.String(20), default='evento')  # reuniao, tarefa, evento
    status = db.Column(db.String(20), default='pendente')  # pendente, concluido, cancelado
    prioridade = db.Column(db.String(10), default='media')  # baixa, media, alta
    localizacao = db.Column(db.String(200))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Compromisso {self.titulo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'alerta_antecedencia': self.alerta_antecedencia,
            'tipo': self.tipo,
            'status': self.status,
            'prioridade': self.prioridade,
            'localizacao': self.localizacao,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }

