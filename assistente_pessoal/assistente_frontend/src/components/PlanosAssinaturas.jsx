import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import {
    Crown, Star, Check, X, CreditCard, Gift,
    Users, Database, Mic, Brain, FileSpreadsheet,
    Zap, Settings, Shield, ArrowRight, Sparkles
} from 'lucide-react'

const PlanosAssinaturas = ({ user }) => {
    const [planos, setPlanos] = useState([])
    const [assinaturaAtual, setAssinaturaAtual] = useState(null)
    const [cupomCodigo, setCupomCodigo] = useState('')
    const [cupomValidado, setCupomValidado] = useState(null)
    const [isLoading, setIsLoading] = useState(true)
    const [processandoPagamento, setProcessandoPagamento] = useState(false)

    useEffect(() => {
        carregarDados()
    }, [])

    const carregarDados = async () => {
        try {
            setIsLoading(true)

            // Carrega planos disponíveis
            const responsePlanos = await fetch('/api/subscription/planos')
            if (responsePlanos.ok) {
                const dataPlanos = await responsePlanos.json()
                setPlanos(dataPlanos.planos)
            }

            // Carrega assinatura atual
            const responseAssinatura = await fetch('/api/subscription/minha-assinatura', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                }
            })

            if (responseAssinatura.ok) {
                const dataAssinatura = await responseAssinatura.json()
                setAssinaturaAtual(dataAssinatura.assinatura)
            }

        } catch (error) {
            console.error('Erro ao carregar dados:', error)
        } finally {
            setIsLoading(false)
        }
    }

    const validarCupom = async (planoId) => {
        if (!cupomCodigo.trim()) {
            setCupomValidado(null)
            return
        }

        try {
            const response = await fetch('/api/subscription/validar-cupom', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: JSON.stringify({
                    codigo: cupomCodigo,
                    plano_id: planoId
                })
            })

            const data = await response.json()

            if (response.ok) {
                setCupomValidado(data)
            } else {
                setCupomValidado({ erro: data.erro })
            }

        } catch (error) {
            setCupomValidado({ erro: 'Erro ao validar cupom' })
        }
    }

    const assinarPlano = async (planoId, tipoPeriodo = 'mensal') => {
        try {
            setProcessandoPagamento(true)

            const dadosAssinatura = {
                plano_id: planoId,
                tipo_periodo: tipoPeriodo
            }

            if (cupomValidado && !cupomValidado.erro) {
                dadosAssinatura.cupom_codigo = cupomCodigo
            }

            const response = await fetch('/api/subscription/assinar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: JSON.stringify(dadosAssinatura)
            })

            const data = await response.json()

            if (response.ok) {
                // Sucesso - recarrega dados
                await carregarDados()
                setCupomCodigo('')
                setCupomValidado(null)

                alert('Assinatura ativada com sucesso!')
            } else {
                alert(`Erro: ${data.erro}`)
            }

        } catch (error) {
            alert('Erro ao processar assinatura')
        } finally {
            setProcessandoPagamento(false)
        }
    }

    const cancelarAssinatura = async () => {
        if (!confirm('Tem certeza que deseja cancelar sua assinatura?')) {
            return
        }

        try {
            const response = await fetch('/api/subscription/cancelar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: JSON.stringify({
                    motivo: 'Cancelamento solicitado pelo usuário'
                })
            })

            if (response.ok) {
                await carregarDados()
                alert('Assinatura cancelada com sucesso')
            }

        } catch (error) {
            alert('Erro ao cancelar assinatura')
        }
    }

    const iconesFuncionalidades = {
        voice_auth: Shield,
        speaker_diarization: Users,
        ai_avancada: Brain,
        relatorios_excel: FileSpreadsheet,
        automacao: Zap,
        api_access: Settings,
        suporte_prioritario: Star
    }

    const nomesFuncionalidades = {
        voice_auth: 'Autenticação por Voz',
        speaker_diarization: 'Reconhecimento de Falantes',
        ai_avancada: 'IA Avançada',
        relatorios_excel: 'Relatórios Excel',
        automacao: 'Centro de Automação',
        api_access: 'Acesso à API',
        suporte_prioritario: 'Suporte Prioritário'
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <Crown className="w-16 h-16 mx-auto text-blue-500 animate-pulse mb-4" />
                    <p className="text-gray-600">Carregando planos...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="text-center">
                <h1 className="text-3xl font-bold mb-2">Planos e Assinaturas</h1>
                <p className="text-gray-600">Escolha o plano ideal para suas necessidades</p>
            </div>

            {/* Assinatura Atual */}
            {assinaturaAtual && (
                <Card className="border-2 border-blue-200 bg-blue-50">
                    <CardHeader className="pb-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                                <Crown className="w-6 h-6 text-blue-600" />
                                <CardTitle className="text-blue-800">Sua Assinatura Atual</CardTitle>
                            </div>
                            <Badge variant="outline" className="bg-blue-100 text-blue-800">
                                {assinaturaAtual.status}
                            </Badge>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="grid md:grid-cols-2 gap-4">
                            <div>
                                <h3 className="font-semibold text-lg text-blue-800">
                                    {assinaturaAtual.plano?.nome}
                                </h3>
                                <p className="text-sm text-blue-600 mb-2">
                                    {assinaturaAtual.plano?.descricao}
                                </p>
                                <div className="text-sm text-blue-700">
                                    <p><strong>Tipo:</strong> {assinaturaAtual.tipo_periodo}</p>
                                    <p><strong>Expira em:</strong> {assinaturaAtual.dias_restantes} dias</p>
                                    {assinaturaAtual.pagamento?.cupom_usado && (
                                        <p><strong>Cupom usado:</strong> {assinaturaAtual.pagamento.cupom_usado}</p>
                                    )}
                                </div>
                            </div>

                            <div>
                                <h4 className="font-medium text-blue-800 mb-2">Uso Atual</h4>
                                <div className="space-y-2 text-sm">
                                    <div>
                                        <div className="flex justify-between">
                                            <span>Transações</span>
                                            <span>{assinaturaAtual.uso_atual?.transacoes_mes}/{assinaturaAtual.plano?.limites?.max_transacoes_mes}</span>
                                        </div>
                                        <div className="bg-blue-200 rounded-full h-2">
                                            <div
                                                className="bg-blue-600 h-2 rounded-full"
                                                style={{ width: `${assinaturaAtual.uso_atual?.percentual_uso?.transacoes || 0}%` }}
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <div className="flex justify-between">
                                            <span>Reuniões</span>
                                            <span>{assinaturaAtual.uso_atual?.reunioes_mes}/{assinaturaAtual.plano?.limites?.max_reunioes_mes}</span>
                                        </div>
                                        <div className="bg-blue-200 rounded-full h-2">
                                            <div
                                                className="bg-blue-600 h-2 rounded-full"
                                                style={{ width: `${assinaturaAtual.uso_atual?.percentual_uso?.reunioes || 0}%` }}
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div className="mt-4 pt-4 border-t border-blue-200">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={cancelarAssinatura}
                                        className="text-red-600 border-red-200 hover:bg-red-50"
                                    >
                                        Cancelar Assinatura
                                    </Button>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Cupom */}
            <Card>
                <CardHeader>
                    <div className="flex items-center space-x-2">
                        <Gift className="w-5 h-5 text-green-600" />
                        <CardTitle className="text-green-800">Tem um cupom?</CardTitle>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="flex space-x-2">
                        <Input
                            placeholder="Digite o código do cupom"
                            value={cupomCodigo}
                            onChange={(e) => setCupomCodigo(e.target.value.toUpperCase())}
                            className="flex-1"
                        />
                        <Button
                            onClick={() => validarCupom(planos[0]?.id)}
                            variant="outline"
                            disabled={!cupomCodigo.trim()}
                        >
                            Validar
                        </Button>
                    </div>

                    {cupomValidado && (
                        <div className="mt-3">
                            {cupomValidado.erro ? (
                                <div className="text-red-600 text-sm">
                                    ❌ {cupomValidado.erro}
                                </div>
                            ) : (
                                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                    <div className="text-green-800 font-medium">
                                        ✅ Cupom "{cupomValidado.cupom.codigo}" válido!
                                    </div>
                                    <div className="text-green-700 text-sm mt-1">
                                        {cupomValidado.cupom.nome} - {cupomValidado.cupom.descricao}
                                    </div>
                                    {cupomValidado.preview && (
                                        <div className="text-green-700 text-sm mt-2">
                                            <strong>Desconto:</strong> R$ {cupomValidado.preview.desconto.toFixed(2)}
                                            ({cupomValidado.preview.percentual_desconto}%)
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Lista de Planos */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {planos.map((plano) => (
                    <Card
                        key={plano.id}
                        className={`relative ${plano.nome === 'Pessoal' ? 'ring-2 ring-blue-500 ring-offset-2' : ''
                            }`}
                    >
                        {plano.nome === 'Pessoal' && (
                            <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                                <Badge className="bg-blue-500 text-white px-3 py-1">
                                    <Sparkles className="w-3 h-3 mr-1" />
                                    Mais Popular
                                </Badge>
                            </div>
                        )}

                        <CardHeader className="text-center pb-4">
                            <CardTitle className="text-xl">{plano.nome}</CardTitle>
                            <div className="text-3xl font-bold text-blue-600">
                                {plano.preco_mensal === 0 ? (
                                    'Grátis'
                                ) : (
                                    <>R$ {plano.preco_mensal.toFixed(2)}<span className="text-sm text-gray-500">/mês</span></>
                                )}
                            </div>
                            {plano.economia_anual?.percentual > 0 && (
                                <div className="text-sm text-green-600">
                                    Economize {plano.economia_anual.percentual}% pagando anual
                                </div>
                            )}
                            <p className="text-sm text-gray-600">{plano.descricao}</p>
                        </CardHeader>

                        <CardContent className="space-y-4">
                            {/* Limites */}
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="flex items-center">
                                        <Database className="w-4 h-4 mr-2" />
                                        Transações/mês
                                    </span>
                                    <span className="font-medium">{plano.limites.max_transacoes_mes}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="flex items-center">
                                        <Users className="w-4 h-4 mr-2" />
                                        Reuniões/mês
                                    </span>
                                    <span className="font-medium">{plano.limites.max_reunioes_mes}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="flex items-center">
                                        <Database className="w-4 h-4 mr-2" />
                                        Armazenamento
                                    </span>
                                    <span className="font-medium">{plano.limites.max_storage_gb}GB</span>
                                </div>
                            </div>

                            {/* Funcionalidades */}
                            <div className="border-t pt-4">
                                <h4 className="font-medium text-sm mb-2">Funcionalidades</h4>
                                <div className="space-y-1 text-sm">
                                    {Object.entries(plano.funcionalidades).map(([key, enabled]) => {
                                        const IconComponent = iconesFuncionalidades[key] || Settings
                                        const nome = nomesFuncionalidades[key] || key

                                        return (
                                            <div key={key} className="flex items-center">
                                                {enabled ? (
                                                    <Check className="w-4 h-4 text-green-500 mr-2" />
                                                ) : (
                                                    <X className="w-4 h-4 text-gray-300 mr-2" />
                                                )}
                                                <IconComponent className="w-4 h-4 mr-2" />
                                                <span className={enabled ? 'text-gray-900' : 'text-gray-400'}>
                                                    {nome}
                                                </span>
                                            </div>
                                        )
                                    })}
                                </div>
                            </div>

                            {/* Botões de Ação */}
                            <div className="border-t pt-4 space-y-2">
                                {assinaturaAtual?.plano?.id === plano.id ? (
                                    <Badge variant="outline" className="w-full text-center py-2">
                                        Plano Atual
                                    </Badge>
                                ) : plano.preco_mensal === 0 ? (
                                    <Button
                                        variant="outline"
                                        className="w-full"
                                        disabled
                                    >
                                        Plano Gratuito
                                    </Button>
                                ) : (
                                    <>
                                        <Button
                                            className="w-full"
                                            onClick={() => assinarPlano(plano.id, 'mensal')}
                                            disabled={processandoPagamento}
                                        >
                                            {processandoPagamento ? (
                                                'Processando...'
                                            ) : (
                                                <>
                                                    <CreditCard className="w-4 h-4 mr-2" />
                                                    Assinar Mensal
                                                </>
                                            )}
                                        </Button>

                                        {plano.preco_anual && (
                                            <Button
                                                variant="outline"
                                                className="w-full"
                                                onClick={() => assinarPlano(plano.id, 'anual')}
                                                disabled={processandoPagamento}
                                            >
                                                <ArrowRight className="w-4 h-4 mr-2" />
                                                Assinar Anual
                                            </Button>
                                        )}
                                    </>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Cupons Promocionais */}
            <Card className="bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200">
                <CardHeader>
                    <CardTitle className="text-purple-800">🎁 Cupons Promocionais Disponíveis</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                        <div className="bg-white rounded-lg p-4 border border-purple-200">
                            <div className="font-mono font-bold text-purple-600">WELCOME30</div>
                            <div className="text-purple-700">30% de desconto na primeira assinatura</div>
                        </div>
                        <div className="bg-white rounded-lg p-4 border border-purple-200">
                            <div className="font-mono font-bold text-purple-600">TESTE7DIAS</div>
                            <div className="text-purple-700">7 dias gratuitos do plano Pessoal</div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

export default PlanosAssinaturas
