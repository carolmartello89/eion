import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX,
  MessageSquare,
  Brain,
  Loader2,
  X
} from 'lucide-react'

const VoiceAssistantAdvanced = ({ isListening, setIsListening }) => {
  const [isProcessing, setIsProcessing] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [response, setResponse] = useState('')
  const [conversation, setConversation] = useState([])
  const [isExpanded, setIsExpanded] = useState(false)
  const [speechSupported, setSpeechSupported] = useState(false)
  
  const recognitionRef = useRef(null)
  const synthRef = useRef(null)

  // Inicializa APIs de voz
  useEffect(() => {
    // Verifica suporte para reconhecimento de voz
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = true
      recognitionRef.current.lang = 'pt-BR'
      
      recognitionRef.current.onstart = () => {
        setIsListening(true)
        setTranscript('')
      }
      
      recognitionRef.current.onresult = (event) => {
        let finalTranscript = ''
        let interimTranscript = ''
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript
          } else {
            interimTranscript += transcript
          }
        }
        
        setTranscript(finalTranscript || interimTranscript)
        
        if (finalTranscript) {
          processVoiceCommand(finalTranscript)
        }
      }
      
      recognitionRef.current.onerror = (event) => {
        console.error('Erro no reconhecimento de voz:', event.error)
        setIsListening(false)
        setIsProcessing(false)
      }
      
      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
      
      setSpeechSupported(true)
    }

    // Inicializa síntese de voz
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
      if (synthRef.current) {
        synthRef.current.cancel()
      }
    }
  }, [setIsListening])

  // Processa comandos de voz com IA
  const processVoiceCommand = async (command) => {
    setIsProcessing(true)
    setIsExpanded(true)
    
    try {
      // Adiciona comando à conversa
      const newMessage = {
        id: Date.now(),
        type: 'user',
        content: command,
        timestamp: new Date()
      }
      
      setConversation(prev => [...prev, newMessage])

      // Processa comando com IA
      const response = await fetch('/api/assistente/process-voice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          command: command,
          context: 'voice_assistant'
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        const aiResponse = {
          id: Date.now() + 1,
          type: 'assistant',
          content: data.response,
          action: data.action,
          timestamp: new Date()
        }
        
        setConversation(prev => [...prev, aiResponse])
        setResponse(data.response)
        
        // Executa ação se necessário
        if (data.action) {
          executeAction(data.action)
        }
        
        // Fala a resposta
        speakResponse(data.response)
        
      } else {
        throw new Error('Erro ao processar comando')
      }
      
    } catch (error) {
      console.error('Erro ao processar comando:', error)
      const errorResponse = 'Desculpe, não consegui processar seu comando. Tente novamente.'
      setResponse(errorResponse)
      speakResponse(errorResponse)
    } finally {
      setIsProcessing(false)
    }
  }

  // Executa ações baseadas na resposta da IA
  const executeAction = (action) => {
    switch (action.type) {
      case 'navigate':
        // Navegar para uma página específica
        if (action.page) {
          window.dispatchEvent(new CustomEvent('navigate', { detail: action.page }))
        }
        break
      
      case 'call':
        // Iniciar ligação
        if (action.number) {
          window.open(`tel:${action.number}`)
        }
        break
      
      case 'create_appointment':
        // Criar compromisso
        window.dispatchEvent(new CustomEvent('create-appointment', { detail: action.data }))
        break
      
      case 'show_schedule':
        // Mostrar agenda
        window.dispatchEvent(new CustomEvent('show-schedule', { detail: action.filter }))
        break
      
      default:
        console.log('Ação não reconhecida:', action)
    }
  }

  // Síntese de voz para respostas
  const speakResponse = (text) => {
    if (!synthRef.current) return
    
    // Cancela qualquer fala anterior
    synthRef.current.cancel()
    
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'pt-BR'
    utterance.rate = 0.9
    utterance.pitch = 1
    
    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)
    
    synthRef.current.speak(utterance)
  }

  // Inicia/para reconhecimento de voz
  const toggleListening = () => {
    if (!speechSupported) {
      alert('Reconhecimento de voz não suportado neste navegador')
      return
    }

    if (isListening) {
      recognitionRef.current?.stop()
    } else {
      recognitionRef.current?.start()
    }
  }

  // Para síntese de voz
  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel()
      setIsSpeaking(false)
    }
  }

  // Limpa conversa
  const clearConversation = () => {
    setConversation([])
    setResponse('')
    setTranscript('')
  }

  if (!isExpanded && !isListening && !isProcessing) {
    return null
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md max-h-[80vh] overflow-hidden">
        <CardContent className="p-0">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b bg-primary/5">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                isListening ? 'bg-red-500 animate-pulse' : 
                isProcessing ? 'bg-yellow-500 animate-pulse' : 
                isSpeaking ? 'bg-blue-500 animate-pulse' : 'bg-gray-400'
              }`} />
              <h3 className="font-semibold">Assistente de Voz</h3>
              <Brain className="w-4 h-4 text-primary" />
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setIsExpanded(false)}
            >
              <X className="w-4 h-4" />
            </Button>
          </div>

          {/* Status atual */}
          <div className="p-4 border-b bg-muted/30">
            {isListening && (
              <div className="flex items-center space-x-2 text-red-600">
                <Mic className="w-4 h-4 animate-pulse" />
                <span className="text-sm">Escutando...</span>
              </div>
            )}
            
            {isProcessing && (
              <div className="flex items-center space-x-2 text-yellow-600">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Processando...</span>
              </div>
            )}
            
            {isSpeaking && (
              <div className="flex items-center space-x-2 text-blue-600">
                <Volume2 className="w-4 h-4 animate-pulse" />
                <span className="text-sm">Falando...</span>
              </div>
            )}
            
            {!isListening && !isProcessing && !isSpeaking && (
              <div className="flex items-center space-x-2 text-muted-foreground">
                <MessageSquare className="w-4 h-4" />
                <span className="text-sm">Pronto para ouvir</span>
              </div>
            )}
          </div>

          {/* Transcrição atual */}
          {transcript && (
            <div className="p-4 border-b">
              <p className="text-sm text-muted-foreground mb-1">Você disse:</p>
              <p className="text-sm font-medium">{transcript}</p>
            </div>
          )}

          {/* Conversa */}
          <div className="max-h-60 overflow-y-auto p-4 space-y-3">
            {conversation.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg text-sm ${
                    message.type === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <p>{message.content}</p>
                  <p className="text-xs opacity-70 mt-1">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Controles */}
          <div className="p-4 border-t bg-background">
            <div className="flex items-center justify-center space-x-4">
              <Button
                variant={isListening ? "destructive" : "default"}
                size="lg"
                className="rounded-full w-12 h-12"
                onClick={toggleListening}
                disabled={isProcessing}
              >
                {isListening ? (
                  <MicOff className="w-5 h-5" />
                ) : (
                  <Mic className="w-5 h-5" />
                )}
              </Button>
              
              {isSpeaking && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={stopSpeaking}
                >
                  <VolumeX className="w-4 h-4 mr-2" />
                  Parar
                </Button>
              )}
              
              {conversation.length > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearConversation}
                >
                  Limpar
                </Button>
              )}
            </div>
            
            <div className="mt-3 text-center">
              <p className="text-xs text-muted-foreground">
                Toque no microfone e fale seu comando
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default VoiceAssistantAdvanced

