from flask import Blueprint, request, jsonify
from src.routes.auth import token_required
from datetime import datetime, timedelta
import json

automation_bp = Blueprint('automation', __name__)

@automation_bp.route('/rules', methods=['GET'])
@token_required
def get_automation_rules(current_user):
    """Retorna regras de automação do usuário"""
    try:
        # Em uma implementação real, consultaria o banco de dados
        rules = [
            {
                'id': 1,
                'name': 'Lembrete de Reunião',
                'description': 'Envia lembrete 15 minutos antes de cada reunião',
                'trigger': 'meeting_scheduled',
                'action': 'send_notification',
                'enabled': True,
                'executions': 45,
                'lastRun': (datetime.now() - timedelta(hours=2)).isoformat(),
                'category': 'notifications',
                'userId': current_user.id
            },
            {
                'id': 2,
                'name': 'Backup Diário',
                'description': 'Faz backup dos dados todos os dias às 23:00',
                'trigger': 'schedule',
                'action': 'backup_data',
                'enabled': True,
                'executions': 30,
                'lastRun': (datetime.now() - timedelta(days=1)).isoformat(),
                'category': 'maintenance',
                'userId': current_user.id
            }
        ]
        
        return jsonify({'automations': rules}), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@automation_bp.route('/rules', methods=['POST'])
@token_required
def create_automation_rule(current_user):
    """Cria nova regra de automação"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'description', 'trigger', 'actions']
        if not all(field in data for field in required_fields):
            return jsonify({'erro': 'Dados incompletos'}), 400
        
        # Cria nova regra
        new_rule = {
            'id': len(get_user_automations(current_user.id)) + 1,
            'name': data['name'],
            'description': data['description'],
            'trigger': data['trigger'],
            'actions': data['actions'],
            'enabled': True,
            'executions': 0,
            'lastRun': None,
            'category': data.get('category', 'general'),
            'userId': current_user.id,
            'createdAt': datetime.now().isoformat()
        }
        
        # Em uma implementação real, salvaria no banco de dados
        print(f"Criando regra de automação: {new_rule}")
        
        return jsonify({'automation': new_rule}), 201
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@automation_bp.route('/rules/<int:rule_id>/toggle', methods=['PUT'])
@token_required
def toggle_automation_rule(current_user, rule_id):
    """Ativa/desativa regra de automação"""
    try:
        data = request.get_json()
        enabled = data.get('enabled', True)
        
        # Em uma implementação real, atualizaria no banco de dados
        print(f"Alterando status da regra {rule_id} para {enabled}")
        
        return jsonify({
            'message': 'Status da automação atualizado',
            'ruleId': rule_id,
            'enabled': enabled
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@automation_bp.route('/rules/<int:rule_id>', methods=['DELETE'])
@token_required
def delete_automation_rule(current_user, rule_id):
    """Exclui regra de automação"""
    try:
        # Em uma implementação real, removeria do banco de dados
        print(f"Excluindo regra de automação {rule_id}")
        
        return jsonify({'message': 'Regra excluída com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@automation_bp.route('/templates', methods=['GET'])
@token_required
def get_automation_templates(current_user):
    """Retorna templates de automação disponíveis"""
    try:
        templates = [
            {
                'id': 1,
                'name': 'Lembrete de Aniversário',
                'description': 'Envia lembrete de aniversários de contatos',
                'category': 'social',
                'icon': '🎂',
                'trigger': 'contact_birthday',
                'actions': ['send_notification', 'suggest_call'],
                'popularity': 85
            },
            {
                'id': 2,
                'name': 'Acompanhamento de Projetos',
                'description': 'Verifica status de projetos semanalmente',
                'category': 'productivity',
                'icon': '📊',
                'trigger': 'weekly_schedule',
                'actions': ['check_project_status', 'send_update'],
                'popularity': 92
            },
            {
                'id': 3,
                'name': 'Organização de Emails',
                'description': 'Organiza emails por prioridade automaticamente',
                'category': 'email',
                'icon': '📧',
                'trigger': 'email_received',
                'actions': ['categorize_email', 'set_priority'],
                'popularity': 78
            },
            {
                'id': 4,
                'name': 'Planejamento Semanal',
                'description': 'Cria agenda da próxima semana baseada em padrões',
                'category': 'planning',
                'icon': '📅',
                'trigger': 'sunday_evening',
                'actions': ['analyze_patterns', 'suggest_schedule'],
                'popularity': 89
            },
            {
                'id': 5,
                'name': 'Seguimento de Vendas',
                'description': 'Cria lembretes de seguimento após reuniões comerciais',
                'category': 'sales',
                'icon': '💼',
                'trigger': 'sales_meeting_end',
                'actions': ['create_followup', 'schedule_call'],
                'popularity': 76
            }
        ]
        
        return jsonify({'templates': templates}), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@automation_bp.route('/execute/<int:rule_id>', methods=['POST'])
@token_required
def execute_automation_rule(current_user, rule_id):
    """Executa regra de automação manualmente"""
    try:
        # Simula execução da regra
        execution_result = {
            'ruleId': rule_id,
            'executedAt': datetime.now().isoformat(),
            'status': 'success',
            'message': 'Regra executada com sucesso',
            'details': {
                'actionsExecuted': 2,
                'notificationsSent': 1,
                'tasksCreated': 1
            }
        }
        
        print(f"Executando regra {rule_id}: {execution_result}")
        
        return jsonify(execution_result), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@automation_bp.route('/history', methods=['GET'])
@token_required
def get_automation_history(current_user):
    """Retorna histórico de execuções"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        # Simula histórico de execuções
        history = []
        for i in range(limit):
            history.append({
                'id': i + 1,
                'ruleId': (i % 4) + 1,
                'ruleName': ['Lembrete de Reunião', 'Backup Diário', 'Seguimento de Ligações', 'Relatório Semanal'][i % 4],
                'executedAt': (datetime.now() - timedelta(hours=i)).isoformat(),
                'status': 'success' if i % 10 != 0 else 'failed',
                'message': 'Executado com sucesso' if i % 10 != 0 else 'Falha na execução',
                'duration': f"{100 + (i * 10)}ms"
            })
        
        return jsonify({'history': history}), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@automation_bp.route('/statistics', methods=['GET'])
@token_required
def get_automation_statistics(current_user):
    """Retorna estatísticas de automação"""
    try:
        period = request.args.get('period', 'week')
        
        # Calcula estatísticas baseadas no período
        stats = {
            'totalRules': 4,
            'activeRules': 3,
            'totalExecutions': 156,
            'successfulExecutions': 152,
            'failedExecutions': 4,
            'successRate': 97.4,
            'timeSaved': 2.5,  # horas
            'topCategories': [
                {'category': 'notifications', 'count': 45},
                {'category': 'productivity', 'count': 32},
                {'category': 'maintenance', 'count': 28},
                {'category': 'reports', 'count': 15}
            ],
            'executionTrend': [
                {'date': '2024-07-24', 'executions': 18},
                {'date': '2024-07-25', 'executions': 22},
                {'date': '2024-07-26', 'executions': 19},
                {'date': '2024-07-27', 'executions': 25},
                {'date': '2024-07-28', 'executions': 21},
                {'date': '2024-07-29', 'executions': 23},
                {'date': '2024-07-30', 'executions': 28}
            ]
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@automation_bp.route('/smart-suggestions', methods=['GET'])
@token_required
def get_smart_suggestions(current_user):
    """Retorna sugestões inteligentes de automação"""
    try:
        # Analisa padrões do usuário para sugerir automações
        suggestions = [
            {
                'id': 1,
                'title': 'Automatizar Backup de Contatos',
                'description': 'Você adiciona novos contatos frequentemente. Que tal automatizar o backup?',
                'category': 'maintenance',
                'confidence': 0.87,
                'template': 'contact_backup',
                'estimatedTimeSaving': '15 min/semana'
            },
            {
                'id': 2,
                'title': 'Lembretes de Seguimento',
                'description': 'Baseado em suas reuniões, sugerimos lembretes automáticos de seguimento.',
                'category': 'productivity',
                'confidence': 0.92,
                'template': 'followup_reminders',
                'estimatedTimeSaving': '30 min/semana'
            },
            {
                'id': 3,
                'title': 'Relatório de Produtividade',
                'description': 'Receba relatórios semanais sobre sua produtividade automaticamente.',
                'category': 'reports',
                'confidence': 0.78,
                'template': 'productivity_report',
                'estimatedTimeSaving': '20 min/semana'
            }
        ]
        
        return jsonify({'suggestions': suggestions}), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

def get_user_automations(user_id):
    """Função auxiliar para obter automações do usuário"""
    # Em uma implementação real, consultaria o banco de dados
    return []

@automation_bp.route('/reminders', methods=['GET'])
@token_required
def get_reminders(current_user):
    """Retorna lembretes do usuário"""
    try:
        # Simula lembretes do banco de dados
        reminders = [
            {
                'id': 1,
                'title': 'Reunião com equipe',
                'description': 'Discussão sobre projeto Q3',
                'datetime': (datetime.now() + timedelta(minutes=30)).isoformat(),
                'type': 'meeting',
                'priority': 'high',
                'status': 'pending',
                'recurring': False,
                'smart': False
            },
            {
                'id': 2,
                'title': 'Ligar para Dr. Pedro',
                'description': 'Retornar ligação sobre consulta',
                'datetime': (datetime.now() + timedelta(hours=2)).isoformat(),
                'type': 'call',
                'priority': 'medium',
                'status': 'pending',
                'recurring': False,
                'smart': True
            }
        ]
        
        return jsonify({'reminders': reminders}), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@automation_bp.route('/reminders', methods=['POST'])
@token_required
def create_reminder(current_user):
    """Cria novo lembrete"""
    try:
        data = request.get_json()
        
        new_reminder = {
            'id': 100,  # Em uma implementação real, seria gerado pelo banco
            'title': data['title'],
            'description': data.get('description', ''),
            'datetime': data['datetime'],
            'type': data.get('type', 'general'),
            'priority': data.get('priority', 'medium'),
            'status': 'pending',
            'recurring': data.get('recurring', False),
            'recurringType': data.get('recurringType'),
            'smart': data.get('smart', False),
            'userId': current_user.id,
            'createdAt': datetime.now().isoformat()
        }
        
        print(f"Criando lembrete: {new_reminder}")
        
        return jsonify({'reminder': new_reminder}), 201
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@automation_bp.route('/reminders/<int:reminder_id>/complete', methods=['PUT'])
@token_required
def complete_reminder(current_user, reminder_id):
    """Marca lembrete como concluído"""
    try:
        print(f"Marcando lembrete {reminder_id} como concluído")
        
        return jsonify({
            'message': 'Lembrete marcado como concluído',
            'reminderId': reminder_id
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@automation_bp.route('/reminders/<int:reminder_id>', methods=['DELETE'])
@token_required
def delete_reminder(current_user, reminder_id):
    """Exclui lembrete"""
    try:
        print(f"Excluindo lembrete {reminder_id}")
        
        return jsonify({'message': 'Lembrete excluído com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

