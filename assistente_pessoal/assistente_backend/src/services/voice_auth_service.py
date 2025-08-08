import numpy as np
import librosa
import torch
from speechbrain.pretrained import EncoderClassifier
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
import tempfile
import os
import logging

from src.models.voice_profile import VoiceProfile, VoiceAuthAttempt
from src.models.user import db

logger = logging.getLogger(__name__)

class VoiceAuthService:
    def __init__(self):
        """Inicializa o serviço de autenticação por voz"""
        try:
            # Carrega modelo pré-treinado para embeddings de voz
            self.voice_encoder = EncoderClassifier.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb",
                savedir="models/spkrec-ecapa-voxceleb",
                run_opts={"device": "cpu"}  # Use GPU se disponível
            )
            logger.info("Modelo de reconhecimento de voz carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo de voz: {e}")
            self.voice_encoder = None
    
    def extract_voice_embedding(self, audio_data, sample_rate=16000):
        """Extrai embedding de voz de um arquivo de áudio"""
        try:
            if self.voice_encoder is None:
                raise Exception("Modelo de voz não carregado")
            
            # Salva áudio temporariamente
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                # Se audio_data é bytes, salva diretamente
                if isinstance(audio_data, bytes):
                    temp_file.write(audio_data)
                    temp_path = temp_file.name
                
                # Carrega e processa áudio
                waveform, sr = librosa.load(temp_path, sr=sample_rate)
                
                # Remove arquivo temporário
                os.unlink(temp_path)
                
                # Converte para tensor
                waveform_tensor = torch.tensor(waveform).unsqueeze(0)
                
                # Extrai embedding
                with torch.no_grad():
                    embedding = self.voice_encoder.encode_batch(waveform_tensor)
                    embedding_np = embedding.squeeze().cpu().numpy()
                
                return embedding_np.tolist()
                
        except Exception as e:
            logger.error(f"Erro ao extrair embedding de voz: {e}")
            return None
    
    def train_voice_profile(self, user_id, audio_samples):
        """Treina perfil de voz com múltiplas amostras"""
        try:
            voice_profile = VoiceProfile.query.filter_by(user_id=user_id).first()
            if not voice_profile:
                voice_profile = VoiceProfile(user_id=user_id)
                db.session.add(voice_profile)
            
            embeddings = []
            successful_samples = 0
            
            for audio_sample in audio_samples:
                embedding = self.extract_voice_embedding(audio_sample)
                if embedding:
                    embeddings.append(embedding)
                    successful_samples += 1
            
            if successful_samples >= 3:
                # Salva embeddings no perfil
                voice_profile.set_embeddings(embeddings)
                voice_profile.voice_samples_count = successful_samples
                voice_profile.is_trained = True
                voice_profile.last_training = datetime.utcnow()
                
                db.session.commit()
                
                logger.info(f"Perfil de voz treinado para usuário {user_id} com {successful_samples} amostras")
                return {
                    'success': True,
                    'samples_processed': successful_samples,
                    'message': 'Perfil de voz treinado com sucesso'
                }
            else:
                return {
                    'success': False,
                    'samples_processed': successful_samples,
                    'message': 'Mínimo de 3 amostras necessárias para treinar o perfil'
                }
                
        except Exception as e:
            logger.error(f"Erro ao treinar perfil de voz: {e}")
            return {
                'success': False,
                'message': f'Erro no treinamento: {str(e)}'
            }
    
    def authenticate_voice(self, user_id, audio_data):
        """Autentica usuário por voz"""
        try:
            voice_profile = VoiceProfile.query.filter_by(user_id=user_id).first()
            
            if not voice_profile or not voice_profile.is_trained:
                self._log_auth_attempt(user_id, 0.0, False, "Perfil não treinado")
                return {
                    'authenticated': False,
                    'confidence': 0.0,
                    'reason': 'Perfil de voz não treinado'
                }
            
            # Verifica se usuário não está bloqueado
            if self._is_user_locked_out(user_id):
                self._log_auth_attempt(user_id, 0.0, False, "Usuário bloqueado")
                return {
                    'authenticated': False,
                    'confidence': 0.0,
                    'reason': 'Muitas tentativas falharam. Tente novamente mais tarde.'
                }
            
            # Extrai embedding do áudio atual
            current_embedding = self.extract_voice_embedding(audio_data)
            if not current_embedding:
                self._log_auth_attempt(user_id, 0.0, False, "Erro ao processar áudio")
                return {
                    'authenticated': False,
                    'confidence': 0.0,
                    'reason': 'Erro ao processar áudio'
                }
            
            # Compara com embeddings salvos
            stored_embeddings = voice_profile.get_embeddings()
            similarities = []
            
            for stored_embedding in stored_embeddings:
                similarity = cosine_similarity(
                    [current_embedding], 
                    [stored_embedding]
                )[0][0]
                similarities.append(similarity)
            
            # Calcula confiança média
            avg_confidence = np.mean(similarities)
            max_confidence = np.max(similarities)
            
            # Usa a maior confiança para decisão
            confidence_score = max_confidence
            threshold = voice_profile.confidence_threshold
            
            is_authenticated = confidence_score >= threshold
            
            # Log da tentativa
            self._log_auth_attempt(
                user_id, 
                confidence_score, 
                is_authenticated,
                None if is_authenticated else f"Confiança {confidence_score:.2f} < {threshold}"
            )
            
            return {
                'authenticated': is_authenticated,
                'confidence': float(confidence_score),
                'threshold': threshold,
                'reason': 'Autenticado com sucesso' if is_authenticated else 'Voz não reconhecida'
            }
            
        except Exception as e:
            logger.error(f"Erro na autenticação por voz: {e}")
            self._log_auth_attempt(user_id, 0.0, False, f"Erro interno: {str(e)}")
            return {
                'authenticated': False,
                'confidence': 0.0,
                'reason': 'Erro interno do sistema'
            }
    
    def _log_auth_attempt(self, user_id, confidence, success, reason):
        """Registra tentativa de autenticação"""
        try:
            attempt = VoiceAuthAttempt(
                user_id=user_id,
                confidence_score=confidence,
                is_successful=success,
                failure_reason=reason
            )
            db.session.add(attempt)
            db.session.commit()
        except Exception as e:
            logger.error(f"Erro ao registrar tentativa de autenticação: {e}")
    
    def _is_user_locked_out(self, user_id):
        """Verifica se usuário está bloqueado por muitas tentativas falhadas"""
        try:
            voice_profile = VoiceProfile.query.filter_by(user_id=user_id).first()
            if not voice_profile:
                return False
            
            # Verifica tentativas nas últimas horas
            cutoff_time = datetime.utcnow() - timedelta(seconds=voice_profile.lockout_duration)
            
            failed_attempts = VoiceAuthAttempt.query.filter(
                VoiceAuthAttempt.user_id == user_id,
                VoiceAuthAttempt.is_successful == False,
                VoiceAuthAttempt.timestamp > cutoff_time
            ).count()
            
            return failed_attempts >= voice_profile.max_failed_attempts
            
        except Exception as e:
            logger.error(f"Erro ao verificar bloqueio: {e}")
            return False
    
    def update_voice_profile_settings(self, user_id, settings):
        """Atualiza configurações do perfil de voz"""
        try:
            voice_profile = VoiceProfile.query.filter_by(user_id=user_id).first()
            if not voice_profile:
                voice_profile = VoiceProfile(user_id=user_id)
                db.session.add(voice_profile)
            
            # Atualiza configurações
            if 'preferred_name' in settings:
                voice_profile.preferred_name = settings['preferred_name']
            
            if 'confidence_threshold' in settings:
                voice_profile.confidence_threshold = float(settings['confidence_threshold'])
            
            if 'voice_activation_enabled' in settings:
                voice_profile.voice_activation_enabled = bool(settings['voice_activation_enabled'])
            
            if 'wake_word_sensitivity' in settings:
                voice_profile.wake_word_sensitivity = float(settings['wake_word_sensitivity'])
            
            if 'voice_auth_enabled' in settings:
                voice_profile.voice_auth_enabled = bool(settings['voice_auth_enabled'])
            
            voice_profile.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {'success': True, 'message': 'Configurações atualizadas'}
            
        except Exception as e:
            logger.error(f"Erro ao atualizar configurações: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_voice_profile_status(self, user_id):
        """Retorna status do perfil de voz"""
        try:
            voice_profile = VoiceProfile.query.filter_by(user_id=user_id).first()
            
            if not voice_profile:
                return {
                    'exists': False,
                    'is_trained': False,
                    'samples_count': 0,
                    'preferred_name': None
                }
            
            # Estatísticas de autenticação
            total_attempts = VoiceAuthAttempt.query.filter_by(user_id=user_id).count()
            successful_attempts = VoiceAuthAttempt.query.filter_by(
                user_id=user_id, 
                is_successful=True
            ).count()
            
            success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
            
            return {
                'exists': True,
                'is_trained': voice_profile.is_trained,
                'samples_count': voice_profile.voice_samples_count,
                'preferred_name': voice_profile.preferred_name,
                'confidence_threshold': voice_profile.confidence_threshold,
                'voice_activation_enabled': voice_profile.voice_activation_enabled,
                'voice_auth_enabled': voice_profile.voice_auth_enabled,
                'last_training': voice_profile.last_training.isoformat() if voice_profile.last_training else None,
                'total_auth_attempts': total_attempts,
                'successful_auth_attempts': successful_attempts,
                'success_rate': round(success_rate, 1),
                'is_locked_out': self._is_user_locked_out(user_id)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status do perfil: {e}")
            return {'exists': False, 'error': str(e)}

