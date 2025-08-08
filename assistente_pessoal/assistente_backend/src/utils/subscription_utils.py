from functools import wraps
from flask import jsonify, request
from src.models.subscription import AssinaturaUsuario
from src.models.auth import AuthUser
from datetime import datetime

def verificar_limite_plano(funcionalidade=None, incrementar_uso=None):
    """
    Decorator para verificar limites do plano do usuário
    
    Args:
        funcionalidade: Nome da funcionalidade a verificar ('voice_auth', 'ai_avancada', etc.)
        incrementar_uso: Tipo de uso a incrementar ('transacoes', 'reunioes', 'storage')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Pega o current_user dos argumentos (deve ser passado pelo @token_required)
            current_user = None
            for arg in args:
                if hasattr(arg, 'id') and hasattr(arg, 'email'):
                    current_user = arg
                    break
            
            if not current_user:
                return jsonify({'erro': 'Usuário não identificado'}), 401
            
            # Busca assinatura ativa
            assinatura = AssinaturaUsuario.query.filter_by(
                user_id=current_user.id,
                status='ativa'
            ).first()
            
            # Se não tem assinatura, permite apenas plano gratuito básico
            if not assinatura:
                if funcionalidade and funcionalidade not in ['basic']:
                    return jsonify({
                        'erro': 'Funcionalidade requer assinatura ativa',
                        'codigo': 'UPGRADE_REQUIRED',
                        'funcionalidade': funcionalidade
                    }), 403
                
                # Permite funcionalidades básicas sem assinatura
                return f(*args, **kwargs)
            
            # Verifica se assinatura expirou
            if assinatura.data_fim < datetime.utcnow():
                assinatura.status = 'expirada'
                from src.models.user import db
                db.session.commit()
                
                return jsonify({
                    'erro': 'Assinatura expirada',
                    'codigo': 'SUBSCRIPTION_EXPIRED',
                    'data_expiracao': assinatura.data_fim.isoformat()
                }), 403
            
            # Verifica funcionalidade específica
            if funcionalidade:
                if not assinatura.pode_usar_funcionalidade(funcionalidade):
                    return jsonify({
                        'erro': f'Funcionalidade {funcionalidade} não disponível no seu plano',
                        'codigo': 'FEATURE_NOT_AVAILABLE',
                        'plano_atual': assinatura.plano.nome,
                        'funcionalidade': funcionalidade
                    }), 403
            
            # Verifica limites de uso
            if incrementar_uso:
                limite_excedido = verificar_e_incrementar_uso(assinatura, incrementar_uso)
                if limite_excedido:
                    return jsonify({
                        'erro': f'Limite de {incrementar_uso} excedido para seu plano',
                        'codigo': 'USAGE_LIMIT_EXCEEDED',
                        'limite_tipo': incrementar_uso,
                        'plano_atual': assinatura.plano.nome
                    }), 403
            
            # Adiciona informações da assinatura ao request
            request.assinatura_atual = assinatura
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def verificar_e_incrementar_uso(assinatura, tipo_uso):
    """Verifica e incrementa contador de uso"""
    from src.models.user import db
    
    if tipo_uso == 'transacoes':
        if assinatura.transacoes_mes_atual >= assinatura.plano.max_transacoes_mes:
            return True
        assinatura.transacoes_mes_atual += 1
    
    elif tipo_uso == 'reunioes':
        if assinatura.reunioes_mes_atual >= assinatura.plano.max_reunioes_mes:
            return True
        assinatura.reunioes_mes_atual += 1
    
    elif tipo_uso == 'storage':
        # Para storage, a verificação deve ser feita pelo tamanho do arquivo
        # Este é apenas um placeholder
        if assinatura.storage_usado_gb >= assinatura.plano.max_storage_gb:
            return True
    
    db.session.commit()
    return False

def obter_status_plano(user_id):
    """Obtém status detalhado do plano do usuário"""
    assinatura = AssinaturaUsuario.query.filter_by(
        user_id=user_id,
        status='ativa'
    ).first()
    
    if not assinatura:
        return {
            'tem_assinatura': False,
            'plano': 'Gratuito',
            'status': 'sem_assinatura',
            'funcionalidades_disponivel': ['basic'],
            'limites': {
                'transacoes_mes': 10,
                'reunioes_mes': 2,
                'storage_gb': 0.1
            }
        }
    
    # Verifica se expirou
    if assinatura.data_fim < datetime.utcnow():
        return {
            'tem_assinatura': False,
            'plano': 'Expirado',
            'status': 'expirada',
            'data_expiracao': assinatura.data_fim.isoformat(),
            'funcionalidades_disponivel': ['basic']
        }
    
    # Monta lista de funcionalidades disponíveis
    funcionalidades = ['basic']
    if assinatura.plano.tem_voice_auth:
        funcionalidades.append('voice_auth')
    if assinatura.plano.tem_speaker_diarization:
        funcionalidades.append('speaker_diarization')
    if assinatura.plano.tem_ai_avancada:
        funcionalidades.append('ai_avancada')
    if assinatura.plano.tem_relatorios_excel:
        funcionalidades.append('relatorios_excel')
    if assinatura.plano.tem_automacao:
        funcionalidades.append('automacao')
    if assinatura.plano.tem_api_access:
        funcionalidades.append('api_access')
    
    return {
        'tem_assinatura': True,
        'plano': assinatura.plano.nome,
        'status': assinatura.status,
        'data_expiracao': assinatura.data_fim.isoformat(),
        'dias_restantes': assinatura.calcular_dias_restantes(),
        'funcionalidades_disponivel': funcionalidades,
        'uso_atual': assinatura.calcular_percentual_uso(),
        'limites_excedidos': assinatura.verificar_limites_excedidos(),
        'auto_renovar': assinatura.auto_renovar
    }

def admin_required(f):
    """Decorator para verificar se usuário é admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Pega o current_user dos argumentos
        current_user = None
        for arg in args:
            if hasattr(arg, 'id') and hasattr(arg, 'email'):
                current_user = arg
                break
        
        if not current_user:
            return jsonify({'erro': 'Usuário não identificado'}), 401
        
        # Verifica se é admin (usando email específico ou campo admin)
        if current_user.email != 'fuda.julio@gmail.com':
            return jsonify({'erro': 'Acesso negado - apenas administradores'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def verificar_funcionalidade_disponivel(user_id, funcionalidade):
    """Verifica se funcionalidade está disponível para o usuário"""
    status = obter_status_plano(user_id)
    return funcionalidade in status.get('funcionalidades_disponivel', [])
