import { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Slider } from '@/components/ui/slider.jsx'
import { 
  User, Mic, Brain, Shield, Volume2, 
  ArrowRight, ArrowLeft, Check, Upload,
  Sparkles, Heart, Zap, Star
} from 'lucide-react'

const SetupWizard = ({ user, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(1)
  const [isRecording, setIsRecording] = useState(false)
  const [recordedSamples, setRecordedSamples] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)
  
  // Dados do wizard
  const [setupData, setSetupData] = useState({
    // Passo 1: Personalização
    preferredName: '',
    iaPersonality: 'friendly', // friendly, professional, casual, witty
    voiceGender: 'female', // female, male
    
    // Passo 2: Configurações de Voz
    voiceAuthEnabled: true,
    alwaysListening: true,
    wakeSensitivity: 0.8,
    confidenceThreshold: 0.75,
    
    // Passo 3: Treinamento de Voz
    voiceSamples: [],
    
    // Passo 4: Preferências de Interação
    responseStyle: 'detailed', // brief, detailed, conversational
    useRealInfo: true,
    proactiveMode: true,
    
    // Passo 5: Configurações de Segurança
    sessionTimeout: 5, // minutos
    maxFailedAttempts: 3,
    requireVoiceAuth: true
  })

  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  const steps = [
    {
      id: 1,
      title: 'Personalização',
      description: 'Como você gostaria que a IA te chame?',
      icon: User
    },
    {
      id: 2,
      title: 'Configurações de Voz',
      description: 'Configure como a IA deve responder',
      icon: Volume2
    },
    {
      id: 3,
      title: 'Treinamento de Voz',
      description: 'Ensine a IA a reconhecer sua voz',
      icon: Mic
    },
    {
      id: 4,
      title: 'Estilo de Interação',
      description: 'Personalize como a IA interage',
      icon: Brain
    },
    {
      id: 5,
      title: 'Segurança',
      description: 'Configure proteções e privacidade',
      icon: Shield
    }
  ]

  const personalities = [
    { id: 'friendly', name: 'Amigável', description: 'Calorosa e acolhedora', emoji: '😊' },
    { id: 'professional', name: 'Profissional', description: 'Formal e eficiente', emoji: '💼' },
    { id: 'casual', name: 'Descontraída', description: 'Relaxada e informal', emoji: '😎' },
    { id: 'witty', name: 'Espirituosa', description: 'Inteligente e divertida', emoji: '🤓' }
  ]

  const responseStyles = [
    { id: 'brief', name: 'Concisa', description: 'Respostas curtas e diretas' },
    { id: 'detailed', name: 'Detalhada', description: 'Explicações completas' },
    { id: 'conversational', name: 'Conversacional', description: 'Como uma conversa natural' }
  ]

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)
      audioChunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        const newSample = {
          id: Date.now(),
          blob: audioBlob,
          duration: Date.now() - recordingStartTime
        }
        
        setRecordedSamples(prev => [...prev, newSample])
        setSetupData(prev => ({
          ...prev,
          voiceSamples: [...prev.voiceSamples, audioBlob]
        }))
      }

      const recordingStartTime = Date.now()
      mediaRecorderRef.current.start()
      setIsRecording(true)

      // Para automaticamente após 10 segundos
      setTimeout(() => {
        if (isRecording) {
          stopRecording()
        }
      }, 10000)

    } catch (error) {
      console.error('Erro ao iniciar gravação:', error)
      alert('Erro ao acessar microfone. Verifique as permissões.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
      setIsRecording(false)
    }
  }

  const removeRecording = (sampleId) => {
    setRecordedSamples(prev => prev.filter(sample => sample.id !== sampleId))
    // Também remove do setupData
    const sampleIndex = recordedSamples.findIndex(s => s.id === sampleId)
    if (sampleIndex >= 0) {
      setSetupData(prev => ({
        ...prev,
        voiceSamples: prev.voiceSamples.filter((_, index) => index !== sampleIndex)
      }))
    }
  }

  const nextStep = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const completeSetup = async () => {
    setIsProcessing(true)
    
    try {
      // Salva configurações do perfil
      const profileResponse = await fetch('/api/voice-auth/voice-profile/setup-wizard', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          preferred_name: setupData.preferredName,
          voice_activation_enabled: setupData.alwaysListening,
          confidence_threshold: setupData.confidenceThreshold,
          wake_word_sensitivity: setupData.wakeSensitivity,
          voice_auth_enabled: setupData.voiceAuthEnabled
        })
      })

      if (!profileResponse.ok) {
        throw new Error('Erro ao salvar perfil')
      }

      // Treina modelo de voz se há amostras
      if (setupData.voiceSamples.length >= 3) {
        const formData = new FormData()
        setupData.voiceSamples.forEach((sample, index) => {
          formData.append('audio_samples', sample, `sample_${index}.wav`)
        })

        const trainingResponse = await fetch('/api/voice-auth/voice-profile/train', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: formData
        })

        if (!trainingResponse.ok) {
          console.warn('Aviso: Treinamento de voz falhou, mas configuração foi salva')
        }
      }

      // Salva preferências de IA
      await fetch('/api/assistente/configurar-personalidade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          personality: setupData.iaPersonality,
          response_style: setupData.responseStyle,
          voice_gender: setupData.voiceGender,
          use_real_info: setupData.useRealInfo,
          proactive_mode: setupData.proactiveMode
        })
      })

      // Marca setup como completo
      localStorage.setItem('setup_completed', 'true')
      
      if (onComplete) {
        onComplete(setupData)
      }

    } catch (error) {
      console.error('Erro ao completar setup:', error)
      alert('Erro ao salvar configurações. Tente novamente.')
    } finally {
      setIsProcessing(false)
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Sparkles className="w-16 h-16 mx-auto text-blue-500 mb-4" />
              <h2 className="text-2xl font-bold mb-2">Bem-vindo à sua IA Pessoal!</h2>
              <p className="text-muted-foreground">Vamos personalizar sua experiência</p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Como você gostaria que eu te chame?</label>
                <Input
                  placeholder="Ex: João, Maria, Dr. Silva..."
                  value={setupData.preferredName}
                  onChange={(e) => setSetupData(prev => ({ ...prev, preferredName: e.target.value }))}
                  className="text-lg"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Este será o nome que usarei para me dirigir a você
                </p>
              </div>

              <div>
                <label className="text-sm font-medium mb-3 block">Que personalidade você prefere?</label>
                <div className="grid grid-cols-2 gap-3">
                  {personalities.map((personality) => (
                    <button
                      key={personality.id}
                      onClick={() => setSetupData(prev => ({ ...prev, iaPersonality: personality.id }))}
                      className={`p-4 border rounded-lg text-left transition-all ${
                        setupData.iaPersonality === personality.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="text-2xl mb-2">{personality.emoji}</div>
                      <div className="font-medium">{personality.name}</div>
                      <div className="text-sm text-muted-foreground">{personality.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-3 block">Voz preferida</label>
                <div className="flex space-x-3">
                  <button
                    onClick={() => setSetupData(prev => ({ ...prev, voiceGender: 'female' }))}
                    className={`flex-1 p-3 border rounded-lg ${
                      setupData.voiceGender === 'female'
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200'
                    }`}
                  >
                    Feminina
                  </button>
                  <button
                    onClick={() => setSetupData(prev => ({ ...prev, voiceGender: 'male' }))}
                    className={`flex-1 p-3 border rounded-lg ${
                      setupData.voiceGender === 'male'
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200'
                    }`}
                  >
                    Masculina
                  </button>
                </div>
              </div>
            </div>
          </div>
        )

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Volume2 className="w-16 h-16 mx-auto text-blue-500 mb-4" />
              <h2 className="text-2xl font-bold mb-2">Configurações de Voz</h2>
              <p className="text-muted-foreground">Configure como a IA deve responder à sua voz</p>
            </div>

            <div className="space-y-6">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h3 className="font-medium">Sempre Escutando</h3>
                  <p className="text-sm text-muted-foreground">IA fica sempre ativa, esperando você dizer "IA"</p>
                </div>
                <button
                  onClick={() => setSetupData(prev => ({ ...prev, alwaysListening: !prev.alwaysListening }))}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    setupData.alwaysListening ? 'bg-blue-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    setupData.alwaysListening ? 'translate-x-6' : 'translate-x-0.5'
                  }`} />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h3 className="font-medium">Autenticação por Voz</h3>
                  <p className="text-sm text-muted-foreground">Reconhece sua voz para maior segurança</p>
                </div>
                <button
                  onClick={() => setSetupData(prev => ({ ...prev, voiceAuthEnabled: !prev.voiceAuthEnabled }))}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    setupData.voiceAuthEnabled ? 'bg-blue-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    setupData.voiceAuthEnabled ? 'translate-x-6' : 'translate-x-0.5'
                  }`} />
                </button>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-medium">Sensibilidade da Palavra-Chave "IA"</label>
                <Slider
                  value={[setupData.wakeSensitivity]}
                  onValueChange={(value) => setSetupData(prev => ({ ...prev, wakeSensitivity: value[0] }))}
                  max={1}
                  min={0.1}
                  step={0.1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Menos sensível</span>
                  <span>{Math.round(setupData.wakeSensitivity * 100)}%</span>
                  <span>Mais sensível</span>
                </div>
              </div>

              {setupData.voiceAuthEnabled && (
                <div className="space-y-3">
                  <label className="text-sm font-medium">Precisão do Reconhecimento de Voz</label>
                  <Slider
                    value={[setupData.confidenceThreshold]}
                    onValueChange={(value) => setSetupData(prev => ({ ...prev, confidenceThreshold: value[0] }))}
                    max={0.95}
                    min={0.5}
                    step={0.05}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Mais permissivo</span>
                    <span>{Math.round(setupData.confidenceThreshold * 100)}%</span>
                    <span>Mais rigoroso</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Mic className="w-16 h-16 mx-auto text-blue-500 mb-4" />
              <h2 className="text-2xl font-bold mb-2">Treinamento de Voz</h2>
              <p className="text-muted-foreground">
                {setupData.voiceAuthEnabled 
                  ? 'Grave 3-5 amostras da sua voz para que eu possa te reconhecer'
                  : 'Treinamento de voz desabilitado'
                }
              </p>
            </div>

            {setupData.voiceAuthEnabled ? (
              <div className="space-y-4">
                <div className="text-center">
                  <Button
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`w-32 h-32 rounded-full text-white ${
                      isRecording ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'
                    }`}
                  >
                    <Mic className="w-8 h-8" />
                  </Button>
                  <p className="mt-4 text-sm">
                    {isRecording ? 'Gravando... (máx. 10 segundos)' : 'Toque para gravar'}
                  </p>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h4 className="font-medium text-yellow-900 mb-2">💡 Dicas para melhor reconhecimento:</h4>
                  <ul className="text-sm text-yellow-800 space-y-1">
                    <li>• Fale naturalmente, como falaria comigo no dia a dia</li>
                    <li>• Grave em ambiente silencioso</li>
                    <li>• Diga frases diferentes em cada gravação</li>
                    <li>• Exemplo: "Oi IA, como você está hoje?"</li>
                  </ul>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">Amostras Gravadas ({recordedSamples.length}/5)</h4>
                  {recordedSamples.map((sample, index) => (
                    <div key={sample.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <Badge variant="outline">#{index + 1}</Badge>
                        <span className="text-sm">
                          Amostra {index + 1} ({Math.round(sample.duration / 1000)}s)
                        </span>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => removeRecording(sample.id)}
                      >
                        Remover
                      </Button>
                    </div>
                  ))}
                </div>

                {recordedSamples.length > 0 && recordedSamples.length < 3 && (
                  <div className="text-center text-sm text-muted-foreground">
                    Grave pelo menos {3 - recordedSamples.length} amostras adicionais
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground mb-4">
                  Autenticação por voz está desabilitada. Você pode pular esta etapa.
                </p>
                <Button variant="outline" onClick={() => setCurrentStep(2)}>
                  Voltar e Habilitar
                </Button>
              </div>
            )}
          </div>
        )

      case 4:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Brain className="w-16 h-16 mx-auto text-blue-500 mb-4" />
              <h2 className="text-2xl font-bold mb-2">Estilo de Interação</h2>
              <p className="text-muted-foreground">Como você prefere que eu me comunique com você?</p>
            </div>

            <div className="space-y-6">
              <div>
                <label className="text-sm font-medium mb-3 block">Estilo de Resposta</label>
                <div className="space-y-2">
                  {responseStyles.map((style) => (
                    <button
                      key={style.id}
                      onClick={() => setSetupData(prev => ({ ...prev, responseStyle: style.id }))}
                      className={`w-full p-4 border rounded-lg text-left transition-all ${
                        setupData.responseStyle === style.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-medium">{style.name}</div>
                      <div className="text-sm text-muted-foreground">{style.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h3 className="font-medium">Usar Informações Reais</h3>
                  <p className="text-sm text-muted-foreground">Busco informações verdadeiras na internet</p>
                </div>
                <button
                  onClick={() => setSetupData(prev => ({ ...prev, useRealInfo: !prev.useRealInfo }))}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    setupData.useRealInfo ? 'bg-blue-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    setupData.useRealInfo ? 'translate-x-6' : 'translate-x-0.5'
                  }`} />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h3 className="font-medium">Modo Proativo</h3>
                  <p className="text-sm text-muted-foreground">Faço sugestões e lembro de tarefas importantes</p>
                </div>
                <button
                  onClick={() => setSetupData(prev => ({ ...prev, proactiveMode: !prev.proactiveMode }))}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    setupData.proactiveMode ? 'bg-blue-500' : 'bg-gray-300'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    setupData.proactiveMode ? 'translate-x-6' : 'translate-x-0.5'
                  }`} />
                </button>
              </div>
            </div>
          </div>
        )

      case 5:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Shield className="w-16 h-16 mx-auto text-blue-500 mb-4" />
              <h2 className="text-2xl font-bold mb-2">Configurações de Segurança</h2>
              <p className="text-muted-foreground">Defina como proteger sua privacidade</p>
            </div>

            <div className="space-y-6">
              <div className="space-y-3">
                <label className="text-sm font-medium">Timeout da Sessão (minutos)</label>
                <Slider
                  value={[setupData.sessionTimeout]}
                  onValueChange={(value) => setSetupData(prev => ({ ...prev, sessionTimeout: value[0] }))}
                  max={30}
                  min={1}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>1 min</span>
                  <span>{setupData.sessionTimeout} minutos</span>
                  <span>30 min</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  Tempo até a sessão expirar por inatividade
                </p>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-medium">Máximo de Tentativas de Voz Falhadas</label>
                <Slider
                  value={[setupData.maxFailedAttempts]}
                  onValueChange={(value) => setSetupData(prev => ({ ...prev, maxFailedAttempts: value[0] }))}
                  max={10}
                  min={1}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>1</span>
                  <span>{setupData.maxFailedAttempts} tentativas</span>
                  <span>10</span>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">🔒 Resumo de Segurança:</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Dados criptografados localmente</li>
                  <li>• Sessões com timeout automático</li>
                  <li>• Autenticação por voz opcional</li>
                  <li>• Logs de auditoria mantidos</li>
                </ul>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-medium text-green-900 mb-2">✨ Configuração Completa!</h4>
                <p className="text-sm text-green-800">
                  Sua IA está pronta para uso com as seguintes configurações:
                </p>
                <ul className="text-sm text-green-800 mt-2 space-y-1">
                  <li>• Nome: {setupData.preferredName || 'Não definido'}</li>
                  <li>• Personalidade: {personalities.find(p => p.id === setupData.iaPersonality)?.name}</li>
                  <li>• Voz: {setupData.voiceGender === 'female' ? 'Feminina' : 'Masculina'}</li>
                  <li>• Sempre escutando: {setupData.alwaysListening ? 'Sim' : 'Não'}</li>
                  <li>• Autenticação por voz: {setupData.voiceAuthEnabled ? 'Sim' : 'Não'}</li>
                  <li>• Amostras de voz: {recordedSamples.length}</li>
                </ul>
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return setupData.preferredName.trim().length > 0
      case 2:
        return true
      case 3:
        return !setupData.voiceAuthEnabled || recordedSamples.length >= 3
      case 4:
        return true
      case 5:
        return true
      default:
        return false
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl shadow-2xl">
        <CardHeader className="text-center">
          <div className="flex justify-center space-x-2 mb-4">
            {steps.map((step) => (
              <div key={step.id} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step.id === currentStep 
                    ? 'bg-blue-500 text-white' 
                    : step.id < currentStep 
                      ? 'bg-green-500 text-white' 
                      : 'bg-gray-200 text-gray-600'
                }`}>
                  {step.id < currentStep ? <Check className="w-4 h-4" /> : step.id}
                </div>
                {step.id < steps.length && (
                  <div className={`w-8 h-0.5 ${
                    step.id < currentStep ? 'bg-green-500' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
          
          <CardTitle className="text-xl">
            {steps.find(s => s.id === currentStep)?.title}
          </CardTitle>
          <p className="text-muted-foreground">
            {steps.find(s => s.id === currentStep)?.description}
          </p>
        </CardHeader>

        <CardContent className="space-y-6">
          {renderStep()}

          {/* Navegação */}
          <div className="flex justify-between pt-6 border-t">
            <Button
              variant="outline"
              onClick={prevStep}
              disabled={currentStep === 1}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Anterior</span>
            </Button>

            {currentStep === steps.length ? (
              <Button
                onClick={completeSetup}
                disabled={!canProceed() || isProcessing}
                className="flex items-center space-x-2 bg-green-600 hover:bg-green-700"
              >
                {isProcessing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    <span>Configurando...</span>
                  </>
                ) : (
                  <>
                    <Check className="w-4 h-4" />
                    <span>Finalizar</span>
                  </>
                )}
              </Button>
            ) : (
              <Button
                onClick={nextStep}
                disabled={!canProceed()}
                className="flex items-center space-x-2"
              >
                <span>Próximo</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default SetupWizard

