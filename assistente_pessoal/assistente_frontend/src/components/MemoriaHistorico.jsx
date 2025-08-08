import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  Search, Brain, Clock, MessageCircle, Lightbulb, 
  User, Bot, Trash2, Download, Filter, Star
} from 'lucide-react'

const MemoriaHistorico = () => {
  const [conversas, setConversas] = useState([])
  const [padroes, setPadroes] = useState([])
  const [memoriaImportante, setMemoriaImportante] = useState([])
  const [busca, setBusca] = useState('')
  const [pergunta, setPergunta] = useState('')
  const [respostaBusca, setRespostaBusca] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [filtroTipo, setFiltroTipo] = useState('')
  const [novaMemoria, setNovaMemoria] = useState({
    chave: '',
    valor: '',
    categoria: 'geral',
    importancia: 3
  })

  useEffect(() => {
    carregarDados()
  }, [])

  const carregarDados = async () => {
    try {
      // Carrega conversas
      const responseConversas = await fetch('/api/memoria/conversas?limit=20', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (responseConversas.ok) {
        const dataConversas = await responseConversas.json()
        setConversas(dataConversas.conversas)
      }

      // Carrega padrões
      const responsePadroes = await fetch('/api/memoria/padroes', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (responsePadroes.ok) {
        const dataPadroes = await responsePadroes.json()
        setPadroes(dataPadroes.padroes)
      }

      // Carrega contexto importante
      const responseContexto = await fetch('/api/memoria/contexto', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (responseContexto.ok) {
        const dataContexto = await responseContexto.json()
        setMemoriaImportante(dataContexto.memoria_importante || [])
      }

    } catch (error) {
      console.error('Erro ao carregar dados:', error)
    }
  }

  const buscarNaMemoria = async () => {
    if (!pergunta.trim()) return

    setIsLoading(true)
    try {
      const response = await fetch('/api/memoria/buscar', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({ pergunta })
      })

      if (response.ok) {
        const data = await response.json()
        setRespostaBusca(data.resposta)
      }
    } catch (error) {
      console.error('Erro na busca:', error)
      setRespostaBusca('Erro ao buscar na memória. Tente novamente.')
    } finally {
      setIsLoading(false)
    }
  }

  const salvarMemoriaImportante = async () => {
    if (!novaMemoria.chave || !novaMemoria.valor) return

    try {
      const response = await fetch('/api/memoria/contexto', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(novaMemoria)
      })

      if (response.ok) {
        setNovaMemoria({ chave: '', valor: '', categoria: 'geral', importancia: 3 })
        carregarDados()
      }
    } catch (error) {
      console.error('Erro ao salvar memória:', error)
    }
  }

  const limparMemoria = async () => {
    if (!confirm('Tem certeza que deseja limpar dados antigos da memória?')) return

    try {
      const response = await fetch('/api/memoria/limpar?dias=90', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        carregarDados()
        alert('Memória limpa com sucesso!')
      }
    } catch (error) {
      console.error('Erro ao limpar memória:', error)
    }
  }

  const conversasFiltradas = conversas.filter(conversa => {
    const matchBusca = !busca || 
      conversa.comando.toLowerCase().includes(busca.toLowerCase()) ||
      conversa.resposta.toLowerCase().includes(busca.toLowerCase())
    
    const matchTipo = !filtroTipo || conversa.tipo_interacao === filtroTipo

    return matchBusca && matchTipo
  })

  const formatarData = (timestamp) => {
    return new Date(timestamp).toLocaleString('pt-BR')
  }

  const getImportanciaColor = (importancia) => {
    switch (importancia) {
      case 5: return 'bg-red-100 text-red-800'
      case 4: return 'bg-orange-100 text-orange-800'
      case 3: return 'bg-yellow-100 text-yellow-800'
      case 2: return 'bg-blue-100 text-blue-800'
      case 1: return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getConfiancaColor = (confianca) => {
    if (confianca >= 0.8) return 'bg-green-100 text-green-800'
    if (confianca >= 0.6) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center space-x-2">
            <Brain className="w-6 h-6" />
            <span>Memória & Histórico</span>
          </h2>
          <p className="text-muted-foreground">
            Sistema inteligente de memória e busca em conversas
          </p>
        </div>
        
        <div className="flex space-x-2">
          <Button variant="outline" onClick={carregarDados}>
            <Clock className="w-4 h-4 mr-2" />
            Atualizar
          </Button>
          <Button variant="outline" onClick={limparMemoria}>
            <Trash2 className="w-4 h-4 mr-2" />
            Limpar Antiga
          </Button>
        </div>
      </div>

      {/* Busca Inteligente */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="w-5 h-5" />
            <span>Busca Inteligente na Memória</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex space-x-2">
            <Input
              placeholder="Pergunte algo sobre o passado... Ex: 'Lembra daquela reunião sobre vendas?'"
              value={pergunta}
              onChange={(e) => setPergunta(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && buscarNaMemoria()}
            />
            <Button onClick={buscarNaMemoria} disabled={isLoading}>
              {isLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
              ) : (
                <Search className="w-4 h-4" />
              )}
            </Button>
          </div>

          {respostaBusca && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start space-x-2">
                <Bot className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="font-medium text-blue-900">Resposta da IA:</p>
                  <p className="text-blue-800 mt-1">{respostaBusca}</p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Tabs defaultValue="conversas" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="conversas">Conversas</TabsTrigger>
          <TabsTrigger value="padroes">Padrões</TabsTrigger>
          <TabsTrigger value="memoria">Memória</TabsTrigger>
          <TabsTrigger value="nova">Nova Memória</TabsTrigger>
        </TabsList>

        {/* Aba Conversas */}
        <TabsContent value="conversas" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <MessageCircle className="w-5 h-5" />
                  <span>Histórico de Conversas</span>
                </CardTitle>
                
                <div className="flex space-x-2">
                  <Input
                    placeholder="Buscar conversas..."
                    value={busca}
                    onChange={(e) => setBusca(e.target.value)}
                    className="w-64"
                  />
                  <select 
                    value={filtroTipo}
                    onChange={(e) => setFiltroTipo(e.target.value)}
                    className="px-3 py-2 border rounded-md"
                  >
                    <option value="">Todos os tipos</option>
                    <option value="voz">Voz</option>
                    <option value="texto">Texto</option>
                    <option value="acao">Ação</option>
                  </select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {conversasFiltradas.map((conversa) => (
                  <div key={conversa.id} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">
                          {conversa.tipo_interacao}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {formatarData(conversa.timestamp)}
                        </span>
                      </div>
                      {conversa.acao_executada && (
                        <Badge variant="secondary">
                          {conversa.acao_executada}
                        </Badge>
                      )}
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-start space-x-2">
                        <User className="w-4 h-4 mt-1 text-blue-600" />
                        <div className="flex-1">
                          <p className="font-medium text-sm">Você:</p>
                          <p className="text-sm">{conversa.comando}</p>
                        </div>
                      </div>

                      <div className="flex items-start space-x-2">
                        <Bot className="w-4 h-4 mt-1 text-green-600" />
                        <div className="flex-1">
                          <p className="font-medium text-sm">Assistente:</p>
                          <p className="text-sm">{conversa.resposta}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {conversasFiltradas.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <MessageCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Nenhuma conversa encontrada</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aba Padrões */}
        <TabsContent value="padroes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Lightbulb className="w-5 h-5" />
                <span>Padrões Detectados</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {padroes.map((padrao) => (
                  <div key={padrao.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium">{padrao.tipo_padrao.replace('_', ' ').toUpperCase()}</h3>
                      <div className="flex items-center space-x-2">
                        <Badge className={getConfiancaColor(padrao.confianca)}>
                          {Math.round(padrao.confianca * 100)}% confiança
                        </Badge>
                        <Badge variant="outline">
                          {padrao.frequencia}x observado
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="text-sm text-muted-foreground">
                      <p>Dados: {JSON.stringify(padrao.dados_padrao, null, 2)}</p>
                      <p>Última ocorrência: {formatarData(padrao.ultima_ocorrencia)}</p>
                    </div>
                  </div>
                ))}

                {padroes.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <Lightbulb className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Nenhum padrão detectado ainda</p>
                    <p className="text-sm">Continue usando o assistente para que ele aprenda seus hábitos</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aba Memória Importante */}
        <TabsContent value="memoria" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Star className="w-5 h-5" />
                <span>Memória Importante</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {memoriaImportante.map((memoria) => (
                  <div key={memoria.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium">{memoria.chave}</h3>
                      <div className="flex items-center space-x-2">
                        <Badge className={getImportanciaColor(memoria.importancia)}>
                          Importância {memoria.importancia}/5
                        </Badge>
                        <Badge variant="outline">
                          {memoria.categoria}
                        </Badge>
                      </div>
                    </div>
                    
                    <p className="text-sm mb-2">{JSON.stringify(memoria.valor)}</p>
                    
                    <div className="text-xs text-muted-foreground">
                      <p>Criado: {formatarData(memoria.criado_em)}</p>
                      {memoria.expira_em && (
                        <p>Expira: {formatarData(memoria.expira_em)}</p>
                      )}
                    </div>
                  </div>
                ))}

                {memoriaImportante.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <Star className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Nenhuma memória importante salva</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aba Nova Memória */}
        <TabsContent value="nova" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Salvar Nova Memória Importante</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Chave/Título</label>
                  <Input
                    placeholder="Ex: Senha do WiFi, Aniversário da Maria..."
                    value={novaMemoria.chave}
                    onChange={(e) => setNovaMemoria(prev => ({ ...prev, chave: e.target.value }))}
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium">Categoria</label>
                  <select 
                    value={novaMemoria.categoria}
                    onChange={(e) => setNovaMemoria(prev => ({ ...prev, categoria: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-md"
                  >
                    <option value="geral">Geral</option>
                    <option value="pessoal">Pessoal</option>
                    <option value="trabalho">Trabalho</option>
                    <option value="financeiro">Financeiro</option>
                    <option value="saude">Saúde</option>
                    <option value="familia">Família</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Informação</label>
                <Textarea
                  placeholder="Digite a informação importante que deseja lembrar..."
                  value={novaMemoria.valor}
                  onChange={(e) => setNovaMemoria(prev => ({ ...prev, valor: e.target.value }))}
                  rows={3}
                />
              </div>

              <div>
                <label className="text-sm font-medium">Importância (1-5)</label>
                <select 
                  value={novaMemoria.importancia}
                  onChange={(e) => setNovaMemoria(prev => ({ ...prev, importancia: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value={1}>1 - Baixa</option>
                  <option value={2}>2 - Pouco importante</option>
                  <option value={3}>3 - Média</option>
                  <option value={4}>4 - Importante</option>
                  <option value={5}>5 - Muito importante</option>
                </select>
              </div>

              <Button onClick={salvarMemoriaImportante} className="w-full">
                <Star className="w-4 h-4 mr-2" />
                Salvar na Memória
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default MemoriaHistorico

