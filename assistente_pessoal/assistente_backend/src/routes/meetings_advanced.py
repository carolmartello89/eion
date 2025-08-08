from flask import Blueprint, request, jsonify, current_app
from src.routes.auth import token_required
import openai
import os
import tempfile
import json
from datetime import datetime

meetings_advanced_bp = Blueprint('meetings_advanced', __name__)

# Configuração do OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_API_BASE')

@meetings_advanced_bp.route('/process-recording', methods=['POST'])
@token_required
def process_recording(current_user):
    """Processa gravação de reunião com IA"""
    try:
        # Verifica se há arquivo de áudio
        if 'audio' not in request.files:
            return jsonify({'erro': 'Arquivo de áudio não fornecido'}), 400
        
        audio_file = request.files['audio']
        meeting_id = request.form.get('meetingId')
        participants = json.loads(request.form.get('participants', '[]'))
        
        if audio_file.filename == '':
            return jsonify({'erro': 'Nenhum arquivo selecionado'}), 400
        
        # Salva arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
            audio_file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Processa áudio com OpenAI Whisper
            transcript = transcribe_audio(temp_path)
            
            # Gera resumo e ações com GPT
            summary, action_items = generate_summary_and_actions(transcript, participants)
            
            # Salva resultados no banco (simulado)
            save_meeting_results(meeting_id, transcript, summary, action_items, current_user)
            
            return jsonify({
                'transcript': transcript,
                'summary': summary,
                'actionItems': action_items,
                'processedAt': datetime.now().isoformat()
            }), 200
            
        finally:
            # Remove arquivo temporário
            try:
                os.unlink(temp_path)
            except:
                pass
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

def transcribe_audio(audio_path):
    """Transcreve áudio usando OpenAI Whisper"""
    try:
        with open(audio_path, 'rb') as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                language="pt"
            )
        return transcript.text
    except Exception as e:
        print(f"Erro na transcrição: {e}")
        return "Erro ao transcrever áudio. Verifique a qualidade da gravação."

def generate_summary_and_actions(transcript, participants):
    """Gera resumo e ações usando GPT"""
    try:
        participants_list = ", ".join(participants) if participants else "participantes"
        
        prompt = f"""
        Analise a seguinte transcrição de reunião e forneça:
        1. Um resumo conciso dos principais pontos discutidos
        2. Lista de ações e tarefas identificadas
        
        Participantes: {participants_list}
        
        Transcrição:
        {transcript}
        
        Responda em JSON com a estrutura:
        {{
            "summary": "resumo da reunião",
            "actionItems": [
                {{
                    "task": "descrição da tarefa",
                    "assignee": "responsável (se mencionado)",
                    "deadline": "prazo (se mencionado)",
                    "priority": "alta/média/baixa"
                }}
            ]
        }}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em análise de reuniões. Responda sempre em JSON válido."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('summary', ''), result.get('actionItems', [])
        
    except Exception as e:
        print(f"Erro na geração de resumo: {e}")
        return "Resumo não disponível", []

def save_meeting_results(meeting_id, transcript, summary, action_items, user):
    """Salva resultados da reunião no banco de dados"""
    # Em uma implementação real, isso salvaria no banco de dados
    # Por enquanto, apenas simula o salvamento
    
    meeting_data = {
        'meeting_id': meeting_id,
        'user_id': user.id,
        'transcript': transcript,
        'summary': summary,
        'action_items': action_items,
        'processed_at': datetime.now().isoformat()
    }
    
    print(f"Salvando dados da reunião: {meeting_data}")
    return True

@meetings_advanced_bp.route('/meeting-insights/<meeting_id>', methods=['GET'])
@token_required
def get_meeting_insights(current_user, meeting_id):
    """Retorna insights da reunião"""
    try:
        # Simulação de insights
        insights = {
            'duration': '45 minutos',
            'participantCount': 4,
            'topicsDiscussed': [
                'Planejamento do projeto',
                'Definição de prazos',
                'Distribuição de tarefas',
                'Próximos passos'
            ],
            'sentimentAnalysis': {
                'overall': 'positivo',
                'confidence': 0.85
            },
            'keyDecisions': [
                'Aprovação do cronograma do projeto',
                'Definição de responsabilidades',
                'Agendamento da próxima reunião'
            ],
            'followUpRequired': True,
            'actionItemsCount': 5,
            'completedTasks': 2
        }
        
        return jsonify(insights), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@meetings_advanced_bp.route('/generate-meeting-notes', methods=['POST'])
@token_required
def generate_meeting_notes(current_user):
    """Gera ata da reunião formatada"""
    try:
        data = request.get_json()
        meeting_data = data.get('meetingData', {})
        
        # Gera ata formatada com IA
        notes = generate_formatted_notes(meeting_data)
        
        return jsonify({
            'notes': notes,
            'generatedAt': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

def generate_formatted_notes(meeting_data):
    """Gera ata formatada da reunião"""
    try:
        prompt = f"""
        Gere uma ata de reunião profissional e bem formatada baseada nos seguintes dados:
        
        Título: {meeting_data.get('title', 'Reunião')}
        Data: {meeting_data.get('date', datetime.now().strftime('%d/%m/%Y'))}
        Participantes: {', '.join(meeting_data.get('participants', []))}
        Resumo: {meeting_data.get('summary', '')}
        Ações: {meeting_data.get('actionItems', [])}
        
        Formate como uma ata profissional com:
        - Cabeçalho
        - Lista de participantes
        - Resumo dos pontos principais
        - Decisões tomadas
        - Ações e responsáveis
        - Próximos passos
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em documentação de reuniões. Gere atas profissionais e bem estruturadas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Erro na geração de ata: {e}")
        return "Erro ao gerar ata da reunião."

@meetings_advanced_bp.route('/meeting-templates', methods=['GET'])
@token_required
def get_meeting_templates(current_user):
    """Retorna templates de reunião"""
    try:
        templates = [
            {
                'id': 1,
                'name': 'Reunião de Planejamento',
                'description': 'Template para reuniões de planejamento de projetos',
                'agenda': [
                    'Revisão do status atual',
                    'Definição de objetivos',
                    'Cronograma e marcos',
                    'Distribuição de responsabilidades',
                    'Próximos passos'
                ]
            },
            {
                'id': 2,
                'name': 'Reunião de Acompanhamento',
                'description': 'Template para reuniões de acompanhamento',
                'agenda': [
                    'Revisão das ações anteriores',
                    'Status dos projetos',
                    'Problemas e soluções',
                    'Novas ações',
                    'Data da próxima reunião'
                ]
            },
            {
                'id': 3,
                'name': 'Reunião de Brainstorming',
                'description': 'Template para sessões criativas',
                'agenda': [
                    'Apresentação do desafio',
                    'Geração de ideias',
                    'Discussão e refinamento',
                    'Seleção das melhores ideias',
                    'Plano de implementação'
                ]
            }
        ]
        
        return jsonify({'templates': templates}), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

