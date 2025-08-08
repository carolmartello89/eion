from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json
import uuid
import requests

financeiro_completo_bp = Blueprint('financeiro_completo', __name__)

# Simulação de dados financeiros
dashboard_financeiro_db = {}
transacoes_db = {}
pagamentos_db = {}
afiliados_db = {}
configuracoes_db = {}
saques_db = {}

@financeiro_completo_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard_financeiro():
    try:
        user_id = get_jwt_identity()
        
        # Calcular métricas em tempo real
        transacoes_usuario = transacoes_db.get(user_id, [])
        
        receita_total = sum(t['valor'] for t in transacoes_usuario if t['status'] == 'aprovado')
        receita_hoje = sum(t['valor'] for t in transacoes_usuario 
                          if t['status'] == 'aprovado' and t['data'].startswith(datetime.now().strftime('%Y-%m-%d')))
        receita_mes = sum(t['valor'] for t in transacoes_usuario 
                         if t['status'] == 'aprovado' and t['data'].startswith(datetime.now().strftime('%Y-%m')))
        
        usuarios_ativos = len(set(t['cliente'] for t in transacoes_usuario if t['status'] == 'aprovado'))
        
        # Calcular métricas avançadas
        total_leads = usuarios_ativos * 12  # Simular leads
        conversao = (usuarios_ativos / total_leads * 100) if total_leads > 0 else 0
        
        # MRR (Monthly Recurring Revenue)
        assinaturas_ativas = len([t for t in transacoes_usuario 
                                 if t['tipo'] == 'assinatura' and t['status'] == 'aprovado'])
        mrr = assinaturas_ativas * 99  # Assumindo plano médio de R$ 99
        
        # LTV e Churn simulados
        ltv = 450.00  # Média baseada em assinaturas
        churn = 2.1   # Taxa de cancelamento baixa
        
        dados = {
            'receita_total': receita_total,
            'receita_hoje': receita_hoje,
            'receita_mes': receita_mes,
            'usuarios_ativos': usuarios_ativos,
            'conversao': round(conversao, 1),
            'churn': churn,
            'ltv': ltv,
            'mrr': mrr,
            'saldo_disponivel': receita_total * 0.85,  # 85% disponível após taxas
            'crescimento_mes': 15.8,
            'ticket_medio': receita_total / usuarios_ativos if usuarios_ativos > 0 else 0
        }
        
        dashboard_financeiro_db[user_id] = dados
        
        return jsonify({
            'success': True,
            'dados': dados
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financeiro_completo_bp.route('/transacoes', methods=['GET'])
@jwt_required()
def listar_transacoes():
    try:
        user_id = get_jwt_identity()
        
        # Transações de exemplo se não houver dados
        if user_id not in transacoes_db:
            transacoes_db[user_id] = [
                {
                    'id': 1,
                    'tipo': 'assinatura',
                    'valor': 99.00,
                    'cliente': 'João Silva',
                    'email': 'joao@email.com',
                    'plano': 'Enterprise',
                    'status': 'aprovado',
                    'metodo': 'pix',
                    'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'comissao_afiliado': 19.80,
                    'id_transacao': str(uuid.uuid4())
                },
                {
                    'id': 2,
                    'tipo': 'upgrade',
                    'valor': 199.00,
                    'cliente': 'Maria Santos',
                    'email': 'maria@email.com',
                    'plano': 'Premium Plus',
                    'status': 'aprovado',
                    'metodo': 'cartao',
                    'data': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M'),
                    'comissao_afiliado': 39.80,
                    'id_transacao': str(uuid.uuid4())
                },
                {
                    'id': 3,
                    'tipo': 'assinatura',
                    'valor': 49.00,
                    'cliente': 'Carlos Lima',
                    'email': 'carlos@email.com',
                    'plano': 'Básico',
                    'status': 'pendente',
                    'metodo': 'boleto',
                    'data': (datetime.now() - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M'),
                    'comissao_afiliado': 9.80,
                    'id_transacao': str(uuid.uuid4())
                }
            ]
        
        transacoes = transacoes_db.get(user_id, [])
        
        return jsonify({
            'success': True,
            'transacoes': transacoes,
            'total': len(transacoes),
            'aprovadas': len([t for t in transacoes if t['status'] == 'aprovado']),
            'pendentes': len([t for t in transacoes if t['status'] == 'pendente'])
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financeiro_completo_bp.route('/pagamentos', methods=['GET'])
@jwt_required()
def listar_pagamentos():
    try:
        user_id = get_jwt_identity()
        
        # Pagamentos de exemplo se não houver dados
        if user_id not in pagamentos_db:
            pagamentos_db[user_id] = [
                {
                    'id': 1,
                    'valor': 15000.00,
                    'tipo': 'saque',
                    'status': 'processado',
                    'data': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M'),
                    'banco': 'PIX - Chave: carol@email.com',
                    'taxa': 0,
                    'id_pagamento': str(uuid.uuid4())
                },
                {
                    'id': 2,
                    'valor': 8500.00,
                    'tipo': 'comissao_afiliados',
                    'status': 'processado',
                    'data': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M'),
                    'banco': 'Transferência automática',
                    'taxa': 0,
                    'id_pagamento': str(uuid.uuid4())
                }
            ]
        
        pagamentos = pagamentos_db.get(user_id, [])
        
        return jsonify({
            'success': True,
            'pagamentos': pagamentos
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financeiro_completo_bp.route('/afiliados', methods=['GET'])
@jwt_required()
def listar_afiliados():
    try:
        user_id = get_jwt_identity()
        
        # Afiliados de exemplo se não houver dados
        if user_id not in afiliados_db:
            afiliados_db[user_id] = [
                {
                    'id': 1,
                    'nome': 'Pedro Oliveira',
                    'email': 'pedro@email.com',
                    'vendas': 15,
                    'comissao_total': 890.50,
                    'comissao_mes': 340.20,
                    'taxa': 20,
                    'status': 'ativo',
                    'data_cadastro': '2025-06-15',
                    'link_afiliado': f'https://assistente.com/ref/{uuid.uuid4()}',
                    'codigo_afiliado': 'PED001'
                },
                {
                    'id': 2,
                    'nome': 'Ana Costa',
                    'email': 'ana@email.com',
                    'vendas': 23,
                    'comissao_total': 1245.80,
                    'comissao_mes': 455.60,
                    'taxa': 25,
                    'status': 'ativo',
                    'data_cadastro': '2025-05-20',
                    'link_afiliado': f'https://assistente.com/ref/{uuid.uuid4()}',
                    'codigo_afiliado': 'ANA002'
                }
            ]
        
        afiliados = afiliados_db.get(user_id, [])
        
        return jsonify({
            'success': True,
            'afiliados': afiliados,
            'total_comissoes': sum(a['comissao_total'] for a in afiliados),
            'comissoes_mes': sum(a['comissao_mes'] for a in afiliados)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financeiro_completo_bp.route('/saques', methods=['POST'])
@jwt_required()
def solicitar_saque():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        valor = float(data.get('valor', 0))
        tipo = data.get('tipo', 'pix')
        descricao = data.get('descricao', '')
        
        # Validações
        if valor <= 0:
            return jsonify({'success': False, 'error': 'Valor inválido'}), 400
        
        # Verificar saldo disponível
        dashboard = dashboard_financeiro_db.get(user_id, {})
        saldo_disponivel = dashboard.get('saldo_disponivel', 0)
        
        if valor > saldo_disponivel:
            return jsonify({'success': False, 'error': 'Saldo insuficiente'}), 400
        
        # Calcular taxa baseada no tipo
        taxas = {
            'pix': 0,
            'ted': 5.50,
            'doc': 3.50
        }
        taxa = taxas.get(tipo, 0)
        
        # Calcular tempo de processamento
        tempos = {
            'pix': 'Instantâneo',
            'ted': '1 dia útil',
            'doc': '1 dia útil'
        }
        tempo = tempos.get(tipo, '1 dia útil')
        
        # Criar registro do saque
        saque = {
            'id': len(saques_db.get(user_id, [])) + 1,
            'valor': valor,
            'tipo': tipo,
            'status': 'processando',
            'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'descricao': descricao,
            'taxa': taxa,
            'valor_liquido': valor - taxa,
            'previsao_pagamento': tempo,
            'id_saque': str(uuid.uuid4())
        }
        
        if user_id not in saques_db:
            saques_db[user_id] = []
        
        saques_db[user_id].append(saque)
        
        # Simular processamento instantâneo para PIX
        if tipo == 'pix':
            saque['status'] = 'processado'
            
            # Adicionar ao histórico de pagamentos
            if user_id not in pagamentos_db:
                pagamentos_db[user_id] = []
            
            pagamentos_db[user_id].append({
                'id': len(pagamentos_db[user_id]) + 1,
                'valor': valor,
                'tipo': 'saque',
                'status': 'processado',
                'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'banco': f'PIX - {tipo}',
                'taxa': taxa,
                'id_pagamento': saque['id_saque']
            })
        
        return jsonify({
            'success': True,
            'saque': saque,
            'previsao_pagamento': tempo,
            'valor_liquido': valor - taxa
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financeiro_completo_bp.route('/configuracoes', methods=['GET'])
@jwt_required()
def obter_configuracoes():
    try:
        user_id = get_jwt_identity()
        
        configuracoes = configuracoes_db.get(user_id, {
            'pix_key': 'carol@email.com',
            'banco': 'Banco do Brasil',
            'agencia': '1234-5',
            'conta': '12345-6',
            'taxa_afiliado': 20,
            'saque_automatico': True,
            'valor_minimo_saque': 100,
            'webhook_url': '',
            'notificacoes_email': True,
            'notificacoes_whatsapp': True
        })
        
        return jsonify({
            'success': True,
            'configuracoes': configuracoes
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financeiro_completo_bp.route('/configuracoes', methods=['POST'])
@jwt_required()
def salvar_configuracoes():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        configuracoes_db[user_id] = data
        
        return jsonify({
            'success': True,
            'message': 'Configurações salvas com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financeiro_completo_bp.route('/relatorios/<tipo>', methods=['GET'])
@jwt_required()
def gerar_relatorio(tipo):
    try:
        user_id = get_jwt_identity()
        
        # Simular geração de relatório
        relatorios_disponiveis = {
            'vendas': 'Relatório de Vendas',
            'financeiro': 'Relatório Financeiro',
            'fiscal': 'Relatório Fiscal',
            'afiliados': 'Relatório de Afiliados'
        }
        
        if tipo not in relatorios_disponiveis:
            return jsonify({'success': False, 'error': 'Tipo de relatório inválido'}), 400
        
        # Simular envio por email
        return jsonify({
            'success': True,
            'message': f'{relatorios_disponiveis[tipo]} será enviado por email em instantes!',
            'tipo': tipo,
            'data_geracao': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financeiro_completo_bp.route('/webhook/pagamento', methods=['POST'])
def webhook_pagamento():
    """Webhook para receber notificações de pagamento de gateways"""
    try:
        data = request.get_json()
        
        # Processar notificação de pagamento
        # Aqui você integraria com Mercado Pago, PagSeguro, Stripe, etc.
        
        return jsonify({
            'success': True,
            'message': 'Webhook processado com sucesso'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financeiro_completo_bp.route('/pix/gerar', methods=['POST'])
@jwt_required()
def gerar_pix():
    """Gerar código PIX para pagamento"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        valor = data.get('valor')
        descricao = data.get('descricao', 'Pagamento Assistente IA')
        
        # Simular geração de código PIX
        codigo_pix = f"00020126580014BR.GOV.BCB.PIX0136{uuid.uuid4()}5204000053039865802BR5925Carol Assistente IA6009SAO PAULO61080540900062070503***6304"
        
        return jsonify({
            'success': True,
            'codigo_pix': codigo_pix,
            'qr_code_url': f'https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={codigo_pix}',
            'valor': valor,
            'validade': '30 minutos'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@financeiro_completo_bp.route('/analytics/vendas', methods=['GET'])
@jwt_required()
def analytics_vendas():
    """Analytics avançado de vendas"""
    try:
        user_id = get_jwt_identity()
        
        # Simular dados de analytics
        analytics = {
            'vendas_por_dia': [
                {'data': '2025-07-26', 'vendas': 12, 'receita': 1188.00},
                {'data': '2025-07-27', 'vendas': 8, 'receita': 792.00},
                {'data': '2025-07-28', 'vendas': 15, 'receita': 1485.00},
                {'data': '2025-07-29', 'vendas': 10, 'receita': 990.00},
                {'data': '2025-07-30', 'vendas': 18, 'receita': 1782.00},
                {'data': '2025-07-31', 'vendas': 14, 'receita': 1386.00},
                {'data': '2025-08-01', 'vendas': 16, 'receita': 1584.00}
            ],
            'top_afiliados': [
                {'nome': 'Ana Costa', 'vendas': 23, 'comissao': 1245.80},
                {'nome': 'Pedro Oliveira', 'vendas': 15, 'comissao': 890.50}
            ],
            'planos_mais_vendidos': [
                {'plano': 'Enterprise', 'vendas': 45, 'percentual': 52.3},
                {'plano': 'Premium', 'vendas': 28, 'percentual': 32.6},
                {'plano': 'Básico', 'vendas': 13, 'percentual': 15.1}
            ],
            'metricas_conversao': {
                'taxa_abandono_carrinho': 15.2,
                'tempo_medio_conversao': '2.3 dias',
                'origem_trafego': [
                    {'fonte': 'Orgânico', 'conversoes': 42},
                    {'fonte': 'Afiliados', 'conversoes': 28},
                    {'fonte': 'Anúncios', 'conversoes': 16}
                ]
            }
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
