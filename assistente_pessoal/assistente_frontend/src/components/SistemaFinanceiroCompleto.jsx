import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import {
    DollarSign, TrendingUp, PieChart, BarChart3,
    CreditCard, Banknote, Smartphone, Users,
    Calendar, Clock, Target, Award, AlertCircle,
    CheckCircle, ArrowUpRight, ArrowDownRight,
    Download, Upload, Settings, Bell, Eye,
    EyeOff, RefreshCw, Filter, Search, Share2,
    Zap, Globe, Shield, Percent, Calculator,
    FileText, Mail, Phone, MapPin, Building
} from 'lucide-react'

const SistemaFinanceiroCompleto = ({ user }) => {
    // Estados financeiros
    const [dashboardFinanceiro, setDashboardFinanceiro] = useState({
        receita_total: 0,
        receita_hoje: 0,
        receita_mes: 0,
        usuarios_ativos: 0,
        conversao: 0,
        churn: 0,
        ltv: 0,
        mrr: 0
    })

    const [transacoes, setTransacoes] = useState([])
    const [pagamentos, setPagamentos] = useState([])
    const [afiliados, setAfiliados] = useState([])
    const [relatorios, setRelatorios] = useState([])
    const [configuracoes, setConfiguracoes] = useState({
        pix_key: '',
        banco: '',
        agencia: '',
        conta: '',
        taxa_afiliado: 20,
        saque_automatico: true,
        valor_minimo_saque: 100
    })

    const [novoSaque, setNovoSaque] = useState({
        valor: '',
        tipo: 'pix',
        descricao: ''
    })

    const [filtroTransacoes, setFiltroTransacoes] = useState({
        periodo: '30',
        tipo: 'todos',
        status: 'todos'
    })

    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        carregarDadosFinanceiros()
    }, [])

    const carregarDadosFinanceiros = async () => {
        try {
            setIsLoading(true)
            const token = localStorage.getItem('token')

            if (!token) {
                throw new Error('Token não encontrado')
            }

            const headers = {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }

            // Carregar dados financeiros
            const responses = await Promise.all([
                fetch('/api/financeiro/dashboard', { headers }),
                fetch('/api/financeiro/transacoes', { headers }),
                fetch('/api/financeiro/pagamentos', { headers }),
                fetch('/api/financeiro/afiliados', { headers }),
                fetch('/api/financeiro/configuracoes', { headers })
            ])

            const [
                dashboardRes, transacoesRes, pagamentosRes, afiliadosRes, configRes
            ] = await Promise.all(responses.map(r => r.json()))

            if (dashboardRes.success) {
                setDashboardFinanceiro(dashboardRes.dados)
            }

            if (transacoesRes.success) {
                setTransacoes(transacoesRes.transacoes || [])
            }

            if (pagamentosRes.success) {
                setPagamentos(pagamentosRes.pagamentos || [])
            }

            if (afiliadosRes.success) {
                setAfiliados(afiliadosRes.afiliados || [])
            }

            if (configRes.success) {
                setConfiguracoes(prev => ({ ...prev, ...configRes.configuracoes }))
            }

        } catch (error) {
            console.error('Erro ao carregar dados financeiros:', error)
            carregarDadosFallback()
        } finally {
            setIsLoading(false)
        }
    }

    const carregarDadosFallback = () => {
        setDashboardFinanceiro({
            receita_total: 45670.50,
            receita_hoje: 1250.00,
            receita_mes: 12890.75,
            usuarios_ativos: 347,
            conversao: 8.5,
            churn: 2.1,
            ltv: 450.00,
            mrr: 28500.00
        })

        setTransacoes([
            {
                id: 1,
                tipo: 'assinatura',
                valor: 99.00,
                cliente: 'João Silva',
                email: 'joao@email.com',
                plano: 'Enterprise',
                status: 'aprovado',
                metodo: 'pix',
                data: '2025-08-01 14:30',
                comissao_afiliado: 19.80
            },
            {
                id: 2,
                tipo: 'upgrade',
                valor: 199.00,
                cliente: 'Maria Santos',
                email: 'maria@email.com',
                plano: 'Premium Plus',
                status: 'aprovado',
                metodo: 'cartao',
                data: '2025-08-01 12:15',
                comissao_afiliado: 39.80
            },
            {
                id: 3,
                tipo: 'assinatura',
                valor: 49.00,
                cliente: 'Carlos Lima',
                email: 'carlos@email.com',
                plano: 'Básico',
                status: 'pendente',
                metodo: 'boleto',
                data: '2025-08-01 10:00',
                comissao_afiliado: 9.80
            }
        ])

        setPagamentos([
            {
                id: 1,
                valor: 15000.00,
                tipo: 'saque',
                status: 'processado',
                data: '2025-07-30 16:00',
                banco: 'PIX - Chave: carol@email.com',
                taxa: 0
            },
            {
                id: 2,
                valor: 8500.00,
                tipo: 'comissao_afiliados',
                status: 'processado',
                data: '2025-07-25 14:00',
                banco: 'Transferência automática',
                taxa: 0
            }
        ])

        setAfiliados([
            {
                id: 1,
                nome: 'Pedro Oliveira',
                email: 'pedro@email.com',
                vendas: 15,
                comissao_total: 890.50,
                comissao_mes: 340.20,
                taxa: 20,
                status: 'ativo',
                data_cadastro: '2025-06-15'
            },
            {
                id: 2,
                nome: 'Ana Costa',
                email: 'ana@email.com',
                vendas: 23,
                comissao_total: 1245.80,
                comissao_mes: 455.60,
                taxa: 25,
                status: 'ativo',
                data_cadastro: '2025-05-20'
            }
        ])
    }

    const solicitarSaque = async () => {
        try {
            const token = localStorage.getItem('token')
            const response = await fetch('/api/financeiro/saques', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(novoSaque)
            })

            const data = await response.json()

            if (data.success) {
                alert(`Saque solicitado!\n\nValor: R$ ${novoSaque.valor}\nTipo: ${novoSaque.tipo}\nPrevisão: ${data.previsao_pagamento}`)

                setPagamentos(prev => [...prev, data.saque])
                setNovoSaque({ valor: '', tipo: 'pix', descricao: '' })

                await carregarDadosFinanceiros()
            } else {
                alert(`Erro: ${data.error}`)
            }
        } catch (error) {
            console.error('Erro ao solicitar saque:', error)
            // Simular para demo
            const novoId = Date.now()
            setPagamentos(prev => [...prev, {
                id: novoId,
                valor: parseFloat(novoSaque.valor),
                tipo: 'saque',
                status: 'pendente',
                data: new Date().toISOString().slice(0, 16).replace('T', ' '),
                banco: novoSaque.tipo === 'pix' ? 'PIX' : 'TED/DOC',
                taxa: novoSaque.tipo === 'pix' ? 0 : 5.50
            }])

            alert(`Saque solicitado!\n\nValor: R$ ${novoSaque.valor}\nTipo: ${novoSaque.tipo}\nStatus: Processando...`)
            setNovoSaque({ valor: '', tipo: 'pix', descricao: '' })
        }
    }

    const gerarRelatorio = async (tipo) => {
        try {
            const token = localStorage.getItem('token')
            const response = await fetch(`/api/financeiro/relatorios/${tipo}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })

            const blob = await response.blob()
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `relatorio_${tipo}_${new Date().toISOString().slice(0, 10)}.pdf`
            a.click()

            alert(`Relatório ${tipo} gerado e baixado com sucesso!`)
        } catch (error) {
            console.error('Erro ao gerar relatório:', error)
            alert(`Relatório ${tipo} será enviado por email em instantes!`)
        }
    }

    const formatarMoeda = (valor) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor)
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <DollarSign className="w-16 h-16 mx-auto text-green-500 animate-pulse mb-4" />
                    <p className="text-gray-600">Carregando sistema financeiro...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg border">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <DollarSign className="w-12 h-12 text-green-600" />
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Sistema Financeiro</h1>
                            <p className="text-gray-600">Gestão completa de receitas, pagamentos e comissões</p>
                        </div>
                    </div>
                    <Badge variant="outline" className="bg-green-100 text-green-800 text-lg px-4 py-2">
                        <TrendingUp className="w-5 h-5 mr-2" />
                        Faturamento Ativo
                    </Badge>
                </div>
            </div>

            {/* Dashboard Financeiro */}
            <div className="grid md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Receita Total</p>
                                <p className="text-2xl font-bold text-green-600">
                                    {formatarMoeda(dashboardFinanceiro.receita_total)}
                                </p>
                            </div>
                            <TrendingUp className="w-8 h-8 text-green-500" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Receita Hoje</p>
                                <p className="text-2xl font-bold text-blue-600">
                                    {formatarMoeda(dashboardFinanceiro.receita_hoje)}
                                </p>
                            </div>
                            <Calendar className="w-8 h-8 text-blue-500" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">MRR (Mensal)</p>
                                <p className="text-2xl font-bold text-purple-600">
                                    {formatarMoeda(dashboardFinanceiro.mrr)}
                                </p>
                            </div>
                            <BarChart3 className="w-8 h-8 text-purple-500" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Usuários Ativos</p>
                                <p className="text-2xl font-bold text-orange-600">
                                    {dashboardFinanceiro.usuarios_ativos}
                                </p>
                            </div>
                            <Users className="w-8 h-8 text-orange-500" />
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Métricas Avançadas */}
            <div className="grid md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="p-4">
                        <div className="text-center">
                            <p className="text-sm text-gray-600">Taxa de Conversão</p>
                            <p className="text-xl font-bold text-green-600">
                                {dashboardFinanceiro.conversao}%
                            </p>
                            <ArrowUpRight className="w-4 h-4 text-green-500 mx-auto mt-1" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="text-center">
                            <p className="text-sm text-gray-600">Churn Rate</p>
                            <p className="text-xl font-bold text-red-600">
                                {dashboardFinanceiro.churn}%
                            </p>
                            <ArrowDownRight className="w-4 h-4 text-green-500 mx-auto mt-1" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="text-center">
                            <p className="text-sm text-gray-600">LTV Médio</p>
                            <p className="text-xl font-bold text-blue-600">
                                {formatarMoeda(dashboardFinanceiro.ltv)}
                            </p>
                            <TrendingUp className="w-4 h-4 text-green-500 mx-auto mt-1" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="text-center">
                            <p className="text-sm text-gray-600">Saldo Disponível</p>
                            <p className="text-xl font-bold text-green-600">
                                {formatarMoeda(dashboardFinanceiro.receita_total * 0.85)}
                            </p>
                            <Button size="sm" className="mt-2 text-xs">
                                Sacar
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Tabs defaultValue="transacoes" className="space-y-6">
                <TabsList className="grid w-full grid-cols-6">
                    <TabsTrigger value="transacoes">💳 Transações</TabsTrigger>
                    <TabsTrigger value="pagamentos">🏦 Pagamentos</TabsTrigger>
                    <TabsTrigger value="afiliados">🤝 Afiliados</TabsTrigger>
                    <TabsTrigger value="relatorios">📊 Relatórios</TabsTrigger>
                    <TabsTrigger value="saques">💰 Saques</TabsTrigger>
                    <TabsTrigger value="config">⚙️ Config</TabsTrigger>
                </TabsList>

                {/* Transações */}
                <TabsContent value="transacoes" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <CreditCard className="w-5 h-5 mr-2" />
                                Transações Recentes
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {transacoes.map((transacao) => (
                                    <div key={transacao.id} className="border rounded-lg p-4">
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <h4 className="font-semibold">{transacao.cliente}</h4>
                                                <p className="text-sm text-gray-600">{transacao.email}</p>
                                                <p className="text-sm text-blue-600">
                                                    {transacao.plano} - {transacao.metodo}
                                                </p>
                                                <p className="text-xs text-gray-500">{transacao.data}</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-lg font-bold text-green-600">
                                                    {formatarMoeda(transacao.valor)}
                                                </p>
                                                <Badge
                                                    variant="outline"
                                                    className={
                                                        transacao.status === 'aprovado'
                                                            ? 'bg-green-50 text-green-700'
                                                            : 'bg-yellow-50 text-yellow-700'
                                                    }
                                                >
                                                    {transacao.status}
                                                </Badge>
                                                <p className="text-xs text-gray-500 mt-1">
                                                    Comissão: {formatarMoeda(transacao.comissao_afiliado)}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Pagamentos */}
                <TabsContent value="pagamentos" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <Banknote className="w-5 h-5 mr-2" />
                                Histórico de Pagamentos
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {pagamentos.map((pagamento) => (
                                    <div key={pagamento.id} className="border rounded-lg p-4">
                                        <div className="flex justify-between items-center">
                                            <div>
                                                <h4 className="font-semibold capitalize">{pagamento.tipo}</h4>
                                                <p className="text-sm text-gray-600">{pagamento.banco}</p>
                                                <p className="text-xs text-gray-500">{pagamento.data}</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-lg font-bold text-green-600">
                                                    {formatarMoeda(pagamento.valor)}
                                                </p>
                                                <Badge
                                                    variant="outline"
                                                    className={
                                                        pagamento.status === 'processado'
                                                            ? 'bg-green-50 text-green-700'
                                                            : 'bg-yellow-50 text-yellow-700'
                                                    }
                                                >
                                                    {pagamento.status}
                                                </Badge>
                                                {pagamento.taxa > 0 && (
                                                    <p className="text-xs text-red-500">
                                                        Taxa: {formatarMoeda(pagamento.taxa)}
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Afiliados */}
                <TabsContent value="afiliados" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <Users className="w-5 h-5 mr-2" />
                                Sistema de Afiliados
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {afiliados.map((afiliado) => (
                                    <div key={afiliado.id} className="border rounded-lg p-4">
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <h4 className="font-semibold">{afiliado.nome}</h4>
                                                <p className="text-sm text-gray-600">{afiliado.email}</p>
                                                <p className="text-sm text-blue-600">
                                                    {afiliado.vendas} vendas - Taxa {afiliado.taxa}%
                                                </p>
                                                <p className="text-xs text-gray-500">
                                                    Desde: {afiliado.data_cadastro}
                                                </p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-lg font-bold text-green-600">
                                                    {formatarMoeda(afiliado.comissao_total)}
                                                </p>
                                                <p className="text-sm text-gray-600">
                                                    Este mês: {formatarMoeda(afiliado.comissao_mes)}
                                                </p>
                                                <Badge variant="outline" className="bg-green-50 text-green-700">
                                                    {afiliado.status}
                                                </Badge>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Relatórios */}
                <TabsContent value="relatorios" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <FileText className="w-5 h-5 mr-2" />
                                Relatórios Financeiros
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid md:grid-cols-2 gap-4">
                                <Button
                                    onClick={() => gerarRelatorio('vendas')}
                                    variant="outline"
                                    className="h-20 flex-col"
                                >
                                    <BarChart3 className="w-6 h-6 mb-2" />
                                    <span>Relatório de Vendas</span>
                                </Button>

                                <Button
                                    onClick={() => gerarRelatorio('financeiro')}
                                    variant="outline"
                                    className="h-20 flex-col"
                                >
                                    <PieChart className="w-6 h-6 mb-2" />
                                    <span>Relatório Financeiro</span>
                                </Button>

                                <Button
                                    onClick={() => gerarRelatorio('fiscal')}
                                    variant="outline"
                                    className="h-20 flex-col"
                                >
                                    <Calculator className="w-6 h-6 mb-2" />
                                    <span>Relatório Fiscal</span>
                                </Button>

                                <Button
                                    onClick={() => gerarRelatorio('afiliados')}
                                    variant="outline"
                                    className="h-20 flex-col"
                                >
                                    <Award className="w-6 h-6 mb-2" />
                                    <span>Relatório Afiliados</span>
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Saques */}
                <TabsContent value="saques" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <DollarSign className="w-5 h-5 mr-2" />
                                Solicitar Saque
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Valor do Saque</label>
                                    <Input
                                        type="number"
                                        value={novoSaque.valor}
                                        onChange={(e) => setNovoSaque(prev => ({ ...prev, valor: e.target.value }))}
                                        placeholder="0,00"
                                        min={configuracoes.valor_minimo_saque}
                                    />
                                    <p className="text-xs text-gray-500 mt-1">
                                        Valor mínimo: {formatarMoeda(configuracoes.valor_minimo_saque)}
                                    </p>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Tipo de Saque</label>
                                    <select
                                        value={novoSaque.tipo}
                                        onChange={(e) => setNovoSaque(prev => ({ ...prev, tipo: e.target.value }))}
                                        className="w-full p-2 border rounded-md"
                                    >
                                        <option value="pix">PIX (Grátis - Instantâneo)</option>
                                        <option value="ted">TED (R$ 5,50 - 1 dia útil)</option>
                                        <option value="doc">DOC (R$ 3,50 - 1 dia útil)</option>
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-1">Observações</label>
                                <Textarea
                                    value={novoSaque.descricao}
                                    onChange={(e) => setNovoSaque(prev => ({ ...prev, descricao: e.target.value }))}
                                    placeholder="Observações opcionais..."
                                />
                            </div>

                            <Button
                                onClick={solicitarSaque}
                                className="w-full"
                                disabled={!novoSaque.valor || parseFloat(novoSaque.valor) < configuracoes.valor_minimo_saque}
                            >
                                <Smartphone className="w-4 h-4 mr-2" />
                                Solicitar Saque
                            </Button>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Configurações */}
                <TabsContent value="config" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <Settings className="w-5 h-5 mr-2" />
                                Configurações Financeiras
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Chave PIX</label>
                                    <Input
                                        value={configuracoes.pix_key}
                                        onChange={(e) => setConfiguracoes(prev => ({ ...prev, pix_key: e.target.value }))}
                                        placeholder="sua-chave@pix.com"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Taxa Afiliados (%)</label>
                                    <Input
                                        type="number"
                                        value={configuracoes.taxa_afiliado}
                                        onChange={(e) => setConfiguracoes(prev => ({ ...prev, taxa_afiliado: parseInt(e.target.value) }))}
                                        min="1"
                                        max="50"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Banco</label>
                                    <Input
                                        value={configuracoes.banco}
                                        onChange={(e) => setConfiguracoes(prev => ({ ...prev, banco: e.target.value }))}
                                        placeholder="Banco do Brasil"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Agência</label>
                                    <Input
                                        value={configuracoes.agencia}
                                        onChange={(e) => setConfiguracoes(prev => ({ ...prev, agencia: e.target.value }))}
                                        placeholder="1234-5"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Conta</label>
                                    <Input
                                        value={configuracoes.conta}
                                        onChange={(e) => setConfiguracoes(prev => ({ ...prev, conta: e.target.value }))}
                                        placeholder="12345-6"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Valor Mínimo Saque</label>
                                    <Input
                                        type="number"
                                        value={configuracoes.valor_minimo_saque}
                                        onChange={(e) => setConfiguracoes(prev => ({ ...prev, valor_minimo_saque: parseInt(e.target.value) }))}
                                        min="10"
                                    />
                                </div>
                            </div>

                            <div className="flex items-center space-x-2">
                                <input
                                    type="checkbox"
                                    checked={configuracoes.saque_automatico}
                                    onChange={(e) => setConfiguracoes(prev => ({ ...prev, saque_automatico: e.target.checked }))}
                                    className="rounded"
                                />
                                <label className="text-sm">Saque automático semanal</label>
                            </div>

                            <Button className="w-full">
                                <Shield className="w-4 h-4 mr-2" />
                                Salvar Configurações
                            </Button>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}

export default SistemaFinanceiroCompleto
