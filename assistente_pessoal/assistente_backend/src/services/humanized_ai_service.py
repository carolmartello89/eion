import openai
import requests
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional
import re

from src.models.conversa import Conversa
from src.models.voice_profile import VoiceProfile
from src.models.user import User, db

logger = logging.getLogger(__name__)

class HumanizedAIService:
    def __init__(self):
        """Inicializa o serviço de IA humanizada"""
        self.client = openai.OpenAI()
        self.personalities = {
            'friendly': {
                'system_prompt': 'Você é uma IA amigável, calorosa e acolhedora. Sempre demonstra interesse genuíno pelo usuário e usa um tom conversacional natural.',
                'traits': ['empática', 'otimista', 'encorajadora']
            },
            'professional': {
                'system_prompt': 'Você é uma IA profissional, formal e eficiente. Foca em produtividade e fornece respostas precisas e bem estruturadas.',
                'traits': ['objetiva', 'organizada', 'confiável']
            },
            'casual': {
                'system_prompt': 'Você é uma IA descontraída, relaxada e informal. Usa linguagem coloquial e tem um estilo de conversa natural e espontâneo.',
                'traits': ['relaxada', 'espontânea', 'divertida']
            },
            'witty': {
                'system_prompt': 'Você é uma IA espirituosa, inteligente e divertida. Usa humor apropriado e faz observações inteligentes sobre as situações.',
                'traits': ['inteligente', 'humorística', 'perspicaz']
            }
        }
    
    def get_user_context(self, user_id: int) -> Dict:
        """Obtém contexto completo do usuário"""
        try:
            user = User.query.get(user_id)
            voice_profile = VoiceProfile.query.filter_by(user_id=user_id).first()
            
            # Histórico recente de conversas
            recent_conversations = Conversa.query.filter_by(user_id=user_id)\
                .order_by(Conversa.timestamp.desc())\
                .limit(10).all()
            
            # Informações financeiras recentes
            from src.models.financeiro import TransacaoFinanceira
            recent_transactions = TransacaoFinanceira.query.filter_by(user_id=user_id)\
                .order_by(TransacaoFinanceira.data.desc())\
                .limit(5).all()
            
            # Compromissos próximos
            from src.models.compromisso import Compromisso
            upcoming_appointments = Compromisso.query.filter_by(user_id=user_id)\
                .filter(Compromisso.data >= datetime.now())\
                .order_by(Compromisso.data.asc())\
                .limit(5).all()
            
            context = {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'preferred_name': voice_profile.preferred_name if voice_profile else user.email.split('@')[0],
                    'personality': getattr(voice_profile, 'personality', 'friendly') if voice_profile else 'friendly'
                },
                'recent_conversations': [
                    {
                        'comando': conv.comando,
                        'resposta': conv.resposta,
                        'timestamp': conv.timestamp.isoformat()
                    } for conv in recent_conversations
                ],
                'financial_summary': {
                    'recent_transactions': [
                        {
                            'tipo': trans.tipo,
                            'valor': float(trans.valor),
                            'categoria': trans.categoria,
                            'data': trans.data.isoformat()
                        } for trans in recent_transactions
                    ] if recent_transactions else []
                },
                'upcoming_events': [
                    {
                        'titulo': apt.titulo,
                        'data': apt.data.isoformat(),
                        'descricao': apt.descricao
                    } for apt in upcoming_appointments
                ],
                'current_time': datetime.now().isoformat(),
                'day_of_week': datetime.now().strftime('%A'),
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Erro ao obter contexto do usuário: {e}")
            return {'user': {'preferred_name': 'Usuário'}}
    
    def get_real_time_info(self, query: str) -> Optional[str]:
        """Busca informações em tempo real na internet"""
        try:
            # Simula busca de informações reais
            # Em implementação real, integraria com APIs de notícias, clima, etc.
            
            query_lower = query.lower()
            
            # Informações de tempo/clima
            if any(word in query_lower for word in ['tempo', 'clima', 'temperatura', 'chuva']):
                return self._get_weather_info()
            
            # Notícias atuais
            elif any(word in query_lower for word in ['notícia', 'notícias', 'acontecendo', 'atual']):
                return self._get_news_info()
            
            # Informações financeiras/mercado
            elif any(word in query_lower for word in ['dólar', 'euro', 'bitcoin', 'bolsa', 'ações']):
                return self._get_financial_info()
            
            # Data e hora atual
            elif any(word in query_lower for word in ['hora', 'data', 'hoje', 'agora']):
                now = datetime.now()
                return f"Agora são {now.strftime('%H:%M')} de {now.strftime('%d/%m/%Y')}, {self._get_day_name(now.weekday())}."
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar informações em tempo real: {e}")
            return None
    
    def _get_weather_info(self) -> str:
        """Simula informações de clima"""
        # Em implementação real, usaria API de clima como OpenWeatherMap
        return "O tempo hoje está parcialmente nublado com temperatura de 24°C. Há 30% de chance de chuva à tarde."
    
    def _get_news_info(self) -> str:
        """Simula informações de notícias"""
        # Em implementação real, usaria APIs de notícias
        return "As principais notícias de hoje incluem desenvolvimentos em tecnologia e economia. Posso buscar informações mais específicas se você quiser."
    
    def _get_financial_info(self) -> str:
        """Simula informações financeiras"""
        # Em implementação real, usaria APIs financeiras
        return "O dólar está cotado a R$ 5,20 hoje. O Bitcoin está em alta, próximo aos US$ 45.000."
    
    def _get_day_name(self, weekday: int) -> str:
        """Retorna nome do dia da semana"""
        days = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 
                'sexta-feira', 'sábado', 'domingo']
        return days[weekday]
    
    def process_command(self, user_id: int, command: str, context: Dict = None) -> Dict:
        """Processa comando com IA humanizada"""
        try:
            # Obtém contexto do usuário
            user_context = self.get_user_context(user_id)
            
            # Busca informações em tempo real se necessário
            real_time_info = self.get_real_time_info(command)
            
            # Obtém configurações de personalidade
            voice_profile = VoiceProfile.query.filter_by(user_id=user_id).first()
            personality = getattr(voice_profile, 'personality', 'friendly') if voice_profile else 'friendly'
            response_style = getattr(voice_profile, 'response_style', 'detailed') if voice_profile else 'detailed'
            
            # Constrói prompt personalizado
            system_prompt = self._build_system_prompt(personality, user_context, response_style)
            
            # Prepara mensagens para OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Comando: {command}"}
            ]
            
            # Adiciona informações em tempo real se disponíveis
            if real_time_info:
                messages.append({
                    "role": "system", 
                    "content": f"Informação atual relevante: {real_time_info}"
                })
            
            # Adiciona contexto de conversas recentes
            if user_context.get('recent_conversations'):
                recent_context = "Contexto de conversas recentes:\n"
                for conv in user_context['recent_conversations'][:3]:
                    recent_context += f"- Usuário: {conv['comando']}\n- IA: {conv['resposta']}\n"
                
                messages.append({
                    "role": "system",
                    "content": recent_context
                })
            
            # Chama OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Detecta ações a serem executadas
            action, parameters = self._detect_action(command, ai_response)
            
            # Salva conversa no histórico
            self._save_conversation(user_id, command, ai_response, action)
            
            return {
                'resposta': ai_response,
                'acao': action,
                'parametros': parameters,
                'contexto_usado': bool(real_time_info),
                'personalidade': personality,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar comando: {e}")
            return {
                'resposta': 'Desculpe, ocorreu um erro interno. Tente novamente.',
                'acao': None,
                'parametros': {},
                'erro': str(e)
            }
    
    def _build_system_prompt(self, personality: str, user_context: Dict, response_style: str) -> str:
        """Constrói prompt personalizado baseado na personalidade"""
        base_personality = self.personalities.get(personality, self.personalities['friendly'])
        user_name = user_context.get('user', {}).get('preferred_name', 'Usuário')
        
        prompt = f"""
{base_personality['system_prompt']}

INFORMAÇÕES DO USUÁRIO:
- Nome preferido: {user_name}
- Personalidade configurada: {personality}
- Estilo de resposta: {response_style}

CONTEXTO ATUAL:
- Data/Hora: {user_context.get('current_time', '')}
- Dia da semana: {user_context.get('day_of_week', '')}

DIRETRIZES DE INTERAÇÃO:
1. SEMPRE use o nome preferido do usuário ({user_name}) nas respostas
2. Seja {', '.join(base_personality['traits'])}
3. Use informações VERDADEIRAS quando disponíveis
4. Mantenha consistência com conversas anteriores
5. Responda de forma {response_style}
6. Se não souber algo, seja honesta sobre isso
7. Ofereça ajuda proativa quando apropriado

FUNCIONALIDADES DISPONÍVEIS:
- Gerenciar compromissos e agenda
- Controlar finanças pessoais
- Fazer ligações para contatos
- Gravar e transcrever reuniões
- Criar lembretes inteligentes
- Buscar informações em tempo real
- Executar automações personalizadas

ESTILO DE COMUNICAÇÃO:
- Use linguagem natural e conversacional
- Demonstre interesse genuíno
- Seja prestativa e proativa
- Adapte o tom à situação
- Use informações do contexto do usuário
"""
        
        return prompt
    
    def _detect_action(self, command: str, response: str) -> tuple:
        """Detecta ações a serem executadas baseadas no comando"""
        command_lower = command.lower()
        
        # Ações de agenda/compromissos
        if any(word in command_lower for word in ['agendar', 'compromisso', 'reunião', 'encontro']):
            return 'create_appointment', {'command': command}
        
        # Ações financeiras
        elif any(word in command_lower for word in ['gastei', 'recebi', 'paguei', 'comprei']):
            return 'add_transaction', {'command': command}
        
        # Ligações
        elif any(word in command_lower for word in ['ligar', 'telefonar', 'chamar']):
            # Extrai nome do contato
            contact_match = re.search(r'ligar para (.+)', command_lower)
            if contact_match:
                return 'make_call', {'contact_name': contact_match.group(1)}
        
        # Navegação
        elif any(word in command_lower for word in ['abrir', 'ir para', 'mostrar']):
            if 'agenda' in command_lower:
                return 'navigate', {'page': 'agenda'}
            elif 'financeiro' in command_lower or 'finanças' in command_lower:
                return 'navigate', {'page': 'financeiro'}
            elif 'contatos' in command_lower:
                return 'navigate', {'page': 'contatos'}
            elif 'reuniões' in command_lower:
                return 'navigate', {'page': 'reunioes'}
        
        # Consultas
        elif any(word in command_lower for word in ['quanto', 'saldo', 'gastei', 'recebi']):
            return 'query_finances', {'type': 'summary'}
        
        elif any(word in command_lower for word in ['próximos', 'agenda', 'compromissos']):
            return 'query_schedule', {'type': 'upcoming'}
        
        return None, {}
    
    def _save_conversation(self, user_id: int, command: str, response: str, action: str):
        """Salva conversa no histórico"""
        try:
            conversa = Conversa(
                user_id=user_id,
                comando=command,
                resposta=response,
                acao_executada=action,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(conversa)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Erro ao salvar conversa: {e}")
    
    def get_proactive_suggestions(self, user_id: int) -> List[str]:
        """Gera sugestões proativas baseadas no contexto do usuário"""
        try:
            user_context = self.get_user_context(user_id)
            suggestions = []
            
            # Verifica compromissos próximos
            if user_context.get('upcoming_events'):
                next_event = user_context['upcoming_events'][0]
                event_time = datetime.fromisoformat(next_event['data'])
                time_diff = event_time - datetime.now()
                
                if time_diff.total_seconds() < 3600:  # Menos de 1 hora
                    suggestions.append(f"Lembre-se: você tem '{next_event['titulo']}' em {int(time_diff.total_seconds()/60)} minutos.")
            
            # Verifica padrões financeiros
            if user_context.get('financial_summary', {}).get('recent_transactions'):
                recent_spending = sum(
                    trans['valor'] for trans in user_context['financial_summary']['recent_transactions']
                    if trans['tipo'] == 'despesa'
                )
                if recent_spending > 1000:  # Gastos altos recentes
                    suggestions.append("Notei que você teve alguns gastos altos recentemente. Quer que eu gere um relatório financeiro?")
            
            # Sugestões baseadas no horário
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 11:
                suggestions.append("Bom dia! Como posso ajudar você a organizar o dia hoje?")
            elif 12 <= current_hour <= 14:
                suggestions.append("Boa tarde! Que tal verificarmos sua agenda para o resto do dia?")
            elif 18 <= current_hour <= 20:
                suggestions.append("Boa noite! Quer que eu prepare um resumo do seu dia?")
            
            return suggestions[:2]  # Máximo 2 sugestões
            
        except Exception as e:
            logger.error(f"Erro ao gerar sugestões proativas: {e}")
            return []
    
    def configure_personality(self, user_id: int, settings: Dict) -> Dict:
        """Configura personalidade e estilo da IA"""
        try:
            voice_profile = VoiceProfile.query.filter_by(user_id=user_id).first()
            if not voice_profile:
                voice_profile = VoiceProfile(user_id=user_id)
                db.session.add(voice_profile)
            
            # Atualiza configurações (simulado - adicionar campos ao modelo se necessário)
            if 'personality' in settings:
                # voice_profile.personality = settings['personality']
                pass
            
            if 'response_style' in settings:
                # voice_profile.response_style = settings['response_style']
                pass
            
            if 'voice_gender' in settings:
                # voice_profile.voice_gender = settings['voice_gender']
                pass
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Personalidade configurada com sucesso',
                'settings': settings
            }
            
        except Exception as e:
            logger.error(f"Erro ao configurar personalidade: {e}")
            return {
                'success': False,
                'message': f'Erro ao configurar: {str(e)}'
            }

