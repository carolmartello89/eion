import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { 
  Users, 
  Clock, 
  Plus, 
  Edit, 
  Trash2, 
  Play,
  Square,
  FileText,
  Mic,
  X,
  Search
} from 'lucide-react'

const Reunioes = () => {
  const [reunioes, setReunioes] = useState([])
  const [filtro, setFiltro] = useState('todas') // todas, hoje, agendadas, em_andamento, concluidas
  const [busca, setBusca] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [formData, setFormData] = useState({
    titulo: '',
    descricao: '',
    data_hora: '',
    participantes: ''
  })

  // Carrega reuniões
  useEffect(() => {
    loadReunioes()
  }, [])

  const loadReunioes = async () => {
    try {
      // Simula dados enquanto a API não está disponível
      const mockReunioes = [
        {
          id: '1',
          titulo: 'Reunião de planejamento',
          descricao: 'Planejamento do sprint da próxima semana',
          data_hora: new Date(Date.now() + 1 * 60 * 60 * 1000).toISOString(),
          participantes: '["João Silva", "Maria Santos", "Pedro Costa"]',
          status: 'agendada',
          audio_url: null,
          transcricao: null,
          resumo: null
        },
        {
          id: '2',
          titulo: 'Reunião com cliente',
          descricao: 'Apresentação do protótipo final',
          data_hora: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          participantes: '["Ana Oliveira", "Carlos Mendes"]',
          status: 'concluida',
          audio_url: '/audio/reuniao-2.mp3',
          transcricao: 'Discussão sobre os requisitos finais do projeto. Cliente aprovou o protótipo apresentado.',
          resumo: 'Reunião bem-sucedida. Cliente aprovou o protótipo e solicitou pequenos ajustes na interface.'
        },
        {
          id: '3',
          titulo: 'Daily Standup',
          descricao: 'Reunião diária da equipe',
          data_hora: new Date().toISOString(),
          participantes: '["Equipe Dev"]',
          status: 'em_andamento',
          audio_url: null,
          transcricao: null,
          resumo: null
        }
      ]
      
      setReunioes(mockReunioes)
    } catch (error) {
      console.error('Erro ao carregar reuniões:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      const participantesArray = formData.participantes
        .split(',')
        .map(p => p.trim())
        .filter(p => p.length > 0)
      
      if (editingId) {
        // Atualizar reunião existente
        setReunioes(prev => prev.map(reuniao => 
          reuniao.id === editingId 
            ? { ...reuniao, ...formData, participantes: JSON.stringify(participantesArray) }
            : reuniao
        ))
      } else {
        // Criar nova reunião
        const novaReuniao = {
          id: Date.now().toString(),
          ...formData,
          participantes: JSON.stringify(participantesArray),
          status: 'agendada',
          audio_url: null,
          transcricao: null,
          resumo: null,
          criado_em: new Date().toISOString()
        }
        setReunioes(prev => [...prev, novaReuniao])
      }
      
      resetForm()
    } catch (error) {
      console.error('Erro ao salvar reunião:', error)
    }
  }

  const resetForm = () => {
    setFormData({
      titulo: '',
      descricao: '',
      data_hora: '',
      participantes: ''
    })
    setShowForm(false)
    setEditingId(null)
  }

  const handleEdit = (reuniao) => {
    const participantes = JSON.parse(reuniao.participantes || '[]').join(', ')
    setFormData({
      titulo: reuniao.titulo,
      descricao: reuniao.descricao,
      data_hora: reuniao.data_hora.slice(0, 16),
      participantes: participantes
    })
    setEditingId(reuniao.id)
    setShowForm(true)
  }

  const handleDelete = async (id) => {
    if (confirm('Tem certeza que deseja excluir esta reunião?')) {
      setReunioes(prev => prev.filter(reuniao => reuniao.id !== id))
    }
  }

  const toggleStatus = async (id, newStatus) => {
    setReunioes(prev => prev.map(reuniao => 
      reuniao.id === id ? { ...reuniao, status: newStatus } : reuniao
    ))
  }

  const gerarResumo = async (id) => {
    const reuniao = reunioes.find(r => r.id === id)
    if (!reuniao || !reuniao.transcricao) {
      alert('Transcrição não disponível para gerar resumo')
      return
    }
    
    // Simula geração de resumo
    const resumoGerado = `Resumo da reunião "${reuniao.titulo}":\n\nPontos principais discutidos durante a reunião. Decisões tomadas e próximos passos definidos.`
    
    setReunioes(prev => prev.map(r => 
      r.id === id ? { ...r, resumo: resumoGerado } : r
    ))
  }

  const formatDateTime = (dateString) => {
    const date = new Date(dateString)
    return {
      date: date.toLocaleDateString('pt-BR'),
      time: date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
      relative: getRelativeTime(date)
    }
  }

  const getRelativeTime = (date) => {
    const now = new Date()
    const diff = date - now
    const hours = Math.floor(Math.abs(diff) / (1000 * 60 * 60))
    const days = Math.floor(hours / 24)
    
    if (diff > 0) {
      if (days > 0) return `em ${days} dia${days > 1 ? 's' : ''}`
      if (hours > 0) return `em ${hours} hora${hours > 1 ? 's' : ''}`
      return 'em breve'
    } else {
      if (days > 0) return `há ${days} dia${days > 1 ? 's' : ''}`
      if (hours > 0) return `há ${hours} hora${hours > 1 ? 's' : ''}`
      return 'agora'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'agendada': return 'bg-blue-100 text-blue-800'
      case 'em_andamento': return 'bg-green-100 text-green-800'
      case 'concluida': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusLabel = (status) => {
    switch (status) {
      case 'agendada': return 'Agendada'
      case 'em_andamento': return 'Em andamento'
      case 'concluida': return 'Concluída'
      default: return status
    }
  }

  const filteredReunioes = reunioes.filter(reuniao => {
    const matchesBusca = reuniao.titulo.toLowerCase().includes(busca.toLowerCase()) ||
                        reuniao.descricao.toLowerCase().includes(busca.toLowerCase())
    
    if (!matchesBusca) return false
    
    const now = new Date()
    const reuniaoDate = new Date(reuniao.data_hora)
    
    switch (filtro) {
      case 'hoje':
        return reuniaoDate.toDateString() === now.toDateString()
      case 'agendadas':
        return reuniao.status === 'agendada'
      case 'em_andamento':
        return reuniao.status === 'em_andamento'
      case 'concluidas':
        return reuniao.status === 'concluida'
      default:
        return true
    }
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Reuniões</h2>
          <p className="text-muted-foreground">Gerencie suas reuniões e gravações</p>
        </div>
        <Button onClick={() => setShowForm(true)} className="touch-target">
          <Plus className="w-4 h-4 mr-2" />
          Nova
        </Button>
      </div>

      {/* Filtros e busca */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Buscar reuniões..."
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <div className="flex space-x-2 overflow-x-auto pb-2">
          {[
            { key: 'todas', label: 'Todas' },
            { key: 'hoje', label: 'Hoje' },
            { key: 'agendadas', label: 'Agendadas' },
            { key: 'em_andamento', label: 'Em andamento' },
            { key: 'concluidas', label: 'Concluídas' }
          ].map(({ key, label }) => (
            <Button
              key={key}
              variant={filtro === key ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFiltro(key)}
              className="whitespace-nowrap"
            >
              {label}
            </Button>
          ))}
        </div>
      </div>

      {/* Lista de reuniões */}
      <div className="space-y-3">
        {filteredReunioes.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <Users className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">
                {busca ? 'Nenhuma reunião encontrada' : 'Nenhuma reunião agendada'}
              </p>
            </CardContent>
          </Card>
        ) : (
          filteredReunioes.map((reuniao) => {
            const dateTime = formatDateTime(reuniao.data_hora)
            const participantes = JSON.parse(reuniao.participantes || '[]')
            
            return (
              <Card key={reuniao.id}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-2">
                        <Users className="w-5 h-5 text-primary" />
                        <h3 className="font-semibold">{reuniao.titulo}</h3>
                        <Badge className={getStatusColor(reuniao.status)}>
                          {getStatusLabel(reuniao.status)}
                        </Badge>
                      </div>
                      
                      {reuniao.descricao && (
                        <p className="text-sm text-muted-foreground mb-2">
                          {reuniao.descricao}
                        </p>
                      )}
                      
                      <div className="flex items-center space-x-4 text-sm text-muted-foreground mb-2">
                        <div className="flex items-center space-x-1">
                          <Clock className="w-4 h-4" />
                          <span>{dateTime.date} às {dateTime.time}</span>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {dateTime.relative}
                        </Badge>
                      </div>
                      
                      {participantes.length > 0 && (
                        <div className="text-sm text-muted-foreground">
                          <span className="font-medium">Participantes:</span> {participantes.join(', ')}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      {reuniao.status === 'agendada' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleStatus(reuniao.id, 'em_andamento')}
                          className="touch-target text-green-600"
                        >
                          <Play className="w-4 h-4" />
                        </Button>
                      )}
                      
                      {reuniao.status === 'em_andamento' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleStatus(reuniao.id, 'concluida')}
                          className="touch-target text-red-600"
                        >
                          <Square className="w-4 h-4" />
                        </Button>
                      )}
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(reuniao)}
                        className="touch-target"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(reuniao.id)}
                        className="touch-target text-destructive"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  
                  {/* Recursos adicionais para reuniões concluídas */}
                  {reuniao.status === 'concluida' && (
                    <div className="border-t pt-3 mt-3 space-y-2">
                      {reuniao.transcricao && (
                        <div className="bg-muted/30 rounded-lg p-3">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium">Transcrição</span>
                            <Mic className="w-4 h-4 text-muted-foreground" />
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {reuniao.transcricao.length > 100 
                              ? `${reuniao.transcricao.substring(0, 100)}...` 
                              : reuniao.transcricao
                            }
                          </p>
                        </div>
                      )}
                      
                      {reuniao.resumo ? (
                        <div className="bg-primary/5 rounded-lg p-3">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium">Resumo</span>
                            <FileText className="w-4 h-4 text-primary" />
                          </div>
                          <p className="text-sm">
                            {reuniao.resumo.length > 150 
                              ? `${reuniao.resumo.substring(0, 150)}...` 
                              : reuniao.resumo
                            }
                          </p>
                        </div>
                      ) : reuniao.transcricao && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => gerarResumo(reuniao.id)}
                          className="w-full"
                        >
                          <FileText className="w-4 h-4 mr-2" />
                          Gerar Resumo
                        </Button>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })
        )}
      </div>

      {/* Modal de formulário */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-end justify-center p-4">
          <Card className="w-full max-w-md max-h-[90vh] overflow-hidden">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>
                    {editingId ? 'Editar Reunião' : 'Nova Reunião'}
                  </CardTitle>
                  <CardDescription>
                    Preencha os detalhes da reunião
                  </CardDescription>
                </div>
                <Button variant="ghost" size="sm" onClick={resetForm}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="overflow-y-auto">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Título *</label>
                  <Input
                    value={formData.titulo}
                    onChange={(e) => setFormData(prev => ({ ...prev, titulo: e.target.value }))}
                    placeholder="Ex: Reunião de planejamento"
                    required
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium">Descrição</label>
                  <Textarea
                    value={formData.descricao}
                    onChange={(e) => setFormData(prev => ({ ...prev, descricao: e.target.value }))}
                    placeholder="Objetivo e pauta da reunião..."
                    rows={3}
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium">Data e Hora *</label>
                  <Input
                    type="datetime-local"
                    value={formData.data_hora}
                    onChange={(e) => setFormData(prev => ({ ...prev, data_hora: e.target.value }))}
                    required
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium">Participantes</label>
                  <Input
                    value={formData.participantes}
                    onChange={(e) => setFormData(prev => ({ ...prev, participantes: e.target.value }))}
                    placeholder="Ex: João Silva, Maria Santos (separados por vírgula)"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Separe os nomes por vírgula
                  </p>
                </div>
                
                <div className="flex space-x-3 pt-4">
                  <Button type="submit" className="flex-1">
                    {editingId ? 'Atualizar' : 'Criar'}
                  </Button>
                  <Button type="button" variant="outline" onClick={resetForm}>
                    Cancelar
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

export default Reunioes

