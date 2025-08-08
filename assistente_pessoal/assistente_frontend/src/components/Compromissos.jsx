import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { 
  Calendar, 
  Clock, 
  Plus, 
  Edit, 
  Trash2, 
  AlertCircle,
  CheckCircle,
  X,
  Search
} from 'lucide-react'

const Compromissos = () => {
  const [compromissos, setCompromissos] = useState([])
  const [filtro, setFiltro] = useState('todos') // todos, hoje, semana, pendentes
  const [busca, setBusca] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [formData, setFormData] = useState({
    titulo: '',
    descricao: '',
    data_hora: '',
    alerta_antecedencia: 30,
    tipo: 'evento',
    prioridade: 'media',
    localizacao: ''
  })

  // Carrega compromissos
  useEffect(() => {
    loadCompromissos()
  }, [filtro])

  const loadCompromissos = async () => {
    try {
      // Simula dados enquanto a API não está disponível
      const mockCompromissos = [
        {
          id: '1',
          titulo: 'Reunião de equipe',
          descricao: 'Reunião semanal com a equipe de desenvolvimento',
          data_hora: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
          alerta_antecedencia: 30,
          tipo: 'reuniao',
          status: 'pendente',
          prioridade: 'alta',
          localizacao: 'Sala de reuniões'
        },
        {
          id: '2',
          titulo: 'Consulta médica',
          descricao: 'Consulta de rotina',
          data_hora: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
          alerta_antecedencia: 60,
          tipo: 'evento',
          status: 'pendente',
          prioridade: 'media',
          localizacao: 'Hospital São Lucas'
        },
        {
          id: '3',
          titulo: 'Apresentação do projeto',
          descricao: 'Apresentar resultados do trimestre',
          data_hora: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
          alerta_antecedencia: 120,
          tipo: 'reuniao',
          status: 'pendente',
          prioridade: 'alta',
          localizacao: 'Auditório principal'
        }
      ]
      
      setCompromissos(mockCompromissos)
    } catch (error) {
      console.error('Erro ao carregar compromissos:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      if (editingId) {
        // Atualizar compromisso existente
        setCompromissos(prev => prev.map(comp => 
          comp.id === editingId ? { ...comp, ...formData } : comp
        ))
      } else {
        // Criar novo compromisso
        const novoCompromisso = {
          id: Date.now().toString(),
          ...formData,
          status: 'pendente',
          criado_em: new Date().toISOString()
        }
        setCompromissos(prev => [...prev, novoCompromisso])
      }
      
      resetForm()
    } catch (error) {
      console.error('Erro ao salvar compromisso:', error)
    }
  }

  const resetForm = () => {
    setFormData({
      titulo: '',
      descricao: '',
      data_hora: '',
      alerta_antecedencia: 30,
      tipo: 'evento',
      prioridade: 'media',
      localizacao: ''
    })
    setShowForm(false)
    setEditingId(null)
  }

  const handleEdit = (compromisso) => {
    setFormData({
      titulo: compromisso.titulo,
      descricao: compromisso.descricao,
      data_hora: compromisso.data_hora.slice(0, 16), // Para input datetime-local
      alerta_antecedencia: compromisso.alerta_antecedencia,
      tipo: compromisso.tipo,
      prioridade: compromisso.prioridade,
      localizacao: compromisso.localizacao
    })
    setEditingId(compromisso.id)
    setShowForm(true)
  }

  const handleDelete = async (id) => {
    if (confirm('Tem certeza que deseja excluir este compromisso?')) {
      setCompromissos(prev => prev.filter(comp => comp.id !== id))
    }
  }

  const toggleStatus = async (id) => {
    setCompromissos(prev => prev.map(comp => 
      comp.id === id 
        ? { ...comp, status: comp.status === 'pendente' ? 'concluido' : 'pendente' }
        : comp
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
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(hours / 24)
    
    if (days > 0) return `em ${days} dia${days > 1 ? 's' : ''}`
    if (hours > 0) return `em ${hours} hora${hours > 1 ? 's' : ''}`
    if (diff > 0) return 'em breve'
    return 'atrasado'
  }

  const getPriorityColor = (prioridade) => {
    switch (prioridade) {
      case 'alta': return 'bg-red-100 text-red-800'
      case 'media': return 'bg-yellow-100 text-yellow-800'
      case 'baixa': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeIcon = (tipo) => {
    switch (tipo) {
      case 'reuniao': return '👥'
      case 'tarefa': return '✅'
      case 'evento': return '📅'
      case 'lembrete': return '🔔'
      default: return '📋'
    }
  }

  const filteredCompromissos = compromissos.filter(comp => {
    const matchesBusca = comp.titulo.toLowerCase().includes(busca.toLowerCase()) ||
                        comp.descricao.toLowerCase().includes(busca.toLowerCase())
    
    if (!matchesBusca) return false
    
    const now = new Date()
    const compDate = new Date(comp.data_hora)
    
    switch (filtro) {
      case 'hoje':
        return compDate.toDateString() === now.toDateString()
      case 'semana':
        const weekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
        return compDate >= now && compDate <= weekFromNow
      case 'pendentes':
        return comp.status === 'pendente'
      default:
        return true
    }
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Compromissos</h2>
          <p className="text-muted-foreground">Gerencie sua agenda pessoal</p>
        </div>
        <Button onClick={() => setShowForm(true)} className="touch-target">
          <Plus className="w-4 h-4 mr-2" />
          Novo
        </Button>
      </div>

      {/* Filtros e busca */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Buscar compromissos..."
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <div className="flex space-x-2 overflow-x-auto pb-2">
          {[
            { key: 'todos', label: 'Todos' },
            { key: 'hoje', label: 'Hoje' },
            { key: 'semana', label: 'Esta semana' },
            { key: 'pendentes', label: 'Pendentes' }
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

      {/* Lista de compromissos */}
      <div className="space-y-3">
        {filteredCompromissos.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <Calendar className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">
                {busca ? 'Nenhum compromisso encontrado' : 'Nenhum compromisso agendado'}
              </p>
            </CardContent>
          </Card>
        ) : (
          filteredCompromissos.map((compromisso) => {
            const dateTime = formatDateTime(compromisso.data_hora)
            return (
              <Card key={compromisso.id} className={`${
                compromisso.status === 'concluido' ? 'opacity-60' : ''
              }`}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-lg">{getTypeIcon(compromisso.tipo)}</span>
                        <h3 className={`font-semibold ${
                          compromisso.status === 'concluido' ? 'line-through' : ''
                        }`}>
                          {compromisso.titulo}
                        </h3>
                        <Badge className={getPriorityColor(compromisso.prioridade)}>
                          {compromisso.prioridade}
                        </Badge>
                      </div>
                      
                      {compromisso.descricao && (
                        <p className="text-sm text-muted-foreground mb-2">
                          {compromisso.descricao}
                        </p>
                      )}
                      
                      <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-4 h-4" />
                          <span>{dateTime.date}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="w-4 h-4" />
                          <span>{dateTime.time}</span>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {dateTime.relative}
                        </Badge>
                      </div>
                      
                      {compromisso.localizacao && (
                        <p className="text-sm text-muted-foreground mt-1">
                          📍 {compromisso.localizacao}
                        </p>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleStatus(compromisso.id)}
                        className="touch-target"
                      >
                        {compromisso.status === 'concluido' ? (
                          <CheckCircle className="w-4 h-4 text-green-600" />
                        ) : (
                          <Clock className="w-4 h-4" />
                        )}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(compromisso)}
                        className="touch-target"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(compromisso.id)}
                        className="touch-target text-destructive"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
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
                    {editingId ? 'Editar Compromisso' : 'Novo Compromisso'}
                  </CardTitle>
                  <CardDescription>
                    Preencha os detalhes do compromisso
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
                    placeholder="Ex: Reunião com cliente"
                    required
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium">Descrição</label>
                  <Textarea
                    value={formData.descricao}
                    onChange={(e) => setFormData(prev => ({ ...prev, descricao: e.target.value }))}
                    placeholder="Detalhes do compromisso..."
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
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Tipo</label>
                    <select
                      value={formData.tipo}
                      onChange={(e) => setFormData(prev => ({ ...prev, tipo: e.target.value }))}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="evento">Evento</option>
                      <option value="reuniao">Reunião</option>
                      <option value="tarefa">Tarefa</option>
                      <option value="lembrete">Lembrete</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Prioridade</label>
                    <select
                      value={formData.prioridade}
                      onChange={(e) => setFormData(prev => ({ ...prev, prioridade: e.target.value }))}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="baixa">Baixa</option>
                      <option value="media">Média</option>
                      <option value="alta">Alta</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium">Localização</label>
                  <Input
                    value={formData.localizacao}
                    onChange={(e) => setFormData(prev => ({ ...prev, localizacao: e.target.value }))}
                    placeholder="Ex: Sala de reuniões"
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium">Alerta (minutos antes)</label>
                  <select
                    value={formData.alerta_antecedencia}
                    onChange={(e) => setFormData(prev => ({ ...prev, alerta_antecedencia: parseInt(e.target.value) }))}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value={5}>5 minutos</option>
                    <option value={15}>15 minutos</option>
                    <option value={30}>30 minutos</option>
                    <option value={60}>1 hora</option>
                    <option value={120}>2 horas</option>
                  </select>
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

export default Compromissos

