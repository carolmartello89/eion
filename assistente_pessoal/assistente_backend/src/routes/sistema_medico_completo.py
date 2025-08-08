from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json
import requests
import base64
from werkzeug.utils import secure_filename
import os

medico_bp = Blueprint('medico', __name__)

# Simulação de dados médicos avançados
medicamentos_db = {}
exames_db = {}
consultas_db = {}
saude_mental_db = {}
nutricao_db = {}
fisioterapia_db = {}
prevencao_db = {}
emergencia_db = {}
dispositivos_db = {}

# Medicamentos - Sistema Completo
@medico_bp.route('/medicamentos', methods=['GET'])
@jwt_required()
def listar_medicamentos():
    try:
        user_id = get_jwt_identity()
        medicamentos = medicamentos_db.get(user_id, [])
        
        return jsonify({
            'success': True,
            'medicamentos': medicamentos
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@medico_bp.route('/medicamentos', methods=['POST'])
@jwt_required()
def adicionar_medicamento():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validações
        if not data.get('nome') or not data.get('dosagem'):
            return jsonify({'success': False, 'error': 'Nome e dosagem são obrigatórios'}), 400
        
        # Verificar interações medicamentosas (simulação)
        interacoes = verificar_interacoes_medicamentosas(user_id, data['nome'])
        
        medicamento = {
            'id': len(medicamentos_db.get(user_id, [])) + 1,
            'nome': data['nome'],
            'dosagem': data['dosagem'],
            'horarios': data.get('horarios', []),
            'frequencia': data.get('frequencia', 'diaria'),
            'duracao': data.get('duracao', 30),
            'observacoes': data.get('observacoes', ''),
            'status': 'ativo',
            'data_inicio': datetime.now().isoformat(),
            'proxima_dose': calcular_proxima_dose(data.get('horarios', [])),
            'interacoes': interacoes,
            'alertas_efeitos': gerar_alertas_efeitos_colaterais(data['nome'])
        }
        
        if user_id not in medicamentos_db:
            medicamentos_db[user_id] = []
        
        medicamentos_db[user_id].append(medicamento)
        
        return jsonify({
            'success': True,
            'medicamento': medicamento,
            'interacoes_detectadas': len(interacoes) > 0,
            'mensagem': f'Medicamento adicionado. {len(interacoes)} interação(ões) detectada(s).' if interacoes else 'Medicamento adicionado com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Exames - Análise com IA
@medico_bp.route('/exames', methods=['GET'])
@jwt_required()
def listar_exames():
    try:
        user_id = get_jwt_identity()
        exames = exames_db.get(user_id, [])
        
        return jsonify({
            'success': True,
            'exames': exames
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@medico_bp.route('/exames/upload', methods=['POST'])
@jwt_required()
def upload_exame():
    try:
        user_id = get_jwt_identity()
        
        if 'arquivo' not in request.files:
            return jsonify({'success': False, 'error': 'Arquivo não encontrado'}), 400
        
        arquivo = request.files['arquivo']
        tipo = request.form.get('tipo')
        data_exame = request.form.get('data')
        observacoes = request.form.get('observacoes', '')
        
        if arquivo.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'}), 400
        
        # Simular análise com IA
        interpretacao_ia = analisar_exame_com_ia(tipo, arquivo)
        
        exame = {
            'id': len(exames_db.get(user_id, [])) + 1,
            'tipo': tipo,
            'data': data_exame,
            'arquivo': secure_filename(arquivo.filename),
            'observacoes': observacoes,
            'status': interpretacao_ia['status'],
            'interpretacao': interpretacao_ia['interpretacao'],
            'alteracoes': interpretacao_ia['alteracoes'],
            'recomendacoes': interpretacao_ia['recomendacoes'],
            'data_upload': datetime.now().isoformat(),
            'ia_confianca': interpretacao_ia['confianca']
        }
        
        if user_id not in exames_db:
            exames_db[user_id] = []
        
        exames_db[user_id].append(exame)
        
        return jsonify({
            'success': True,
            'exame': exame
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Telemedicina
@medico_bp.route('/consultas', methods=['GET'])
@jwt_required()
def listar_consultas():
    try:
        user_id = get_jwt_identity()
        consultas = consultas_db.get(user_id, [])
        
        return jsonify({
            'success': True,
            'consultas': consultas
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@medico_bp.route('/consultas', methods=['POST'])
@jwt_required()
def agendar_consulta():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Selecionar médico disponível
        medico_info = selecionar_medico_disponivel(data['especialidade'], data['data'], data['horario'])
        
        # Calcular valor baseado na especialidade e urgência
        valor = calcular_valor_consulta(data['especialidade'], data.get('prioridade', 'normal'))
        
        consulta = {
            'id': len(consultas_db.get(user_id, [])) + 1,
            'especialidade': data['especialidade'],
            'medico': medico_info['nome'],
            'medico_crm': medico_info['crm'],
            'data': data['data'],
            'horario': data['horario'],
            'sintomas': data.get('sintomas', ''),
            'prioridade': data.get('prioridade', 'normal'),
            'status': 'agendada',
            'tipo': 'telemedicina',
            'valor': valor,
            'pagamento': 'manual',  # Sempre manual como solicitado
            'link_chamada': gerar_link_telemedicina(),
            'data_agendamento': datetime.now().isoformat()
        }
        
        if user_id not in consultas_db:
            consultas_db[user_id] = []
        
        consultas_db[user_id].append(consulta)
        
        return jsonify({
            'success': True,
            'consulta': consulta
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Saúde Mental
@medico_bp.route('/saude-mental', methods=['GET'])
@jwt_required()
def obter_saude_mental():
    try:
        user_id = get_jwt_identity()
        dados = saude_mental_db.get(user_id, {
            'humor_hoje': 5,
            'ansiedade': 3,
            'energia': 7,
            'sono_qualidade': 6,
            'exercicio_mindfulness': False,
            'historico_humor': [6, 7, 5, 8, 7, 7, 7],
            'analise_ia': gerar_analise_saude_mental_ia()
        })
        
        return jsonify({
            'success': True,
            'dados': dados
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@medico_bp.route('/saude-mental', methods=['POST'])
@jwt_required()
def atualizar_saude_mental():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Atualizar dados de saúde mental
        if user_id not in saude_mental_db:
            saude_mental_db[user_id] = {}
        
        saude_mental_db[user_id].update(data)
        saude_mental_db[user_id]['ultima_atualizacao'] = datetime.now().isoformat()
        
        # Análise automática de risco
        alerta_risco = analisar_risco_saude_mental(data)
        
        return jsonify({
            'success': True,
            'dados': saude_mental_db[user_id],
            'alerta_risco': alerta_risco
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Nutrição
@medico_bp.route('/nutricao', methods=['GET'])
@jwt_required()
def obter_nutricao():
    try:
        user_id = get_jwt_identity()
        dados = nutricao_db.get(user_id, {
            'refeicoes_hoje': [],
            'agua_consumida': 0,
            'meta_agua': 2500,
            'meta_calorias': 2000,
            'calorias_consumidas': 0,
            'restricoes': []
        })
        
        return jsonify({
            'success': True,
            'dados': dados
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@medico_bp.route('/nutricao/analisar-prato', methods=['POST'])
@jwt_required()
def analisar_prato():
    try:
        user_id = get_jwt_identity()
        
        if 'imagem' not in request.files:
            return jsonify({'success': False, 'error': 'Imagem não encontrada'}), 400
        
        imagem = request.files['imagem']
        
        # Simular análise com IA de imagem
        analise = analisar_imagem_comida_ia(imagem)
        
        return jsonify({
            'success': True,
            'analise': analise
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Fisioterapia
@medico_bp.route('/fisioterapia', methods=['GET'])
@jwt_required()
def obter_fisioterapia():
    try:
        user_id = get_jwt_identity()
        dados = fisioterapia_db.get(user_id, {
            'exercicios_hoje': [],
            'plano_ativo': None,
            'progresso_semanal': []
        })
        
        return jsonify({
            'success': True,
            'dados': dados
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Medicina Preventiva
@medico_bp.route('/prevencao', methods=['GET'])
@jwt_required()
def obter_prevencao():
    try:
        user_id = get_jwt_identity()
        dados = prevencao_db.get(user_id, {
            'proximos_exames': [],
            'vacinas_pendentes': [],
            'check_ups': []
        })
        
        return jsonify({
            'success': True,
            'dados': dados
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Emergência
@medico_bp.route('/emergencia', methods=['GET'])
@jwt_required()
def obter_emergencia():
    try:
        user_id = get_jwt_identity()
        dados = emergencia_db.get(user_id, {
            'contatos_emergencia': [],
            'condicoes_medicas': [],
            'alergias': [],
            'medicamentos_uso': []
        })
        
        return jsonify({
            'success': True,
            'dados': dados
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Dispositivos IoT
@medico_bp.route('/dispositivos', methods=['GET'])
@jwt_required()
def obter_dispositivos():
    try:
        user_id = get_jwt_identity()
        dados = dispositivos_db.get(user_id, {
            'conectados': [],
            'leituras_recentes': [],
            'alertas': []
        })
        
        return jsonify({
            'success': True,
            'dados': dados
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Funções auxiliares
def verificar_interacoes_medicamentosas(user_id, novo_medicamento):
    """Simula verificação de interações medicamentosas"""
    medicamentos_usuario = medicamentos_db.get(user_id, [])
    interacoes = []
    
    # Base de dados de interações (simulada)
    base_interacoes = {
        'Varfarina': ['Aspirina', 'Ibuprofeno'],
        'Losartana': ['Suplementos de Potássio'],
        'Metformina': ['Álcool', 'Contraste iodado']
    }
    
    for med in medicamentos_usuario:
        if med['status'] == 'ativo':
            if novo_medicamento in base_interacoes.get(med['nome'], []) or \
               med['nome'] in base_interacoes.get(novo_medicamento, []):
                interacoes.append({
                    'medicamento': med['nome'],
                    'tipo_interacao': 'moderada',
                    'descricao': f'Possível interação entre {novo_medicamento} e {med["nome"]}'
                })
    
    return interacoes

def calcular_proxima_dose(horarios):
    """Calcula o horário da próxima dose"""
    if not horarios:
        return "08:00"
    
    now = datetime.now()
    hoje = now.strftime("%H:%M")
    
    for horario in sorted(horarios):
        if horario > hoje:
            return horario
    
    return horarios[0]  # Próximo dia

def gerar_alertas_efeitos_colaterais(medicamento):
    """Gera alertas de efeitos colaterais baseados no medicamento"""
    base_efeitos = {
        'Losartana': ['Tontura', 'Tosse seca', 'Hipotensão'],
        'Metformina': ['Náusea', 'Diarreia', 'Sabor metálico'],
        'Aspirina': ['Irritação gástrica', 'Sangramento']
    }
    
    return base_efeitos.get(medicamento, [])

def analisar_exame_com_ia(tipo_exame, arquivo):
    """Simula análise de exame com IA"""
    
    analises_simuladas = {
        'hemograma': {
            'status': 'normal',
            'interpretacao': 'Hemograma dentro dos parâmetros de normalidade',
            'alteracoes': [],
            'recomendacoes': ['Manter acompanhamento de rotina'],
            'confianca': 95
        },
        'lipidico': {
            'status': 'alterado',
            'interpretacao': 'Colesterol total elevado',
            'alteracoes': ['Colesterol total: 245 mg/dL (elevado)'],
            'recomendacoes': [
                'Consulta com cardiologista',
                'Dieta com baixo teor de gordura saturada',
                'Atividade física regular'
            ],
            'confianca': 92
        },
        'glicemia': {
            'status': 'normal',
            'interpretacao': 'Glicemia e HbA1c dentro da normalidade',
            'alteracoes': [],
            'recomendacoes': ['Manter controle dietético'],
            'confianca': 97
        }
    }
    
    return analises_simuladas.get(tipo_exame, {
        'status': 'analisado',
        'interpretacao': 'Exame analisado pela IA médica',
        'alteracoes': [],
        'recomendacoes': ['Consulte seu médico para interpretação detalhada'],
        'confianca': 85
    })

def selecionar_medico_disponivel(especialidade, data, horario):
    """Seleciona médico disponível para a especialidade"""
    medicos = {
        'clinica_geral': {'nome': 'Dr. João Silva', 'crm': '12345-SP'},
        'cardiologia': {'nome': 'Dr. Ricardo Santos', 'crm': '23456-SP'},
        'dermatologia': {'nome': 'Dra. Ana Costa', 'crm': '34567-SP'},
        'psiquiatria': {'nome': 'Dr. Carlos Lima', 'crm': '45678-SP'},
        'endocrinologia': {'nome': 'Dra. Maria Oliveira', 'crm': '56789-SP'},
        'ginecologia': {'nome': 'Dra. Paula Santos', 'crm': '67890-SP'},
        'pediatria': {'nome': 'Dr. Roberto Silva', 'crm': '78901-SP'},
        'ortopedia': {'nome': 'Dr. Fernando Costa', 'crm': '89012-SP'},
        'neurologia': {'nome': 'Dra. Luiza Fernandes', 'crm': '90123-SP'}
    }
    
    return medicos.get(especialidade, {'nome': 'Dr. João Silva', 'crm': '12345-SP'})

def calcular_valor_consulta(especialidade, prioridade):
    """Calcula valor da consulta baseado na especialidade e prioridade"""
    valores_base = {
        'clinica_geral': 120,
        'cardiologia': 200,
        'dermatologia': 180,
        'psiquiatria': 220,
        'endocrinologia': 190,
        'ginecologia': 170,
        'pediatria': 150,
        'ortopedia': 180,
        'neurologia': 210
    }
    
    valor_base = valores_base.get(especialidade, 120)
    
    if prioridade == 'urgente':
        valor_base *= 1.5
    elif prioridade == 'emergencia':
        valor_base *= 2.0
    
    return f"R$ {valor_base:.2f}".replace('.', ',')

def gerar_link_telemedicina():
    """Gera link para telemedicina"""
    import uuid
    return f"https://telemedicina.assistente.com/sala/{uuid.uuid4()}"

def gerar_analise_saude_mental_ia():
    """Gera análise de saúde mental com IA"""
    return {
        'status': 'normal',
        'recomendacoes': [
            'Manter rotina de exercícios de mindfulness',
            'Estabelecer horário regular de sono',
            'Praticar atividade física 3x por semana'
        ],
        'alertas': []
    }

def analisar_risco_saude_mental(dados):
    """Analisa risco de saúde mental baseado nos dados"""
    humor = dados.get('humor_hoje', 5)
    ansiedade = dados.get('ansiedade', 5)
    
    if humor <= 3 and ansiedade >= 8:
        return {
            'nivel': 'alto',
            'mensagem': 'Padrão preocupante detectado. Recomendamos consulta com psicólogo.',
            'acao_recomendada': 'agendar_consulta_psicologia'
        }
    elif humor <= 4 or ansiedade >= 7:
        return {
            'nivel': 'moderado',
            'mensagem': 'Atenção necessária. Considere exercícios de relaxamento.',
            'acao_recomendada': 'exercicios_relaxamento'
        }
    
    return None

def analisar_imagem_comida_ia(imagem):
    """Simula análise de imagem de comida com IA"""
    # Simulação de análise nutricional
    return {
        'alimentos_detectados': [
            'Arroz branco (150g)',
            'Feijão carioca (100g)',
            'Frango grelhado (120g)',
            'Salada verde (80g)'
        ],
        'calorias_estimadas': 580,
        'macronutrientes': {
            'proteinas': '35g',
            'carboidratos': '65g',
            'gorduras': '18g'
        },
        'avaliacao_nutricional': 'Refeição equilibrada e saudável',
        'sugestoes': [
            'Adicionar mais vegetais coloridos',
            'Considerar reduzir a porção de arroz'
        ],
        'confianca': 88
    }
