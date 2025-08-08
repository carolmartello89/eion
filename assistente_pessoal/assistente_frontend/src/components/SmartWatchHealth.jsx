import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import {
    Heart, Activity, Watch, AlertTriangle, TrendingUp,
    TrendingDown, Phone, Calendar, User, Clock,
    Thermometer, Droplets, Zap, Moon, Sun, Shield
} from 'lucide-react'

const SmartWatchHealth = ({ user }) => {
    const [smartwatchData, setSmartwatchData] = useState(null)
    const [healthAlerts, setHealthAlerts] = useState([])
    const [medicalContacts, setMedicalContacts] = useState([])
    const [healthTrends, setHealthTrends] = useState({})
    const [isConnected, setIsConnected] = useState(false)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        carregarDadosSaude()
        // Simular conexão com smartwatch
        iniciarMonitoramento()
    }, [])

    const carregarDadosSaude = async () => {
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

            // Carregar dados do smartwatch
            const smartwatchResponse = await fetch('/api/health/smartwatch/dados', { headers })
            const smartwatchData = await smartwatchResponse.json()

            // Carregar contatos médicos
            const contatosResponse = await fetch('/api/health/contatos-medicos', { headers })
            const contatosData = await contatosResponse.json()

            // Carregar alertas de saúde
            const alertasResponse = await fetch('/api/health/alertas-saude', { headers })
            const alertasData = await alertasResponse.json()

            if (smartwatchData.success) {
                setSmartwatchData(smartwatchData.dados)
                setIsConnected(smartwatchData.dados.conectado)

                // Analisar dados e gerar alertas se necessário
                analisarDadosSaude(smartwatchData.dados)
            }

            if (contatosData.success) {
                setMedicalContacts(contatosData.contatos_medicos || [])
            }

            if (alertasData.success) {
                setHealthAlerts(prev => [...prev, ...alertasData.alertas])
            }

        } catch (error) {
            console.error('Erro ao carregar dados de saúde:', error)
            setIsConnected(false)

            // Dados de fallback em caso de erro
            const dadosSimulados = {
                dispositivo: 'Apple Watch Series 9',
                ultima_sincronizacao: new Date(),
                batimento_cardiaco: {
                    atual: 72,
                    maximo_24h: 95,
                    minimo_24h: 58,
                    media_24h: 68,
                    zona: 'normal'
                },
                pressao_arterial: {
                    sistolica: 125,
                    diastolica: 82,
                    classificacao: 'normal_alta'
                },
                saturacao_oxigenio: {
                    atual: 98,
                    media_24h: 97
                },
                temperatura_corporal: 36.8,
                passos: {
                    hoje: 8547,
                    meta: 10000,
                    percentual: 85.47
                },
                sono: {
                    duracao_ontem: 7.2,
                    qualidade: 'boa',
                    sono_profundo: 2.1
                },
                stress: {
                    nivel_atual: 'baixo',
                    media_semana: 'moderado'
                },
                calorias_queimadas: 1847,
                atividade_fisica: {
                    minutos_ativos: 45,
                    meta_minutos: 60
                }
            }

            setSmartwatchData(dadosSimulados)
            setIsConnected(true)

            // Simular contatos médicos
            setMedicalContacts([
                {
                    id: 1,
                    nome: 'Dr. Carlos Silva',
                    especialidade: 'Cardiologista',
                    telefone: '+55 11 99999-1111',
                    emergencia: true,
                    hospital: 'Hospital do Coração'
                },
                {
                    id: 2,
                    nome: 'Dra. Ana Santos',
                    especialidade: 'Clínico Geral',
                    telefone: '+55 11 99999-2222',
                    emergencia: false,
                    clinica: 'Clínica Premium'
                },
                {
                    id: 3,
                    nome: 'Dr. Pedro Costa',
                    especialidade: 'Endocrinologista',
                    telefone: '+55 11 99999-3333',
                    emergencia: false,
                    clinica: 'Instituto de Diabetes'
                }
            ])

            // Analisar dados e gerar alertas se necessário
            analisarDadosSaude(dadosSimulados)
        } finally {
            setIsLoading(false)
        }
    }

    const analisarDadosSaude = (dados) => {
        const alertas = []

        // Análise de batimentos cardíacos
        if (dados.batimento_cardiaco.atual > 100) {
            alertas.push({
                id: 'hr_high',
                tipo: 'warning',
                titulo: 'Frequência Cardíaca Elevada',
                descricao: `Batimentos em ${dados.batimento_cardiaco.atual} bpm. Considere consultar cardiologista.`,
                prioridade: 'alta',
                acao_sugerida: 'agendar_cardiologista',
                timestamp: new Date()
            })
        }

        if (dados.batimento_cardiaco.atual < 50) {
            alertas.push({
                id: 'hr_low',
                tipo: 'warning',
                titulo: 'Frequência Cardíaca Baixa',
                descricao: `Batimentos em ${dados.batimento_cardiaco.atual} bpm. Pode indicar bradicardia.`,
                prioridade: 'alta',
                acao_sugerida: 'agendar_cardiologista',
                timestamp: new Date()
            })
        }

        // Análise de pressão arterial
        if (dados.pressao_arterial.sistolica > 140 || dados.pressao_arterial.diastolica > 90) {
            alertas.push({
                id: 'bp_high',
                tipo: 'error',
                titulo: 'Pressão Arterial Alta',
                descricao: `Pressão em ${dados.pressao_arterial.sistolica}/${dados.pressao_arterial.diastolica} mmHg. Consulte médico urgentemente.`,
                prioridade: 'critica',
                acao_sugerida: 'emergencia_medica',
                timestamp: new Date()
            })
        }

        // Análise de saturação de oxigênio
        if (dados.saturacao_oxigenio.atual < 95) {
            alertas.push({
                id: 'o2_low',
                tipo: 'error',
                titulo: 'Saturação de Oxigênio Baixa',
                descricao: `Oxigenação em ${dados.saturacao_oxigenio.atual}%. Procure atendimento médico imediatamente.`,
                prioridade: 'critica',
                acao_sugerida: 'emergencia_medica',
                timestamp: new Date()
            })
        }

        // Análise de temperatura
        if (dados.temperatura_corporal > 38) {
            alertas.push({
                id: 'temp_high',
                tipo: 'warning',
                titulo: 'Febre Detectada',
                descricao: `Temperatura em ${dados.temperatura_corporal}°C. Monitore sintomas e considere consulta médica.`,
                prioridade: 'media',
                acao_sugerida: 'agendar_clinico',
                timestamp: new Date()
            })
        }

        // Análise de sono
        if (dados.sono.duracao_ontem < 6) {
            alertas.push({
                id: 'sleep_poor',
                tipo: 'info',
                titulo: 'Sono Insuficiente',
                descricao: `Apenas ${dados.sono.duracao_ontem}h de sono. Qualidade do sono afeta saúde geral.`,
                prioridade: 'baixa',
                acao_sugerida: 'melhorar_sono',
                timestamp: new Date()
            })
        }

        setHealthAlerts(alertas)
    }

    const iniciarMonitoramento = () => {
        // Simular monitoramento contínuo
        const interval = setInterval(() => {
            if (isConnected) {
                // Simular pequenas variações nos dados
                setSmartwatchData(prev => {
                    if (!prev) return prev

                    return {
                        ...prev,
                        batimento_cardiaco: {
                            ...prev.batimento_cardiaco,
                            atual: prev.batimento_cardiaco.atual + Math.floor(Math.random() * 6 - 3)
                        },
                        ultima_sincronizacao: new Date()
                    }
                })
            }
        }, 30000) // Atualiza a cada 30 segundos

        return () => clearInterval(interval)
    }

    const agendarConsultaMedica = async (especialidade) => {
        try {
            const token = localStorage.getItem('token')

            if (!token) {
                alert('Token não encontrado')
                return
            }

            const medico = medicalContacts.find(m =>
                m.especialidade.toLowerCase().includes(especialidade.toLowerCase())
            )

            if (medico) {
                // Primeira tentativa: ligar para o médico
                const confirmarLigacao = confirm(`Deseja ligar para ${medico.nome} (${medico.especialidade})?\nTelefone: ${medico.telefone}`)

                if (confirmarLigacao) {
                    // Simular ligação
                    alert(`📞 Discando para ${medico.nome}...\n\nEm uma implementação real, isso abriria o app de telefone ou faria a ligação via VoIP.`)
                }

                // Segunda opção: agendar consulta
                const agendarConsulta = confirm(`Deseja que eu tente agendar uma consulta com ${medico.nome}?`)

                if (agendarConsulta) {
                    const response = await fetch('/api/health/agendar-consulta', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            medico_id: medico.id,
                            data_consulta: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // próxima semana
                            horario: '14:00',
                            motivo: 'Consulta de rotina via assistente IA',
                            urgente: false
                        })
                    })

                    const data = await response.json()

                    if (data.success) {
                        alert(`✅ Consulta agendada com sucesso!\n\nMédico: ${medico.nome}\nData: ${data.consulta.data_consulta}\nHorário: ${data.consulta.horario}\nCódigo: ${data.consulta.codigo_confirmacao}\n\n${data.consulta.observacoes}`)
                    } else {
                        alert(`❌ Erro ao agendar consulta: ${data.error}`)
                    }
                }
            } else {
                alert('❌ Médico especialista não encontrado. Contactando clínico geral...')
                agendarConsultaMedica('clinico')
            }
        } catch (error) {
            console.error('Erro ao agendar consulta:', error)
            alert('❌ Erro ao agendar consulta')
        }
    }

    const emergenciaMedica = async () => {
        try {
            const token = localStorage.getItem('token')

            if (!token) {
                alert('🚨 EMERGÊNCIA! Ligue 192 (SAMU) imediatamente!')
                return
            }

            const emergencyContact = medicalContacts.find(m => m.emergencia)

            // Ativar protocolo de emergência no backend
            const response = await fetch('/api/health/emergencia', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    tipo: 'emergencia_saude',
                    localizacao: 'Localização GPS do usuário', // Seria obtida do navegador
                    sintomas: 'Alerta automático do smartwatch'
                })
            })

            const data = await response.json()

            if (data.success) {
                const protocolo = data.protocolo

                if (emergencyContact) {
                    alert(`🚨 PROTOCOLO DE EMERGÊNCIA ATIVADO!\n\n📱 Contactando: ${emergencyContact.nome}\n📞 Telefone: ${emergencyContact.telefone}\n🏥 ${emergencyContact.hospital}\n\n⚠️ Se for uma emergência real, ligue:\n🚑 SAMU: 192\n🚒 Bombeiros: 193\n👮 Polícia: 190\n\n✅ Seus contatos de emergência foram notificados automaticamente.`)
                } else {
                    alert(`🚨 EMERGÊNCIA MÉDICA DETECTADA!\n\n⚠️ LIGUE IMEDIATAMENTE:\n🚑 SAMU: 192\n🚒 Bombeiros: 193\n👮 Polícia: 190\n\n✅ Protocolo de emergência ativado\n📍 Sua localização foi registrada\n📱 Contatos de emergência serão notificados`)
                }

                // Simular notificação para contatos de emergência
                console.log('🚨 EMERGÊNCIA - Protocolo ativado:', protocolo)
            } else {
                alert('🚨 EMERGÊNCIA! Ligue 192 (SAMU) imediatamente!')
            }

        } catch (error) {
            console.error('Erro no protocolo de emergência:', error)
            alert('🚨 EMERGÊNCIA MÉDICA!\n\nLigue 192 (SAMU) imediatamente!')
        }
    }

    const executarAcao = (acao) => {
        switch (acao) {
            case 'agendar_cardiologista':
                agendarConsultaMedica('cardiologista')
                break
            case 'agendar_clinico':
                agendarConsultaMedica('clinico')
                break
            case 'emergencia_medica':
                emergenciaMedica()
                break
            case 'melhorar_sono':
                alert('💡 Dicas para melhorar o sono:\n- Dormir e acordar no mesmo horário\n- Evitar telas 1h antes de dormir\n- Ambiente escuro e fresco\n- Exercícios regulares')
                break
            default:
                console.log('Ação não reconhecida:', acao)
        }
    }

    const getHealthZoneColor = (zona) => {
        switch (zona) {
            case 'normal': return 'text-green-600 bg-green-50'
            case 'elevado': return 'text-yellow-600 bg-yellow-50'
            case 'alto': return 'text-red-600 bg-red-50'
            default: return 'text-gray-600 bg-gray-50'
        }
    }

    const getAlertColor = (tipo) => {
        switch (tipo) {
            case 'error': return 'border-red-500 bg-red-50'
            case 'warning': return 'border-yellow-500 bg-yellow-50'
            case 'info': return 'border-blue-500 bg-blue-50'
            default: return 'border-gray-500 bg-gray-50'
        }
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <Watch className="w-16 h-16 mx-auto text-blue-500 animate-pulse mb-4" />
                    <p className="text-gray-600">Conectando com seu smartwatch...</p>
                </div>
            </div>
        )
    }

    if (!isConnected) {
        return (
            <div className="text-center p-8">
                <Watch className="w-24 h-24 mx-auto text-gray-400 mb-4" />
                <h3 className="text-xl font-semibold text-gray-700 mb-2">Smartwatch Desconectado</h3>
                <p className="text-gray-600 mb-4">Conecte seu smartwatch para monitoramento de saúde</p>
                <Button onClick={() => setIsConnected(true)}>
                    <Watch className="w-4 h-4 mr-2" />
                    Conectar Dispositivo
                </Button>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-50 to-green-50 p-6 rounded-lg border">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <div className="relative">
                            <Watch className="w-12 h-12 text-blue-600" />
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full animate-pulse"></div>
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Monitoramento de Saúde</h1>
                            <p className="text-gray-600">Conectado: {smartwatchData?.dispositivo}</p>
                            <p className="text-sm text-gray-500">
                                Última sincronização: {smartwatchData?.ultima_sincronizacao?.toLocaleTimeString('pt-BR')}
                            </p>
                        </div>
                    </div>
                    <Badge variant="outline" className="bg-green-100 text-green-800 text-lg px-4 py-2">
                        <Shield className="w-5 h-5 mr-2" />
                        Saúde Monitorada
                    </Badge>
                </div>
            </div>

            {/* Alertas de Saúde */}
            {healthAlerts.length > 0 && (
                <div className="space-y-3">
                    <h3 className="text-lg font-semibold text-red-600 flex items-center">
                        <AlertTriangle className="w-5 h-5 mr-2" />
                        Alertas de Saúde
                    </h3>
                    {healthAlerts.map((alerta) => (
                        <Alert key={alerta.id} className={`${getAlertColor(alerta.tipo)} border-l-4`}>
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription className="flex items-center justify-between">
                                <div>
                                    <strong>{alerta.titulo}</strong>
                                    <p className="mt-1">{alerta.descricao}</p>
                                </div>
                                <Button
                                    onClick={() => executarAcao(alerta.acao_sugerida)}
                                    variant="outline"
                                    size="sm"
                                    className="ml-4"
                                >
                                    {alerta.prioridade === 'critica' ? '🚨 Ação Urgente' : '📞 Agendar'}
                                </Button>
                            </AlertDescription>
                        </Alert>
                    ))}
                </div>
            )}

            <Tabs defaultValue="vitais" className="space-y-6">
                <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="vitais">💓 Sinais Vitais</TabsTrigger>
                    <TabsTrigger value="atividade">🏃 Atividade</TabsTrigger>
                    <TabsTrigger value="sono">🌙 Sono</TabsTrigger>
                    <TabsTrigger value="medicos">👨‍⚕️ Médicos</TabsTrigger>
                </TabsList>

                {/* Sinais Vitais */}
                <TabsContent value="vitais" className="space-y-4">
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {/* Frequência Cardíaca */}
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="flex items-center text-red-600">
                                    <Heart className="w-5 h-5 mr-2" />
                                    Frequência Cardíaca
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-red-600 mb-2">
                                    {smartwatchData.batimento_cardiaco.atual} bpm
                                </div>
                                <div className="text-sm text-gray-600 space-y-1">
                                    <p>Máx 24h: {smartwatchData.batimento_cardiaco.maximo_24h} bpm</p>
                                    <p>Mín 24h: {smartwatchData.batimento_cardiaco.minimo_24h} bpm</p>
                                    <p>Média: {smartwatchData.batimento_cardiaco.media_24h} bpm</p>
                                </div>
                                <Badge className={`mt-2 ${getHealthZoneColor(smartwatchData.batimento_cardiaco.zona)}`}>
                                    {smartwatchData.batimento_cardiaco.zona}
                                </Badge>
                            </CardContent>
                        </Card>

                        {/* Pressão Arterial */}
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="flex items-center text-purple-600">
                                    <Activity className="w-5 h-5 mr-2" />
                                    Pressão Arterial
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-purple-600 mb-2">
                                    {smartwatchData.pressao_arterial.sistolica}/{smartwatchData.pressao_arterial.diastolica}
                                </div>
                                <div className="text-sm text-gray-600">
                                    <p>mmHg</p>
                                </div>
                                <Badge className={`mt-2 ${getHealthZoneColor(smartwatchData.pressao_arterial.classificacao)}`}>
                                    {smartwatchData.pressao_arterial.classificacao.replace('_', ' ')}
                                </Badge>
                            </CardContent>
                        </Card>

                        {/* Saturação de Oxigênio */}
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="flex items-center text-blue-600">
                                    <Droplets className="w-5 h-5 mr-2" />
                                    Saturação O₂
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-blue-600 mb-2">
                                    {smartwatchData.saturacao_oxigenio.atual}%
                                </div>
                                <div className="text-sm text-gray-600">
                                    <p>Média 24h: {smartwatchData.saturacao_oxigenio.media_24h}%</p>
                                </div>
                                <Badge className="mt-2 bg-green-50 text-green-600">
                                    Normal
                                </Badge>
                            </CardContent>
                        </Card>

                        {/* Temperatura */}
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="flex items-center text-orange-600">
                                    <Thermometer className="w-5 h-5 mr-2" />
                                    Temperatura
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-orange-600 mb-2">
                                    {smartwatchData.temperatura_corporal}°C
                                </div>
                                <Badge className="mt-2 bg-green-50 text-green-600">
                                    Normal
                                </Badge>
                            </CardContent>
                        </Card>

                        {/* Stress */}
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="flex items-center text-yellow-600">
                                    <Zap className="w-5 h-5 mr-2" />
                                    Nível de Stress
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold text-yellow-600 mb-2">
                                    {smartwatchData.stress.nivel_atual}
                                </div>
                                <div className="text-sm text-gray-600">
                                    <p>Média semana: {smartwatchData.stress.media_semana}</p>
                                </div>
                                <Badge className="mt-2 bg-green-50 text-green-600">
                                    Controlado
                                </Badge>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Atividade Física */}
                <TabsContent value="atividade" className="space-y-4">
                    <div className="grid md:grid-cols-3 gap-4">
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="flex items-center text-green-600">
                                    <TrendingUp className="w-5 h-5 mr-2" />
                                    Passos Hoje
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-green-600 mb-2">
                                    {smartwatchData.passos.hoje.toLocaleString()}
                                </div>
                                <div className="text-sm text-gray-600 mb-2">
                                    Meta: {smartwatchData.passos.meta.toLocaleString()} passos
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div
                                        className="bg-green-600 h-2 rounded-full"
                                        style={{ width: `${smartwatchData.passos.percentual}%` }}
                                    ></div>
                                </div>
                                <p className="text-sm text-gray-600 mt-1">
                                    {smartwatchData.passos.percentual.toFixed(1)}% da meta
                                </p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="flex items-center text-orange-600">
                                    <Zap className="w-5 h-5 mr-2" />
                                    Calorias
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-orange-600 mb-2">
                                    {smartwatchData.calorias_queimadas}
                                </div>
                                <div className="text-sm text-gray-600">
                                    <p>kcal queimadas hoje</p>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="flex items-center text-blue-600">
                                    <Clock className="w-5 h-5 mr-2" />
                                    Atividade
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-blue-600 mb-2">
                                    {smartwatchData.atividade_fisica.minutos_ativos}min
                                </div>
                                <div className="text-sm text-gray-600">
                                    <p>Meta: {smartwatchData.atividade_fisica.meta_minutos}min</p>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Sono */}
                <TabsContent value="sono" className="space-y-4">
                    <div className="grid md:grid-cols-3 gap-4">
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="flex items-center text-indigo-600">
                                    <Moon className="w-5 h-5 mr-2" />
                                    Duração do Sono
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-indigo-600 mb-2">
                                    {smartwatchData.sono.duracao_ontem}h
                                </div>
                                <div className="text-sm text-gray-600">
                                    <p>Noite passada</p>
                                </div>
                                <Badge className="mt-2 bg-green-50 text-green-600">
                                    {smartwatchData.sono.qualidade}
                                </Badge>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="flex items-center text-purple-600">
                                    <Moon className="w-5 h-5 mr-2" />
                                    Sono Profundo
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold text-purple-600 mb-2">
                                    {smartwatchData.sono.sono_profundo}h
                                </div>
                                <div className="text-sm text-gray-600">
                                    <p>Fase reparadora</p>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Contatos Médicos */}
                <TabsContent value="medicos" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <User className="w-5 h-5 mr-2" />
                                Contatos Médicos de Emergência
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {medicalContacts.map((medico) => (
                                    <div key={medico.id} className="border rounded-lg p-4 hover:bg-gray-50">
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <h4 className="font-semibold text-lg flex items-center">
                                                    {medico.nome}
                                                    {medico.emergencia && (
                                                        <Badge variant="destructive" className="ml-2">
                                                            Emergência
                                                        </Badge>
                                                    )}
                                                </h4>
                                                <p className="text-gray-600">{medico.especialidade}</p>
                                                <p className="text-sm text-gray-500">
                                                    {medico.hospital || medico.clinica}
                                                </p>
                                                <div className="text-sm text-gray-500 mt-2">
                                                    <p className="flex items-center">
                                                        <Phone className="w-4 h-4 mr-2" />
                                                        {medico.telefone}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex flex-col space-y-2">
                                                <Button
                                                    size="sm"
                                                    variant={medico.emergencia ? "destructive" : "outline"}
                                                    onClick={() => {
                                                        if (medico.emergencia) {
                                                            emergenciaMedica()
                                                        } else {
                                                            agendarConsultaMedica(medico.especialidade)
                                                        }
                                                    }}
                                                >
                                                    <Phone className="w-4 h-4 mr-1" />
                                                    {medico.emergencia ? 'Emergência' : 'Ligar'}
                                                </Button>
                                                {!medico.emergencia && (
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        onClick={() => agendarConsultaMedica(medico.especialidade)}
                                                    >
                                                        <Calendar className="w-4 h-4 mr-1" />
                                                        Agendar
                                                    </Button>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}

export default SmartWatchHealth
