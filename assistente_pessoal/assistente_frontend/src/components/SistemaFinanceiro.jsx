import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  DollarSign, TrendingUp, TrendingDown, PieChart, 
  Calendar, Bell, Download, Plus, Trash2, Edit,
  CreditCard, Wallet, Target, AlertTriangle
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Cell } from 'recharts'

const SistemaFinanceiro = () => {
  const [transacoes, setTransacoes] = useState([])
  const [lembretes, setLembretes] = useState([])
  const [metas, setMetas] = useState([])
  const [resumo, setResumo] = useState({})
  const [recomendacoes, setRecomendacoes] = useState([])
  const [novaTransacao, setNovaTransacao] = useState({
    tipo: 'despesa',
    valor: '',
    categoria: '',
    descricao: '',
    data: new Date().toISOString().split('T')[0]
  })
  const [novoLembrete, setNovoLembrete] = useState({
    titulo: '',
    valor: '',
    data_vencimento: '',
    recorrente: false,
    categoria: 'conta'
  })

  const categorias = [
    'Alimentação', 'Transporte', 'Moradia', 'Saúde', 'Educação',
    'Entretenimento', 'Roupas', 'Tecnologia', 'Viagem', 'Outros'
  ]

  const cores = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1', '#d084d0']

  useEffect(() => {
    carregarDados()
  }, [])

  const carregarDados = async () => {
    try {
      // Carrega transações
      const responseTransacoes = await fetch('/api/financeiro/transacoes?limit=50', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (responseTransacoes.ok) {
        const dataTransacoes = await responseTransacoes.json()
        setTransacoes(dataTransacoes.transacoes)
      }

      // Carrega resumo
      const responseResumo = await fetch('/api/financeiro/resumo', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (responseResumo.ok) {
        const dataResumo = await responseResumo.json()
        setResumo(dataResumo)
      }

      // Carrega lembretes
      const responseLembretes = await fetch('/api/financeiro/lembretes', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (responseLembretes.ok) {
        const dataLembretes = await responseLembretes.json()
        setLembretes(dataLembretes.lembretes)
      }

      // Carrega recomendações
      const responseRecomendacoes = await fetch('/api/financeiro/recomendacoes', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (responseRecomendacoes.ok) {
        const dataRecomendacoes = await responseRecomendacoes.json()
        setRecomendacoes(dataRecomendacoes.recomendacoes)
      }

    } catch (error) {
      console.error('Erro ao carregar dados financeiros:', error)
    }
  }

  const adicionarTransacao = async () => {
    if (!novaTransacao.valor || !novaTransacao.categoria) return

    try {
      const response = await fetch('/api/financeiro/transacoes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          ...novaTransacao,
          valor: parseFloat(novaTransacao.valor)
        })
      })

      if (response.ok) {
        setNovaTransacao({
          tipo: 'despesa',
          valor: '',
          categoria: '',
          descricao: '',
          data: new Date().toISOString().split('T')[0]
        })
        carregarDados()
      }
    } catch (error) {
      console.error('Erro ao adicionar transação:', error)
    }
  }

  const adicionarLembrete = async () => {
    if (!novoLembrete.titulo || !novoLembrete.data_vencimento) return

    try {
      const response = await fetch('/api/financeiro/lembretes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          ...novoLembrete,
          valor: novoLembrete.valor ? parseFloat(novoLembrete.valor) : null
        })
      })

      if (response.ok) {
        setNovoLembrete({
          titulo: '',
          valor: '',
          data_vencimento: '',
          recorrente: false,
          categoria: 'conta'
        })
        carregarDados()
      }
    } catch (error) {
      console.error('Erro ao adicionar lembrete:', error)
    }
  }

  const gerarRelatorio = async () => {
    try {
      const response = await fetch('/api/financeiro/relatorio', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `relatorio_financeiro_${new Date().toISOString().split('T')[0]}.xlsx`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Erro ao gerar relatório:', error)
    }
  }

  const formatarMoeda = (valor) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor)
  }

  const formatarData = (data) => {
    return new Date(data).toLocaleDateString('pt-BR')
  }

  const getDiasAteVencimento = (dataVencimento) => {
    const hoje = new Date()
    const vencimento = new Date(dataVencimento)
    const diffTime = vencimento - hoje
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  const getCorLembrete = (diasRestantes) => {
    if (diasRestantes < 0) return 'bg-red-100 text-red-800'
    if (diasRestantes <= 3) return 'bg-orange-100 text-orange-800'
    if (diasRestantes <= 7) return 'bg-yellow-100 text-yellow-800'
    return 'bg-green-100 text-green-800'
  }

  const dadosGrafico = transacoes
    .filter(t => t.data >= new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString())
    .reduce((acc, transacao) => {
      const data = transacao.data.split('T')[0]
      const existing = acc.find(item => item.data === data)
      
      if (existing) {
        if (transacao.tipo === 'receita') {
          existing.receitas += transacao.valor
        } else {
          existing.despesas += transacao.valor
        }
      } else {
        acc.push({
          data,
          receitas: transacao.tipo === 'receita' ? transacao.valor : 0,
          despesas: transacao.tipo === 'despesa' ? transacao.valor : 0
        })
      }
      
      return acc
    }, [])
    .sort((a, b) => new Date(a.data) - new Date(b.data))

  const dadosPizza = Object.entries(resumo.gastos_por_categoria || {}).map(([categoria, valor]) => ({
    name: categoria,
    value: valor
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center space-x-2">
            <DollarSign className="w-6 h-6" />
            <span>Sistema Financeiro</span>
          </h2>
          <p className="text-muted-foreground">
            Controle completo das suas finanças pessoais
          </p>
        </div>
        
        <div className="flex space-x-2">
          <Button variant="outline" onClick={carregarDados}>
            <TrendingUp className="w-4 h-4 mr-2" />
            Atualizar
          </Button>
          <Button onClick={gerarRelatorio}>
            <Download className="w-4 h-4 mr-2" />
            Relatório Excel
          </Button>
        </div>
      </div>

      {/* Cards de Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Saldo Total</p>
                <p className="text-2xl font-bold">{formatarMoeda(resumo.saldo_total || 0)}</p>
              </div>
              <Wallet className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Receitas (Mês)</p>
                <p className="text-2xl font-bold text-green-600">{formatarMoeda(resumo.receitas_mes || 0)}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Despesas (Mês)</p>
                <p className="text-2xl font-bold text-red-600">{formatarMoeda(resumo.despesas_mes || 0)}</p>
              </div>
              <TrendingDown className="w-8 h-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Economia (Mês)</p>
                <p className="text-2xl font-bold">{formatarMoeda((resumo.receitas_mes || 0) - (resumo.despesas_mes || 0))}</p>
              </div>
              <Target className="w-8 h-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="dashboard" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="transacoes">Transações</TabsTrigger>
          <TabsTrigger value="lembretes">Lembretes</TabsTrigger>
          <TabsTrigger value="recomendacoes">IA Financeira</TabsTrigger>
          <TabsTrigger value="nova">Nova Transação</TabsTrigger>
        </TabsList>

        {/* Dashboard */}
        <TabsContent value="dashboard" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gráfico de Linha */}
            <Card>
              <CardHeader>
                <CardTitle>Fluxo Financeiro (30 dias)</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={dadosGrafico}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="data" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatarMoeda(value)} />
                    <Line type="monotone" dataKey="receitas" stroke="#22c55e" strokeWidth={2} />
                    <Line type="monotone" dataKey="despesas" stroke="#ef4444" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Gráfico de Pizza */}
            <Card>
              <CardHeader>
                <CardTitle>Gastos por Categoria</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <Pie
                      data={dadosPizza}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {dadosPizza.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={cores[index % cores.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatarMoeda(value)} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Transações */}
        <TabsContent value="transacoes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Histórico de Transações</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {transacoes.map((transacao) => (
                  <div key={transacao.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className={`w-3 h-3 rounded-full ${transacao.tipo === 'receita' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                      <div>
                        <p className="font-medium">{transacao.descricao}</p>
                        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                          <Badge variant="outline">{transacao.categoria}</Badge>
                          <span>{formatarData(transacao.data)}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <p className={`font-bold ${transacao.tipo === 'receita' ? 'text-green-600' : 'text-red-600'}`}>
                        {transacao.tipo === 'receita' ? '+' : '-'}{formatarMoeda(transacao.valor)}
                      </p>
                    </div>
                  </div>
                ))}

                {transacoes.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <DollarSign className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Nenhuma transação encontrada</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Lembretes */}
        <TabsContent value="lembretes" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Lista de Lembretes */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Bell className="w-5 h-5" />
                  <span>Lembretes de Pagamento</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {lembretes.map((lembrete) => {
                    const diasRestantes = getDiasAteVencimento(lembrete.data_vencimento)
                    return (
                      <div key={lembrete.id} className="p-3 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-medium">{lembrete.titulo}</h3>
                          <Badge className={getCorLembrete(diasRestantes)}>
                            {diasRestantes < 0 ? `${Math.abs(diasRestantes)} dias atrasado` :
                             diasRestantes === 0 ? 'Vence hoje' :
                             `${diasRestantes} dias`}
                          </Badge>
                        </div>
                        
                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline">{lembrete.categoria}</Badge>
                            {lembrete.recorrente && <Badge variant="secondary">Recorrente</Badge>}
                          </div>
                          <div className="text-right">
                            {lembrete.valor && <p className="font-medium">{formatarMoeda(lembrete.valor)}</p>}
                            <p className="text-muted-foreground">{formatarData(lembrete.data_vencimento)}</p>
                          </div>
                        </div>
                      </div>
                    )
                  })}

                  {lembretes.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <Bell className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>Nenhum lembrete cadastrado</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Novo Lembrete */}
            <Card>
              <CardHeader>
                <CardTitle>Novo Lembrete</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="Título do lembrete"
                  value={novoLembrete.titulo}
                  onChange={(e) => setNovoLembrete(prev => ({ ...prev, titulo: e.target.value }))}
                />
                
                <Input
                  type="number"
                  placeholder="Valor (opcional)"
                  value={novoLembrete.valor}
                  onChange={(e) => setNovoLembrete(prev => ({ ...prev, valor: e.target.value }))}
                />
                
                <Input
                  type="date"
                  value={novoLembrete.data_vencimento}
                  onChange={(e) => setNovoLembrete(prev => ({ ...prev, data_vencimento: e.target.value }))}
                />
                
                <select 
                  value={novoLembrete.categoria}
                  onChange={(e) => setNovoLembrete(prev => ({ ...prev, categoria: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="conta">Conta</option>
                  <option value="cartao">Cartão</option>
                  <option value="financiamento">Financiamento</option>
                  <option value="investimento">Investimento</option>
                  <option value="outros">Outros</option>
                </select>
                
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="recorrente"
                    checked={novoLembrete.recorrente}
                    onChange={(e) => setNovoLembrete(prev => ({ ...prev, recorrente: e.target.checked }))}
                  />
                  <label htmlFor="recorrente" className="text-sm">Lembrete recorrente</label>
                </div>
                
                <Button onClick={adicionarLembrete} className="w-full">
                  <Plus className="w-4 h-4 mr-2" />
                  Criar Lembrete
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Recomendações IA */}
        <TabsContent value="recomendacoes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5" />
                <span>Recomendações Financeiras com IA</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recomendacoes.map((recomendacao, index) => (
                  <div key={index} className="p-4 border rounded-lg">
                    <div className="flex items-start space-x-3">
                      <div className={`w-2 h-2 rounded-full mt-2 ${
                        recomendacao.prioridade === 'alta' ? 'bg-red-500' :
                        recomendacao.prioridade === 'media' ? 'bg-yellow-500' : 'bg-green-500'
                      }`}></div>
                      <div className="flex-1">
                        <h3 className="font-medium mb-1">{recomendacao.titulo}</h3>
                        <p className="text-sm text-muted-foreground mb-2">{recomendacao.descricao}</p>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline">{recomendacao.categoria}</Badge>
                          <Badge className={
                            recomendacao.prioridade === 'alta' ? 'bg-red-100 text-red-800' :
                            recomendacao.prioridade === 'media' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }>
                            {recomendacao.prioridade}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {recomendacoes.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <AlertTriangle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Nenhuma recomendação disponível</p>
                    <p className="text-sm">Continue usando o sistema para receber dicas personalizadas</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Nova Transação */}
        <TabsContent value="nova" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Nova Transação</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Tipo</label>
                  <select 
                    value={novaTransacao.tipo}
                    onChange={(e) => setNovaTransacao(prev => ({ ...prev, tipo: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-md"
                  >
                    <option value="despesa">Despesa</option>
                    <option value="receita">Receita</option>
                  </select>
                </div>
                
                <div>
                  <label className="text-sm font-medium">Valor</label>
                  <Input
                    type="number"
                    placeholder="0,00"
                    value={novaTransacao.valor}
                    onChange={(e) => setNovaTransacao(prev => ({ ...prev, valor: e.target.value }))}
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Categoria</label>
                <select 
                  value={novaTransacao.categoria}
                  onChange={(e) => setNovaTransacao(prev => ({ ...prev, categoria: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="">Selecione uma categoria</option>
                  {categorias.map(categoria => (
                    <option key={categoria} value={categoria}>{categoria}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-sm font-medium">Descrição</label>
                <Input
                  placeholder="Descrição da transação"
                  value={novaTransacao.descricao}
                  onChange={(e) => setNovaTransacao(prev => ({ ...prev, descricao: e.target.value }))}
                />
              </div>

              <div>
                <label className="text-sm font-medium">Data</label>
                <Input
                  type="date"
                  value={novaTransacao.data}
                  onChange={(e) => setNovaTransacao(prev => ({ ...prev, data: e.target.value }))}
                />
              </div>

              <Button onClick={adicionarTransacao} className="w-full">
                <Plus className="w-4 h-4 mr-2" />
                Adicionar Transação
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default SistemaFinanceiro

