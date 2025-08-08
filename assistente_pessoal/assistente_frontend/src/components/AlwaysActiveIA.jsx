import { useState, useEffect, useRef, useCallback } from 'react'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Mic, MicOff, Volume2, VolumeX, Settings, 
  Brain, Zap, Shield, Eye, EyeOff 
} from 'lucide-react'

const AlwaysActiveIA = ({ user, onCommand, onVoiceAuth }) => {
  // Estados principais
  const [isListening, setIsListening] = useState(false)
  const [isActive, setIsActive] = useState(false)
  const [wakeWordDetected, setWakeWordDetected] = useState(false)
  const [currentTranscript, setCurrentTranscript] = useState('')
  const [iaResponse, setIaResponse] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  
  // Estados de configuração
  const [sensitivity, setSensitivity] = useState(0.8)
  const [voiceAuthEnabled, setVoiceAuthEnabled] = useState(true)
  const [alwaysListening, setAlwaysListening] = useState(true)
  const [visualFeedback, setVisualFeedback] = useState(true)
  const [preferredName, setPreferredName] = useState(user?.preferred_name || 'Usuário')
  
  // Estados de status
  const [authStatus, setAuthStatus] = useState('idle') // idle, authenticating, authenticated, failed
  const [lastActivity, setLastActivity] = useState(null)
  const [sessionActive, setSessionActive] = useState(false)
  
  // Refs
  const recognitionRef = useRef(null)
  const audioContextRef = useRef(null)
  const mediaStreamRef = useRef(null)
  const wakeWordTimeoutRef = useRef(null)
  const sessionTimeoutRef = useRef(null)
  const synthRef = useRef(null)

  // Inicialização
  useEffect(() => {
    initializeVoiceRecognition()
    initializeSpeechSynthesis()
    loadUserSettings()
    
    return () => {
      cleanup()
    }
  }, [])

  // Auto-start listening quando habilitado
  useEffect(() => {
    if (alwaysListening && !isListening) {
      startListening()
    } else if (!alwaysListening && isListening) {
      stopListening()
    }
  }, [alwaysListening])

  const initializeVoiceRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      
      const recognition = recognitionRef.current
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = 'pt-BR'
      recognition.maxAlternatives = 1

      recognition.onstart = () => {
        setIsListening(true)
        console.log('🎤 IA: Escutando...')
      }

      recognition.onresult = (event) => {
        let interimTranscript = ''
        let finalTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript.toLowerCase().trim()
          
          if (event.results[i].isFinal) {
            finalTranscript += transcript
          } else {
            interimTranscript += transcript
          }
        }

        const fullTranscript = (finalTranscript + interimTranscript).toLowerCase()
        setCurrentTranscript(fullTranscript)

        // Detecta palavra-chave "IA"
        if (!wakeWordDetected && (fullTranscript.includes('ia') || fullTranscript.includes('hey ia') || fullTranscript.includes('oi ia'))) {
          handleWakeWordDetected(fullTranscript)
        }

        // Se já detectou wake word, processa comando
        if (wakeWordDetected && finalTranscript) {
          handleCommand(finalTranscript)
        }
      }

      recognition.onerror = (event) => {
        console.error('Erro no reconhecimento de voz:', event.error)
        
        // Reinicia automaticamente em caso de erro
        setTimeout(() => {
          if (alwaysListening) {
            startListening()
          }
        }, 1000)
      }

      recognition.onend = () => {
        setIsListening(false)
        
        // Reinicia automaticamente se deve estar sempre escutando
        if (alwaysListening && !isProcessing) {
          setTimeout(() => {
            startListening()
          }, 500)
        }
      }
    }
  }

  const initializeSpeechSynthesis = () => {
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis
    }
  }

  const loadUserSettings = async () => {
    try {
      const response = await fetch('/api/voice-auth/voice-profile/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        const profile = data.profile
        
        if (profile.exists) {
          setPreferredName(profile.preferred_name || 'Usuário')
          setSensitivity(profile.wake_word_sensitivity || 0.8)
          setVoiceAuthEnabled(profile.voice_auth_enabled)
          setAlwaysListening(profile.voice_activation_enabled)
        }
      }
    } catch (error) {
      console.error('Erro ao carregar configurações:', error)
    }
  }

  const startListening = useCallback(() => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start()
      } catch (error) {
        console.error('Erro ao iniciar reconhecimento:', error)
      }
    }
  }, [isListening])

  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
    }
  }, [isListening])

  const handleWakeWordDetected = async (transcript) => {
    console.log('🔥 Wake word "IA" detectada!')
    setWakeWordDetected(true)
    setIsActive(true)
    setLastActivity(new Date())

    // Feedback visual
    if (visualFeedback) {
      document.body.style.background = 'linear-gradient(45deg, #3b82f6, #8b5cf6)'
      setTimeout(() => {
        document.body.style.background = ''
      }, 2000)
    }

    // Autenticação por voz se habilitada
    if (voiceAuthEnabled && !sessionActive) {
      await authenticateByVoice(transcript)
    } else {
      // Resposta de ativação
      const greeting = getGreeting()
      speak(`Olá ${preferredName}! ${greeting} Como posso ajudar?`)
      setSessionActive(true)
      startSessionTimeout()
    }

    // Reset wake word após 10 segundos
    wakeWordTimeoutRef.current = setTimeout(() => {
      setWakeWordDetected(false)
      setIsActive(false)
      setCurrentTranscript('')
    }, 10000)
  }

  const authenticateByVoice = async (audioTranscript) => {
    setAuthStatus('authenticating')
    
    try {
      // Simula captura de áudio para autenticação
      // Em implementação real, capturaria áudio específico
      const response = await fetch('/api/voice-auth/voice-profile/authenticate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: new FormData() // Adicionar áudio real aqui
      })

      const result = await response.json()

      if (result.authenticated) {
        setAuthStatus('authenticated')
        setSessionActive(true)
        speak(`Voz reconhecida! Olá ${preferredName}, como posso ajudar?`)
        startSessionTimeout()
        
        if (onVoiceAuth) {
          onVoiceAuth(result)
        }
      } else {
        setAuthStatus('failed')
        speak('Desculpe, não reconheci sua voz. Tente novamente.')
        
        setTimeout(() => {
          setAuthStatus('idle')
          setWakeWordDetected(false)
          setIsActive(false)
        }, 3000)
      }
    } catch (error) {
      console.error('Erro na autenticação por voz:', error)
      setAuthStatus('failed')
      speak('Erro na autenticação. Tente novamente.')
    }
  }

  const handleCommand = async (command) => {
    if (!sessionActive && voiceAuthEnabled) {
      speak('Por favor, autentique-se primeiro dizendo "IA".')
      return
    }

    setIsProcessing(true)
    setCurrentTranscript(command)
    
    try {
      // Processa comando com IA
      const response = await fetch('/api/assistente/processar-comando', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          comando: command,
          contexto: {
            usuario: preferredName,
            sessao_ativa: sessionActive,
            timestamp: new Date().toISOString()
          }
        })
      })

      if (response.ok) {
        const result = await response.json()
        setIaResponse(result.resposta)
        speak(result.resposta)
        
        // Executa ação se necessário
        if (result.acao && onCommand) {
          onCommand(result.acao, result.parametros)
        }
        
        setLastActivity(new Date())
        startSessionTimeout()
      } else {
        speak('Desculpe, não consegui processar seu comando.')
      }
    } catch (error) {
      console.error('Erro ao processar comando:', error)
      speak('Ocorreu um erro. Tente novamente.')
    } finally {
      setIsProcessing(false)
    }
  }

  const speak = (text) => {
    if (synthRef.current && text) {
      // Para qualquer fala anterior
      synthRef.current.cancel()
      
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'pt-BR'
      utterance.rate = 0.9
      utterance.pitch = 1.0
      utterance.volume = 0.8
      
      // Seleciona voz feminina se disponível
      const voices = synthRef.current.getVoices()
      const femaleVoice = voices.find(voice => 
        voice.lang.includes('pt') && voice.name.toLowerCase().includes('female')
      ) || voices.find(voice => voice.lang.includes('pt'))
      
      if (femaleVoice) {
        utterance.voice = femaleVoice
      }

      utterance.onstart = () => setIsSpeaking(true)
      utterance.onend = () => setIsSpeaking(false)
      utterance.onerror = () => setIsSpeaking(false)

      synthRef.current.speak(utterance)
    }
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Bom dia!'
    if (hour < 18) return 'Boa tarde!'
    return 'Boa noite!'
  }

  const startSessionTimeout = () => {
    // Limpa timeout anterior
    if (sessionTimeoutRef.current) {
      clearTimeout(sessionTimeoutRef.current)
    }

    // Nova sessão expira em 5 minutos de inatividade
    sessionTimeoutRef.current = setTimeout(() => {
      setSessionActive(false)
      setWakeWordDetected(false)
      setIsActive(false)
      setCurrentTranscript('')
      setIaResponse('')
      console.log('🔒 Sessão IA expirada por inatividade')
    }, 5 * 60 * 1000)
  }

  const toggleAlwaysListening = () => {
    setAlwaysListening(!alwaysListening)
  }

  const toggleVoiceAuth = () => {
    setVoiceAuthEnabled(!voiceAuthEnabled)
  }

  const cleanup = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    if (synthRef.current) {
      synthRef.current.cancel()
    }
    if (wakeWordTimeoutRef.current) {
      clearTimeout(wakeWordTimeoutRef.current)
    }
    if (sessionTimeoutRef.current) {
      clearTimeout(sessionTimeoutRef.current)
    }
  }

  const getStatusColor = () => {
    if (authStatus === 'authenticating') return 'bg-yellow-500'
    if (authStatus === 'authenticated' || sessionActive) return 'bg-green-500'
    if (authStatus === 'failed') return 'bg-red-500'
    if (isListening) return 'bg-blue-500'
    return 'bg-gray-400'
  }

  const getStatusText = () => {
    if (authStatus === 'authenticating') return 'Autenticando...'
    if (authStatus === 'authenticated' || sessionActive) return 'Autenticado'
    if (authStatus === 'failed') return 'Falha na autenticação'
    if (wakeWordDetected) return 'IA Ativa - Escutando comando'
    if (isListening) return 'Escutando "IA"...'
    return 'Inativo'
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Indicador Visual Principal */}
      <div className={`relative ${isActive ? 'animate-pulse' : ''}`}>
        {/* Círculo de Status */}
        <div className={`w-16 h-16 rounded-full ${getStatusColor()} flex items-center justify-center shadow-lg transition-all duration-300 ${
          wakeWordDetected ? 'scale-110 shadow-2xl' : ''
        }`}>
          <Brain className="w-8 h-8 text-white" />
          
          {/* Animação de ondas sonoras */}
          {isListening && (
            <>
              <div className="absolute inset-0 rounded-full border-2 border-white opacity-75 animate-ping"></div>
              <div className="absolute inset-0 rounded-full border-2 border-white opacity-50 animate-ping" style={{ animationDelay: '0.5s' }}></div>
            </>
          )}
        </div>

        {/* Badge de Status */}
        <Badge 
          className={`absolute -top-2 -right-2 text-xs px-2 py-1 ${
            sessionActive ? 'bg-green-600' : 'bg-gray-600'
          }`}
        >
          IA
        </Badge>

        {/* Indicador de Fala */}
        {isSpeaking && (
          <div className="absolute -bottom-2 -left-2">
            <Volume2 className="w-6 h-6 text-blue-500 animate-bounce" />
          </div>
        )}
      </div>

      {/* Painel de Controle (expandido quando ativo) */}
      {isActive && (
        <Card className="absolute bottom-20 right-0 w-80 shadow-2xl border-2 border-blue-200">
          <CardContent className="p-4 space-y-4">
            {/* Status */}
            <div className="text-center">
              <h3 className="font-bold text-lg flex items-center justify-center space-x-2">
                <Brain className="w-5 h-5" />
                <span>IA Assistente</span>
              </h3>
              <p className="text-sm text-muted-foreground">{getStatusText()}</p>
            </div>

            {/* Transcrição Atual */}
            {currentTranscript && (
              <div className="p-3 bg-blue-50 rounded-lg">
                <p className="text-sm">
                  <strong>Você:</strong> {currentTranscript}
                </p>
              </div>
            )}

            {/* Resposta da IA */}
            {iaResponse && (
              <div className="p-3 bg-green-50 rounded-lg">
                <p className="text-sm">
                  <strong>IA:</strong> {iaResponse}
                </p>
              </div>
            )}

            {/* Processando */}
            {isProcessing && (
              <div className="text-center">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-sm text-muted-foreground mt-2">Processando...</p>
              </div>
            )}

            {/* Controles Rápidos */}
            <div className="flex justify-between items-center">
              <Button
                variant="outline"
                size="sm"
                onClick={toggleAlwaysListening}
                className="flex items-center space-x-1"
              >
                {alwaysListening ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
                <span>{alwaysListening ? 'Ativo' : 'Inativo'}</span>
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={toggleVoiceAuth}
                className="flex items-center space-x-1"
              >
                <Shield className="w-4 h-4" />
                <span>{voiceAuthEnabled ? 'Seguro' : 'Livre'}</span>
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setVisualFeedback(!visualFeedback)}
              >
                {visualFeedback ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
              </Button>
            </div>

            {/* Informações da Sessão */}
            {sessionActive && lastActivity && (
              <div className="text-xs text-muted-foreground text-center">
                Sessão ativa • Última atividade: {lastActivity.toLocaleTimeString('pt-BR')}
              </div>
            )}

            {/* Dicas */}
            {!sessionActive && (
              <div className="text-xs text-muted-foreground text-center p-2 bg-gray-50 rounded">
                💡 Diga "IA" para ativar o assistente
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Configurações Rápidas */}
      {!isActive && (
        <Button
          variant="ghost"
          size="sm"
          className="absolute -top-12 right-0"
          onClick={() => setIsActive(true)}
        >
          <Settings className="w-4 h-4" />
        </Button>
      )}
    </div>
  )
}

export default AlwaysActiveIA

