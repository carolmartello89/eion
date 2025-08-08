from flask import Blueprint, request, jsonify
from src.models.reuniao import Reuniao
from src.models.compromisso import Compromisso
from src.models.contato import Contato
from src.models.user import db
from datetime import datetime, timedelta
import json
import re

assistente_bp = Blueprint('assistente', __name__)

@assistente_bp.route('/assistente/processar-comando', methods=['POST'])
def processar_comando():
    """Processa comandos de voz do assistente"""
    try:
        dados = request.get_json()
        comando = dados.get('comando', '').lower().strip()
        
        if not comando:
            return jsonify({'erro': 'Comando não fornecido'}), 400
        
        # Analisa o comando e executa a ação apropriada
        resposta = analisar_comando(comando)
        
        return jsonify(resposta)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

def analisar_comando(comando):
    """Analisa o comando de voz e retorna a resposta apropriada"""
    
    # Comando: Agendar reunião/compromisso
    if any(palavra in comando for palavra in ['agendar', 'marcar', 'criar reunião', 'criar compromisso']):
        return processar_agendamento(comando)
    
    # Comando: Ligar para contato
    elif any(palavra in comando for palavra in ['ligar para', 'chamar', 'telefonar']):
        return processar_ligacao(comando)
    
    # Comando: Próximos compromissos
    elif any(palavra in comando for palavra in ['próximos compromissos', 'próximas reuniões', 'agenda']):
        return listar_proximos_compromissos()
    
    # Comando: Resumir última reunião
    elif any(palavra in comando for palavra in ['resumir', 'resumo', 'última reunião']):
        return resumir_ultima_reuniao()
    
    # Comando: Adicionar lembrete
    elif any(palavra in comando for palavra in ['lembrete', 'lembrar']):
        return criar_lembrete(comando)
    
    # Comando: Buscar contato
    elif any(palavra in comando for palavra in ['buscar contato', 'encontrar', 'procurar']):
        return buscar_contato(comando)
    
    # Comando: Status do dia
    elif any(palavra in comando for palavra in ['como está meu dia', 'agenda hoje', 'compromissos hoje']):
        return status_do_dia()
    
    else:
        return {
            'tipo': 'erro',
            'mensagem': 'Comando não reconhecido. Tente: "Agendar reunião", "Ligar para [nome]", "Próximos compromissos", "Resumir última reunião"',
            'sugestoes': [
                'Agendar reunião com João para amanhã às 14h',
                'Ligar para Maria',
                'Próximos compromissos',
                'Resumir última reunião',
                'Como está meu dia hoje?'
            ]
        }

def processar_agendamento(comando):
    """Processa comandos de agendamento"""
    try:
        # Extrai informações do comando
        info = extrair_info_agendamento(comando)
        
        if not info['titulo']:
            return {
                'tipo': 'erro',
                'mensagem': 'Não consegui identificar o título da reunião. Tente: "Agendar reunião com João para amanhã às 14h"'
            }
        
        # Cria o compromisso
        compromisso = Compromisso(
            titulo=info['titulo'],
            descricao=info['descricao'],
            data_hora=info['data_hora'],
            tipo='reuniao' if 'reunião' in comando else 'evento',
            alerta_antecedencia=30
        )
        
        db.session.add(compromisso)
        db.session.commit()
        
        return {
            'tipo': 'sucesso',
            'acao': 'agendamento',
            'mensagem': f"Compromisso '{info['titulo']}' agendado para {info['data_hora'].strftime('%d/%m/%Y às %H:%M')}",
            'dados': compromisso.to_dict()
        }
    except Exception as e:
        return {
            'tipo': 'erro',
            'mensagem': f'Erro ao agendar: {str(e)}'
        }

def processar_ligacao(comando):
    """Processa comandos de ligação"""
    try:
        # Extrai nome do contato
        nome = extrair_nome_contato(comando)
        
        if not nome:
            return {
                'tipo': 'erro',
                'mensagem': 'Não consegui identificar o nome do contato. Tente: "Ligar para João"'
            }
        
        # Busca contato
        contato = Contato.query.filter(Contato.nome.ilike(f'%{nome}%')).first()
        
        if not contato:
            return {
                'tipo': 'erro',
                'mensagem': f'Contato "{nome}" não encontrado. Verifique se o nome está correto.'
            }
        
        if not contato.telefone:
            return {
                'tipo': 'erro',
                'mensagem': f'Contato "{contato.nome}" não possui telefone cadastrado.'
            }
        
        telefone_limpo = ''.join(filter(str.isdigit, contato.telefone))
        
        return {
            'tipo': 'sucesso',
            'acao': 'ligacao',
            'mensagem': f'Iniciando ligação para {contato.nome}',
            'dados': {
                'contato': contato.to_dict(),
                'url_ligacao': f'tel:{telefone_limpo}'
            }
        }
    except Exception as e:
        return {
            'tipo': 'erro',
            'mensagem': f'Erro ao processar ligação: {str(e)}'
        }

def listar_proximos_compromissos():
    """Lista próximos compromissos"""
    try:
        agora = datetime.utcnow()
        proximas_24h = agora + timedelta(hours=24)
        
        compromissos = Compromisso.query.filter(
            Compromisso.data_hora >= agora,
            Compromisso.data_hora <= proximas_24h,
            Compromisso.status == 'pendente'
        ).order_by(Compromisso.data_hora.asc()).limit(5).all()
        
        if not compromissos:
            return {
                'tipo': 'info',
                'mensagem': 'Você não tem compromissos nas próximas 24 horas.',
                'dados': []
            }
        
        lista_compromissos = []
        for comp in compromissos:
            tempo_restante = comp.data_hora - agora
            horas = int(tempo_restante.total_seconds() // 3600)
            minutos = int((tempo_restante.total_seconds() % 3600) // 60)
            
            if horas > 0:
                tempo_str = f'em {horas}h {minutos}min'
            else:
                tempo_str = f'em {minutos} minutos'
            
            lista_compromissos.append(f"{comp.titulo} - {tempo_str}")
        
        mensagem = f"Você tem {len(compromissos)} compromissos próximos:\n" + "\n".join(lista_compromissos)
        
        return {
            'tipo': 'sucesso',
            'acao': 'lista_compromissos',
            'mensagem': mensagem,
            'dados': [comp.to_dict() for comp in compromissos]
        }
    except Exception as e:
        return {
            'tipo': 'erro',
            'mensagem': f'Erro ao listar compromissos: {str(e)}'
        }

def resumir_ultima_reuniao():
    """Resume a última reunião"""
    try:
        ultima_reuniao = Reuniao.query.filter(
            Reuniao.status == 'concluida'
        ).order_by(Reuniao.data_hora.desc()).first()
        
        if not ultima_reuniao:
            return {
                'tipo': 'info',
                'mensagem': 'Nenhuma reunião concluída encontrada.'
            }
        
        if not ultima_reuniao.resumo:
            if ultima_reuniao.transcricao:
                # Gera resumo básico
                resumo = f"Reunião '{ultima_reuniao.titulo}' realizada em {ultima_reuniao.data_hora.strftime('%d/%m/%Y')}.\n"
                resumo += "Resumo automático baseado na transcrição disponível."
                ultima_reuniao.resumo = resumo
                db.session.commit()
            else:
                return {
                    'tipo': 'info',
                    'mensagem': f"A reunião '{ultima_reuniao.titulo}' não possui resumo ou transcrição disponível."
                }
        
        return {
            'tipo': 'sucesso',
            'acao': 'resumo_reuniao',
            'mensagem': f"Resumo da última reunião:\n{ultima_reuniao.resumo}",
            'dados': ultima_reuniao.to_dict()
        }
    except Exception as e:
        return {
            'tipo': 'erro',
            'mensagem': f'Erro ao resumir reunião: {str(e)}'
        }

def criar_lembrete(comando):
    """Cria um lembrete"""
    try:
        # Extrai informações do lembrete
        info = extrair_info_lembrete(comando)
        
        compromisso = Compromisso(
            titulo=f"Lembrete: {info['titulo']}",
            descricao=info['descricao'],
            data_hora=info['data_hora'],
            tipo='lembrete',
            alerta_antecedencia=5  # 5 minutos de antecedência para lembretes
        )
        
        db.session.add(compromisso)
        db.session.commit()
        
        return {
            'tipo': 'sucesso',
            'acao': 'lembrete',
            'mensagem': f"Lembrete criado: {info['titulo']} para {info['data_hora'].strftime('%d/%m/%Y às %H:%M')}",
            'dados': compromisso.to_dict()
        }
    except Exception as e:
        return {
            'tipo': 'erro',
            'mensagem': f'Erro ao criar lembrete: {str(e)}'
        }

def buscar_contato(comando):
    """Busca contato por nome"""
    try:
        nome = extrair_nome_contato(comando)
        
        if not nome:
            return {
                'tipo': 'erro',
                'mensagem': 'Não consegui identificar o nome do contato para buscar.'
            }
        
        contatos = Contato.query.filter(
            Contato.nome.ilike(f'%{nome}%')
        ).limit(5).all()
        
        if not contatos:
            return {
                'tipo': 'info',
                'mensagem': f'Nenhum contato encontrado com o nome "{nome}".'
            }
        
        if len(contatos) == 1:
            contato = contatos[0]
            return {
                'tipo': 'sucesso',
                'acao': 'contato_encontrado',
                'mensagem': f'Contato encontrado: {contato.nome} - {contato.telefone or "Sem telefone"}',
                'dados': contato.to_dict()
            }
        else:
            nomes = [c.nome for c in contatos]
            return {
                'tipo': 'sucesso',
                'acao': 'multiplos_contatos',
                'mensagem': f'Encontrei {len(contatos)} contatos: {", ".join(nomes)}',
                'dados': [c.to_dict() for c in contatos]
            }
    except Exception as e:
        return {
            'tipo': 'erro',
            'mensagem': f'Erro ao buscar contato: {str(e)}'
        }

def status_do_dia():
    """Retorna status dos compromissos do dia"""
    try:
        hoje = datetime.now().date()
        inicio_dia = datetime.combine(hoje, datetime.min.time())
        fim_dia = datetime.combine(hoje, datetime.max.time())
        
        compromissos = Compromisso.query.filter(
            Compromisso.data_hora >= inicio_dia,
            Compromisso.data_hora <= fim_dia,
            Compromisso.status != 'cancelado'
        ).order_by(Compromisso.data_hora.asc()).all()
        
        if not compromissos:
            return {
                'tipo': 'info',
                'mensagem': 'Você não tem compromissos agendados para hoje. Dia livre!'
            }
        
        pendentes = [c for c in compromissos if c.status == 'pendente']
        concluidos = [c for c in compromissos if c.status == 'concluido']
        
        mensagem = f"Status do seu dia:\n"
        mensagem += f"• {len(compromissos)} compromissos no total\n"
        mensagem += f"• {len(pendentes)} pendentes\n"
        mensagem += f"• {len(concluidos)} concluídos\n\n"
        
        if pendentes:
            mensagem += "Próximos compromissos:\n"
            for comp in pendentes[:3]:
                mensagem += f"• {comp.titulo} às {comp.data_hora.strftime('%H:%M')}\n"
        
        return {
            'tipo': 'sucesso',
            'acao': 'status_dia',
            'mensagem': mensagem,
            'dados': {
                'total': len(compromissos),
                'pendentes': len(pendentes),
                'concluidos': len(concluidos),
                'compromissos': [c.to_dict() for c in compromissos]
            }
        }
    except Exception as e:
        return {
            'tipo': 'erro',
            'mensagem': f'Erro ao obter status do dia: {str(e)}'
        }

# Funções auxiliares para extração de informações

def extrair_info_agendamento(comando):
    """Extrai informações de agendamento do comando"""
    info = {
        'titulo': '',
        'descricao': '',
        'data_hora': datetime.now() + timedelta(hours=1)  # padrão: 1 hora a partir de agora
    }
    
    # Extrai título (após "com" ou "para")
    if ' com ' in comando:
        titulo_match = re.search(r' com ([^0-9]+?)(?:\s+para|\s+às|\s+em|$)', comando)
        if titulo_match:
            info['titulo'] = f"Reunião com {titulo_match.group(1).strip()}"
    elif 'reunião' in comando:
        info['titulo'] = 'Nova reunião'
    else:
        info['titulo'] = 'Novo compromisso'
    
    # Extrai data/hora (simplificado)
    if 'amanhã' in comando:
        info['data_hora'] = datetime.now() + timedelta(days=1)
        if 'às' in comando:
            hora_match = re.search(r'às (\d{1,2})h?', comando)
            if hora_match:
                hora = int(hora_match.group(1))
                info['data_hora'] = info['data_hora'].replace(hour=hora, minute=0, second=0, microsecond=0)
    
    return info

def extrair_nome_contato(comando):
    """Extrai nome do contato do comando"""
    # Remove palavras de comando
    comando_limpo = comando.replace('ligar para', '').replace('chamar', '').replace('telefonar para', '')
    comando_limpo = comando_limpo.replace('buscar contato', '').replace('encontrar', '').replace('procurar', '')
    
    # Remove artigos e preposições
    palavras_ignorar = ['o', 'a', 'os', 'as', 'para', 'de', 'da', 'do', 'na', 'no']
    palavras = comando_limpo.split()
    nome_palavras = [p for p in palavras if p.lower() not in palavras_ignorar and len(p) > 1]
    
    return ' '.join(nome_palavras).strip()

def extrair_info_lembrete(comando):
    """Extrai informações do lembrete"""
    info = {
        'titulo': 'Lembrete',
        'descricao': '',
        'data_hora': datetime.now() + timedelta(hours=1)
    }
    
    # Extrai título do lembrete
    if 'lembrar' in comando:
        titulo_match = re.search(r'lembrar (.+?)(?:\s+às|\s+em|\s+para|$)', comando)
        if titulo_match:
            info['titulo'] = titulo_match.group(1).strip()
    
    return info

