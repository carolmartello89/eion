from flask import Blueprint, request, jsonify, send_file
from src.routes.auth import token_required
from datetime import datetime, timedelta
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard_analytics(current_user):
    """Retorna dados de analytics para o dashboard"""
    try:
        period = request.args.get('period', 'week')
        
        # Calcula datas baseado no período
        end_date = datetime.now()
        if period == 'day':
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)
        
        # Gera dados de analytics
        analytics_data = generate_analytics_data(current_user, start_date, end_date, period)
        
        return jsonify(analytics_data), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

def generate_analytics_data(user, start_date, end_date, period):
    """Gera dados de analytics baseado no período"""
    
    # Em uma implementação real, isso consultaria o banco de dados
    # Por enquanto, retorna dados simulados baseados no usuário e período
    
    import random
    
    # Dados base simulados
    base_appointments = 45 if period == 'month' else 15 if period == 'week' else 3
    base_meetings = 12 if period == 'month' else 4 if period == 'week' else 1
    base_calls = 28 if period == 'month' else 9 if period == 'week' else 2
    
    # Adiciona variação aleatória
    appointments = base_appointments + random.randint(-5, 10)
    meetings = base_meetings + random.randint(-2, 5)
    calls = base_calls + random.randint(-3, 8)
    
    # Calcula score de produtividade
    productivity_score = min(100, max(60, 
        (appointments * 2 + meetings * 5 + calls * 1) // 2 + random.randint(-10, 15)
    ))
    
    # Gera dados por dia da semana
    days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    appointments_by_day = []
    
    for day in days:
        count = random.randint(2, 12) if day not in ['Sáb', 'Dom'] else random.randint(0, 4)
        completed = max(0, count - random.randint(0, 2))
        appointments_by_day.append({
            'day': day,
            'count': count,
            'completed': completed
        })
    
    # Gera tendência de produtividade
    productivity_trend = []
    base_score = productivity_score
    
    for i in range(7):
        date = (end_date - timedelta(days=6-i)).strftime('%d/%m')
        score = max(50, min(100, base_score + random.randint(-10, 10)))
        productivity_trend.append({
            'date': date,
            'score': score
        })
        base_score = score
    
    # Distribuição de tempo
    time_distribution = [
        {'name': 'Reuniões', 'value': 35, 'color': '#3b82f6'},
        {'name': 'Ligações', 'value': 25, 'color': '#ef4444'},
        {'name': 'Planejamento', 'value': 20, 'color': '#10b981'},
        {'name': 'Emails', 'value': 15, 'color': '#f59e0b'},
        {'name': 'Outros', 'value': 5, 'color': '#8b5cf6'}
    ]
    
    # Top contatos
    contacts = [
        {'name': 'Dr. Pedro Costa', 'type': 'profissional'},
        {'name': 'João Silva', 'type': 'trabalho'},
        {'name': 'Maria Santos', 'type': 'pessoal'},
        {'name': 'Ana Oliveira', 'type': 'trabalho'},
        {'name': 'Carlos Mendes', 'type': 'profissional'}
    ]
    
    top_contacts = []
    for contact in contacts[:4]:
        interactions = random.randint(3, 10)
        top_contacts.append({
            'name': contact['name'],
            'interactions': interactions,
            'type': contact['type']
        })
    
    # Insights
    insights = generate_insights(appointments, meetings, calls, productivity_score, period)
    
    return {
        'summary': {
            'totalAppointments': appointments,
            'totalMeetings': meetings,
            'totalCalls': calls,
            'productivityScore': productivity_score,
            'trends': {
                'appointments': random.randint(-15, 20),
                'meetings': random.randint(-10, 15),
                'calls': random.randint(-8, 18),
                'productivity': random.randint(0, 10)
            }
        },
        'appointmentsByDay': appointments_by_day,
        'productivityTrend': productivity_trend,
        'timeDistribution': time_distribution,
        'topContacts': top_contacts,
        'upcomingInsights': insights,
        'period': period,
        'dateRange': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        }
    }

def generate_insights(appointments, meetings, calls, productivity, period):
    """Gera insights baseado nos dados"""
    
    insights = []
    
    # Insights baseados em produtividade
    if productivity >= 90:
        insights.append('Excelente produtividade! Continue assim.')
    elif productivity >= 75:
        insights.append('Boa produtividade. Considere otimizar seu tempo.')
    else:
        insights.append('Produtividade pode melhorar. Revise sua agenda.')
    
    # Insights baseados em reuniões
    if meetings > 15:
        insights.append('Muitas reuniões agendadas. Considere consolidar algumas.')
    elif meetings < 5:
        insights.append('Poucas reuniões. Talvez seja hora de agendar mais encontros.')
    
    # Insights baseados em ligações
    if calls > 30:
        insights.append('Alto volume de ligações. Considere usar emails para algumas comunicações.')
    
    # Insights baseados no período
    if period == 'week':
        insights.append('Melhor dia da semana para produtividade: Terça-feira')
    elif period == 'month':
        insights.append('Padrão mensal mostra picos de atividade nas segundas semanas')
    
    # Insights gerais
    insights.extend([
        f'Tempo médio de reunião: {45 + (meetings % 15)} minutos',
        f'Taxa de conclusão de compromissos: {85 + (appointments % 10)}%',
        'Recomendação: Reserve 30min diários para planejamento'
    ])
    
    return insights[:6]  # Retorna no máximo 6 insights

@analytics_bp.route('/export', methods=['POST'])
@token_required
def export_report(current_user):
    """Exporta relatório em PDF"""
    try:
        data = request.get_json()
        period = data.get('period', 'week')
        format_type = data.get('format', 'pdf')
        
        if format_type != 'pdf':
            return jsonify({'erro': 'Formato não suportado'}), 400
        
        # Gera dados para o relatório
        end_date = datetime.now()
        if period == 'day':
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)
        
        analytics_data = generate_analytics_data(current_user, start_date, end_date, period)
        
        # Gera PDF
        pdf_buffer = generate_pdf_report(analytics_data, current_user, period)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f'relatorio_{period}_{datetime.now().strftime("%Y%m%d")}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

def generate_pdf_report(data, user, period):
    """Gera relatório em PDF"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    period_name = {'day': 'Diário', 'week': 'Semanal', 'month': 'Mensal'}.get(period, 'Semanal')
    title = Paragraph(f'Relatório {period_name} - Assistente Pessoal', title_style)
    story.append(title)
    
    # Informações do usuário
    user_info = Paragraph(f'Usuário: {user.email}<br/>Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}', styles['Normal'])
    story.append(user_info)
    story.append(Spacer(1, 20))
    
    # Resumo executivo
    summary_title = Paragraph('Resumo Executivo', styles['Heading2'])
    story.append(summary_title)
    
    summary_data = [
        ['Métrica', 'Valor', 'Tendência'],
        ['Compromissos', str(data['summary']['totalAppointments']), f"{data['summary']['trends']['appointments']:+d}%"],
        ['Reuniões', str(data['summary']['totalMeetings']), f"{data['summary']['trends']['meetings']:+d}%"],
        ['Ligações', str(data['summary']['totalCalls']), f"{data['summary']['trends']['calls']:+d}%"],
        ['Produtividade', f"{data['summary']['productivityScore']}%", f"+{data['summary']['trends']['productivity']}%"]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Top contatos
    contacts_title = Paragraph('Contatos Mais Frequentes', styles['Heading2'])
    story.append(contacts_title)
    
    contacts_data = [['Nome', 'Interações', 'Tipo']]
    for contact in data['topContacts']:
        contacts_data.append([
            contact['name'],
            str(contact['interactions']),
            contact['type'].title()
        ])
    
    contacts_table = Table(contacts_data)
    contacts_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(contacts_table)
    story.append(Spacer(1, 20))
    
    # Insights
    insights_title = Paragraph('Insights e Recomendações', styles['Heading2'])
    story.append(insights_title)
    
    for insight in data['upcomingInsights']:
        bullet = Paragraph(f'• {insight}', styles['Normal'])
        story.append(bullet)
    
    story.append(Spacer(1, 20))
    
    # Rodapé
    footer = Paragraph(
        'Relatório gerado automaticamente pelo Assistente Pessoal',
        styles['Normal']
    )
    story.append(footer)
    
    # Constrói o PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer

@analytics_bp.route('/productivity-tips', methods=['GET'])
@token_required
def get_productivity_tips(current_user):
    """Retorna dicas de produtividade personalizadas"""
    try:
        # Gera dicas baseadas no perfil do usuário
        tips = [
            {
                'title': 'Bloqueie tempo para foco',
                'description': 'Reserve 2-3 horas diárias sem interrupções para trabalho profundo.',
                'category': 'tempo',
                'priority': 'alta'
            },
            {
                'title': 'Use a técnica Pomodoro',
                'description': 'Trabalhe em blocos de 25 minutos com pausas de 5 minutos.',
                'category': 'foco',
                'priority': 'média'
            },
            {
                'title': 'Revise sua agenda semanalmente',
                'description': 'Dedique 30 minutos toda sexta para planejar a próxima semana.',
                'category': 'planejamento',
                'priority': 'alta'
            },
            {
                'title': 'Limite reuniões consecutivas',
                'description': 'Deixe pelo menos 15 minutos entre reuniões para transição.',
                'category': 'reuniões',
                'priority': 'média'
            },
            {
                'title': 'Use templates para tarefas recorrentes',
                'description': 'Crie modelos para atividades que você faz regularmente.',
                'category': 'automação',
                'priority': 'baixa'
            }
        ]
        
        return jsonify({'tips': tips}), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@analytics_bp.route('/time-tracking', methods=['POST'])
@token_required
def track_time(current_user):
    """Registra tempo gasto em atividades"""
    try:
        data = request.get_json()
        activity = data.get('activity')
        duration = data.get('duration')  # em minutos
        category = data.get('category')
        
        if not all([activity, duration, category]):
            return jsonify({'erro': 'Dados incompletos'}), 400
        
        # Em uma implementação real, salvaria no banco de dados
        time_entry = {
            'user_id': current_user.id,
            'activity': activity,
            'duration': duration,
            'category': category,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"Registrando tempo: {time_entry}")
        
        return jsonify({
            'message': 'Tempo registrado com sucesso',
            'entry': time_entry
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

