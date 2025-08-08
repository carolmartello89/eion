import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { 
  TrendingUp, 
  TrendingDown, 
  Calendar, 
  Clock, 
  Users, 
  Phone,
  Target,
  Activity,
  Download,
  Filter,
  RefreshCw
} from 'lucide-react'

const Analytics = () => {
  const [analyticsData, setAnalyticsData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [selectedPeriod, setSelectedPeriod] = useState('week')
  const [lastUpdated, setLastUpdated] = useState(new Date())

  // Cores para gráficos
  const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']

  useEffect(() => {
    loadAnalytics()
  }, [selectedPeriod])

  const loadAnalytics = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`/api/analytics/dashboard?period=${selectedPeriod}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setAnalyticsData(data)
        setLastUpdated(new Date())
      } else {
        // Dados simulados para demonstração
        setAnalyticsData(generateMockData())
      }
    } catch (error) {
      console.error('Erro ao carregar analytics:', error)
      setAnalyticsData(generateMockData())
    } finally {
      setIsLoading(false)
    }
  }

  const generateMockData = () => {
    return {
      summary: {
        totalAppointments: 45,
        totalMeetings: 12,
        totalCalls: 28,
        productivityScore: 87,
        trends: {
          appointments: 12,
          meetings: -5,
          calls: 8,
          productivity: 3
        }
      },
      appointmentsByDay: [
        { day: 'Seg', count: 8, completed: 7 },
        { day: 'Ter', count: 6, completed: 6 },
        { day: 'Qua', count: 9, completed: 8 },
        { day: 'Qui', count: 7, completed: 6 },
        { day: 'Sex', count: 10, completed: 9 },
        { day: 'Sáb', count: 3, completed: 3 },
        { day: 'Dom', count: 2, completed: 2 }
      ],
      productivityTrend: [
        { date: '01/07', score: 75 },
        { date: '02/07', score: 82 },
        { date: '03/07', score: 78 },
        { date: '04/07', score: 85 },
        { date: '05/07', score: 90 },
        { date: '06/07', score: 87 },
        { date: '07/07', score: 92 }
      ],
      timeDistribution: [
        { name: 'Reuniões', value: 35, color: '#3b82f6' },
        { name: 'Ligações', value: 25, color: '#ef4444' },
        { name: 'Planejamento', value: 20, color: '#10b981' },
        { name: 'Emails', value: 15, color: '#f59e0b' },
        { name: 'Outros', value: 5, color: '#8b5cf6' }
      ],
      topContacts: [
        { name: 'Dr. Pedro Costa', interactions: 8, type: 'profissional' },
        { name: 'João Silva', interactions: 6, type: 'trabalho' },
        { name: 'Maria Santos', interactions: 5, type: 'pessoal' },
        { name: 'Ana Oliveira', interactions: 4, type: 'trabalho' }
      ],
      upcomingInsights: [
        'Você tem 3 reuniões agendadas para amanhã',
        'Sua produtividade aumentou 15% esta semana',
        'Tempo médio de reunião: 45 minutos',
        'Melhor dia da semana: Sexta-feira'
      ]
    }
  }

  const exportReport = async () => {
    try {
      const response = await fetch('/api/analytics/export', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          period: selectedPeriod,
          format: 'pdf'
        })
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `relatorio_${selectedPeriod}_${new Date().toISOString().split('T')[0]}.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Erro ao exportar relatório:', error)
      alert('Erro ao exportar relatório')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin" />
        <span className="ml-2">Carregando analytics...</span>
      </div>
    )
  }

  if (!analyticsData) {
    return (
      <div className="text-center py-8">
        <p>Erro ao carregar dados de analytics</p>
        <Button onClick={loadAnalytics} className="mt-4">
          Tentar novamente
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Analytics & Relatórios</h2>
          <p className="text-muted-foreground">
            Última atualização: {lastUpdated.toLocaleString()}
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1">
            {['day', 'week', 'month'].map((period) => (
              <Button
                key={period}
                variant={selectedPeriod === period ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedPeriod(period)}
              >
                {period === 'day' ? 'Hoje' : period === 'week' ? 'Semana' : 'Mês'}
              </Button>
            ))}
          </div>
          
          <Button variant="outline" size="sm" onClick={loadAnalytics}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Atualizar
          </Button>
          
          <Button variant="outline" size="sm" onClick={exportReport}>
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </Button>
        </div>
      </div>

      {/* Cards de resumo */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Compromissos</p>
                <p className="text-2xl font-bold">{analyticsData.summary.totalAppointments}</p>
              </div>
              <div className="flex items-center space-x-1">
                {analyticsData.summary.trends.appointments > 0 ? (
                  <TrendingUp className="w-4 h-4 text-green-500" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-500" />
                )}
                <span className={`text-sm ${
                  analyticsData.summary.trends.appointments > 0 ? 'text-green-500' : 'text-red-500'
                }`}>
                  {Math.abs(analyticsData.summary.trends.appointments)}%
                </span>
              </div>
            </div>
            <Calendar className="w-8 h-8 text-primary mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Reuniões</p>
                <p className="text-2xl font-bold">{analyticsData.summary.totalMeetings}</p>
              </div>
              <div className="flex items-center space-x-1">
                {analyticsData.summary.trends.meetings > 0 ? (
                  <TrendingUp className="w-4 h-4 text-green-500" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-500" />
                )}
                <span className={`text-sm ${
                  analyticsData.summary.trends.meetings > 0 ? 'text-green-500' : 'text-red-500'
                }`}>
                  {Math.abs(analyticsData.summary.trends.meetings)}%
                </span>
              </div>
            </div>
            <Users className="w-8 h-8 text-primary mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Ligações</p>
                <p className="text-2xl font-bold">{analyticsData.summary.totalCalls}</p>
              </div>
              <div className="flex items-center space-x-1">
                {analyticsData.summary.trends.calls > 0 ? (
                  <TrendingUp className="w-4 h-4 text-green-500" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-500" />
                )}
                <span className={`text-sm ${
                  analyticsData.summary.trends.calls > 0 ? 'text-green-500' : 'text-red-500'
                }`}>
                  {Math.abs(analyticsData.summary.trends.calls)}%
                </span>
              </div>
            </div>
            <Phone className="w-8 h-8 text-primary mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Produtividade</p>
                <p className="text-2xl font-bold">{analyticsData.summary.productivityScore}%</p>
              </div>
              <div className="flex items-center space-x-1">
                <TrendingUp className="w-4 h-4 text-green-500" />
                <span className="text-sm text-green-500">
                  +{analyticsData.summary.trends.productivity}%
                </span>
              </div>
            </div>
            <Target className="w-8 h-8 text-primary mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Compromissos por dia */}
        <Card>
          <CardHeader>
            <CardTitle>Compromissos por Dia</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analyticsData.appointmentsByDay}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" name="Agendados" />
                <Bar dataKey="completed" fill="#10b981" name="Concluídos" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Tendência de produtividade */}
        <Card>
          <CardHeader>
            <CardTitle>Tendência de Produtividade</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analyticsData.productivityTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  name="Score"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Distribuição de tempo e insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribuição de tempo */}
        <Card>
          <CardHeader>
            <CardTitle>Distribuição de Tempo</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analyticsData.timeDistribution}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {analyticsData.timeDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top contatos */}
        <Card>
          <CardHeader>
            <CardTitle>Contatos Mais Frequentes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analyticsData.topContacts.map((contact, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium">
                        {contact.name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium">{contact.name}</p>
                      <Badge variant="outline" className="text-xs">
                        {contact.type}
                      </Badge>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{contact.interactions}</p>
                    <p className="text-xs text-muted-foreground">interações</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Insights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="w-5 h-5" />
            <span>Insights e Recomendações</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analyticsData.upcomingInsights.map((insight, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-muted/30 rounded-lg">
                <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                <p className="text-sm">{insight}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Analytics

