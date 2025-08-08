from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json
from ..models.auth import Usuario
from .. import db

health_bp = Blueprint('health', __name__)

# ===============================
# DADOS DO SMARTWATCH
# ===============================

@health_bp.route('/smartwatch/dados', methods=['GET'])
@jwt_required()
def get_smartwatch_data():
    """Obter dados do smartwatch"""
    try:
        user_id = get_jwt_identity()
        
        # Simular dados do smartwatch (aqui seria integração real com APIs)
        dados_simulados = {
            'dispositivo': 'Apple Watch Series 9',
            'conectado': True,
            'ultima_sincronizacao': datetime.now().isoformat(),
            'batimento_cardiaco': {
                'atual': 72,
                'maximo_24h': 95,
                'minimo_24h': 58,
                'media_24h': 68,
                'zona': 'normal'
            },
            'pressao_arterial': {
                'sistolica': 125,
                'diastolica': 82,
                'classificacao': 'normal_alta'
            },
            'saturacao_oxigenio': {
                'atual': 98,
                'media_24h': 97
            },
            'temperatura_corporal': 36.8,
            'passos': {
                'hoje': 8547,
                'meta': 10000,
                'percentual': 85.47
            },
            'sono': {
                'duracao_ontem': 7.2,
                'qualidade': 'boa',
                'sono_profundo': 2.1
            },
            'stress': {
                'nivel_atual': 'baixo',
                'media_semana': 'moderado'
            },
            'calorias_queimadas': 1847,
            'atividade_fisica': {
                'minutos_ativos': 45,
                'meta_minutos': 60
            }
        }
        
        return jsonify({
            'success': True,
            'dados': dados_simulados
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@health_bp.route('/smartwatch/sincronizar', methods=['POST'])
@jwt_required()
def sync_smartwatch():
    """Sincronizar dados do smartwatch"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Aqui seria a lógica para sincronizar com APIs reais
        # Apple HealthKit, Google Fit, Samsung Health, etc.
        
        # Analisar dados recebidos e gerar alertas
        alertas = analisar_dados_saude(data.get('dados', {}))
        
        return jsonify({
            'success': True,
            'message': 'Dados sincronizados com sucesso',
            'alertas_gerados': len(alertas),
            'alertas': alertas
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# ANÁLISE DE SAÚDE
# ===============================

def analisar_dados_saude(dados):
    """Analisar dados de saúde e gerar alertas"""
    alertas = []
    
    if not dados:
        return alertas
    
    # Análise de frequência cardíaca
    if 'batimento_cardiaco' in dados:
        hr = dados['batimento_cardiaco'].get('atual', 0)
        
        if hr > 100:
            alertas.append({
                'tipo': 'warning',
                'titulo': 'Frequência Cardíaca Elevada',
                'descricao': f'Batimentos em {hr} bpm. Considere consultar cardiologista.',
                'prioridade': 'alta',
                'acao_sugerida': 'agendar_cardiologista'
            })
        elif hr < 50 and hr > 0:
            alertas.append({
                'tipo': 'warning',
                'titulo': 'Frequência Cardíaca Baixa',
                'descricao': f'Batimentos em {hr} bpm. Pode indicar bradicardia.',
                'prioridade': 'alta',
                'acao_sugerida': 'agendar_cardiologista'
            })
    
    # Análise de pressão arterial
    if 'pressao_arterial' in dados:
        sistolica = dados['pressao_arterial'].get('sistolica', 0)
        diastolica = dados['pressao_arterial'].get('diastolica', 0)
        
        if sistolica > 140 or diastolica > 90:
            alertas.append({
                'tipo': 'error',
                'titulo': 'Pressão Arterial Alta',
                'descricao': f'Pressão em {sistolica}/{diastolica} mmHg. Consulte médico urgentemente.',
                'prioridade': 'critica',
                'acao_sugerida': 'emergencia_medica'
            })
    
    # Análise de saturação de oxigênio
    if 'saturacao_oxigenio' in dados:
        o2 = dados['saturacao_oxigenio'].get('atual', 0)
        
        if o2 < 95 and o2 > 0:
            alertas.append({
                'tipo': 'error',
                'titulo': 'Saturação de Oxigênio Baixa',
                'descricao': f'Oxigenação em {o2}%. Procure atendimento médico imediatamente.',
                'prioridade': 'critica',
                'acao_sugerida': 'emergencia_medica'
            })
    
    # Análise de temperatura
    if 'temperatura_corporal' in dados:
        temp = dados.get('temperatura_corporal', 0)
        
        if temp > 38:
            alertas.append({
                'tipo': 'warning',
                'titulo': 'Febre Detectada',
                'descricao': f'Temperatura em {temp}°C. Monitore sintomas e considere consulta médica.',
                'prioridade': 'media',
                'acao_sugerida': 'agendar_clinico'
            })
    
    # Análise de sono
    if 'sono' in dados:
        duracao = dados['sono'].get('duracao_ontem', 0)
        
        if duracao < 6:
            alertas.append({
                'tipo': 'info',
                'titulo': 'Sono Insuficiente',
                'descricao': f'Apenas {duracao}h de sono. Qualidade do sono afeta saúde geral.',
                'prioridade': 'baixa',
                'acao_sugerida': 'melhorar_sono'
            })
    
    return alertas

@health_bp.route('/alertas-saude', methods=['GET'])
@jwt_required()
def get_health_alerts():
    """Obter alertas de saúde ativos"""
    try:
        user_id = get_jwt_identity()
        
        # Buscar alertas de saúde (aqui seria do banco de dados)
        alertas_simulados = [
            {
                'id': 1,
                'tipo': 'info',
                'titulo': 'Check-up Anual',
                'descricao': 'Está na hora do seu check-up médico anual.',
                'prioridade': 'baixa',
                'acao_sugerida': 'agendar_clinico',
                'data_criacao': datetime.now().isoformat()
            }
        ]
        
        return jsonify({
            'success': True,
            'alertas': alertas_simulados,
            'total': len(alertas_simulados)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# CONTATOS MÉDICOS
# ===============================

@health_bp.route('/contatos-medicos', methods=['GET'])
@jwt_required()
def get_medical_contacts():
    """Obter contatos médicos do usuário"""
    try:
        user_id = get_jwt_identity()
        
        # Buscar contatos médicos (aqui seria do banco de dados)
        contatos_medicos = [
            {
                'id': 1,
                'nome': 'Dr. Carlos Silva',
                'especialidade': 'Cardiologista',
                'telefone': '+55 11 99999-1111',
                'email': 'carlos@cardioclinica.com.br',
                'emergencia': True,
                'hospital': 'Hospital do Coração',
                'endereco': 'Rua das Palmeiras, 123',
                'convenio': True
            },
            {
                'id': 2,
                'nome': 'Dra. Ana Santos',
                'especialidade': 'Clínico Geral',
                'telefone': '+55 11 99999-2222',
                'email': 'ana@clinicapremium.com.br',
                'emergencia': False,
                'clinica': 'Clínica Premium',
                'endereco': 'Av. Paulista, 456',
                'convenio': True
            },
            {
                'id': 3,
                'nome': 'Dr. Pedro Costa',
                'especialidade': 'Endocrinologista',
                'telefone': '+55 11 99999-3333',
                'email': 'pedro@institutodiabetes.com.br',
                'emergencia': False,
                'clinica': 'Instituto de Diabetes',
                'endereco': 'Rua dos Médicos, 789',
                'convenio': False
            }
        ]
        
        return jsonify({
            'success': True,
            'contatos_medicos': contatos_medicos,
            'total': len(contatos_medicos)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@health_bp.route('/contato-medico', methods=['POST'])
@jwt_required()
def add_medical_contact():
    """Adicionar novo contato médico"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['nome', 'especialidade', 'telefone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Campo {field} é obrigatório'}), 400
        
        # Aqui seria inserido no banco de dados
        novo_contato = {
            'id': 999,  # Seria gerado pelo banco
            'nome': data['nome'],
            'especialidade': data['especialidade'],
            'telefone': data['telefone'],
            'email': data.get('email', ''),
            'emergencia': data.get('emergencia', False),
            'hospital': data.get('hospital', ''),
            'clinica': data.get('clinica', ''),
            'endereco': data.get('endereco', ''),
            'convenio': data.get('convenio', False)
        }
        
        return jsonify({
            'success': True,
            'message': 'Contato médico adicionado com sucesso',
            'contato': novo_contato
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# AGENDAMENTO MÉDICO
# ===============================

@health_bp.route('/agendar-consulta', methods=['POST'])
@jwt_required()
def schedule_medical_appointment():
    """Agendar consulta médica"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        medico_id = data.get('medico_id')
        data_consulta = data.get('data_consulta')
        horario = data.get('horario')
        motivo = data.get('motivo', '')
        urgente = data.get('urgente', False)
        
        if not all([medico_id, data_consulta, horario]):
            return jsonify({'success': False, 'error': 'Dados incompletos'}), 400
        
        # Simular agendamento (aqui seria integração com sistema do médico)
        consulta_agendada = {
            'id': 'CONS001',
            'medico_id': medico_id,
            'data_consulta': data_consulta,
            'horario': horario,
            'motivo': motivo,
            'status': 'agendada',
            'codigo_confirmacao': 'ABC123',
            'observacoes': 'Chegue 15 minutos antes da consulta'
        }
        
        return jsonify({
            'success': True,
            'message': 'Consulta agendada com sucesso',
            'consulta': consulta_agendada
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# EMERGÊNCIA MÉDICA
# ===============================

@health_bp.route('/emergencia', methods=['POST'])
@jwt_required()
def medical_emergency():
    """Protocolo de emergência médica"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        tipo_emergencia = data.get('tipo', 'geral')
        localizacao = data.get('localizacao', '')
        sintomas = data.get('sintomas', '')
        
        # Protocolo de emergência
        protocolo = {
            'timestamp': datetime.now().isoformat(),
            'usuario_id': user_id,
            'tipo_emergencia': tipo_emergencia,
            'localizacao': localizacao,
            'sintomas': sintomas,
            'acoes_realizadas': [
                'Alerta de emergência ativado',
                'Contatos de emergência notificados',
                'Localização enviada para serviços médicos'
            ],
            'numeros_emergencia': {
                'SAMU': '192',
                'Bombeiros': '193',
                'Polícia': '190'
            },
            'contato_emergencia_medico': {
                'nome': 'Dr. Carlos Silva',
                'telefone': '+55 11 99999-1111',
                'hospital': 'Hospital do Coração'
            }
        }
        
        # Log da emergência (importante para auditoria)
        print(f"🚨 EMERGÊNCIA MÉDICA - Usuário {user_id} - {datetime.now()}")
        print(f"Tipo: {tipo_emergencia}")
        print(f"Localização: {localizacao}")
        print(f"Sintomas: {sintomas}")
        
        return jsonify({
            'success': True,
            'message': 'Protocolo de emergência ativado',
            'protocolo': protocolo
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# HISTÓRICO DE SAÚDE
# ===============================

@health_bp.route('/historico-saude', methods=['GET'])
@jwt_required()
def get_health_history():
    """Obter histórico de saúde do usuário"""
    try:
        user_id = get_jwt_identity()
        
        # Buscar histórico (aqui seria do banco de dados)
        historico = {
            'consultas_recentes': [
                {
                    'data': '2025-07-15',
                    'medico': 'Dr. Carlos Silva',
                    'especialidade': 'Cardiologista',
                    'diagnostico': 'Check-up normal',
                    'observacoes': 'Pressão arterial ok, continuar exercícios'
                }
            ],
            'exames_realizados': [
                {
                    'data': '2025-07-10',
                    'tipo': 'Eletrocardiograma',
                    'resultado': 'Normal',
                    'laboratorio': 'Lab Premium'
                }
            ],
            'medicamentos_atuais': [
                {
                    'nome': 'Omega 3',
                    'dosagem': '1 cápsula/dia',
                    'prescrito_por': 'Dr. Carlos Silva',
                    'inicio': '2025-07-15'
                }
            ],
            'alergias': ['Penicilina'],
            'condicoes_cronicas': [],
            'vacinas': [
                {
                    'nome': 'COVID-19',
                    'data': '2025-06-01',
                    'dose': '5ª dose'
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'historico': historico
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# RELATÓRIOS DE SAÚDE
# ===============================

@health_bp.route('/relatorio-saude', methods=['GET'])
@jwt_required()
def generate_health_report():
    """Gerar relatório de saúde"""
    try:
        user_id = get_jwt_identity()
        periodo = request.args.get('periodo', '30')  # dias
        
        # Gerar relatório baseado nos dados do smartwatch
        relatorio = {
            'periodo': f'Últimos {periodo} dias',
            'resumo': {
                'frequencia_cardiaca_media': 68,
                'pressao_arterial_media': '125/82',
                'passos_por_dia_media': 8500,
                'horas_sono_media': 7.2,
                'calorias_queimadas_media': 1800
            },
            'tendencias': {
                'frequencia_cardiaca': 'estável',
                'atividade_fisica': 'melhorando',
                'qualidade_sono': 'boa',
                'stress': 'controlado'
            },
            'recomendacoes': [
                'Manter rotina de exercícios',
                'Continuar monitorando pressão arterial',
                'Agendar check-up anual',
                'Considerar aumentar meta de passos para 10.000'
            ],
            'alertas_periodo': 1,
            'consultas_agendadas': 0
        }
        
        return jsonify({
            'success': True,
            'relatorio': relatorio
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
