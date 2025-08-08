from flask import Blueprint, request, jsonify
from src.routes.auth import token_required
from src.models.conversa import Conversa, PadraoUsuario, MemoriaContexto
from src.models.user import db
from datetime import datetime, timedelta
import openai
import os
import json

memoria_bp = Blueprint('memoria', __name__)

@memoria_bp.route('/conversas', methods=['POST'])
@token_required
def salvar_conversa(current_user):
    """Salva uma conversa do assistente"""
    try:
        data = request.get_json()
        
        nova_conversa = Conversa(
            user_id=current_user.id,
            comando=data['comando'],
            resposta=data['resposta'],
            acao_executada=data.get('acao_executada'),
            tipo_interacao=data.get('tipo_interacao', 'voz')
        )
        
        # Define contexto se fornecido
        if data.get('contexto'):
            nova_conversa.set_contexto(data['contexto'])
        
        db.session.add(nova_conversa)
        db.session.commit()
        
        # Detecta padrões após salvar conversa
        detectar_padroes_conversa(current_user.id, nova_conversa)
        
        return jsonify({
            'message': 'Conversa salva com sucesso',
            'conversa': nova_conversa.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@memoria_bp.route('/conversas', methods=['GET'])
@token_required
def obter_historico(current_user):
    """Obtém histórico de conversas"""
    try:
        limit = request.args.get('limit', 50, type=int)
        busca = request.args.get('busca', '')
        tipo = request.args.get('tipo', '')
        
        query = Conversa.query.filter_by(user_id=current_user.id)
        
        # Filtro por busca
        if busca:
            query = query.filter(
                db.or_(
                    Conversa.comando.contains(busca),
                    Conversa.resposta.contains(busca)
                )
            )
        
        # Filtro por tipo
        if tipo:
            query = query.filter_by(tipo_interacao=tipo)
        
        conversas = query.order_by(Conversa.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'conversas': [conversa.to_dict() for conversa in conversas],
            'total': query.count()
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@memoria_bp.route('/contexto', methods=['GET'])
@token_required
def obter_contexto(current_user):
    """Obtém contexto das últimas conversas para IA"""
    try:
        limite_conversas = request.args.get('limite', 10, type=int)
        
        # Últimas conversas
        ultimas_conversas = Conversa.query.filter_by(user_id=current_user.id)\
                                         .order_by(Conversa.timestamp.desc())\
                                         .limit(limite_conversas).all()
        
        contexto_conversas = []
        for conversa in reversed(ultimas_conversas):
            contexto_conversas.append({
                'usuario': conversa.comando,
                'assistente': conversa.resposta,
                'acao': conversa.acao_executada,
                'timestamp': conversa.timestamp.isoformat() if conversa.timestamp else None
            })
        
        # Padrões do usuário
        padroes = PadraoUsuario.query.filter_by(user_id=current_user.id)\
                                   .filter(PadraoUsuario.confianca >= 0.6)\
                                   .order_by(PadraoUsuario.frequencia.desc())\
                                   .limit(5).all()
        
        contexto_padroes = [padrao.to_dict() for padrao in padroes]
        
        # Memória de contexto importante
        memoria_importante = MemoriaContexto.query.filter_by(user_id=current_user.id)\
                                                 .filter(MemoriaContexto.importancia >= 3)\
                                                 .filter(
                                                     db.or_(
                                                         MemoriaContexto.expira_em.is_(None),
                                                         MemoriaContexto.expira_em > datetime.utcnow()
                                                     )
                                                 )\
                                                 .order_by(MemoriaContexto.importancia.desc())\
                                                 .limit(10).all()
        
        contexto_memoria = [memoria.to_dict() for memoria in memoria_importante]
        
        return jsonify({
            'conversas_recentes': contexto_conversas,
            'padroes_usuario': contexto_padroes,
            'memoria_importante': contexto_memoria
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@memoria_bp.route('/buscar', methods=['POST'])
@token_required
def buscar_na_memoria(current_user):
    """Busca informações na memória baseado em uma pergunta"""
    try:
        data = request.get_json()
        pergunta = data.get('pergunta', '')
        
        if not pergunta:
            return jsonify({'erro': 'Pergunta é obrigatória'}), 400
        
        # Busca em conversas
        conversas_relevantes = Conversa.query.filter_by(user_id=current_user.id)\
                                           .filter(
                                               db.or_(
                                                   Conversa.comando.contains(pergunta),
                                                   Conversa.resposta.contains(pergunta)
                                               )
                                           )\
                                           .order_by(Conversa.timestamp.desc())\
                                           .limit(10).all()
        
        # Busca em memória de contexto
        palavras_chave = pergunta.lower().split()
        memoria_relevante = []
        
        for palavra in palavras_chave:
            memoria = MemoriaContexto.query.filter_by(user_id=current_user.id)\
                                          .filter(
                                              db.or_(
                                                  MemoriaContexto.chave.contains(palavra),
                                                  MemoriaContexto.valor.contains(palavra)
                                              )
                                          ).all()
            memoria_relevante.extend(memoria)
        
        # Remove duplicatas
        memoria_relevante = list(set(memoria_relevante))
        
        # Gera resposta usando IA
        resposta_ia = gerar_resposta_memoria(
            pergunta, 
            [conv.to_dict() for conv in conversas_relevantes],
            [mem.to_dict() for mem in memoria_relevante]
        )
        
        return jsonify({
            'pergunta': pergunta,
            'resposta': resposta_ia,
            'conversas_encontradas': len(conversas_relevantes),
            'memorias_encontradas': len(memoria_relevante),
            'detalhes': {
                'conversas': [conv.to_dict() for conv in conversas_relevantes[:5]],
                'memorias': [mem.to_dict() for mem in memoria_relevante[:5]]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@memoria_bp.route('/contexto', methods=['POST'])
@token_required
def salvar_contexto(current_user):
    """Salva informação importante na memória de contexto"""
    try:
        data = request.get_json()
        
        chave = data.get('chave')
        valor = data.get('valor')
        categoria = data.get('categoria', 'geral')
        importancia = data.get('importancia', 3)
        expira_em = data.get('expira_em')
        
        if not chave or not valor:
            return jsonify({'erro': 'Chave e valor são obrigatórios'}), 400
        
        # Verifica se já existe
        contexto_existente = MemoriaContexto.query.filter_by(
            user_id=current_user.id,
            chave=chave
        ).first()
        
        if contexto_existente:
            # Atualiza existente
            contexto_existente.set_valor(valor)
            contexto_existente.categoria = categoria
            contexto_existente.importancia = importancia
            contexto_existente.atualizado_em = datetime.utcnow()
            
            if expira_em:
                contexto_existente.expira_em = datetime.fromisoformat(expira_em)
            
            contexto = contexto_existente
        else:
            # Cria novo
            contexto = MemoriaContexto(
                user_id=current_user.id,
                chave=chave,
                categoria=categoria,
                importancia=importancia
            )
            contexto.set_valor(valor)
            
            if expira_em:
                contexto.expira_em = datetime.fromisoformat(expira_em)
            
            db.session.add(contexto)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Contexto salvo com sucesso',
            'contexto': contexto.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@memoria_bp.route('/padroes', methods=['GET'])
@token_required
def obter_padroes(current_user):
    """Obtém padrões detectados do usuário"""
    try:
        tipo = request.args.get('tipo', '')
        
        query = PadraoUsuario.query.filter_by(user_id=current_user.id)
        
        if tipo:
            query = query.filter_by(tipo_padrao=tipo)
        
        padroes = query.order_by(PadraoUsuario.confianca.desc()).all()
        
        return jsonify({
            'padroes': [padrao.to_dict() for padrao in padroes]
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@memoria_bp.route('/limpar', methods=['DELETE'])
@token_required
def limpar_memoria(current_user):
    """Limpa dados antigos da memória"""
    try:
        dias_limite = request.args.get('dias', 90, type=int)
        data_limite = datetime.utcnow() - timedelta(days=dias_limite)
        
        # Remove conversas antigas
        conversas_antigas = Conversa.query.filter_by(user_id=current_user.id)\
                                         .filter(Conversa.timestamp < data_limite)
        count_conversas = conversas_antigas.count()
        conversas_antigas.delete()
        
        # Remove contextos expirados
        contextos_expirados = MemoriaContexto.query.filter_by(user_id=current_user.id)\
                                                  .filter(MemoriaContexto.expira_em < datetime.utcnow())
        count_contextos = contextos_expirados.count()
        contextos_expirados.delete()
        
        # Remove padrões com baixa confiança
        padroes_baixa_confianca = PadraoUsuario.query.filter_by(user_id=current_user.id)\
                                                    .filter(PadraoUsuario.confianca < 0.3)
        count_padroes = padroes_baixa_confianca.count()
        padroes_baixa_confianca.delete()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Limpeza concluída',
            'removidos': {
                'conversas': count_conversas,
                'contextos': count_contextos,
                'padroes': count_padroes
            }
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

def detectar_padroes_conversa(user_id, conversa):
    """Detecta padrões baseado em uma nova conversa"""
    try:
        comando = conversa.comando.lower()
        
        # Padrão de horários de atividades
        if any(palavra in comando for palavra in ['reunião', 'compromisso', 'encontro']):
            hora_atual = conversa.timestamp.hour
            
            padrao = PadraoUsuario.query.filter_by(
                user_id=user_id,
                tipo_padrao='horario_atividades'
            ).first()
            
            if padrao:
                dados = padrao.get_dados_padrao()
                horarios = dados.get('horarios', {})
                horarios[str(hora_atual)] = horarios.get(str(hora_atual), 0) + 1
                
                padrao.set_dados_padrao({'horarios': horarios})
                padrao.frequencia += 1
                padrao.ultima_ocorrencia = datetime.utcnow()
                padrao.confianca = min(1.0, padrao.frequencia / 10.0)
            else:
                padrao = PadraoUsuario(
                    user_id=user_id,
                    tipo_padrao='horario_atividades',
                    frequencia=1,
                    confianca=0.1
                )
                padrao.set_dados_padrao({'horarios': {str(hora_atual): 1}})
                db.session.add(padrao)
        
        # Padrão de contatos frequentes
        if 'ligar' in comando or 'contato' in comando:
            # Extrai possível nome do comando
            palavras = comando.split()
            for i, palavra in enumerate(palavras):
                if palavra in ['ligar', 'para', 'contato'] and i + 1 < len(palavras):
                    nome_possivel = palavras[i + 1]
                    
                    padrao = PadraoUsuario.query.filter_by(
                        user_id=user_id,
                        tipo_padrao='contatos_frequentes'
                    ).first()
                    
                    if padrao:
                        dados = padrao.get_dados_padrao()
                        contatos = dados.get('contatos', {})
                        contatos[nome_possivel] = contatos.get(nome_possivel, 0) + 1
                        
                        padrao.set_dados_padrao({'contatos': contatos})
                        padrao.frequencia += 1
                        padrao.confianca = min(1.0, padrao.frequencia / 5.0)
                    else:
                        padrao = PadraoUsuario(
                            user_id=user_id,
                            tipo_padrao='contatos_frequentes',
                            frequencia=1,
                            confianca=0.2
                        )
                        padrao.set_dados_padrao({'contatos': {nome_possivel: 1}})
                        db.session.add(padrao)
                    break
        
        db.session.commit()
        
    except Exception as e:
        print(f"Erro ao detectar padrões: {e}")

def gerar_resposta_memoria(pergunta, conversas, memorias):
    """Gera resposta baseada na memória usando IA"""
    try:
        # Prepara contexto para IA
        contexto_conversas = ""
        if conversas:
            contexto_conversas = "Conversas relevantes encontradas:\n"
            for conv in conversas[:3]:  # Limita a 3 conversas mais relevantes
                contexto_conversas += f"- Usuário: {conv['comando']}\n"
                contexto_conversas += f"  Assistente: {conv['resposta']}\n"
                if conv['timestamp']:
                    data = datetime.fromisoformat(conv['timestamp'].replace('Z', '+00:00'))
                    contexto_conversas += f"  Data: {data.strftime('%d/%m/%Y %H:%M')}\n"
                contexto_conversas += "\n"
        
        contexto_memorias = ""
        if memorias:
            contexto_memorias = "Informações importantes salvas:\n"
            for mem in memorias[:3]:  # Limita a 3 memórias mais relevantes
                contexto_memorias += f"- {mem['chave']}: {mem['valor']}\n"
        
        prompt = f"""
        Você é um assistente pessoal inteligente. O usuário fez a seguinte pergunta sobre informações passadas:
        
        Pergunta: {pergunta}
        
        {contexto_conversas}
        
        {contexto_memorias}
        
        Com base nas informações encontradas na memória, responda de forma útil e contextualizada. 
        Se não encontrar informações relevantes, informe isso educadamente.
        Seja específico sobre datas e detalhes quando disponíveis.
        """
        
        # Usa a API do OpenAI se disponível
        if os.getenv('OPENAI_API_KEY'):
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content
        else:
            # Resposta básica sem IA
            if conversas or memorias:
                return f"Encontrei {len(conversas)} conversas e {len(memorias)} informações relacionadas à sua pergunta. Verifique os detalhes retornados para mais informações."
            else:
                return "Não encontrei informações relevantes na memória sobre essa pergunta. Talvez você possa me fornecer mais detalhes?"
                
    except Exception as e:
        return f"Encontrei algumas informações, mas houve um erro ao processar a resposta: {str(e)}"

