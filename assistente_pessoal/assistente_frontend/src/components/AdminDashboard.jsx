import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import {
    Shield, Users, Gift, TrendingUp, DollarSign,
    Plus, Edit, Trash2, Eye, Calendar, Percent,
    Crown, Target, AlertCircle, CheckCircle
} from 'lucide-react'

const AdminDashboard = ({ user }) => {
    const [analytics, setAnalytics] = useState({})
    const [cupons, setCupons] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const [showCreateCupom, setShowCreateCupom] = useState(false)
    const [novoCupom, setNovoCupom] = useState({
        nome: '',
        descricao: '',
        tipo_desconto: 'percentual',
        valor_desconto: '',
        data_inicio: new Date().toISOString().split('T')[0],
        data_fim: '',
        max_usos_total: '',
        max_usos_por_usuario: 1,
        valor_minimo_compra: '',
        uso_interno: false
    })

    useEffect(() => {
        carregarDados()
    }, [])

    const carregarDados = async () => {
        try {
            setIsLoading(true)

            // Carrega analytics
            const responseAnalytics = await fetch('/api/subscription/analytics', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                }
            })

            if (responseAnalytics.ok) {
                const dataAnalytics = await responseAnalytics.json()
                setAnalytics(dataAnalytics)
            }

            // Carrega cupons
            const responseCupons = await fetch('/api/subscription/cupons', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                }
            })

            if (responseCupons.ok) {
                const dataCupons = await responseCupons.json()
                setCupons(dataCupons.cupons)
            }

        } catch (error) {
            console.error('Erro ao carregar dados:', error)
        } finally {
            setIsLoading(false)
        }
    }

    const criarCupom = async () => {
        try {
            const response = await fetch('/api/subscription/cupons', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: JSON.stringify(novoCupom)
            })

            if (response.ok) {
                await carregarDados()
                setShowCreateCupom(false)
                setNovoCupom({
                    nome: '',
                    descricao: '',
                    tipo_desconto: 'percentual',
                    valor_desconto: '',
                    data_inicio: new Date().toISOString().split('T')[0],
                    data_fim: '',
                    max_usos_total: '',
                    max_usos_por_usuario: 1,
                    valor_minimo_compra: '',
                    uso_interno: false
                })
                alert('Cupom criado com sucesso!')
            } else {
                const data = await response.json()
                alert(`Erro: ${data.erro}`)
            }

        } catch (error) {
            alert('Erro ao criar cupom')
        }
    }

    const gerarCupomGratuito = async () => {
        const email = prompt('Email do usuário:')
        if (!email) return

        const planoId = prompt('ID do plano (deixe vazio para escolher):')

        try {
            const response = await fetch('/api/subscription/cupons/gerar-gratuito', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: JSON.stringify({
                    email_usuario: email,
                    plano_id: planoId || null,
                    validade_dias: 30
                })
            })

            const data = await response.json()

            if (response.ok) {
                await carregarDados()
                alert(`Cupom criado! Código: ${data.cupom.codigo}\n\n${data.instrucoes}`)
            } else {
                alert(`Erro: ${data.erro}`)
            }

        } catch (error) {
            alert('Erro ao gerar cupom gratuito')
        }
    }

    const formatarData = (dateString) => {
        return new Date(dateString).toLocaleDateString('pt-BR')
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
                    <Shield className="w-16 h-16 mx-auto text-blue-500 animate-pulse mb-4" />
                    <p className="text-gray-600">Carregando dashboard administrativo...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Dashboard Administrativo</h1>
                    <p className="text-gray-600">Gerenciamento de assinaturas e cupons</p>
                </div>
                <Badge variant="outline" className="bg-red-50 text-red-700">
                    <Shield className="w-4 h-4 mr-1" />
                    Admin
                </Badge>
            </div>

            <Tabs defaultValue="analytics" className="space-y-6">
                <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="analytics">📊 Analytics</TabsTrigger>
                    <TabsTrigger value="cupons">🎫 Cupons</TabsTrigger>
                    <TabsTrigger value="acoes">⚡ Ações Rápidas</TabsTrigger>
                </TabsList>

                {/* Analytics */}
                <TabsContent value="analytics" className="space-y-6">
                    {/* Resumo Geral */}
                    <div className="grid md:grid-cols-4 gap-4">
                        <Card>
                            <CardContent className="p-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-gray-600">Total Assinaturas</p>
                                        <p className="text-2xl font-bold">{analytics.resumo?.total_assinaturas || 0}</p>
                                    </div>
                                    <Users className="w-8 h-8 text-blue-500" />
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardContent className="p-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-gray-600">Assinaturas Ativas</p>
                                        <p className="text-2xl font-bold text-green-600">{analytics.resumo?.assinaturas_ativas || 0}</p>
                                    </div>
                                    <CheckCircle className="w-8 h-8 text-green-500" />
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardContent className="p-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-gray-600">Receita Total</p>
                                        <p className="text-2xl font-bold text-blue-600">
                                            {formatarMoeda(analytics.resumo?.total_receita || 0)}
                                        </p>
                                    </div>
                                    <DollarSign className="w-8 h-8 text-blue-500" />
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardContent className="p-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-gray-600">Taxa Conversão</p>
                                        <p className="text-2xl font-bold text-purple-600">
                                            {analytics.resumo?.taxa_conversao || 0}%
                                        </p>
                                    </div>
                                    <TrendingUp className="w-8 h-8 text-purple-500" />
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Assinaturas por Plano */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Assinaturas por Plano</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {analytics.assinaturas_por_plano?.map((item, index) => (
                                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                        <div>
                                            <p className="font-medium">{item.plano}</p>
                                            <p className="text-sm text-gray-600">{item.total} assinaturas</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-bold text-green-600">{formatarMoeda(item.receita)}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Cupons Mais Usados */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Cupons Mais Usados</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {analytics.cupons_mais_usados?.map((cupom, index) => (
                                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                                        <div>
                                            <p className="font-mono font-bold text-purple-600">{cupom.codigo}</p>
                                            <p className="text-sm text-gray-600">{cupom.nome}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-medium">{cupom.usos} usos</p>
                                            <p className="text-sm text-red-600">-{formatarMoeda(cupom.desconto_total)}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Gestão de Cupons */}
                <TabsContent value="cupons" className="space-y-6">
                    <div className="flex justify-between items-center">
                        <h2 className="text-xl font-bold">Gestão de Cupons</h2>
                        <Button onClick={() => setShowCreateCupom(true)}>
                            <Plus className="w-4 h-4 mr-2" />
                            Novo Cupom
                        </Button>
                    </div>

                    {/* Lista de Cupons */}
                    <div className="grid gap-4">
                        {cupons.map((cupom) => (
                            <Card key={cupom.id} className={`${cupom.ativo ? '' : 'opacity-60'}`}>
                                <CardHeader className="pb-3">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-3">
                                            <div className="font-mono font-bold text-lg text-purple-600">
                                                {cupom.codigo}
                                            </div>
                                            <Badge variant={cupom.ativo ? 'default' : 'secondary'}>
                                                {cupom.ativo ? 'Ativo' : 'Inativo'}
                                            </Badge>
                                            {cupom.uso_interno && (
                                                <Badge variant="outline" className="bg-red-50 text-red-700">
                                                    Interno
                                                </Badge>
                                            )}
                                        </div>
                                        <div className="text-right">
                                            <p className="font-bold text-green-600">
                                                {cupom.tipo_desconto === 'gratuito' ? 'GRÁTIS' :
                                                    cupom.tipo_desconto === 'percentual' ? `${cupom.valor_desconto}%` :
                                                        formatarMoeda(cupom.valor_desconto)}
                                            </p>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="grid md:grid-cols-2 gap-4">
                                        <div>
                                            <h4 className="font-medium">{cupom.nome}</h4>
                                            <p className="text-sm text-gray-600 mb-2">{cupom.descricao}</p>
                                            <div className="text-xs text-gray-500 space-y-1">
                                                <p><strong>Válido:</strong> {formatarData(cupom.validade.data_inicio)} - {formatarData(cupom.validade.data_fim)}</p>
                                                {cupom.restricoes.valor_minimo_compra > 0 && (
                                                    <p><strong>Valor mínimo:</strong> {formatarMoeda(cupom.restricoes.valor_minimo_compra)}</p>
                                                )}
                                            </div>
                                        </div>
                                        <div>
                                            <div className="text-sm space-y-1">
                                                <div className="flex justify-between">
                                                    <span>Usos:</span>
                                                    <span className="font-medium">
                                                        {cupom.uso.usos_atual}/{cupom.uso.max_usos_total || '∞'}
                                                    </span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>Max por usuário:</span>
                                                    <span className="font-medium">{cupom.uso.max_usos_por_usuario}</span>
                                                </div>
                                                {cupom.uso.usos_restantes !== null && (
                                                    <div className="flex justify-between">
                                                        <span>Restantes:</span>
                                                        <span className="font-medium text-blue-600">{cupom.uso.usos_restantes}</span>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>

                    {/* Modal de Criar Cupom */}
                    {showCreateCupom && (
                        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
                            <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                                <CardHeader>
                                    <CardTitle>Criar Novo Cupom</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="grid md:grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium mb-1">Nome</label>
                                            <Input
                                                value={novoCupom.nome}
                                                onChange={(e) => setNovoCupom(prev => ({ ...prev, nome: e.target.value }))}
                                                placeholder="Nome do cupom"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium mb-1">Código (opcional)</label>
                                            <Input
                                                value={novoCupom.codigo || ''}
                                                onChange={(e) => setNovoCupom(prev => ({ ...prev, codigo: e.target.value.toUpperCase() }))}
                                                placeholder="Será gerado automaticamente"
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium mb-1">Descrição</label>
                                        <Textarea
                                            value={novoCupom.descricao}
                                            onChange={(e) => setNovoCupom(prev => ({ ...prev, descricao: e.target.value }))}
                                            placeholder="Descrição do cupom"
                                        />
                                    </div>

                                    <div className="grid md:grid-cols-3 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium mb-1">Tipo de Desconto</label>
                                            <select
                                                value={novoCupom.tipo_desconto}
                                                onChange={(e) => setNovoCupom(prev => ({ ...prev, tipo_desconto: e.target.value }))}
                                                className="w-full p-2 border rounded-md"
                                            >
                                                <option value="percentual">Percentual</option>
                                                <option value="valor_fixo">Valor Fixo</option>
                                                <option value="gratuito">Gratuito</option>
                                            </select>
                                        </div>
                                        {novoCupom.tipo_desconto !== 'gratuito' && (
                                            <div>
                                                <label className="block text-sm font-medium mb-1">
                                                    Valor {novoCupom.tipo_desconto === 'percentual' ? '(%)' : '(R$)'}
                                                </label>
                                                <Input
                                                    type="number"
                                                    value={novoCupom.valor_desconto}
                                                    onChange={(e) => setNovoCupom(prev => ({ ...prev, valor_desconto: e.target.value }))}
                                                    placeholder="0"
                                                />
                                            </div>
                                        )}
                                        <div>
                                            <label className="block text-sm font-medium mb-1">Max Usos Total</label>
                                            <Input
                                                type="number"
                                                value={novoCupom.max_usos_total}
                                                onChange={(e) => setNovoCupom(prev => ({ ...prev, max_usos_total: e.target.value }))}
                                                placeholder="Ilimitado"
                                            />
                                        </div>
                                    </div>

                                    <div className="grid md:grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium mb-1">Data Início</label>
                                            <Input
                                                type="date"
                                                value={novoCupom.data_inicio}
                                                onChange={(e) => setNovoCupom(prev => ({ ...prev, data_inicio: e.target.value }))}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium mb-1">Data Fim</label>
                                            <Input
                                                type="date"
                                                value={novoCupom.data_fim}
                                                onChange={(e) => setNovoCupom(prev => ({ ...prev, data_fim: e.target.value }))}
                                            />
                                        </div>
                                    </div>

                                    <div className="flex items-center space-x-2">
                                        <input
                                            type="checkbox"
                                            checked={novoCupom.uso_interno}
                                            onChange={(e) => setNovoCupom(prev => ({ ...prev, uso_interno: e.target.checked }))}
                                            className="rounded"
                                        />
                                        <label className="text-sm">Uso interno (apenas admins)</label>
                                    </div>

                                    <div className="flex justify-end space-x-2 pt-4 border-t">
                                        <Button variant="outline" onClick={() => setShowCreateCupom(false)}>
                                            Cancelar
                                        </Button>
                                        <Button onClick={criarCupom}>
                                            Criar Cupom
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    )}
                </TabsContent>

                {/* Ações Rápidas */}
                <TabsContent value="acoes" className="space-y-6">
                    <h2 className="text-xl font-bold">Ações Rápidas</h2>

                    <div className="grid md:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Gift className="w-5 h-5 mr-2 text-green-600" />
                                    Gerar Cupom Gratuito
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-gray-600 mb-4">
                                    Gera um cupom gratuito personalizado para um usuário específico.
                                </p>
                                <Button onClick={gerarCupomGratuito} className="w-full">
                                    <Crown className="w-4 h-4 mr-2" />
                                    Gerar Cupom Gratuito
                                </Button>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
                                    Recarregar Dados
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-gray-600 mb-4">
                                    Atualiza todas as informações do dashboard.
                                </p>
                                <Button onClick={carregarDados} variant="outline" className="w-full">
                                    <AlertCircle className="w-4 h-4 mr-2" />
                                    Recarregar Dashboard
                                </Button>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    )
}

export default AdminDashboard
