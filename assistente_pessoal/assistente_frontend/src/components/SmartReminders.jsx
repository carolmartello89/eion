import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { 
  Bell, 
  Clock, 
  Plus, 
  X, 
  Check, 
  AlertTriangle,
  Calendar,
  Repeat,
  Zap,
  Brain,
  Settings
} from 'lucide-react'

const SmartReminders = () => {
  const [reminders, setReminders] = useState([])
  const [smartSuggestions, setSmartSuggestions] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newReminder, setNewReminder] = useState({
    title: '',
    description: '',
    datetime: '',
    type: 'general',
    priority: 'medium',
    recurring: false,
    recurringType: 'daily'
  })

  useEffect(() => {
    loadReminders()
    loadSmartSuggestions()
  }, [])

  const loadReminders = async () => {
    try {
      const response = await fetch('/api/reminders', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setReminders(data.reminders)
      } else {
        // Dados simulados
        setReminders(generateMockReminders())
      }
    } catch (error) {
      console.error('Erro ao carregar lembretes:', error)
      setReminders(generateMockReminders())
    } finally {
      setIsLoading(false)
    }
  }

  const loadSmartSuggestions = async () => {
    try {
      const response = await fetch('/api/assistente/smart-reminders', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setSmartSuggestions(data.reminders)
      }
    } catch (error) {
      console.error('Erro ao carregar sugestões:', error)
    }
  }

  const generateMockReminders = () => {
    const now = new Date()
    return [
      {
        id: 1,
        title: 'Reunião com equipe',
        description: 'Discussão sobre projeto Q3',
        datetime: new Date(now.getTime() + 30 * 60000).toISOString(),
        type: 'meeting',
        priority: 'high',
        status: 'pending',
        recurring: false,
        smart: false
      },
      {
        id: 2,
        title: 'Ligar para Dr. Pedro',
        description: 'Retornar ligação sobre consulta',
        datetime: new Date(now.getTime() + 2 * 60 * 60000).toISOString(),
        type: 'call',
        priority: 'medium',
        status: 'pending',
        recurring: false,
        smart: true
      },
      {
        id: 3,
        title: 'Revisar relatório mensal',
        description: 'Finalizar análise de performance',
        datetime: new Date(now.getTime() + 4 * 60 * 60000).toISOString(),
        type: 'task',
        priority: 'low',
        status: 'pending',
        recurring: true,
        recurringType: 'monthly',
        smart: true
      }
    ]
  }

  const createReminder = async () => {
    if (!newReminder.title || !newReminder.datetime) {
      alert('Título e data/hora são obrigatórios')
      return
    }

    try {
      const response = await fetch('/api/reminders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(newReminder)
      })

      if (response.ok) {
        const data = await response.json()
        setReminders(prev => [...prev, data.reminder])
        setNewReminder({
          title: '',
          description: '',
          datetime: '',
          type: 'general',
          priority: 'medium',
          recurring: false,
          recurringType: 'daily'
        })
        setShowCreateForm(false)
      }
    } catch (error) {
      console.error('Erro ao criar lembrete:', error)
      alert('Erro ao criar lembrete')
    }
  }

  const completeReminder = async (id) => {
    try {
      const response = await fetch(`/api/reminders/${id}/complete`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        setReminders(prev => 
          prev.map(reminder => 
            reminder.id === id 
              ? { ...reminder, status: 'completed' }
              : reminder
          )
        )
      }
    } catch (error) {
      console.error('Erro ao completar lembrete:', error)
    }
  }

  const dismissReminder = async (id) => {
    try {
      const response = await fetch(`/api/reminders/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        setReminders(prev => prev.filter(reminder => reminder.id !== id))
      }
    } catch (error) {
      console.error('Erro ao remover lembrete:', error)
    }
  }

  const acceptSmartSuggestion = async (suggestion) => {
    const reminderData = {
      title: suggestion.title,
      description: suggestion.description,
      datetime: suggestion.time,
      type: suggestion.type,
      priority: suggestion.priority,
      smart: true
    }

    try {
      const response = await fetch('/api/reminders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(reminderData)
      })

      if (response.ok) {
        const data = await response.json()
        setReminders(prev => [...prev, data.reminder])
        setSmartSuggestions(prev => prev.filter(s => s.id !== suggestion.id))
      }
    } catch (error) {
      console.error('Erro ao aceitar sugestão:', error)
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'meeting': return <Calendar className="w-4 h-4" />
      case 'call': return <Bell className="w-4 h-4" />
      case 'task': return <Check className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  const formatDateTime = (datetime) => {
    const date = new Date(datetime)
    const now = new Date()
    const diffMs = date.getTime() - now.getTime()
    const diffMins = Math.floor(diffMs / 60000)

    if (diffMins < 0) {
      return 'Atrasado'
    } else if (diffMins < 60) {
      return `Em ${diffMins} min`
    } else if (diffMins < 1440) {
      return `Em ${Math.floor(diffMins / 60)}h ${diffMins % 60}min`
    } else {
      return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }

  const pendingReminders = reminders.filter(r => r.status === 'pending')
  const urgentReminders = pendingReminders.filter(r => {
    const diffMs = new Date(r.datetime).getTime() - new Date().getTime()
    return diffMs < 60 * 60000 && diffMs > 0 // Próxima hora
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Lembretes Inteligentes</h2>
          <p className="text-muted-foreground">
            {pendingReminders.length} lembretes pendentes
            {urgentReminders.length > 0 && (
              <span className="ml-2 text-red-600 font-medium">
                • {urgentReminders.length} urgentes
              </span>
            )}
          </p>
        </div>
        
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Novo Lembrete
        </Button>
      </div>

      {/* Sugestões inteligentes */}
      {smartSuggestions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="w-5 h-5" />
              <span>Sugestões Inteligentes</span>
              <Badge variant="secondary">IA</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {smartSuggestions.map((suggestion) => (
                <div key={suggestion.id} className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      {getTypeIcon(suggestion.type)}
                    </div>
                    <div>
                      <p className="font-medium">{suggestion.title}</p>
                      <p className="text-sm text-muted-foreground">{suggestion.description}</p>
                      <p className="text-xs text-blue-600">{formatDateTime(suggestion.time)}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button 
                      size="sm" 
                      onClick={() => acceptSmartSuggestion(suggestion)}
                    >
                      <Zap className="w-4 h-4 mr-1" />
                      Aceitar
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => setSmartSuggestions(prev => prev.filter(s => s.id !== suggestion.id))}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Lembretes urgentes */}
      {urgentReminders.length > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-red-700">
              <AlertTriangle className="w-5 h-5" />
              <span>Lembretes Urgentes</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {urgentReminders.map((reminder) => (
                <div key={reminder.id} className="flex items-center justify-between p-3 bg-white rounded-lg border">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                      {getTypeIcon(reminder.type)}
                    </div>
                    <div>
                      <p className="font-medium">{reminder.title}</p>
                      <p className="text-sm text-muted-foreground">{reminder.description}</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge className={getPriorityColor(reminder.priority)}>
                          {reminder.priority}
                        </Badge>
                        <span className="text-xs text-red-600 font-medium">
                          {formatDateTime(reminder.datetime)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button 
                      size="sm" 
                      onClick={() => completeReminder(reminder.id)}
                    >
                      <Check className="w-4 h-4" />
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => dismissReminder(reminder.id)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Todos os lembretes */}
      <Card>
        <CardHeader>
          <CardTitle>Todos os Lembretes</CardTitle>
        </CardHeader>
        <CardContent>
          {pendingReminders.length === 0 ? (
            <div className="text-center py-8">
              <Bell className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">Nenhum lembrete pendente</p>
            </div>
          ) : (
            <div className="space-y-3">
              {pendingReminders.map((reminder) => (
                <div key={reminder.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/30 transition-colors">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-muted rounded-full flex items-center justify-center">
                      {getTypeIcon(reminder.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <p className="font-medium">{reminder.title}</p>
                        {reminder.smart && (
                          <Badge variant="outline" className="text-xs">
                            <Brain className="w-3 h-3 mr-1" />
                            IA
                          </Badge>
                        )}
                        {reminder.recurring && (
                          <Badge variant="outline" className="text-xs">
                            <Repeat className="w-3 h-3 mr-1" />
                            Recorrente
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{reminder.description}</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge className={getPriorityColor(reminder.priority)}>
                          {reminder.priority}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {formatDateTime(reminder.datetime)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button 
                      size="sm" 
                      onClick={() => completeReminder(reminder.id)}
                    >
                      <Check className="w-4 h-4" />
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => dismissReminder(reminder.id)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Formulário de criação */}
      {showCreateForm && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Novo Lembrete</span>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setShowCreateForm(false)}
              >
                <X className="w-4 h-4" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Título</label>
              <Input
                value={newReminder.title}
                onChange={(e) => setNewReminder(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Digite o título do lembrete"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium">Descrição</label>
              <Textarea
                value={newReminder.description}
                onChange={(e) => setNewReminder(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Descrição opcional"
                rows={3}
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Data e Hora</label>
                <Input
                  type="datetime-local"
                  value={newReminder.datetime}
                  onChange={(e) => setNewReminder(prev => ({ ...prev, datetime: e.target.value }))}
                />
              </div>
              
              <div>
                <label className="text-sm font-medium">Prioridade</label>
                <select 
                  className="w-full p-2 border rounded"
                  value={newReminder.priority}
                  onChange={(e) => setNewReminder(prev => ({ ...prev, priority: e.target.value }))}
                >
                  <option value="low">Baixa</option>
                  <option value="medium">Média</option>
                  <option value="high">Alta</option>
                </select>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Tipo</label>
                <select 
                  className="w-full p-2 border rounded"
                  value={newReminder.type}
                  onChange={(e) => setNewReminder(prev => ({ ...prev, type: e.target.value }))}
                >
                  <option value="general">Geral</option>
                  <option value="meeting">Reunião</option>
                  <option value="call">Ligação</option>
                  <option value="task">Tarefa</option>
                </select>
              </div>
              
              <div>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={newReminder.recurring}
                    onChange={(e) => setNewReminder(prev => ({ ...prev, recurring: e.target.checked }))}
                  />
                  <span className="text-sm font-medium">Recorrente</span>
                </label>
                {newReminder.recurring && (
                  <select 
                    className="w-full p-2 border rounded mt-2"
                    value={newReminder.recurringType}
                    onChange={(e) => setNewReminder(prev => ({ ...prev, recurringType: e.target.value }))}
                  >
                    <option value="daily">Diário</option>
                    <option value="weekly">Semanal</option>
                    <option value="monthly">Mensal</option>
                  </select>
                )}
              </div>
            </div>
            
            <div className="flex justify-end space-x-2">
              <Button 
                variant="outline"
                onClick={() => setShowCreateForm(false)}
              >
                Cancelar
              </Button>
              <Button onClick={createReminder}>
                Criar Lembrete
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default SmartReminders

