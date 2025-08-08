from src.models.user import db
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import json

class PlanoAssinatura(db.Model):
    __tablename__ = 'planos_assinatura'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    
    # Preços
    preco_mensal = db.Column(db.Numeric(10, 2), nullable=False)
    preco_anual = db.Column(db.Numeric(10, 2))
    
    # Limites e recursos
    max_usuarios = db.Column(db.Integer, default=1)
    max_transacoes_mes = db.Column(db.Integer, default=100)
    max_reunioes_mes = db.Column(db.Integer, default=10)
    max_storage_gb = db.Column(db.Float, default=1.0)
    
    # Funcionalidades
    tem_voice_auth = db.Column(db.Boolean, default=False)
    tem_speaker_diarization = db.Column(db.Boolean, default=False)
    tem_ai_avancada = db.Column(db.Boolean, default=False)
    tem_relatorios_excel = db.Column(db.Boolean, default=False)
    tem_automacao = db.Column(db.Boolean, default=False)
    tem_api_access = db.Column(db.Boolean, default=False)
    tem_suporte_prioritario = db.Column(db.Boolean, default=False)
    
    # Status
    ativo = db.Column(db.Boolean, default=True)
    ordem_exibicao = db.Column(db.Integer, default=0)
    
    # Metadados
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    assinaturas = db.relationship('AssinaturaUsuario', backref='plano', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'preco_mensal': float(self.preco_mensal) if self.preco_mensal else 0,
            'preco_anual': float(self.preco_anual) if self.preco_anual else 0,
            'economia_anual': self.calcular_economia_anual(),
            'limites': {
                'max_usuarios': self.max_usuarios,
                'max_transacoes_mes': self.max_transacoes_mes,
                'max_reunioes_mes': self.max_reunioes_mes,
                'max_storage_gb': self.max_storage_gb
            },
            'funcionalidades': {
                'voice_auth': self.tem_voice_auth,
                'speaker_diarization': self.tem_speaker_diarization,
                'ai_avancada': self.tem_ai_avancada,
                'relatorios_excel': self.tem_relatorios_excel,
                'automacao': self.tem_automacao,
                'api_access': self.tem_api_access,
                'suporte_prioritario': self.tem_suporte_prioritario
            },
            'ativo': self.ativo,
            'ordem_exibicao': self.ordem_exibicao
        }
    
    def calcular_economia_anual(self):
        if self.preco_mensal and self.preco_anual:
            preco_mensal_x12 = float(self.preco_mensal) * 12
            economia = preco_mensal_x12 - float(self.preco_anual)
            percentual = (economia / preco_mensal_x12) * 100
            return {
                'valor': economia,
                'percentual': round(percentual, 1)
            }
        return {'valor': 0, 'percentual': 0}

class AssinaturaUsuario(db.Model):
    __tablename__ = 'assinaturas_usuarios'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('auth_users.id'), nullable=False)
    plano_id = db.Column(db.String(36), db.ForeignKey('planos_assinatura.id'), nullable=False)
    
    # Período da assinatura
    tipo_periodo = db.Column(db.String(20), nullable=False)  # 'mensal', 'anual'
    data_inicio = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='ativa')  # 'ativa', 'cancelada', 'expirada', 'suspensa'
    auto_renovar = db.Column(db.Boolean, default=True)
    
    # Pagamento
    valor_pago = db.Column(db.Numeric(10, 2), nullable=False)
    desconto_aplicado = db.Column(db.Numeric(10, 2), default=0)
    cupom_usado = db.Column(db.String(50))
    
    # Uso atual
    transacoes_mes_atual = db.Column(db.Integer, default=0)
    reunioes_mes_atual = db.Column(db.Integer, default=0)
    storage_usado_gb = db.Column(db.Float, default=0)
    
    # Metadados
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    cancelada_em = db.Column(db.DateTime)
    motivo_cancelamento = db.Column(db.String(200))
    
    # Relacionamentos
    user = db.relationship('AuthUser', backref=db.backref('assinaturas', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'plano': self.plano.to_dict() if self.plano else None,
            'tipo_periodo': self.tipo_periodo,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'dias_restantes': self.calcular_dias_restantes(),
            'status': self.status,
            'auto_renovar': self.auto_renovar,
            'pagamento': {
                'valor_pago': float(self.valor_pago) if self.valor_pago else 0,
                'desconto_aplicado': float(self.desconto_aplicado) if self.desconto_aplicado else 0,
                'cupom_usado': self.cupom_usado
            },
            'uso_atual': {
                'transacoes_mes': self.transacoes_mes_atual,
                'reunioes_mes': self.reunioes_mes_atual,
                'storage_gb': self.storage_usado_gb,
                'percentual_uso': self.calcular_percentual_uso()
            },
            'limites_excedidos': self.verificar_limites_excedidos()
        }
    
    def calcular_dias_restantes(self):
        if self.data_fim:
            delta = self.data_fim - datetime.utcnow()
            return max(0, delta.days)
        return 0
    
    def calcular_percentual_uso(self):
        if not self.plano:
            return {}
        
        return {
            'transacoes': min(100, (self.transacoes_mes_atual / self.plano.max_transacoes_mes) * 100) if self.plano.max_transacoes_mes > 0 else 0,
            'reunioes': min(100, (self.reunioes_mes_atual / self.plano.max_reunioes_mes) * 100) if self.plano.max_reunioes_mes > 0 else 0,
            'storage': min(100, (self.storage_usado_gb / self.plano.max_storage_gb) * 100) if self.plano.max_storage_gb > 0 else 0
        }
    
    def verificar_limites_excedidos(self):
        if not self.plano:
            return []
        
        excedidos = []
        if self.transacoes_mes_atual >= self.plano.max_transacoes_mes:
            excedidos.append('transacoes')
        if self.reunioes_mes_atual >= self.plano.max_reunioes_mes:
            excedidos.append('reunioes')
        if self.storage_usado_gb >= self.plano.max_storage_gb:
            excedidos.append('storage')
        
        return excedidos
    
    def pode_usar_funcionalidade(self, funcionalidade):
        """Verifica se o usuário pode usar uma funcionalidade específica"""
        if not self.plano or self.status != 'ativa':
            return False
        
        funcionalidades_map = {
            'voice_auth': self.plano.tem_voice_auth,
            'speaker_diarization': self.plano.tem_speaker_diarization,
            'ai_avancada': self.plano.tem_ai_avancada,
            'relatorios_excel': self.plano.tem_relatorios_excel,
            'automacao': self.plano.tem_automacao,
            'api_access': self.plano.tem_api_access,
            'suporte_prioritario': self.plano.tem_suporte_prioritario
        }
        
        return funcionalidades_map.get(funcionalidade, False)

class CupomDesconto(db.Model):
    __tablename__ = 'cupons_desconto'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    
    # Tipo de desconto
    tipo_desconto = db.Column(db.String(20), nullable=False)  # 'percentual', 'valor_fixo', 'gratuito'
    valor_desconto = db.Column(db.Numeric(10, 2))  # Valor ou percentual
    
    # Validade
    data_inicio = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime, nullable=False)
    
    # Limites de uso
    max_usos_total = db.Column(db.Integer)  # null = ilimitado
    max_usos_por_usuario = db.Column(db.Integer, default=1)
    usos_atual = db.Column(db.Integer, default=0)
    
    # Restrições
    planos_permitidos = db.Column(db.Text)  # JSON array de IDs de planos
    usuarios_permitidos = db.Column(db.Text)  # JSON array de emails
    valor_minimo_compra = db.Column(db.Numeric(10, 2))
    
    # Status
    ativo = db.Column(db.Boolean, default=True)
    uso_interno = db.Column(db.Boolean, default=False)  # Para uso por admins
    
    # Metadados
    criado_por = db.Column(db.String(36), db.ForeignKey('auth_users.id'))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nome': self.nome,
            'descricao': self.descricao,
            'tipo_desconto': self.tipo_desconto,
            'valor_desconto': float(self.valor_desconto) if self.valor_desconto else 0,
            'validade': {
                'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
                'data_fim': self.data_fim.isoformat() if self.data_fim else None,
                'ativo': self.esta_valido()
            },
            'uso': {
                'max_usos_total': self.max_usos_total,
                'max_usos_por_usuario': self.max_usos_por_usuario,
                'usos_atual': self.usos_atual,
                'usos_restantes': self.calcular_usos_restantes()
            },
            'restricoes': {
                'planos_permitidos': self.get_planos_permitidos(),
                'usuarios_permitidos': self.get_usuarios_permitidos(),
                'valor_minimo_compra': float(self.valor_minimo_compra) if self.valor_minimo_compra else 0
            },
            'ativo': self.ativo,
            'uso_interno': self.uso_interno
        }
    
    def esta_valido(self):
        agora = datetime.utcnow()
        return (self.ativo and 
                self.data_inicio <= agora <= self.data_fim and
                (self.max_usos_total is None or self.usos_atual < self.max_usos_total))
    
    def calcular_usos_restantes(self):
        if self.max_usos_total is None:
            return None
        return max(0, self.max_usos_total - self.usos_atual)
    
    def get_planos_permitidos(self):
        if self.planos_permitidos:
            try:
                return json.loads(self.planos_permitidos)
            except:
                return []
        return []
    
    def get_usuarios_permitidos(self):
        if self.usuarios_permitidos:
            try:
                return json.loads(self.usuarios_permitidos)
            except:
                return []
        return []
    
    def set_planos_permitidos(self, planos_list):
        if planos_list:
            self.planos_permitidos = json.dumps(planos_list)
        else:
            self.planos_permitidos = None
    
    def set_usuarios_permitidos(self, usuarios_list):
        if usuarios_list:
            self.usuarios_permitidos = json.dumps(usuarios_list)
        else:
            self.usuarios_permitidos = None
    
    def calcular_desconto(self, valor_original):
        """Calcula o valor do desconto para um preço"""
        if self.tipo_desconto == 'gratuito':
            return valor_original
        elif self.tipo_desconto == 'percentual':
            return valor_original * (float(self.valor_desconto) / 100)
        elif self.tipo_desconto == 'valor_fixo':
            return min(float(self.valor_desconto), valor_original)
        return 0

class UsoCupom(db.Model):
    __tablename__ = 'uso_cupons'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cupom_id = db.Column(db.String(36), db.ForeignKey('cupons_desconto.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('auth_users.id'), nullable=False)
    assinatura_id = db.Column(db.String(36), db.ForeignKey('assinaturas_usuarios.id'))
    
    valor_original = db.Column(db.Numeric(10, 2), nullable=False)
    valor_desconto = db.Column(db.Numeric(10, 2), nullable=False)
    valor_final = db.Column(db.Numeric(10, 2), nullable=False)
    
    usado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    cupom = db.relationship('CupomDesconto', backref='usos')
    user = db.relationship('AuthUser', backref='cupons_usados')
    assinatura = db.relationship('AssinaturaUsuario', backref='cupom_usado_rel')
    
    def to_dict(self):
        return {
            'id': self.id,
            'cupom': self.cupom.to_dict() if self.cupom else None,
            'valor_original': float(self.valor_original),
            'valor_desconto': float(self.valor_desconto),
            'valor_final': float(self.valor_final),
            'usado_em': self.usado_em.isoformat() if self.usado_em else None
        }
