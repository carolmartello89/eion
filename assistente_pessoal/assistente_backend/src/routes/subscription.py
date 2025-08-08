from flask import Blueprint, request, jsonify
from src.routes.auth import token_required, admin_required
from src.utils.subscription_utils import obter_status_plano
from src.models.subscription import PlanoAssinatura, AssinaturaUsuario, CupomDesconto, UsoCupom
from src.models.user import db
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import uuid
import random
import string

subscription_bp = Blueprint('subscription', __name__)

# ==================== PLANOS ====================

@subscription_bp.route('/planos', methods=['GET'])
def listar_planos():
    """Lista todos os planos disponíveis (público)"""
    try:
        planos = PlanoAssinatura.query.filter_by(ativo=True)\
            .order_by(PlanoAssinatura.ordem_exibicao.asc()).all()
        
        return jsonify({
            'planos': [plano.to_dict() for plano in planos]
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@subscription_bp.route('/planos', methods=['POST'])
@admin_required
def criar_plano(current_user):
    """Cria novo plano (admin)"""
    try:
        data = request.get_json()
        
        plano = PlanoAssinatura(
            nome=data['nome'],
            descricao=data.get('descricao'),
            preco_mensal=data['preco_mensal'],
            preco_anual=data.get('preco_anual'),
            max_usuarios=data.get('max_usuarios', 1),
            max_transacoes_mes=data.get('max_transacoes_mes', 100),
            max_reunioes_mes=data.get('max_reunioes_mes', 10),
            max_storage_gb=data.get('max_storage_gb', 1.0),
            tem_voice_auth=data.get('tem_voice_auth', False),
            tem_speaker_diarization=data.get('tem_speaker_diarization', False),
            tem_ai_avancada=data.get('tem_ai_avancada', False),
            tem_relatorios_excel=data.get('tem_relatorios_excel', False),
            tem_automacao=data.get('tem_automacao', False),
            tem_api_access=data.get('tem_api_access', False),
            tem_suporte_prioritario=data.get('tem_suporte_prioritario', False),
            ordem_exibicao=data.get('ordem_exibicao', 0)
        )
        
        db.session.add(plano)
        db.session.commit()
        
        return jsonify({
            'message': 'Plano criado com sucesso',
            'plano': plano.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

# ==================== ASSINATURAS ====================

@subscription_bp.route('/status', methods=['GET'])
@token_required
def obter_status_usuario(current_user):
    """Obtém status detalhado do plano do usuário"""
    try:
        status = obter_status_plano(current_user.id)
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@subscription_bp.route('/minha-assinatura', methods=['GET'])
@token_required
def obter_minha_assinatura(current_user):
    """Obtém assinatura atual do usuário"""
    try:
        assinatura = AssinaturaUsuario.query.filter_by(
            user_id=current_user.id,
            status='ativa'
        ).first()
        
        if not assinatura:
            return jsonify({
                'assinatura': None,
                'status': 'sem_assinatura',
                'message': 'Usuário não possui assinatura ativa'
            }), 200
        
        return jsonify({
            'assinatura': assinatura.to_dict(),
            'status': 'ativa'
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@subscription_bp.route('/assinar', methods=['POST'])
@token_required
def criar_assinatura(current_user):
    """Cria nova assinatura para o usuário"""
    try:
        data = request.get_json()
        
        # Verifica se já tem assinatura ativa
        assinatura_existente = AssinaturaUsuario.query.filter_by(
            user_id=current_user.id,
            status='ativa'
        ).first()
        
        if assinatura_existente:
            return jsonify({'erro': 'Usuário já possui assinatura ativa'}), 400
        
        # Busca o plano
        plano = PlanoAssinatura.query.get(data['plano_id'])
        if not plano:
            return jsonify({'erro': 'Plano não encontrado'}), 404
        
        # Calcula preço
        tipo_periodo = data.get('tipo_periodo', 'mensal')
        if tipo_periodo == 'anual' and plano.preco_anual:
            valor_original = float(plano.preco_anual)
        else:
            valor_original = float(plano.preco_mensal)
            tipo_periodo = 'mensal'
        
        valor_final = valor_original
        desconto_aplicado = 0
        cupom_usado = None
        
        # Aplica cupom se fornecido
        if data.get('cupom_codigo'):
            resultado_cupom = aplicar_cupom(
                data['cupom_codigo'], 
                current_user.id, 
                plano.id, 
                valor_original
            )
            
            if resultado_cupom['sucesso']:
                valor_final = resultado_cupom['valor_final']
                desconto_aplicado = resultado_cupom['desconto']
                cupom_usado = data['cupom_codigo']
            else:
                return jsonify({'erro': resultado_cupom['erro']}), 400
        
        # Calcula datas
        data_inicio = datetime.utcnow()
        if tipo_periodo == 'anual':
            data_fim = data_inicio + relativedelta(years=1)
        else:
            data_fim = data_inicio + relativedelta(months=1)
        
        # Cria assinatura
        assinatura = AssinaturaUsuario(
            user_id=current_user.id,
            plano_id=plano.id,
            tipo_periodo=tipo_periodo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            valor_pago=valor_final,
            desconto_aplicado=desconto_aplicado,
            cupom_usado=cupom_usado
        )
        
        db.session.add(assinatura)
        db.session.commit()
        
        # Registra uso do cupom se aplicado
        if cupom_usado:
            registrar_uso_cupom(data['cupom_codigo'], current_user.id, assinatura.id, valor_original, desconto_aplicado, valor_final)
        
        return jsonify({
            'message': 'Assinatura criada com sucesso',
            'assinatura': assinatura.to_dict(),
            'pagamento': {
                'valor_original': valor_original,
                'desconto_aplicado': desconto_aplicado,
                'valor_final': valor_final,
                'cupom_usado': cupom_usado
            }
        }), 201
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@subscription_bp.route('/cancelar', methods=['POST'])
@token_required
def cancelar_assinatura(current_user):
    """Cancela assinatura do usuário"""
    try:
        data = request.get_json()
        
        assinatura = AssinaturaUsuario.query.filter_by(
            user_id=current_user.id,
            status='ativa'
        ).first()
        
        if not assinatura:
            return jsonify({'erro': 'Nenhuma assinatura ativa encontrada'}), 404
        
        assinatura.status = 'cancelada'
        assinatura.cancelada_em = datetime.utcnow()
        assinatura.motivo_cancelamento = data.get('motivo', 'Cancelamento solicitado pelo usuário')
        assinatura.auto_renovar = False
        
        db.session.commit()
        
        return jsonify({
            'message': 'Assinatura cancelada com sucesso',
            'assinatura': assinatura.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

# ==================== CUPONS ====================

@subscription_bp.route('/validar-cupom', methods=['POST'])
@token_required
def validar_cupom(current_user):
    """Valida um cupom de desconto"""
    try:
        data = request.get_json()
        codigo = data.get('codigo', '').upper()
        plano_id = data.get('plano_id')
        
        if not codigo:
            return jsonify({'erro': 'Código do cupom é obrigatório'}), 400
        
        cupom = CupomDesconto.query.filter_by(codigo=codigo).first()
        
        if not cupom:
            return jsonify({'erro': 'Cupom não encontrado'}), 404
        
        # Validações
        validacao = validar_cupom_uso(cupom, current_user.id, plano_id)
        
        if not validacao['valido']:
            return jsonify({'erro': validacao['erro']}), 400
        
        # Calcula desconto para preview
        plano = PlanoAssinatura.query.get(plano_id) if plano_id else None
        valor_exemplo = 0
        desconto_exemplo = 0
        
        if plano:
            valor_exemplo = float(plano.preco_mensal)
            desconto_exemplo = cupom.calcular_desconto(valor_exemplo)
        
        return jsonify({
            'cupom': cupom.to_dict(),
            'valido': True,
            'preview': {
                'valor_original': valor_exemplo,
                'desconto': desconto_exemplo,
                'valor_final': valor_exemplo - desconto_exemplo,
                'percentual_desconto': round((desconto_exemplo / valor_exemplo) * 100, 1) if valor_exemplo > 0 else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@subscription_bp.route('/cupons', methods=['GET'])
@admin_required
def listar_cupons(current_user):
    """Lista todos os cupons (admin)"""
    try:
        cupons = CupomDesconto.query.order_by(CupomDesconto.criado_em.desc()).all()
        
        return jsonify({
            'cupons': [cupom.to_dict() for cupom in cupons]
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@subscription_bp.route('/cupons', methods=['POST'])
@admin_required
def criar_cupom(current_user):
    """Cria novo cupom (admin)"""
    try:
        data = request.get_json()
        
        # Gera código se não fornecido
        codigo = data.get('codigo')
        if not codigo:
            codigo = gerar_codigo_cupom()
        else:
            codigo = codigo.upper()
        
        # Verifica se código já existe
        cupom_existente = CupomDesconto.query.filter_by(codigo=codigo).first()
        if cupom_existente:
            return jsonify({'erro': 'Código de cupom já existe'}), 400
        
        cupom = CupomDesconto(
            codigo=codigo,
            nome=data['nome'],
            descricao=data.get('descricao'),
            tipo_desconto=data['tipo_desconto'],
            valor_desconto=data.get('valor_desconto'),
            data_inicio=datetime.fromisoformat(data['data_inicio']),
            data_fim=datetime.fromisoformat(data['data_fim']),
            max_usos_total=data.get('max_usos_total'),
            max_usos_por_usuario=data.get('max_usos_por_usuario', 1),
            valor_minimo_compra=data.get('valor_minimo_compra'),
            uso_interno=data.get('uso_interno', False),
            criado_por=current_user.id
        )
        
        # Define restrições
        if data.get('planos_permitidos'):
            cupom.set_planos_permitidos(data['planos_permitidos'])
        
        if data.get('usuarios_permitidos'):
            cupom.set_usuarios_permitidos(data['usuarios_permitidos'])
        
        db.session.add(cupom)
        db.session.commit()
        
        return jsonify({
            'message': 'Cupom criado com sucesso',
            'cupom': cupom.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@subscription_bp.route('/cupons/gerar-gratuito', methods=['POST'])
@admin_required
def gerar_cupom_gratuito(current_user):
    """Gera cupom gratuito para usuário específico (admin)"""
    try:
        data = request.get_json()
        
        email_usuario = data.get('email_usuario')
        plano_id = data.get('plano_id')
        validade_dias = data.get('validade_dias', 30)
        
        if not email_usuario or not plano_id:
            return jsonify({'erro': 'Email do usuário e plano são obrigatórios'}), 400
        
        plano = PlanoAssinatura.query.get(plano_id)
        if not plano:
            return jsonify({'erro': 'Plano não encontrado'}), 404
        
        # Gera código único
        codigo = f"GRATIS_{gerar_codigo_cupom()}"
        
        cupom = CupomDesconto(
            codigo=codigo,
            nome=f"Cupom Gratuito - {plano.nome}",
            descricao=f"Cupom gratuito para {email_usuario}",
            tipo_desconto='gratuito',
            data_inicio=datetime.utcnow(),
            data_fim=datetime.utcnow() + timedelta(days=validade_dias),
            max_usos_total=1,
            max_usos_por_usuario=1,
            uso_interno=True,
            criado_por=current_user.id
        )
        
        # Restringe ao usuário específico
        cupom.set_usuarios_permitidos([email_usuario])
        cupom.set_planos_permitidos([plano_id])
        
        db.session.add(cupom)
        db.session.commit()
        
        return jsonify({
            'message': 'Cupom gratuito gerado com sucesso',
            'cupom': cupom.to_dict(),
            'instrucoes': f'Envie o código {codigo} para {email_usuario}'
        }), 201
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

# ==================== FUNÇÕES AUXILIARES ====================

def aplicar_cupom(codigo, user_id, plano_id, valor_original):
    """Aplica cupom e retorna resultado"""
    try:
        cupom = CupomDesconto.query.filter_by(codigo=codigo.upper()).first()
        
        if not cupom:
            return {'sucesso': False, 'erro': 'Cupom não encontrado'}
        
        # Validações
        validacao = validar_cupom_uso(cupom, user_id, plano_id)
        if not validacao['valido']:
            return {'sucesso': False, 'erro': validacao['erro']}
        
        # Calcula desconto
        desconto = cupom.calcular_desconto(valor_original)
        valor_final = valor_original - desconto
        
        return {
            'sucesso': True,
            'desconto': desconto,
            'valor_final': valor_final,
            'cupom_id': cupom.id
        }
        
    except Exception as e:
        return {'sucesso': False, 'erro': f'Erro ao aplicar cupom: {str(e)}'}

def validar_cupom_uso(cupom, user_id, plano_id):
    """Valida se cupom pode ser usado"""
    # Verifica se está ativo
    if not cupom.ativo:
        return {'valido': False, 'erro': 'Cupom não está ativo'}
    
    # Verifica validade
    if not cupom.esta_valido():
        return {'valido': False, 'erro': 'Cupom expirado ou inválido'}
    
    # Verifica uso máximo por usuário
    usos_usuario = UsoCupom.query.filter_by(cupom_id=cupom.id, user_id=user_id).count()
    if usos_usuario >= cupom.max_usos_por_usuario:
        return {'valido': False, 'erro': 'Limite de uso do cupom excedido'}
    
    # Verifica planos permitidos
    planos_permitidos = cupom.get_planos_permitidos()
    if planos_permitidos and plano_id not in planos_permitidos:
        return {'valido': False, 'erro': 'Cupom não válido para este plano'}
    
    # Verifica usuários permitidos
    from src.models.auth import AuthUser
    user = AuthUser.query.get(user_id)
    usuarios_permitidos = cupom.get_usuarios_permitidos()
    if usuarios_permitidos and user.email not in usuarios_permitidos:
        return {'valido': False, 'erro': 'Cupom não disponível para este usuário'}
    
    return {'valido': True}

def registrar_uso_cupom(codigo, user_id, assinatura_id, valor_original, desconto, valor_final):
    """Registra o uso de um cupom"""
    try:
        cupom = CupomDesconto.query.filter_by(codigo=codigo.upper()).first()
        if not cupom:
            return False
        
        uso = UsoCupom(
            cupom_id=cupom.id,
            user_id=user_id,
            assinatura_id=assinatura_id,
            valor_original=valor_original,
            valor_desconto=desconto,
            valor_final=valor_final
        )
        
        # Incrementa contador
        cupom.usos_atual += 1
        
        db.session.add(uso)
        db.session.commit()
        
        return True
        
    except Exception as e:
        print(f"Erro ao registrar uso do cupom: {e}")
        return False

def gerar_codigo_cupom():
    """Gera código único para cupom"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ==================== ANALYTICS E ADMIN ====================

@subscription_bp.route('/analytics', methods=['GET'])
@admin_required
def analytics_assinaturas(current_user):
    """Analytics de assinaturas (admin)"""
    try:
        # Estatísticas gerais
        total_assinaturas = AssinaturaUsuario.query.count()
        assinaturas_ativas = AssinaturaUsuario.query.filter_by(status='ativa').count()
        total_receita = db.session.query(db.func.sum(AssinaturaUsuario.valor_pago)).scalar() or 0
        
        # Assinaturas por plano
        assinaturas_por_plano = db.session.query(
            PlanoAssinatura.nome,
            db.func.count(AssinaturaUsuario.id).label('total'),
            db.func.sum(AssinaturaUsuario.valor_pago).label('receita')
        ).join(AssinaturaUsuario).group_by(PlanoAssinatura.id).all()
        
        # Cupons mais usados
        cupons_mais_usados = db.session.query(
            CupomDesconto.codigo,
            CupomDesconto.nome,
            db.func.count(UsoCupom.id).label('usos'),
            db.func.sum(UsoCupom.valor_desconto).label('desconto_total')
        ).join(UsoCupom).group_by(CupomDesconto.id).order_by(db.desc('usos')).limit(10).all()
        
        return jsonify({
            'resumo': {
                'total_assinaturas': total_assinaturas,
                'assinaturas_ativas': assinaturas_ativas,
                'total_receita': float(total_receita),
                'taxa_conversao': round((assinaturas_ativas / max(total_assinaturas, 1)) * 100, 2)
            },
            'assinaturas_por_plano': [
                {
                    'plano': row[0],
                    'total': row[1],
                    'receita': float(row[2] or 0)
                } for row in assinaturas_por_plano
            ],
            'cupons_mais_usados': [
                {
                    'codigo': row[0],
                    'nome': row[1],
                    'usos': row[2],
                    'desconto_total': float(row[3] or 0)
                } for row in cupons_mais_usados
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500
