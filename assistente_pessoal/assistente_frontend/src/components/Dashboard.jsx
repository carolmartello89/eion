import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
import { 
  Calendar, 
  Users, 
  Phone, 
  Clock,
  CheckCircle,
  AlertCircle,
  Plus,
  Mic,
  TrendingUp
} from 'lucide-react'

const Dashboard = () => {
  const [stats, setStats] = useState({
    compromissosHoje: 0,
    reunioesHoje: 0,
    contatosTotal: 0,
    proximoCompromisso: null
  })

  const [recentActivity, setRecentActivity] = useState([])
  const [quickActions] = useState([
    {
      id: 1,
      title: 'Nova Reunião',
      description: 'Agendar reunião rapidamente',
      icon: Users,
      color: 'bg-blue-500',
      action: 'criar-reuniao'
    },
    {
      id: 2,
      title: 'Novo Compromisso',
      description: 'Adicionar à agenda',
      icon: Calendar,
      color: 'bg-green-500',
      action: 'criar-compromisso'
    },
    {
      id: 3,
      title: 'Ligar para Contato',
      description: 'Fazer ligação rápida',
      icon: Phone,
      color: 'bg-purple-500',
      action: 'ligar-contato'
    },
    {
      id: 4,
      title: 'Comando de Voz',
      description: 'Usar assistente de voz',
      icon: Mic,
      color: 'bg-orange-500',
      action: 'ativar-voz'
    }
  ])

  useEffect(() => {
    // Simula carregamento de dados do dashboard
    const loadDashboardData = async () => {
      try {
        // Aqui seriam feitas as chamadas reais para a API
        setStats({
          compromissosHoje: 3,
          reunioesHoje: 2,
          contatosTotal: 25,
          proximoCompromisso: {
            titulo: 'Reunião com equipe',
            horario: '14:30',
            em: '2 horas'
          }
        })

        setRecentActivity([
          {
            id: 1,
            type: 'reuniao',
            title: 'Reunião finalizada',
            description: 'Reunião de planejamento concluída',
            time: '1 hora atrás',
            status: 'success'
          },
          {
            id: 2,
            type: 'compromisso',
            title: 'Compromisso adicionado',
            description: 'Consulta médica agendada',
            time: '2 horas atrás',
            status: 'info'
          },
          {
            id: 3,
            type: 'contato',
            title: 'Novo contato',
            description: 'João Silva adicionado',
            time: '3 horas atrás',
            status: 'success'
          }
        ])
      } catch (error) {
        console.error('Erro ao carregar dados do dashboard:', error)
      }
    }

    loadDashboardData()
  }, [])

  const handleQuickAction = (action) => {
    switch (action) {
      case 'criar-reuniao':
        // Navegar para criação de reunião
        console.log('Criar reunião')
        break
      case 'criar-compromisso':
        // Navegar para criação de compromisso
        console.log('Criar compromisso')
        break
      case 'ligar-contato':
        // Abrir lista de contatos
        console.log('Ligar para contato')
        break
      case 'ativar-voz':
        // Ativar assistente de voz
        console.log('Ativar voz')
        break
      default:
        break
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />
      case 'info':
        return <Clock className="w-4 h-4 text-blue-500" />
      default:
        return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Saudação */}
      <div className="text-center py-4">
        <h2 className="text-2xl font-bold mb-2">
          Olá! Como posso ajudar hoje?
        </h2>
        <p className="text-muted-foreground">
          {new Date().toLocaleDateString('pt-BR', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </p>
      </div>

      {/* Próximo compromisso em destaque */}
      {stats.proximoCompromisso && (
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Próximo Compromisso</CardTitle>
              <Badge variant="secondary">{stats.proximoCompromisso.em}</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                <Clock className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="font-medium">{stats.proximoCompromisso.titulo}</p>
                <p className="text-sm text-muted-foreground">
                  Hoje às {stats.proximoCompromisso.horario}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Estatísticas rápidas */}
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <Calendar className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.compromissosHoje}</p>
                <p className="text-sm text-muted-foreground">Hoje</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <Users className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.reunioesHoje}</p>
                <p className="text-sm text-muted-foreground">Reuniões</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Ações rápidas */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Ações Rápidas</CardTitle>
          <CardDescription>
            Acesse rapidamente as funcionalidades principais
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3">
            {quickActions.map((action) => {
              const IconComponent = action.icon
              return (
                <Button
                  key={action.id}
                  variant="outline"
                  className="h-auto p-4 flex-col space-y-2 touch-target"
                  onClick={() => handleQuickAction(action.action)}
                >
                  <div className={`w-8 h-8 ${action.color} rounded-full flex items-center justify-center`}>
                    <IconComponent className="w-4 h-4 text-white" />
                  </div>
                  <div className="text-center">
                    <p className="font-medium text-sm">{action.title}</p>
                    <p className="text-xs text-muted-foreground">{action.description}</p>
                  </div>
                </Button>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Atividade recente */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Atividade Recente</CardTitle>
          <CardDescription>
            Últimas ações realizadas no sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3 p-3 rounded-lg bg-muted/30">
                <div className="mt-0.5">
                  {getStatusIcon(activity.status)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm">{activity.title}</p>
                  <p className="text-sm text-muted-foreground">{activity.description}</p>
                  <p className="text-xs text-muted-foreground mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Dica do assistente */}
      <Card className="border-dashed">
        <CardContent className="p-4">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
              <Mic className="w-4 h-4 text-white" />
            </div>
            <div>
              <p className="font-medium text-sm">💡 Dica do Assistente</p>
              <p className="text-sm text-muted-foreground mt-1">
                Toque no botão do microfone e diga "Próximos compromissos" para ver sua agenda rapidamente!
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Dashboard

