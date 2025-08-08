from flask import Blueprint, request, jsonify
from src.routes.auth import token_required
import openai
import os
import json
import re
from datetime import datetime, timedelta

assistente_advanced_bp = Blueprint('assistente_advanced', __name__)

# Configuração do OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_API_BASE')

@assistente_advanced_bp.route('/process-voice', methods=['POST'])
@token_required
def process_voice_command(current_user):
    """Processa comandos de voz com IA"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        context = data.get('context', 'general')
        
        if not command:
            return jsonify({'erro': 'Comando não fornecido'}), 400
        
        # Processa comando com OpenAI
        response_data = process_with_ai(command, context, current_user)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

def process_with_ai(command, context, user):
    """Processa comando usando OpenAI"""
    
    # Prompt do sistema para o assistente
    system_prompt = f"""
    Você é um assistente pessoal inteligente chamado "Assistente". Você ajuda o usuário {user.email} a gerenciar:
    - Compromissos e agenda
    - Reuniões e contatos
    - Ligações telefônicas
    - Navegação no aplicativo
    
    Responda de forma natural, amigável e concisa em português brasileiro.
    
    Comandos disponíveis:
    - "próximos compromissos" ou "agenda" -> mostrar agenda
    - "ligar para [nome]" -> iniciar ligação
    - "agendar [evento]" -> criar compromisso
    - "ir para [página]" -> navegar no app
    - "que horas são" -> mostrar horário
    - "data de hoje" -> mostrar data
    
    Para ações específicas, inclua um objeto 'action' na resposta com:
    - type: tipo da ação (navigate, call, create_appointment, show_schedule)
    - dados necessários para a ação
    
    Responda sempre em JSON com 'response' (texto) e opcionalmente 'action' (objeto).
    """
    
    try:
        # Chama OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": command}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Tenta parsear como JSON
        try:
            parsed_response = json.loads(ai_response)
            if isinstance(parsed_response, dict) and 'response' in parsed_response:
                return parsed_response
        except json.JSONDecodeError:
            pass
        
        # Se não for JSON válido, processa manualmente
        return process_command_manually(command, ai_response)
        
    except Exception as e:
        print(f"Erro na API OpenAI: {e}")
        # Fallback para processamento manual
        return process_command_manually(command, None)

def process_command_manually(command, ai_response=None):
    """Processamento manual de comandos como fallback"""
    
    command_lower = command.lower()
    
    # Comandos de agenda
    if any(word in command_lower for word in ['agenda', 'compromisso', 'próximo']):
        return {
            'response': ai_response or 'Aqui estão seus próximos compromissos.',
            'action': {
                'type': 'show_schedule',
                'filter': 'upcoming'
            }
        }
    
    # Comandos de ligação
    ligar_match = re.search(r'ligar para (.+)', command_lower)
    if ligar_match or 'ligar' in command_lower:
        nome = ligar_match.group(1) if ligar_match else 'contato'
        return {
            'response': ai_response or f'Iniciando ligação para {nome}.',
            'action': {
                'type': 'call',
                'contact': nome
            }
        }
    
    # Comandos de navegação
    if any(word in command_lower for word in ['ir para', 'abrir', 'mostrar']):
        if 'reuniões' in command_lower or 'reunião' in command_lower:
            return {
                'response': ai_response or 'Abrindo página de reuniões.',
                'action': {
                    'type': 'navigate',
                    'page': 'reunioes'
                }
            }
        elif 'contatos' in command_lower or 'contato' in command_lower:
            return {
                'response': ai_response or 'Abrindo página de contatos.',
                'action': {
                    'type': 'navigate',
                    'page': 'contatos'
                }
            }
        elif 'agenda' in command_lower or 'compromissos' in command_lower:
            return {
                'response': ai_response or 'Abrindo sua agenda.',
                'action': {
                    'type': 'navigate',
                    'page': 'compromissos'
                }
            }
    
    # Comandos de horário
    if any(word in command_lower for word in ['que horas', 'horário', 'hora']):
        now = datetime.now()
        return {
            'response': f'Agora são {now.strftime("%H:%M")} de {now.strftime("%d/%m/%Y")}.'
        }
    
    # Comandos de data
    if any(word in command_lower for word in ['data', 'hoje', 'dia']):
        today = datetime.now()
        return {
            'response': f'Hoje é {today.strftime("%A, %d de %B de %Y")}.'
        }
    
    # Saudações
    if any(word in command_lower for word in ['olá', 'oi', 'bom dia', 'boa tarde', 'boa noite']):
        hour = datetime.now().hour
        if hour < 12:
            greeting = 'Bom dia'
        elif hour < 18:
            greeting = 'Boa tarde'
        else:
            greeting = 'Boa noite'
        
        return {
            'response': f'{greeting}! Como posso ajudá-lo hoje?'
        }
    
    # Resposta padrão
    return {
        'response': ai_response or 'Desculpe, não entendi seu comando. Tente falar "próximos compromissos", "ligar para [nome]" ou "que horas são".'
    }

@assistente_advanced_bp.route('/suggestions', methods=['GET'])
@token_required
def get_suggestions(current_user):
    """Retorna sugestões inteligentes baseadas no contexto"""
    try:
        hour = datetime.now().hour
        day_of_week = datetime.now().weekday()
        
        suggestions = []
        
        # Sugestões baseadas no horário
        if 6 <= hour < 12:
            suggestions.extend([
                "Verificar agenda do dia",
                "Revisar compromissos da manhã",
                "Ligar para contatos importantes"
            ])
        elif 12 <= hour < 18:
            suggestions.extend([
                "Agendar reuniões da tarde",
                "Verificar próximos compromissos",
                "Fazer ligações pendentes"
            ])
        else:
            suggestions.extend([
                "Revisar atividades do dia",
                "Planejar agenda de amanhã",
                "Verificar lembretes"
            ])
        
        # Sugestões baseadas no dia da semana
        if day_of_week == 0:  # Segunda-feira
            suggestions.append("Planejar semana")
        elif day_of_week == 4:  # Sexta-feira
            suggestions.append("Revisar semana")
        
        return jsonify({
            'suggestions': suggestions[:5]  # Máximo 5 sugestões
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@assistente_advanced_bp.route('/smart-reminders', methods=['GET'])
@token_required
def get_smart_reminders(current_user):
    """Retorna lembretes inteligentes"""
    try:
        now = datetime.now()
        reminders = []
        
        # Simulação de lembretes inteligentes
        # Em uma implementação real, isso consultaria o banco de dados
        
        # Lembrete de reunião próxima
        reminders.append({
            'id': 1,
            'type': 'meeting',
            'title': 'Reunião em 30 minutos',
            'description': 'Reunião com equipe de desenvolvimento',
            'time': (now + timedelta(minutes=30)).isoformat(),
            'priority': 'high'
        })
        
        # Lembrete de ligação
        reminders.append({
            'id': 2,
            'type': 'call',
            'title': 'Retornar ligação',
            'description': 'Ligar para Dr. Pedro Costa',
            'time': now.isoformat(),
            'priority': 'medium'
        })
        
        # Lembrete de tarefa
        reminders.append({
            'id': 3,
            'type': 'task',
            'title': 'Revisar relatório',
            'description': 'Finalizar relatório mensal',
            'time': (now + timedelta(hours=2)).isoformat(),
            'priority': 'low'
        })
        
        return jsonify({
            'reminders': reminders
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

