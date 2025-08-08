import { useState, useEffect, useRef } from 'react'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX,
  MessageCircle,
  X
} from 'lucide-react'

const VoiceAssistant = ({ isListening, setIsListening }) => {
  const [isVisible, setIsVisible] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [response, setResponse] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [recognition, setRecognition] = useState(null)
  const [synthesis, setSynthesis] = useState(null)

  const responseRef = useRef(null)

  // Inicializa APIs de voz
  useEffect(() => {
    // Web Speech API - Reconhecimento de voz
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      const recognitionInstance = new SpeechRecognition()
      
      recognitionInstance.continuous = false
      recognitionInstance.interimResults = true
      recognitionInstance.lang = 'pt-BR'
      
      recognitionInstance.onstart = () => {
        console.log('Reconhecimento de voz iniciado')
      }
      
      recognitionInstance.onresult = (event) => {
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
      
      recognitionInstance.onerror = (event) => {
        console.error('Erro no reconhecimento de voz:', event.error)
        setIsListening(false)
        setResponse('Desculpe, não consegui entender. Tente novamente.')
      }
      
      recognitionInstance.onend = () => {
        setIsListening(false)
      }
      
      setRecognition(recognitionInstance)
    }

    // Web Speech API - Síntese de voz
    if ('speechSynthesis' in window) {
      setSynthesis(window.speechSynthesis)
    }
  }, [setIsListening])

  // Controla o reconhecimento de voz
  useEffect(() => {
    if (recognition) {
      if (isListening) {
        setIsVisible(true)
        setTranscript('')
        setResponse('')
        recognition.start()
      } else {
        recognition.stop()
      }
    }
  }, [isListening, recognition])

  // Processa comandos de voz
  const processVoiceCommand = async (command) => {
    setIsProcessing(true)
    
    try {
      // Simula processamento do comando
      // Aqui seria feita a chamada real para a API do backend
      const response = await fetch('/api/assistente/processar-comando', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ comando: command }),
      })
      
      if (response.ok) {
        const data = await response.json()
        setResponse(data.mensagem)
        
        // Executa ação específica baseada no tipo de resposta
        if (data.acao === 'ligacao' && data.dados?.url_ligacao) {
          window.location.href = data.dados.url_ligacao
        }
      } else {
        throw new Error('Erro na API')
      }
    } catch (error) {
      console.error('Erro ao processar comando:', error)
      
      // Fallback para comandos básicos sem API
      const fallbackResponse = processFallbackCommand(command)
      setResponse(fallbackResponse)
    }
    
    setIsProcessing(false)
  }

  // Processamento local de comandos básicos
  const processFallbackCommand = (command) => {
    const lowerCommand = command.toLowerCase()
    
    if (lowerCommand.includes('olá') || lowerCommand.includes('oi')) {
      return 'Olá! Como posso ajudar você hoje?'
    } else if (lowerCommand.includes('hora') || lowerCommand.includes('horas')) {
      const now = new Date()
      return `Agora são ${now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`
    } else if (lowerCommand.includes('data') || lowerCommand.includes('hoje')) {
      const today = new Date()
      return `Hoje é ${today.toLocaleDateString('pt-BR', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })}`
    } else if (lowerCommand.includes('próximos compromissos') || lowerCommand.includes('agenda')) {
      return 'Você tem 3 compromissos hoje: Reunião às 14:30, Consulta às 16:00 e Jantar às 19:30'
    } else if (lowerCommand.includes('ligar para')) {
      const nome = lowerCommand.replace('ligar para', '').trim()
      return `Procurando contato "${nome}" para iniciar ligação...`
    } else {
      return 'Comando não reconhecido. Tente: "Próximos compromissos", "Que horas são?" ou "Ligar para [nome]"'
    }
  }

  // Síntese de voz para resposta
  const speakResponse = (text) => {
    if (synthesis && text) {
      // Para qualquer fala anterior
      synthesis.cancel()
      
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'pt-BR'
      utterance.rate = 0.9
      utterance.pitch = 1
      
      utterance.onstart = () => setIsSpeaking(true)
      utterance.onend = () => setIsSpeaking(false)
      utterance.onerror = () => setIsSpeaking(false)
      
      synthesis.speak(utterance)
    }
  }

  // Para a síntese de voz
  const stopSpeaking = () => {
    if (synthesis) {
      synthesis.cancel()
      setIsSpeaking(false)
    }
  }

  // Fecha o assistente
  const closeAssistant = () => {
    setIsVisible(false)
    setIsListening(false)
    stopSpeaking()
    setTranscript('')
    setResponse('')
  }

  // Auto-scroll para a resposta
  useEffect(() => {
    if (response && responseRef.current) {
      responseRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [response])

  if (!isVisible) return null

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-end justify-center p-4">
      <Card className="w-full max-w-md max-h-[80vh] overflow-hidden">
        <CardContent className="p-0">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <MessageCircle className="w-4 h-4 text-primary-foreground" />
              </div>
              <div>
                <h3 className="font-semibold">Assistente de Voz</h3>
                <p className="text-xs text-muted-foreground">
                  {isListening ? 'Escutando...' : isProcessing ? 'Processando...' : 'Pronto'}
                </p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={closeAssistant}>
              <X className="w-4 h-4" />
            </Button>
          </div>

          {/* Conteúdo */}
          <div className="p-4 space-y-4 max-h-96 overflow-y-auto">
            {/* Status visual */}
            <div className="flex justify-center">
              <div className={`w-20 h-20 rounded-full flex items-center justify-center ${
                isListening ? 'bg-red-100 voice-recording' : 
                isProcessing ? 'bg-yellow-100 voice-pulse' : 
                'bg-primary/10'
              }`}>
                {isListening ? (
                  <Mic className="w-8 h-8 text-red-600" />
                ) : isProcessing ? (
                  <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Mic className="w-8 h-8 text-primary" />
                )}
              </div>
            </div>

            {/* Transcrição */}
            {transcript && (
              <div className="bg-muted/50 rounded-lg p-3">
                <p className="text-sm font-medium mb-1">Você disse:</p>
                <p className="text-sm">{transcript}</p>
              </div>
            )}

            {/* Resposta */}
            {response && (
              <div ref={responseRef} className="bg-primary/10 rounded-lg p-3">
                <div className="flex items-start justify-between mb-2">
                  <p className="text-sm font-medium">Assistente:</p>
                  <div className="flex space-x-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                      onClick={() => speakResponse(response)}
                      disabled={isSpeaking}
                    >
                      <Volume2 className="w-3 h-3" />
                    </Button>
                    {isSpeaking && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0"
                        onClick={stopSpeaking}
                      >
                        <VolumeX className="w-3 h-3" />
                      </Button>
                    )}
                  </div>
                </div>
                <p className="text-sm">{response}</p>
                {isSpeaking && (
                  <Badge variant="secondary" className="mt-2 text-xs">
                    Falando...
                  </Badge>
                )}
              </div>
            )}

            {/* Instruções */}
            {!transcript && !response && (
              <div className="text-center text-muted-foreground">
                <p className="text-sm mb-2">
                  {isListening ? 'Fale agora...' : 'Toque no microfone para começar'}
                </p>
                <div className="text-xs space-y-1">
                  <p>Comandos disponíveis:</p>
                  <p>• "Próximos compromissos"</p>
                  <p>• "Ligar para [nome]"</p>
                  <p>• "Que horas são?"</p>
                  <p>• "Agendar reunião"</p>
                </div>
              </div>
            )}
          </div>

          {/* Controles */}
          <div className="flex items-center justify-center space-x-4 p-4 border-t">
            <Button
              variant={isListening ? "destructive" : "default"}
              size="lg"
              className="rounded-full w-12 h-12"
              onClick={() => setIsListening(!isListening)}
              disabled={isProcessing}
            >
              {isListening ? (
                <MicOff className="w-5 h-5" />
              ) : (
                <Mic className="w-5 h-5" />
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default VoiceAssistant

