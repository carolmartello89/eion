from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.compromisso import Compromisso
from datetime import datetime, timedelta

compromisso_bp = Blueprint('compromisso', __name__)

@compromisso_bp.route('/compromissos', methods=['GET'])
def listar_compromissos():
    """Lista todos os compromissos"""
    try:
        # Parâmetros de filtro opcionais
        status = request.args.get('status')
        tipo = request.args.get('tipo')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = Compromisso.query
        
        if status:
            query = query.filter(Compromisso.status == status)
        if tipo:
            query = query.filter(Compromisso.tipo == tipo)
        if data_inicio:
            data_inicio_dt = datetime.fromisoformat(data_inicio.replace('Z', '+00:00'))
            query = query.filter(Compromisso.data_hora >= data_inicio_dt)
        if data_fim:
            data_fim_dt = datetime.fromisoformat(data_fim.replace('Z', '+00:00'))
            query = query.filter(Compromisso.data_hora <= data_fim_dt)
        
        compromissos = query.order_by(Compromisso.data_hora.asc()).all()
        return jsonify([compromisso.to_dict() for compromisso in compromissos])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@compromisso_bp.route('/compromissos', methods=['POST'])
def criar_compromisso():
    """Cria um novo compromisso"""
    try:
        dados = request.get_json()
        
        # Validação básica
        if not dados.get('titulo'):
            return jsonify({'erro': 'Título é obrigatório'}), 400
        
        if not dados.get('data_hora'):
            return jsonify({'erro': 'Data e hora são obrigatórias'}), 400
        
        # Converte string de data para datetime
        data_hora = datetime.fromisoformat(dados['data_hora'].replace('Z', '+00:00'))
        
        compromisso = Compromisso(
            titulo=dados['titulo'],
            descricao=dados.get('descricao', ''),
            data_hora=data_hora,
            alerta_antecedencia=dados.get('alerta_antecedencia', 30),
            tipo=dados.get('tipo', 'evento'),
            status=dados.get('status', 'pendente'),
            prioridade=dados.get('prioridade', 'media'),
            localizacao=dados.get('localizacao', '')
        )
        
        db.session.add(compromisso)
        db.session.commit()
        
        return jsonify(compromisso.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@compromisso_bp.route('/compromissos/<compromisso_id>', methods=['GET'])
def obter_compromisso(compromisso_id):
    """Obtém um compromisso específico"""
    try:
        compromisso = Compromisso.query.get_or_404(compromisso_id)
        return jsonify(compromisso.to_dict())
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@compromisso_bp.route('/compromissos/<compromisso_id>', methods=['PUT'])
def atualizar_compromisso(compromisso_id):
    """Atualiza um compromisso"""
    try:
        compromisso = Compromisso.query.get_or_404(compromisso_id)
        dados = request.get_json()
        
        # Atualiza campos se fornecidos
        if 'titulo' in dados:
            compromisso.titulo = dados['titulo']
        if 'descricao' in dados:
            compromisso.descricao = dados['descricao']
        if 'data_hora' in dados:
            compromisso.data_hora = datetime.fromisoformat(dados['data_hora'].replace('Z', '+00:00'))
        if 'alerta_antecedencia' in dados:
            compromisso.alerta_antecedencia = dados['alerta_antecedencia']
        if 'tipo' in dados:
            compromisso.tipo = dados['tipo']
        if 'status' in dados:
            compromisso.status = dados['status']
        if 'prioridade' in dados:
            compromisso.prioridade = dados['prioridade']
        if 'localizacao' in dados:
            compromisso.localizacao = dados['localizacao']
        
        compromisso.atualizado_em = datetime.utcnow()
        db.session.commit()
        
        return jsonify(compromisso.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@compromisso_bp.route('/compromissos/<compromisso_id>', methods=['DELETE'])
def deletar_compromisso(compromisso_id):
    """Deleta um compromisso"""
    try:
        compromisso = Compromisso.query.get_or_404(compromisso_id)
        db.session.delete(compromisso)
        db.session.commit()
        return jsonify({'mensagem': 'Compromisso deletado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@compromisso_bp.route('/compromissos/hoje', methods=['GET'])
def compromissos_hoje():
    """Lista compromissos de hoje"""
    try:
        hoje = datetime.now().date()
        inicio_dia = datetime.combine(hoje, datetime.min.time())
        fim_dia = datetime.combine(hoje, datetime.max.time())
        
        compromissos = Compromisso.query.filter(
            Compromisso.data_hora >= inicio_dia,
            Compromisso.data_hora <= fim_dia,
            Compromisso.status != 'cancelado'
        ).order_by(Compromisso.data_hora.asc()).all()
        
        return jsonify([compromisso.to_dict() for compromisso in compromissos])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@compromisso_bp.route('/compromissos/proximos', methods=['GET'])
def compromissos_proximos():
    """Lista próximos compromissos (próximas 24 horas)"""
    try:
        agora = datetime.utcnow()
        proximas_24h = agora + timedelta(hours=24)
        
        compromissos = Compromisso.query.filter(
            Compromisso.data_hora >= agora,
            Compromisso.data_hora <= proximas_24h,
            Compromisso.status == 'pendente'
        ).order_by(Compromisso.data_hora.asc()).all()
        
        return jsonify([compromisso.to_dict() for compromisso in compromissos])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@compromisso_bp.route('/compromissos/alertas', methods=['GET'])
def compromissos_com_alerta():
    """Lista compromissos que precisam de alerta agora"""
    try:
        agora = datetime.utcnow()
        
        # Busca compromissos que devem ter alerta nos próximos minutos
        compromissos_alerta = []
        compromissos = Compromisso.query.filter(
            Compromisso.status == 'pendente',
            Compromisso.data_hora > agora
        ).all()
        
        for compromisso in compromissos:
            tempo_para_compromisso = compromisso.data_hora - agora
            minutos_para_compromisso = tempo_para_compromisso.total_seconds() / 60
            
            # Se está dentro do tempo de antecedência do alerta
            if minutos_para_compromisso <= compromisso.alerta_antecedencia:
                compromissos_alerta.append(compromisso)
        
        return jsonify([compromisso.to_dict() for compromisso in compromissos_alerta])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@compromisso_bp.route('/compromissos/semana', methods=['GET'])
def compromissos_semana():
    """Lista compromissos da semana atual"""
    try:
        hoje = datetime.now().date()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        
        inicio_semana_dt = datetime.combine(inicio_semana, datetime.min.time())
        fim_semana_dt = datetime.combine(fim_semana, datetime.max.time())
        
        compromissos = Compromisso.query.filter(
            Compromisso.data_hora >= inicio_semana_dt,
            Compromisso.data_hora <= fim_semana_dt,
            Compromisso.status != 'cancelado'
        ).order_by(Compromisso.data_hora.asc()).all()
        
        return jsonify([compromisso.to_dict() for compromisso in compromissos])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

