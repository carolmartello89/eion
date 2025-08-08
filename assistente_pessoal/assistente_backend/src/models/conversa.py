from src.models.user import db
from datetime import datetime
import json

class Conversa(db.Model):
    __tablename__ = 'conversas'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comando = db.Column(db.Text, nullable=False)  # O que o usuário disse
    resposta = db.Column(db.Text, nullable=False)  # O que o assistente respondeu
    acao_executada = db.Column(db.String(100))  # Que ação foi feita
    contexto = db.Column(db.Text)  # Dados extras da conversa em JSON
    tipo_interacao = db.Column(db.String(50), default='voz')  # voz, texto, acao
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com usuário
    user = db.relationship('User', backref=db.backref('conversas', lazy=True))
    
    def to_dict(self):
        contexto_dict = {}
        if self.contexto:
            try:
                contexto_dict = json.loads(self.contexto)
            except:
                contexto_dict = {}
                
        return {
            'id': self.id,
            'comando': self.comando,
            'resposta': self.resposta,
            'acao_executada': self.acao_executada,
            'contexto': contexto_dict,
            'tipo_interacao': self.tipo_interacao,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def set_contexto(self, contexto_dict):
        """Define contexto como JSON string"""
        if contexto_dict:
            self.contexto = json.dumps(contexto_dict, ensure_ascii=False)
        else:
            self.contexto = None
    
    def get_contexto(self):
        """Retorna contexto como dicionário"""
        if self.contexto:
            try:
                return json.loads(self.contexto)
            except:
                return {}
        return {}

class PadraoUsuario(db.Model):
    __tablename__ = 'padroes_usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tipo_padrao = db.Column(db.String(50), nullable=False)  # 'horario_reuniao', 'contato_frequente', etc
    dados_padrao = db.Column(db.Text)  # Dados específicos do padrão em JSON
    frequencia = db.Column(db.Integer, default=1)  # Quantas vezes foi observado
    confianca = db.Column(db.Float, default=0.5)  # Nível de confiança do padrão (0-1)
    ultima_ocorrencia = db.Column(db.DateTime, default=datetime.utcnow)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com usuário
    user = db.relationship('User', backref=db.backref('padroes', lazy=True))
    
    def to_dict(self):
        dados_dict = {}
        if self.dados_padrao:
            try:
                dados_dict = json.loads(self.dados_padrao)
            except:
                dados_dict = {}
                
        return {
            'id': self.id,
            'tipo_padrao': self.tipo_padrao,
            'dados_padrao': dados_dict,
            'frequencia': self.frequencia,
            'confianca': self.confianca,
            'ultima_ocorrencia': self.ultima_ocorrencia.isoformat() if self.ultima_ocorrencia else None,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }
    
    def set_dados_padrao(self, dados_dict):
        """Define dados do padrão como JSON string"""
        if dados_dict:
            self.dados_padrao = json.dumps(dados_dict, ensure_ascii=False)
        else:
            self.dados_padrao = None
    
    def get_dados_padrao(self):
        """Retorna dados do padrão como dicionário"""
        if self.dados_padrao:
            try:
                return json.loads(self.dados_padrao)
            except:
                return {}
        return {}

class MemoriaContexto(db.Model):
    __tablename__ = 'memoria_contexto'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chave = db.Column(db.String(100), nullable=False)  # Chave para identificar o contexto
    valor = db.Column(db.Text)  # Valor do contexto em JSON
    categoria = db.Column(db.String(50))  # Categoria do contexto (pessoal, trabalho, etc)
    importancia = db.Column(db.Integer, default=1)  # Nível de importância (1-5)
    expira_em = db.Column(db.DateTime)  # Quando o contexto expira (opcional)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com usuário
    user = db.relationship('User', backref=db.backref('memoria_contexto', lazy=True))
    
    def to_dict(self):
        valor_dict = {}
        if self.valor:
            try:
                valor_dict = json.loads(self.valor)
            except:
                valor_dict = self.valor
                
        return {
            'id': self.id,
            'chave': self.chave,
            'valor': valor_dict,
            'categoria': self.categoria,
            'importancia': self.importancia,
            'expira_em': self.expira_em.isoformat() if self.expira_em else None,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }
    
    def set_valor(self, valor_obj):
        """Define valor como JSON string se for dict/list, senão como string"""
        if isinstance(valor_obj, (dict, list)):
            self.valor = json.dumps(valor_obj, ensure_ascii=False)
        else:
            self.valor = str(valor_obj)
    
    def get_valor(self):
        """Retorna valor como objeto original"""
        if self.valor:
            try:
                return json.loads(self.valor)
            except:
                return self.valor
        return None

