import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  Mic, 
  Square, 
  Play, 
  Pause, 
  Download,
  Trash2,
  FileAudio,
  Clock,
  Users,
  MessageSquare,
  Brain,
  Loader2
} from 'lucide-react'

const MeetingRecorder = ({ meetingId, participants = [], onRecordingComplete }) => {
  const [isRecording, setIsRecording] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [audioBlob, setAudioBlob] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [summary, setSummary] = useState('')
  const [actionItems, setActionItems] = useState([])
  
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const timerRef = useRef(null)
  const streamRef = useRef(null)

  // Cleanup ao desmontar componente
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  // Inicia gravação
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      })
      
      streamRef.current = stream
      audioChunksRef.current = []
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorderRef.current = mediaRecorder
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: 'audio/webm;codecs=opus' 
        })
        setAudioBlob(audioBlob)
        
        // Para o stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
        }
      }
      
      mediaRecorder.start(1000) // Coleta dados a cada segundo
      setIsRecording(true)
      setIsPaused(false)
      
      // Inicia timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
      
    } catch (error) {
      console.error('Erro ao iniciar gravação:', error)
      alert('Erro ao acessar microfone. Verifique as permissões.')
    }
  }

  // Para gravação
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setIsPaused(false)
      
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }

  // Pausa/resume gravação
  const togglePause = () => {
    if (mediaRecorderRef.current) {
      if (isPaused) {
        mediaRecorderRef.current.resume()
        timerRef.current = setInterval(() => {
          setRecordingTime(prev => prev + 1)
        }, 1000)
      } else {
        mediaRecorderRef.current.pause()
        if (timerRef.current) {
          clearInterval(timerRef.current)
        }
      }
      setIsPaused(!isPaused)
    }
  }

  // Processa áudio com IA
  const processAudio = async () => {
    if (!audioBlob) return
    
    setIsProcessing(true)
    
    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')
      formData.append('meetingId', meetingId)
      formData.append('participants', JSON.stringify(participants))
      
      const response = await fetch('/api/meetings/process-recording', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: formData
      })
      
      if (response.ok) {
        const data = await response.json()
        setTranscript(data.transcript || '')
        setSummary(data.summary || '')
        setActionItems(data.actionItems || [])
        
        if (onRecordingComplete) {
          onRecordingComplete({
            audioBlob,
            transcript: data.transcript,
            summary: data.summary,
            actionItems: data.actionItems,
            duration: recordingTime
          })
        }
      } else {
        throw new Error('Erro ao processar áudio')
      }
      
    } catch (error) {
      console.error('Erro ao processar áudio:', error)
      alert('Erro ao processar gravação. Tente novamente.')
    } finally {
      setIsProcessing(false)
    }
  }

  // Download do áudio
  const downloadAudio = () => {
    if (audioBlob) {
      const url = URL.createObjectURL(audioBlob)
      const a = document.createElement('a')
      a.href = url
      a.download = `reuniao_${meetingId}_${new Date().toISOString().split('T')[0]}.webm`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
  }

  // Limpa gravação
  const clearRecording = () => {
    setAudioBlob(null)
    setTranscript('')
    setSummary('')
    setActionItems([])
    setRecordingTime(0)
  }

  // Formata tempo
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-4">
      {/* Controles de gravação */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileAudio className="w-5 h-5" />
            <span>Gravação da Reunião</span>
            {isRecording && (
              <Badge variant="destructive" className="animate-pulse">
                REC
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Status da gravação */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4" />
                <span className="font-mono text-lg">{formatTime(recordingTime)}</span>
              </div>
              
              {participants.length > 0 && (
                <div className="flex items-center space-x-2">
                  <Users className="w-4 h-4" />
                  <span className="text-sm">{participants.length} participantes</span>
                </div>
              )}
            </div>
            
            {isRecording && (
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                <span className="text-sm text-red-600">
                  {isPaused ? 'Pausado' : 'Gravando'}
                </span>
              </div>
            )}
          </div>

          {/* Controles */}
          <div className="flex items-center justify-center space-x-4">
            {!isRecording && !audioBlob && (
              <Button onClick={startRecording} className="flex items-center space-x-2">
                <Mic className="w-4 h-4" />
                <span>Iniciar Gravação</span>
              </Button>
            )}
            
            {isRecording && (
              <>
                <Button 
                  variant="outline" 
                  onClick={togglePause}
                  className="flex items-center space-x-2"
                >
                  {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                  <span>{isPaused ? 'Continuar' : 'Pausar'}</span>
                </Button>
                
                <Button 
                  variant="destructive" 
                  onClick={stopRecording}
                  className="flex items-center space-x-2"
                >
                  <Square className="w-4 h-4" />
                  <span>Parar</span>
                </Button>
              </>
            )}
            
            {audioBlob && !isProcessing && (
              <>
                <Button 
                  onClick={processAudio}
                  className="flex items-center space-x-2"
                >
                  <Brain className="w-4 h-4" />
                  <span>Processar com IA</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  onClick={downloadAudio}
                  className="flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  onClick={clearRecording}
                  className="flex items-center space-x-2"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Limpar</span>
                </Button>
              </>
            )}
            
            {isProcessing && (
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processando com IA...</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Resultados do processamento */}
      {(transcript || summary || actionItems.length > 0) && (
        <div className="space-y-4">
          {/* Transcrição */}
          {transcript && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <MessageSquare className="w-5 h-5" />
                  <span>Transcrição</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="max-h-40 overflow-y-auto p-3 bg-muted/30 rounded-lg">
                  <p className="text-sm whitespace-pre-wrap">{transcript}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Resumo */}
          {summary && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="w-5 h-5" />
                  <span>Resumo da Reunião</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm">{summary}</p>
              </CardContent>
            </Card>
          )}

          {/* Ações e tarefas */}
          {actionItems.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Ações e Tarefas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {actionItems.map((item, index) => (
                    <div key={index} className="flex items-start space-x-2 p-2 bg-muted/30 rounded">
                      <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="text-sm font-medium">{item.task}</p>
                        {item.assignee && (
                          <p className="text-xs text-muted-foreground">
                            Responsável: {item.assignee}
                          </p>
                        )}
                        {item.deadline && (
                          <p className="text-xs text-muted-foreground">
                            Prazo: {item.deadline}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

export default MeetingRecorder

