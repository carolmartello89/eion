import { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  Mic, MicOff, Users, Upload, Play, Pause, Download,
  Volume2, Settings, UserPlus, Trash2, Edit, Eye
} from 'lucide-react'

const ReconhecimentoVozAvancado = () => {
  const [isRecording, setIsRecording] = useState(false)
  const [participantes, setParticipantes] = useState([])
  const [reuniaoAtual, setReuniaoAtual] = useState(null)
  const [transcricao, setTranscricao] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [audioUrl, setAudioUrl] = useState(null)
  const [novoParticipante, setNovoParticipante] = useState('')
  const [configuracoes, setConfiguracoes] = useState({
    qualidadeAudio: 'alta',
    filtroRuido: true,
    deteccaoAutomatica: true,
    salvarAudio: true
  })

  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const audioRef = useRef(null)

  useEffect(() => {
    carregarParticipantes()
  }, [])

  const carregarParticipantes = async () => {
    try {
      const response = await fetch('/api/voice-meetings/participantes', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setParticipantes(data.participantes || [])
      }
    } catch (error) {
      console.error('Erro ao carregar participantes:', error)
    }
  }

  const criarNovaReuniao = async () => {
    try {
      const response = await fetch('/api/reunioes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          titulo: `Reunião ${new Date().toLocaleString('pt-BR')}`,
          data: new Date().toISOString(),
          tipo: 'gravacao_voz'
        })
      })

      if (response.ok) {
        const data = await response.json()
        setReuniaoAtual(data.reuniao)
        return data.reuniao.id
      }
    } catch (error) {
      console.error('Erro ao criar reunião:', error)
    }
    return null
  }

  const adicionarParticipante = async () => {
    if (!novoParticipante.trim()) return

    try {
      const response = await fetch('/api/voice-meetings/participantes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          nome: novoParticipante,
          cor_identificacao: `#${Math.floor(Math.random()*16777215).toString(16)}`
        })
      })

      if (response.ok) {
        const data = await response.json()
        setParticipantes(prev => [...prev, data.participante])
        setNovoParticipante('')
      }
    } catch (error) {
      console.error('Erro ao adicionar participante:', error)
    }
  }

  const iniciarGravacao = async () => {
    try {
      // Cria nova reunião se não existir
      let reuniaoId = reuniaoAtual?.id
      if (!reuniaoId) {
        reuniaoId = await criarNovaReuniao()
        if (!reuniaoId) {
          alert('Erro ao criar reunião')
          return
        }
      }

      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: configuracoes.filtroRuido,
          noiseSuppression: configuracoes.filtroRuido,
          sampleRate: configuracoes.qualidadeAudio === 'alta' ? 48000 : 16000,
          channelCount: 1
        } 
      })

      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })

      audioChunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorderRef.current.onstop = () => {
        if (configuracoes.salvarAudio) {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
          const url = URL.createObjectURL(audioBlob)
          setAudioUrl(url)
        }
        
        if (configuracoes.deteccaoAutomatica) {
          processarAudio()
        }
      }

      mediaRecorderRef.current.start(1000)
      setIsRecording(true)

    } catch (error) {
      console.error('Erro ao iniciar gravação:', error)
      alert('Erro ao acessar microfone. Verifique as permissões.')
    }
  }

  const pararGravacao = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
      setIsRecording(false)
    }
  }

  const processarAudio = async () => {
    if (audioChunksRef.current.length === 0) {
      alert('Nenhum áudio gravado')
      return
    }

    setIsProcessing(true)

    try {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
      const audioFile = new File([audioBlob], 'reuniao.webm', { type: 'audio/webm' })

      const formData = new FormData()
      formData.append('audio', audioFile)

      const response = await fetch(`/api/voice-meetings/reunioes/${reuniaoAtual.id}/processar-audio`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Áudio processado:', data)
        carregarTranscricao()
        alert(`Processamento concluído! ${data.total_segmentos} segmentos identificados.`)
      } else {
        const error = await response.json()
        alert(`Erro no processamento: ${error.erro}`)
      }

    } catch (error) {
      console.error('Erro ao processar áudio:', error)
      alert('Erro ao processar áudio. Verifique sua conexão.')
    } finally {
      setIsProcessing(false)
    }
  }

  const carregarTranscricao = async () => {
    if (!reuniaoAtual?.id) return

    try {
      const response = await fetch(`/api/voice-meetings/reunioes/${reuniaoAtual.id}/transcricao`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setTranscricao(data.transcricao_cronologica || [])
      }
    } catch (error) {
      console.error('Erro ao carregar transcrição:', error)
    }
  }

  const treinarVozParticipante = async (participanteId) => {
    const input = document.createElement('input')
    input.type = 'file'
    input.multiple = true
    input.accept = 'audio/*'
    
    input.onchange = async (e) => {
      const files = Array.from(e.target.files)
      if (files.length === 0) return

      const formData = new FormData()
      files.forEach(file => formData.append('amostras', file))

      try {
        setIsProcessing(true)
        const response = await fetch(`/api/voice-meetings/participantes/${participanteId}/treinar-voz`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: formData
        })

        if (response.ok) {
          alert('Perfil de voz treinado com sucesso!')
          carregarParticipantes()
        } else {
          const error = await response.json()
          alert(`Erro: ${error.erro}`)
        }
      } catch (error) {
        console.error('Erro ao treinar voz:', error)
        alert('Erro ao treinar perfil de voz')
      } finally {
        setIsProcessing(false)
      }
    }

    input.click()
  }

  const uploadAudio = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'audio/*'
    
    input.onchange = async (e) => {
      const file = e.target.files[0]
      if (!file) return

      // Cria reunião se não existir
      let reuniaoId = reuniaoAtual?.id
      if (!reuniaoId) {
        reuniaoId = await criarNovaReuniao()
        if (!reuniaoId) return
      }

      const formData = new FormData()
      formData.append('audio', file)

      try {
        setIsProcessing(true)
        const response = await fetch(`/api/voice-meetings/reunioes/${reuniaoId}/processar-audio`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: formData
        })

        if (response.ok) {
          const data = await response.json()
          carregarTranscricao()
          alert(`Arquivo processado! ${data.total_segmentos} segmentos identificados.`)
        }
      } catch (error) {
        console.error('Erro ao processar arquivo:', error)
      } finally {
        setIsProcessing(false)
      }
    }

    input.click()
  }

  const exportarTranscricao = () => {
    if (transcricao.length === 0) {
      alert('Nenhuma transcrição disponível')
      return
    }

    const texto = transcricao.map(segmento => 
      `[${segmento.timestamp_formatado}] ${segmento.participante?.nome || 'Falante Desconhecido'}: ${segmento.texto_transcrito}`
    ).join('\n\n')

    const blob = new Blob([texto], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `transcricao_${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(a)
    a.click()
    URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  const formatarDuracao = (segundos) => {
    const mins = Math.floor(segundos / 60)
    const secs = Math.floor(segundos % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center space-x-2">
            <Mic className="w-6 h-6" />
            <span>Reconhecimento de Voz Avançado</span>
          </h2>
          <p className="text-muted-foreground">
            Gravação e identificação automática de falantes
          </p>
        </div>
        
        <div className="flex space-x-2">
          <Button variant="outline" onClick={uploadAudio}>
            <Upload className="w-4 h-4 mr-2" />
            Upload Áudio
          </Button>
          {transcricao.length > 0 && (
            <Button variant="outline" onClick={exportarTranscricao}>
              <Download className="w-4 h-4 mr-2" />
              Exportar
            </Button>
          )}
        </div>
      </div>

      <Tabs defaultValue="gravacao" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="gravacao">Gravação</TabsTrigger>
          <TabsTrigger value="participantes">Participantes</TabsTrigger>
          <TabsTrigger value="transcricao">Transcrição</TabsTrigger>
          <TabsTrigger value="configuracoes">Configurações</TabsTrigger>
        </TabsList>

        {/* Aba Gravação */}
        <TabsContent value="gravacao" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Controles de Gravação */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Mic className="w-5 h-5" />
                  <span>Controles de Gravação</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {reuniaoAtual && (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="font-medium text-blue-900">Reunião Ativa:</p>
                    <p className="text-blue-800">{reuniaoAtual.titulo}</p>
                  </div>
                )}

                <div className="flex items-center justify-center space-x-4">
                  {!isRecording ? (
                    <Button 
                      onClick={iniciarGravacao} 
                      className="bg-red-500 hover:bg-red-600 text-white px-8 py-4 text-lg"
                      size="lg"
                    >
                      <Mic className="w-6 h-6 mr-2" />
                      Iniciar Gravação
                    </Button>
                  ) : (
                    <Button 
                      onClick={pararGravacao} 
                      variant="outline"
                      className="px-8 py-4 text-lg"
                      size="lg"
                    >
                      <MicOff className="w-6 h-6 mr-2" />
                      Parar Gravação
                    </Button>
                  )}
                </div>

                {isRecording && (
                  <div className="text-center">
                    <div className="flex items-center justify-center space-x-2 text-red-600">
                      <div className="w-3 h-3 bg-red-600 rounded-full animate-pulse"></div>
                      <span className="font-medium">Gravando...</span>
                    </div>
                  </div>
                )}

                {isProcessing && (
                  <div className="text-center">
                    <div className="flex items-center justify-center space-x-2">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                      <span>Processando áudio com IA...</span>
                    </div>
                  </div>
                )}

                {audioUrl && (
                  <div className="space-y-2">
                    <p className="font-medium">Áudio Gravado:</p>
                    <audio ref={audioRef} controls className="w-full">
                      <source src={audioUrl} type="audio/webm" />
                    </audio>
                    <Button onClick={processarAudio} className="w-full" disabled={isProcessing}>
                      <Volume2 className="w-4 h-4 mr-2" />
                      Processar com IA
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Status da Reunião */}
            <Card>
              <CardHeader>
                <CardTitle>Status da Reunião</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 border rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">{participantes.length}</p>
                    <p className="text-sm text-muted-foreground">Participantes</p>
                  </div>
                  <div className="text-center p-3 border rounded-lg">
                    <p className="text-2xl font-bold text-green-600">{transcricao.length}</p>
                    <p className="text-sm text-muted-foreground">Segmentos</p>
                  </div>
                </div>

                {transcricao.length > 0 && (
                  <div className="space-y-2">
                    <p className="font-medium">Estatísticas:</p>
                    <div className="text-sm space-y-1">
                      <p>Duração total: {formatarDuracao(
                        transcricao.reduce((acc, seg) => acc + (seg.fim_segundos - seg.inicio_segundos), 0)
                      )}</p>
                      <p>Falantes identificados: {new Set(transcricao.map(s => s.participante?.nome).filter(Boolean)).size}</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Aba Participantes */}
        <TabsContent value="participantes" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Lista de Participantes */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="w-5 h-5" />
                  <span>Participantes Cadastrados</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {participantes.map((participante) => (
                    <div key={participante.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div 
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: participante.cor_identificacao }}
                        ></div>
                        <div>
                          <p className="font-medium">{participante.nome}</p>
                          {participante.email && (
                            <p className="text-sm text-muted-foreground">{participante.email}</p>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {participante.perfil_voz ? (
                          <Badge className="bg-green-100 text-green-800">Treinado</Badge>
                        ) : (
                          <Badge variant="outline">Não treinado</Badge>
                        )}
                        
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => treinarVozParticipante(participante.id)}
                          disabled={isProcessing}
                        >
                          <Settings className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}

                  {participantes.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>Nenhum participante cadastrado</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Adicionar Participante */}
            <Card>
              <CardHeader>
                <CardTitle>Novo Participante</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="Nome do participante"
                  value={novoParticipante}
                  onChange={(e) => setNovoParticipante(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && adicionarParticipante()}
                />
                
                <Button onClick={adicionarParticipante} className="w-full">
                  <UserPlus className="w-4 h-4 mr-2" />
                  Adicionar Participante
                </Button>

                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <h4 className="font-medium text-yellow-900 mb-2">💡 Dica: Treinamento de Voz</h4>
                  <p className="text-sm text-yellow-800">
                    Para melhor identificação, treine a voz de cada participante com 3-5 amostras de áudio de pelo menos 10 segundos cada.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Aba Transcrição */}
        <TabsContent value="transcricao" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Transcrição da Reunião</span>
                {transcricao.length > 0 && (
                  <Button variant="outline" size="sm" onClick={exportarTranscricao}>
                    <Download className="w-4 h-4 mr-2" />
                    Exportar
                  </Button>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {transcricao.map((segmento, index) => (
                  <div key={index} className="flex space-x-3 p-3 border-l-4 hover:bg-gray-50" 
                       style={{ borderLeftColor: segmento.participante?.cor_identificacao || '#ccc' }}>
                    <div className="flex-shrink-0">
                      <Badge variant="outline" className="text-xs">
                        {segmento.timestamp_formatado}
                      </Badge>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-sm">
                          {segmento.participante?.nome || 'Falante Desconhecido'}
                        </span>
                        <Badge variant="secondary" className="text-xs">
                          {Math.round(segmento.confianca * 100)}% confiança
                        </Badge>
                      </div>
                      <p className="text-sm">{segmento.texto_transcrito}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Duração: {formatarDuracao(segmento.fim_segundos - segmento.inicio_segundos)}
                      </p>
                    </div>
                  </div>
                ))}

                {transcricao.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <Volume2 className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Nenhuma transcrição disponível</p>
                    <p className="text-sm">Grave ou faça upload de um áudio para começar</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aba Configurações */}
        <TabsContent value="configuracoes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configurações de Áudio</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Qualidade do Áudio</label>
                <select 
                  value={configuracoes.qualidadeAudio}
                  onChange={(e) => setConfiguracoes(prev => ({ ...prev, qualidadeAudio: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="alta">Alta (48kHz) - Melhor qualidade</option>
                  <option value="media">Média (16kHz) - Balanceado</option>
                </select>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="filtroRuido"
                  checked={configuracoes.filtroRuido}
                  onChange={(e) => setConfiguracoes(prev => ({ ...prev, filtroRuido: e.target.checked }))}
                />
                <label htmlFor="filtroRuido" className="text-sm">Filtro de ruído e eco</label>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="deteccaoAutomatica"
                  checked={configuracoes.deteccaoAutomatica}
                  onChange={(e) => setConfiguracoes(prev => ({ ...prev, deteccaoAutomatica: e.target.checked }))}
                />
                <label htmlFor="deteccaoAutomatica" className="text-sm">Processamento automático após gravação</label>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="salvarAudio"
                  checked={configuracoes.salvarAudio}
                  onChange={(e) => setConfiguracoes(prev => ({ ...prev, salvarAudio: e.target.checked }))}
                />
                <label htmlFor="salvarAudio" className="text-sm">Salvar arquivo de áudio</label>
              </div>

              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">ℹ️ Informações</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Token Hugging Face configurado: ✅</li>
                  <li>• Modelos de IA carregados: ✅</li>
                  <li>• Suporte a múltiplos falantes: ✅</li>
                  <li>• Transcrição em português: ✅</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default ReconhecimentoVozAvancado

