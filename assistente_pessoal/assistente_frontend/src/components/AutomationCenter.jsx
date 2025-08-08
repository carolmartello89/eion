import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { 
  Zap, 
  Settings, 
  Plus, 
  Play, 
  Pause, 
  Edit, 
  Trash2,
  Clock,
  Calendar,
  Phone,
  Mail,
  MessageSquare,
  Bot,
  Workflow,
  Target
} from 'lucide-react'

const AutomationCenter = () => {
  const [automations, setAutomations] = useState([])
  const [templates, setTemplates] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadAutomations()
    loadTemplates()
  }, [])

  const loadAutomations = async () => {
    try {
      const response = await fetch('/api/automation/rules', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setAutomations(data.automations)
      } else {
        setAutomations(generateMockAutomations())
      }
    } catch (error) {
      console.error('Erro ao carregar automações:', error)
      setAutomations(generateMockAutomations())
    } finally {
      setIsLoading(false)
    }
  }

  const loadTemplates = async () => {
    try {
      const response = await fetch('/api/automation/templates', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setTemplates(data.templates)
      } else {
        setTemplates(generateMockTemplates())
      }
    } catch (error) {
      console.error('Erro ao carregar templates:', error)
      setTemplates(generateMockTemplates())
    }
  }

  const generateMockAutomations = () => {
    return [
      {
        id: 1,
        name: 'Lembrete de Reunião',
        description: 'Envia lembrete 15 minutos antes de cada reunião',
        trigger: 'meeting_scheduled',
        action: 'send_notification',
        enabled: true,
        executions: 45,
        lastRun: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        category: 'notifications'
      },
      {
        id: 2,
        name: 'Backup Diário',
        description: 'Faz backup dos dados todos os dias às 23:00',
        trigger: 'schedule',
        action: 'backup_data',
        enabled: true,
        executions: 30,
        lastRun: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        category: 'maintenance'
      },
      {
        id: 3,
        name: 'Seguimento de Ligações',
        description: 'Cria tarefa de seguimento após ligações importantes',
        trigger: 'call_completed',
        action: 'create_followup',
        enabled: false,
        executions: 12,
        lastRun: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        category: 'productivity'
      },
      {
        id: 4,
        name: 'Relatório Semanal',
        description: 'Gera e envia relatório de produtividade toda sexta',
        trigger: 'weekly_schedule',
        action: 'generate_report',
        enabled: true,
        executions: 8,
        lastRun: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        category: 'reports'
      }
    ]
  }

  const generateMockTemplates = () => {
    return [
      {
        id: 1,
        name: 'Lembrete de Aniversário',
        description: 'Envia lembrete de aniversários de contatos',
        category: 'social',
        icon: '🎂',
        trigger: 'contact_birthday',
        actions: ['send_notification', 'suggest_call']
      },
      {
        id: 2,
        name: 'Acompanhamento de Projetos',
        description: 'Verifica status de projetos semanalmente',
        category: 'productivity',
        icon: '📊',
        trigger: 'weekly_schedule',
        actions: ['check_project_status', 'send_update']
      },
      {
        id: 3,
        name: 'Organização de Emails',
        description: 'Organiza emails por prioridade automaticamente',
        category: 'email',
        icon: '📧',
        trigger: 'email_received',
        actions: ['categorize_email', 'set_priority']
      },
      {
        id: 4,
        name: 'Planejamento Semanal',
        description: 'Cria agenda da próxima semana baseada em padrões',
        category: 'planning',
        icon: '📅',
        trigger: 'sunday_evening',
        actions: ['analyze_patterns', 'suggest_schedule']
      }
    ]
  }

  const toggleAutomation = async (id, enabled) => {
    try {
      const response = await fetch(`/api/automation/rules/${id}/toggle`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({ enabled })
      })

      if (response.ok) {
        setAutomations(prev => 
          prev.map(automation => 
            automation.id === id 
              ? { ...automation, enabled }
              : automation
          )
        )
      }
    } catch (error) {
      console.error('Erro ao alterar automação:', error)
    }
  }

  const createAutomationFromTemplate = async (template) => {
    try {
      const response = await fetch('/api/automation/rules', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          templateId: template.id,
          name: template.name,
          description: template.description,
          trigger: template.trigger,
          actions: template.actions
        })
      })

      if (response.ok) {
        const data = await response.json()
        setAutomations(prev => [...prev, data.automation])
        alert('Automação criada com sucesso!')
      }
    } catch (error) {
      console.error('Erro ao criar automação:', error)
      alert('Erro ao criar automação')
    }
  }

  const deleteAutomation = async (id) => {
    if (!confirm('Tem certeza que deseja excluir esta automação?')) return

    try {
      const response = await fetch(`/api/automation/rules/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        setAutomations(prev => prev.filter(automation => automation.id !== id))
      }
    } catch (error) {
      console.error('Erro ao excluir automação:', error)
    }
  }

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'notifications': return <Bell className="w-4 h-4" />
      case 'maintenance': return <Settings className="w-4 h-4" />
      case 'productivity': return <Target className="w-4 h-4" />
      case 'reports': return <MessageSquare className="w-4 h-4" />
      case 'social': return <Phone className="w-4 h-4" />
      case 'email': return <Mail className="w-4 h-4" />
      case 'planning': return <Calendar className="w-4 h-4" />
      default: return <Zap className="w-4 h-4" />
    }
  }

  const getCategoryColor = (category) => {
    switch (category) {
      case 'notifications': return 'bg-blue-100 text-blue-800'
      case 'maintenance': return 'bg-gray-100 text-gray-800'
      case 'productivity': return 'bg-green-100 text-green-800'
      case 'reports': return 'bg-purple-100 text-purple-800'
      case 'social': return 'bg-pink-100 text-pink-800'
      case 'email': return 'bg-yellow-100 text-yellow-800'
      case 'planning': return 'bg-indigo-100 text-indigo-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatLastRun = (datetime) => {
    const date = new Date(datetime)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)

    if (diffHours < 1) {
      return 'Há poucos minutos'
    } else if (diffHours < 24) {
      return `Há ${diffHours} horas`
    } else {
      return `Há ${diffDays} dias`
    }
  }

  const activeAutomations = automations.filter(a => a.enabled)
  const totalExecutions = automations.reduce((sum, a) => sum + a.executions, 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Centro de Automação</h2>
          <p className="text-muted-foreground">
            {activeAutomations.length} automações ativas • {totalExecutions} execuções totais
          </p>
        </div>
        
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Nova Automação
        </Button>
      </div>

      {/* Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Automações Ativas</p>
                <p className="text-2xl font-bold">{activeAutomations.length}</p>
              </div>
              <Zap className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Execuções Hoje</p>
                <p className="text-2xl font-bold">23</p>
              </div>
              <Play className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Tempo Economizado</p>
                <p className="text-2xl font-bold">2.5h</p>
              </div>
              <Clock className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Taxa de Sucesso</p>
                <p className="text-2xl font-bold">98%</p>
              </div>
              <Target className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Automações ativas */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Workflow className="w-5 h-5" />
            <span>Automações Configuradas</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {automations.map((automation) => (
              <div key={automation.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-muted rounded-lg flex items-center justify-center">
                    {getCategoryIcon(automation.category)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-medium">{automation.name}</h3>
                      <Badge className={getCategoryColor(automation.category)}>
                        {automation.category}
                      </Badge>
                      {automation.enabled && (
                        <Badge variant="outline" className="text-green-600 border-green-600">
                          Ativa
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {automation.description}
                    </p>
                    <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                      <span>{automation.executions} execuções</span>
                      <span>Última execução: {formatLastRun(automation.lastRun)}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={automation.enabled}
                    onCheckedChange={(enabled) => toggleAutomation(automation.id, enabled)}
                  />
                  <Button variant="outline" size="sm">
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => deleteAutomation(automation.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Templates de automação */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Bot className="w-5 h-5" />
            <span>Templates de Automação</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {templates.map((template) => (
              <div key={template.id} className="p-4 border rounded-lg hover:bg-muted/30 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl">{template.icon}</div>
                    <div className="flex-1">
                      <h3 className="font-medium">{template.name}</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        {template.description}
                      </p>
                      <Badge className={`${getCategoryColor(template.category)} mt-2`}>
                        {template.category}
                      </Badge>
                    </div>
                  </div>
                  
                  <Button 
                    size="sm"
                    onClick={() => createAutomationFromTemplate(template)}
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Usar
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Histórico de execuções */}
      <Card>
        <CardHeader>
          <CardTitle>Histórico Recente</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { time: '14:30', automation: 'Lembrete de Reunião', status: 'success', message: 'Notificação enviada com sucesso' },
              { time: '12:00', automation: 'Backup Diário', status: 'success', message: 'Backup realizado (2.3 MB)' },
              { time: '09:15', automation: 'Seguimento de Ligações', status: 'failed', message: 'Erro ao criar tarefa de seguimento' },
              { time: '08:00', automation: 'Planejamento Semanal', status: 'success', message: 'Agenda da semana atualizada' }
            ].map((execution, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    execution.status === 'success' ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <div>
                    <p className="font-medium text-sm">{execution.automation}</p>
                    <p className="text-xs text-muted-foreground">{execution.message}</p>
                  </div>
                </div>
                <span className="text-xs text-muted-foreground">{execution.time}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default AutomationCenter

