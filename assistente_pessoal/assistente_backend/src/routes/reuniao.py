from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.reuniao import Reuniao
from datetime import datetime
import json

reuniao_bp = Blueprint('reuniao', __name__)

@reuniao_bp.route('/reunioes', methods=['GET'])
def listar_reunioes():
    """Lista todas as reuniões"""
    try:
        reunioes = Reuniao.query.order_by(Reuniao.data_hora.desc()).all()
        return jsonify([reuniao.to_dict() for reuniao in reunioes])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@reuniao_bp.route('/reunioes', methods=['POST'])
def criar_reuniao():
    """Cria uma nova reunião"""
    try:
        dados = request.get_json()
        
        # Validação básica
        if not dados.get('titulo'):
            return jsonify({'erro': 'Título é obrigatório'}), 400
        
        if not dados.get('data_hora'):
            return jsonify({'erro': 'Data e hora são obrigatórias'}), 400
        
        # Converte string de data para datetime
        data_hora = datetime.fromisoformat(dados['data_hora'].replace('Z', '+00:00'))
        
        # Converte participantes para JSON string se for lista
        participantes = dados.get('participantes', [])
        if isinstance(participantes, list):
            participantes = json.dumps(participantes)
        
        reuniao = Reuniao(
            titulo=dados['titulo'],
            descricao=dados.get('descricao', ''),
            data_hora=data_hora,
            participantes=participantes,
            status=dados.get('status', 'agendada')
        )
        
        db.session.add(reuniao)
        db.session.commit()
        
        return jsonify(reuniao.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@reuniao_bp.route('/reunioes/<reuniao_id>', methods=['GET'])
def obter_reuniao(reuniao_id):
    """Obtém uma reunião específica"""
    try:
        reuniao = Reuniao.query.get_or_404(reuniao_id)
        return jsonify(reuniao.to_dict())
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@reuniao_bp.route('/reunioes/<reuniao_id>', methods=['PUT'])
def atualizar_reuniao(reuniao_id):
    """Atualiza uma reunião"""
    try:
        reuniao = Reuniao.query.get_or_404(reuniao_id)
        dados = request.get_json()
        
        # Atualiza campos se fornecidos
        if 'titulo' in dados:
            reuniao.titulo = dados['titulo']
        if 'descricao' in dados:
            reuniao.descricao = dados['descricao']
        if 'data_hora' in dados:
            reuniao.data_hora = datetime.fromisoformat(dados['data_hora'].replace('Z', '+00:00'))
        if 'participantes' in dados:
            participantes = dados['participantes']
            if isinstance(participantes, list):
                participantes = json.dumps(participantes)
            reuniao.participantes = participantes
        if 'audio_url' in dados:
            reuniao.audio_url = dados['audio_url']
        if 'transcricao' in dados:
            reuniao.transcricao = dados['transcricao']
        if 'resumo' in dados:
            reuniao.resumo = dados['resumo']
        if 'status' in dados:
            reuniao.status = dados['status']
        
        reuniao.atualizado_em = datetime.utcnow()
        db.session.commit()
        
        return jsonify(reuniao.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@reuniao_bp.route('/reunioes/<reuniao_id>', methods=['DELETE'])
def deletar_reuniao(reuniao_id):
    """Deleta uma reunião"""
    try:
        reuniao = Reuniao.query.get_or_404(reuniao_id)
        db.session.delete(reuniao)
        db.session.commit()
        return jsonify({'mensagem': 'Reunião deletada com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@reuniao_bp.route('/reunioes/<reuniao_id>/resumo', methods=['POST'])
def gerar_resumo(reuniao_id):
    """Gera resumo automático da reunião baseado na transcrição"""
    try:
        reuniao = Reuniao.query.get_or_404(reuniao_id)
        
        if not reuniao.transcricao:
            return jsonify({'erro': 'Transcrição não disponível'}), 400
        
        # Aqui seria implementada a lógica de IA para gerar resumo
        # Por enquanto, vamos criar um resumo simples
        transcricao = reuniao.transcricao
        palavras = transcricao.split()
        
        # Resumo básico - primeiras e últimas frases
        frases = transcricao.split('.')
        if len(frases) > 3:
            resumo = f"Resumo da reunião '{reuniao.titulo}':\n\n"
            resumo += f"Início: {frases[0].strip()}.\n"
            resumo += f"Pontos principais discutidos durante a reunião.\n"
            resumo += f"Conclusão: {frases[-2].strip()}.\n\n"
            resumo += f"Duração estimada: {len(palavras)} palavras discutidas."
        else:
            resumo = f"Resumo da reunião '{reuniao.titulo}':\n\n{transcricao}"
        
        reuniao.resumo = resumo
        reuniao.atualizado_em = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'resumo': resumo})
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@reuniao_bp.route('/reunioes/proximas', methods=['GET'])
def reunioes_proximas():
    """Lista reuniões próximas (próximas 24 horas)"""
    try:
        agora = datetime.utcnow()
        from datetime import timedelta
        proximas_24h = agora + timedelta(hours=24)
        
        reunioes = Reuniao.query.filter(
            Reuniao.data_hora >= agora,
            Reuniao.data_hora <= proximas_24h,
            Reuniao.status.in_(['agendada', 'em_andamento'])
        ).order_by(Reuniao.data_hora.asc()).all()
        
        return jsonify([reuniao.to_dict() for reuniao in reunioes])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

