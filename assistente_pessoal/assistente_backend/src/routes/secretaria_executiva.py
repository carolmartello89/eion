from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import requests
import json
from ..models.auth import Usuario
from ..models.compromisso import Compromisso
from ..models.contato import Contato
from ..models.reuniao import Reuniao
from .. import db

secretaria_bp = Blueprint('secretaria', __name__)

# ===============================
# AGENDA EXECUTIVA
# ===============================

@secretaria_bp.route('/agenda-executiva', methods=['GET'])
@jwt_required()
def get_agenda_executiva():
    """Obter agenda executiva do dia"""
    try:
        user_id = get_jwt_identity()
        hoje = datetime.now().date()
        
        # Buscar compromissos do dia
        compromissos = Compromisso.query.filter(
            Compromisso.user_id == user_id,
            Compromisso.data_inicio >= hoje,
            Compromisso.data_inicio < hoje + timedelta(days=1)
        ).order_by(Compromisso.data_inicio).all()
        
        # Buscar reuniões do dia
        reunioes = Reuniao.query.filter(
            Reuniao.user_id == user_id,
            Reuniao.data_inicio >= hoje,
            Reuniao.data_inicio < hoje + timedelta(days=1)
        ).order_by(Reuniao.data_inicio).all()
        
        agenda = []
        
        # Adicionar compromissos
        for compromisso in compromissos:
            agenda.append({
                'id': compromisso.id,
                'tipo': 'compromisso',
                'titulo': compromisso.titulo,
                'horario': compromisso.data_inicio.strftime('%H:%M'),
                'duracao': f"{compromisso.duracao_minutos}min" if compromisso.duracao_minutos else "1h",
                'local': compromisso.local or 'Não informado',
                'descricao': compromisso.descricao,
                'prioridade': compromisso.prioridade or 'media'
            })
        
        # Adicionar reuniões
        for reuniao in reunioes:
            duracao = 60  # padrão
            if reuniao.data_fim:
                delta = reuniao.data_fim - reuniao.data_inicio
                duracao = int(delta.total_seconds() / 60)
            
            agenda.append({
                'id': reuniao.id,
                'tipo': 'reuniao',
                'titulo': reuniao.titulo,
                'horario': reuniao.data_inicio.strftime('%H:%M'),
                'duracao': f"{duracao}min",
                'local': reuniao.local or 'Virtual',
                'participantes': reuniao.participantes,
                'observacoes': reuniao.descricao
            })
        
        # Ordenar por horário
        agenda.sort(key=lambda x: x['horario'])
        
        return jsonify({
            'success': True,
            'agenda': agenda,
            'data': hoje.strftime('%Y-%m-%d'),
            'total_compromissos': len(agenda)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# TAREFAS URGENTES
# ===============================

@secretaria_bp.route('/tarefas-urgentes', methods=['GET'])
@jwt_required()
def get_tarefas_urgentes():
    """Obter tarefas urgentes e importantes"""
    try:
        user_id = get_jwt_identity()
        
        # Buscar compromissos com alta prioridade nos próximos 3 dias
        data_limite = datetime.now() + timedelta(days=3)
        
        compromissos_urgentes = Compromisso.query.filter(
            Compromisso.user_id == user_id,
            Compromisso.prioridade == 'alta',
            Compromisso.data_inicio <= data_limite,
            Compromisso.status != 'concluido'
        ).order_by(Compromisso.data_inicio).all()
        
        tarefas = []
        for compromisso in compromissos_urgentes:
            dias_restantes = (compromisso.data_inicio.date() - datetime.now().date()).days
            
            if dias_restantes == 0:
                prazo = "Hoje"
            elif dias_restantes == 1:
                prazo = "Amanhã"
            else:
                prazo = f"Em {dias_restantes} dias"
            
            tarefas.append({
                'id': compromisso.id,
                'titulo': compromisso.titulo,
                'tipo': 'compromisso',
                'prioridade': compromisso.prioridade,
                'prazo': prazo,
                'data_completa': compromisso.data_inicio.strftime('%d/%m/%Y %H:%M'),
                'status': compromisso.status or 'pendente',
                'descricao': compromisso.descricao
            })
        
        return jsonify({
            'success': True,
            'tarefas_urgentes': tarefas,
            'total': len(tarefas)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@secretaria_bp.route('/tarefa-urgente/<int:tarefa_id>/concluir', methods=['PUT'])
@jwt_required()
def concluir_tarefa_urgente(tarefa_id):
    """Marcar tarefa urgente como concluída"""
    try:
        user_id = get_jwt_identity()
        
        compromisso = Compromisso.query.filter(
            Compromisso.id == tarefa_id,
            Compromisso.user_id == user_id
        ).first()
        
        if not compromisso:
            return jsonify({'success': False, 'error': 'Tarefa não encontrada'}), 404
        
        compromisso.status = 'concluido'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarefa marcada como concluída'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# CONTATOS VIP
# ===============================

@secretaria_bp.route('/contatos-vip', methods=['GET'])
@jwt_required()
def get_contatos_vip():
    """Obter contatos VIP"""
    try:
        user_id = get_jwt_identity()
        
        contatos = Contato.query.filter(
            Contato.user_id == user_id,
            Contato.categoria.in_(['vip', 'importante', 'executivo'])
        ).order_by(Contato.nome).all()
        
        contatos_vip = []
        for contato in contatos:
            contatos_vip.append({
                'id': contato.id,
                'nome': contato.nome,
                'cargo': contato.cargo,
                'empresa': contato.empresa,
                'telefone': contato.telefone,
                'email': contato.email,
                'categoria': contato.categoria,
                'observacoes': contato.observacoes,
                'preferencias': contato.preferencias_comunicacao
            })
        
        return jsonify({
            'success': True,
            'contatos_vip': contatos_vip,
            'total': len(contatos_vip)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# SISTEMA DE RESERVAS
# ===============================

@secretaria_bp.route('/reserva', methods=['POST'])
@jwt_required()
def criar_reserva():
    """Criar nova reserva"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['tipo', 'local', 'data', 'horario', 'pessoas']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Campo {field} é obrigatório'}), 400
        
        # Criar compromisso para a reserva
        data_reserva = datetime.strptime(f"{data['data']} {data['horario']}", '%Y-%m-%d %H:%M')
        
        compromisso = Compromisso(
            user_id=user_id,
            titulo=f"Reserva - {data['local']}",
            descricao=f"Tipo: {data['tipo']}\nPessoas: {data['pessoas']}\nObservações: {data.get('observacoes', '')}",
            data_inicio=data_reserva,
            duracao_minutos=120,  # 2 horas padrão
            local=data['local'],
            categoria='reserva',
            prioridade='media'
        )
        
        db.session.add(compromisso)
        db.session.commit()
        
        # Simular confirmação da reserva (aqui seria integração real)
        reserva_confirmada = {
            'id': compromisso.id,
            'numero_reserva': f"RES{compromisso.id:06d}",
            'status': 'confirmada',
            'local': data['local'],
            'data': data['data'],
            'horario': data['horario'],
            'pessoas': data['pessoas'],
            'tipo': data['tipo'],
            'observacoes': data.get('observacoes', '')
        }
        
        return jsonify({
            'success': True,
            'message': 'Reserva criada com sucesso',
            'reserva': reserva_confirmada
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# ORGANIZAÇÃO DE VIAGENS
# ===============================

@secretaria_bp.route('/viagem', methods=['POST'])
@jwt_required()
def organizar_viagem():
    """Organizar nova viagem"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['destino', 'data_ida', 'data_volta']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Campo {field} é obrigatório'}), 400
        
        # Criar compromisso para a viagem
        data_ida = datetime.strptime(data['data_ida'], '%Y-%m-%d')
        data_volta = datetime.strptime(data['data_volta'], '%Y-%m-%d')
        
        # Compromisso de ida
        compromisso_ida = Compromisso(
            user_id=user_id,
            titulo=f"Viagem para {data['destino']}",
            descricao=f"Destino: {data['destino']}\nClasse: {data.get('classe_voo', 'executiva')}\nHospedagem: {data.get('tipo_hospedagem', 'hotel')}\nObservações: {data.get('observacoes', '')}",
            data_inicio=data_ida,
            data_fim=data_volta,
            local=data['destino'],
            categoria='viagem',
            prioridade='alta'
        )
        
        db.session.add(compromisso_ida)
        db.session.commit()
        
        # Simular organização da viagem completa
        viagem_organizada = {
            'id': compromisso_ida.id,
            'numero_viagem': f"VIG{compromisso_ida.id:06d}",
            'destino': data['destino'],
            'data_ida': data['data_ida'],
            'data_volta': data['data_volta'],
            'classe_voo': data.get('classe_voo', 'executiva'),
            'hospedagem': data.get('tipo_hospedagem', 'hotel'),
            'status': 'organizada',
            'observacoes': data.get('observacoes', ''),
            'itinerario': {
                'voo_ida': f"Voo confirmado para {data['destino']}",
                'hospedagem': f"Reserva confirmada - {data.get('tipo_hospedagem', 'hotel')}",
                'voo_volta': f"Voo de retorno confirmado",
                'transfer': "Transfer executivo incluído"
            }
        }
        
        return jsonify({
            'success': True,
            'message': 'Viagem organizada com sucesso',
            'viagem': viagem_organizada
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# LEMBRETES PESSOAIS
# ===============================

@secretaria_bp.route('/lembretes-pessoais', methods=['GET'])
@jwt_required()
def get_lembretes_pessoais():
    """Obter lembretes pessoais importantes"""
    try:
        user_id = get_jwt_identity()
        
        # Buscar compromissos pessoais importantes
        lembretes = Compromisso.query.filter(
            Compromisso.user_id == user_id,
            Compromisso.categoria.in_(['pessoal', 'familia', 'saude']),
            Compromisso.data_inicio >= datetime.now()
        ).order_by(Compromisso.data_inicio).limit(10).all()
        
        lembretes_pessoais = []
        for lembrete in lembretes:
            dias_restantes = (lembrete.data_inicio.date() - datetime.now().date()).days
            
            lembretes_pessoais.append({
                'id': lembrete.id,
                'titulo': lembrete.titulo,
                'tipo': lembrete.categoria,
                'data': lembrete.data_inicio.strftime('%Y-%m-%d'),
                'dias_restantes': dias_restantes,
                'observacoes': lembrete.descricao,
                'prioridade': lembrete.prioridade
            })
        
        return jsonify({
            'success': True,
            'lembretes_pessoais': lembretes_pessoais,
            'total': len(lembretes_pessoais)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# PREFERÊNCIAS EXECUTIVAS
# ===============================

@secretaria_bp.route('/preferencias', methods=['GET'])
@jwt_required()
def get_preferencias():
    """Obter preferências do executivo"""
    try:
        user_id = get_jwt_identity()
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuário não encontrado'}), 404
        
        # Preferências padrão + personalizadas
        preferencias = {
            'horario_trabalho': {
                'inicio': '08:00',
                'fim': '18:00',
                'almoco_inicio': '12:00',
                'almoco_fim': '14:00'
            },
            'reunioes': {
                'buffer_minutos': 15,
                'duracao_padrao': 60,
                'max_consecutivas': 3
            },
            'contatos': {
                'forma_preferida': 'email',
                'horario_nao_disturb': '19:00-08:00'
            },
            'viagens': {
                'classe_preferida': 'executiva',
                'hotel_categoria': '5_estrelas',
                'companhia_aerea': 'LATAM',
                'assento_preferido': 'corredor'
            },
            'restaurantes': {
                'cozinha_favorita': 'internacional',
                'restricoes': [],
                'preco_range': 'alto'
            }
        }
        
        return jsonify({
            'success': True,
            'preferencias': preferencias,
            'usuario': {
                'nome': usuario.preferred_name or usuario.email.split('@')[0],
                'cargo': 'CEO',  # Pode ser configurável
                'empresa': 'Empresa ABC'  # Pode ser configurável
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@secretaria_bp.route('/preferencias', methods=['PUT'])
@jwt_required()
def atualizar_preferencias():
    """Atualizar preferências do executivo"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Aqui seria salvo no banco as preferências personalizadas
        # Por simplicidade, vamos apenas confirmar o recebimento
        
        return jsonify({
            'success': True,
            'message': 'Preferências atualizadas com sucesso',
            'preferencias_atualizadas': data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# DASHBOARD EXECUTIVO
# ===============================

@secretaria_bp.route('/dashboard-executivo', methods=['GET'])
@jwt_required()
def get_dashboard_executivo():
    """Obter dados para dashboard executivo"""
    try:
        user_id = get_jwt_identity()
        hoje = datetime.now().date()
        
        # Compromissos hoje
        compromissos_hoje = Compromisso.query.filter(
            Compromisso.user_id == user_id,
            Compromisso.data_inicio >= hoje,
            Compromisso.data_inicio < hoje + timedelta(days=1)
        ).count()
        
        # Tarefas urgentes pendentes
        tarefas_urgentes = Compromisso.query.filter(
            Compromisso.user_id == user_id,
            Compromisso.prioridade == 'alta',
            Compromisso.status != 'concluido',
            Compromisso.data_inicio <= datetime.now() + timedelta(days=3)
        ).count()
        
        # Contatos VIP
        contatos_vip = Contato.query.filter(
            Contato.user_id == user_id,
            Contato.categoria.in_(['vip', 'importante', 'executivo'])
        ).count()
        
        # Próxima viagem
        proxima_viagem = Compromisso.query.filter(
            Compromisso.user_id == user_id,
            Compromisso.categoria == 'viagem',
            Compromisso.data_inicio >= datetime.now()
        ).order_by(Compromisso.data_inicio).first()
        
        dashboard = {
            'resumo': {
                'compromissos_hoje': compromissos_hoje,
                'tarefas_urgentes': tarefas_urgentes,
                'contatos_vip': contatos_vip,
                'proxima_viagem': proxima_viagem.titulo if proxima_viagem else None
            },
            'status': {
                'agenda_livre': compromissos_hoje < 5,
                'carga_trabalho': 'normal' if tarefas_urgentes < 3 else 'alta',
                'disponibilidade': 'disponivel'
            }
        }
        
        return jsonify({
            'success': True,
            'dashboard': dashboard
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
