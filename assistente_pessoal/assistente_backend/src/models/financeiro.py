from src.models.user import db
from datetime import datetime, date
import json
from decimal import Decimal

class CategoriaFinanceira(db.Model):
    __tablename__ = 'categorias_financeiras'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'receita' ou 'despesa'
    cor = db.Column(db.String(7), default='#3b82f6')  # Cor em hex para gráficos
    icone = db.Column(db.String(50), default='💰')
    ativa = db.Column(db.Boolean, default=True)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref=db.backref('categorias_financeiras', lazy=True))
    transacoes = db.relationship('TransacaoFinanceira', backref='categoria', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'cor': self.cor,
            'icone': self.icone,
            'ativa': self.ativa,
            'criada_em': self.criada_em.isoformat() if self.criada_em else None
        }

class TransacaoFinanceira(db.Model):
    __tablename__ = 'transacoes_financeiras'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_financeiras.id'), nullable=False)
    
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'receita' ou 'despesa'
    data_transacao = db.Column(db.Date, nullable=False, default=date.today)
    
    # Campos opcionais
    observacoes = db.Column(db.Text)
    tags = db.Column(db.Text)  # JSON array de tags
    anexo_url = db.Column(db.String(500))  # URL do comprovante/nota fiscal
    
    # Campos para transações recorrentes
    recorrente = db.Column(db.Boolean, default=False)
    frequencia_recorrencia = db.Column(db.String(20))  # 'mensal', 'semanal', 'anual'
    proxima_ocorrencia = db.Column(db.Date)
    
    # Metadados
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizada_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref=db.backref('transacoes_financeiras', lazy=True))
    
    def to_dict(self):
        tags_list = []
        if self.tags:
            try:
                tags_list = json.loads(self.tags)
            except:
                tags_list = []
                
        return {
            'id': self.id,
            'categoria_id': self.categoria_id,
            'categoria': self.categoria.to_dict() if self.categoria else None,
            'descricao': self.descricao,
            'valor': float(self.valor) if self.valor else 0,
            'tipo': self.tipo,
            'data_transacao': self.data_transacao.isoformat() if self.data_transacao else None,
            'observacoes': self.observacoes,
            'tags': tags_list,
            'anexo_url': self.anexo_url,
            'recorrente': self.recorrente,
            'frequencia_recorrencia': self.frequencia_recorrencia,
            'proxima_ocorrencia': self.proxima_ocorrencia.isoformat() if self.proxima_ocorrencia else None,
            'criada_em': self.criada_em.isoformat() if self.criada_em else None,
            'atualizada_em': self.atualizada_em.isoformat() if self.atualizada_em else None
        }
    
    def set_tags(self, tags_list):
        """Define tags como JSON string"""
        if tags_list:
            self.tags = json.dumps(tags_list, ensure_ascii=False)
        else:
            self.tags = None
    
    def get_tags(self):
        """Retorna tags como lista"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except:
                return []
        return []

class MetaFinanceira(db.Model):
    __tablename__ = 'metas_financeiras'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    valor_objetivo = db.Column(db.Numeric(10, 2), nullable=False)
    valor_atual = db.Column(db.Numeric(10, 2), default=0)
    
    tipo_meta = db.Column(db.String(20), nullable=False)  # 'economia', 'investimento', 'pagamento_divida'
    prazo_final = db.Column(db.Date)
    
    status = db.Column(db.String(20), default='ativa')  # 'ativa', 'concluida', 'pausada', 'cancelada'
    prioridade = db.Column(db.Integer, default=3)  # 1-5, sendo 5 mais importante
    
    # Configurações de acompanhamento
    lembrete_ativo = db.Column(db.Boolean, default=True)
    frequencia_lembrete = db.Column(db.String(20), default='semanal')  # 'diario', 'semanal', 'mensal'
    
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizada_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref=db.backref('metas_financeiras', lazy=True))
    
    def to_dict(self):
        progresso = 0
        if self.valor_objetivo and self.valor_objetivo > 0:
            progresso = float(self.valor_atual / self.valor_objetivo * 100)
        
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'valor_objetivo': float(self.valor_objetivo) if self.valor_objetivo else 0,
            'valor_atual': float(self.valor_atual) if self.valor_atual else 0,
            'progresso_percentual': min(100, progresso),
            'tipo_meta': self.tipo_meta,
            'prazo_final': self.prazo_final.isoformat() if self.prazo_final else None,
            'status': self.status,
            'prioridade': self.prioridade,
            'lembrete_ativo': self.lembrete_ativo,
            'frequencia_lembrete': self.frequencia_lembrete,
            'criada_em': self.criada_em.isoformat() if self.criada_em else None,
            'atualizada_em': self.atualizada_em.isoformat() if self.atualizada_em else None
        }

class ContaFinanceira(db.Model):
    __tablename__ = 'contas_financeiras'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    nome = db.Column(db.String(100), nullable=False)
    tipo_conta = db.Column(db.String(30), nullable=False)  # 'conta_corrente', 'poupanca', 'investimento', 'cartao_credito'
    banco = db.Column(db.String(100))
    saldo_atual = db.Column(db.Numeric(10, 2), default=0)
    
    # Configurações
    incluir_no_total = db.Column(db.Boolean, default=True)
    cor = db.Column(db.String(7), default='#10b981')
    icone = db.Column(db.String(50), default='🏦')
    
    # Para cartões de crédito
    limite_credito = db.Column(db.Numeric(10, 2))
    dia_vencimento = db.Column(db.Integer)  # Dia do mês
    dia_fechamento = db.Column(db.Integer)  # Dia do mês
    
    ativa = db.Column(db.Boolean, default=True)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizada_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref=db.backref('contas_financeiras', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo_conta': self.tipo_conta,
            'banco': self.banco,
            'saldo_atual': float(self.saldo_atual) if self.saldo_atual else 0,
            'incluir_no_total': self.incluir_no_total,
            'cor': self.cor,
            'icone': self.icone,
            'limite_credito': float(self.limite_credito) if self.limite_credito else None,
            'dia_vencimento': self.dia_vencimento,
            'dia_fechamento': self.dia_fechamento,
            'ativa': self.ativa,
            'criada_em': self.criada_em.isoformat() if self.criada_em else None,
            'atualizada_em': self.atualizada_em.isoformat() if self.atualizada_em else None
        }

class LembreteFinanceiro(db.Model):
    __tablename__ = 'lembretes_financeiros'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    tipo_lembrete = db.Column(db.String(30), nullable=False)  # 'pagamento', 'recebimento', 'investimento', 'meta'
    
    valor = db.Column(db.Numeric(10, 2))
    data_vencimento = db.Column(db.Date, nullable=False)
    
    # Configurações de recorrência
    recorrente = db.Column(db.Boolean, default=False)
    frequencia = db.Column(db.String(20))  # 'mensal', 'anual', 'semanal'
    
    # Configurações de notificação
    dias_antecedencia = db.Column(db.Integer, default=3)
    notificacao_enviada = db.Column(db.Boolean, default=False)
    
    status = db.Column(db.String(20), default='pendente')  # 'pendente', 'concluido', 'atrasado'
    prioridade = db.Column(db.String(20), default='media')  # 'baixa', 'media', 'alta'
    
    # Relacionamento com transação (quando o lembrete é cumprido)
    transacao_id = db.Column(db.Integer, db.ForeignKey('transacoes_financeiras.id'))
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref=db.backref('lembretes_financeiros', lazy=True))
    transacao = db.relationship('TransacaoFinanceira', backref='lembrete_origem')
    
    def to_dict(self):
        dias_restantes = None
        if self.data_vencimento:
            dias_restantes = (self.data_vencimento - date.today()).days
        
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'tipo_lembrete': self.tipo_lembrete,
            'valor': float(self.valor) if self.valor else None,
            'data_vencimento': self.data_vencimento.isoformat() if self.data_vencimento else None,
            'dias_restantes': dias_restantes,
            'recorrente': self.recorrente,
            'frequencia': self.frequencia,
            'dias_antecedencia': self.dias_antecedencia,
            'notificacao_enviada': self.notificacao_enviada,
            'status': self.status,
            'prioridade': self.prioridade,
            'transacao_id': self.transacao_id,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }

class OrcamentoMensal(db.Model):
    __tablename__ = 'orcamentos_mensais'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_financeiras.id'), nullable=False)
    
    mes = db.Column(db.Integer, nullable=False)  # 1-12
    ano = db.Column(db.Integer, nullable=False)
    
    valor_orcado = db.Column(db.Numeric(10, 2), nullable=False)
    valor_gasto = db.Column(db.Numeric(10, 2), default=0)
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref=db.backref('orcamentos_mensais', lazy=True))
    categoria = db.relationship('CategoriaFinanceira', backref='orcamentos')
    
    # Índice único para evitar duplicatas
    __table_args__ = (db.UniqueConstraint('user_id', 'categoria_id', 'mes', 'ano'),)
    
    def to_dict(self):
        percentual_usado = 0
        if self.valor_orcado and self.valor_orcado > 0:
            percentual_usado = float(self.valor_gasto / self.valor_orcado * 100)
        
        return {
            'id': self.id,
            'categoria_id': self.categoria_id,
            'categoria': self.categoria.to_dict() if self.categoria else None,
            'mes': self.mes,
            'ano': self.ano,
            'valor_orcado': float(self.valor_orcado) if self.valor_orcado else 0,
            'valor_gasto': float(self.valor_gasto) if self.valor_gasto else 0,
            'valor_restante': float(self.valor_orcado - self.valor_gasto) if self.valor_orcado and self.valor_gasto else 0,
            'percentual_usado': min(100, percentual_usado),
            'status': 'ok' if percentual_usado <= 80 else 'atencao' if percentual_usado <= 100 else 'excedido',
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }

