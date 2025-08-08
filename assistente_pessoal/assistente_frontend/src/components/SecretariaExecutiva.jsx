import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import {
    Briefcase, Clock, Users, Phone, Mail, FileText,
    Calendar, AlertCircle, CheckCircle, Star, Target,
    Building, MapPin, Car, Coffee, Gift, Plane,
    MessageSquare, Video, Headphones, Archive,
    Heart, Watch
} from 'lucide-react'

import SmartWatchHealth from './SmartWatchHealth.jsx'
import SistemaMedicoCompleto from './SistemaMedicoCompleto.jsx'

const SecretariaExecutiva = ({ user }) => {
    const [executivo, setExecutivo] = useState({
        nome: '',
        cargo: '',
        empresa: '',
        preferencias: {},
        contatos_vip: [],
        agenda_preferencias: {}
    })

    const [tarefasUrgentes, setTarefasUrgentes] = useState([])
    const [compromissosHoje, setCompromissosHoje] = useState([])
    const [lembretesPessoais, setLembretesPessoais] = useState([])
    const [contatosVIP, setContatosVIP] = useState([])
    const [isLoading, setIsLoading] = useState(true)

    const [novaReserva, setNovaReserva] = useState({
        tipo: 'restaurante',
        local: '',
        data: '',
        horario: '',
        pessoas: 2,
        observacoes: ''
    })

    const [novaViagem, setNovaViagem] = useState({
        destino: '',
        data_ida: '',
        data_volta: '',
        tipo_hospedagem: 'hotel',
        classe_voo: 'executiva',
        observacoes: ''
    })

    useEffect(() => {
        carregarDadosExecutivos()
    }, [])

    const carregarDadosExecutivos = async () => {
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

            // Carregar dashboard executivo
            const dashboardResponse = await fetch('/api/secretaria/dashboard-executivo', { headers })
            const dashboardData = await dashboardResponse.json()

            // Carregar agenda de hoje
            const agendaResponse = await fetch('/api/secretaria/agenda-executiva', { headers })
            const agendaData = await agendaResponse.json()

            // Carregar tarefas urgentes
            const tarefasResponse = await fetch('/api/secretaria/tarefas-urgentes', { headers })
            const tarefasData = await tarefasResponse.json()

            // Carregar contatos VIP
            const contatosResponse = await fetch('/api/secretaria/contatos-vip', { headers })
            const contatosData = await contatosResponse.json()

            // Carregar lembretes pessoais
            const lembretesResponse = await fetch('/api/secretaria/lembretes-pessoais', { headers })
            const lembretesData = await lembretesResponse.json()

            // Carregar preferências
            const prefResponse = await fetch('/api/secretaria/preferencias', { headers })
            const prefData = await prefResponse.json()

            if (agendaData.success) {
                setCompromissosHoje(agendaData.agenda || [])
            }

            if (tarefasData.success) {
                setTarefasUrgentes(tarefasData.tarefas_urgentes || [])
            }

            if (contatosData.success) {
                setContatosVIP(contatosData.contatos_vip || [])
            }

            if (lembretesData.success) {
                setLembretesPessoais(lembretesData.lembretes_pessoais || [])
            }

            if (prefData.success) {
                setExecutivo(prevState => ({
                    ...prevState,
                    ...prefData.usuario,
                    preferencias: prefData.preferencias
                }))
            }

        } catch (error) {
            console.error('Erro ao carregar dados:', error)

            // Dados de fallback em caso de erro
            setExecutivo({
                nome: user?.preferred_name || 'Executivo',
                cargo: 'CEO',
                empresa: 'Empresa ABC',
                preferencias: {
                    horario_chegada: '08:00',
                    horario_saida: '18:00',
                    tempo_buffer_reunioes: 15,
                    restaurante_favorito: 'Fasano',
                    hotel_preferido: 'Copacabana Palace',
                    companhia_aerea: 'LATAM'
                }
            })

            setTarefasUrgentes([
                {
                    id: 1,
                    tipo: 'ligacao',
                    titulo: 'Retornar ligação do Dr. Silva',
                    prioridade: 'alta',
                    prazo: '16:00 hoje',
                    status: 'pendente'
                },
                {
                    id: 2,
                    tipo: 'documento',
                    titulo: 'Revisar contrato partnership',
                    prioridade: 'alta',
                    prazo: 'Amanhã 10h',
                    status: 'pendente'
                }
            ])

            setCompromissosHoje([
                {
                    id: 1,
                    titulo: 'Reunião Diretoria',
                    horario: '09:00',
                    duracao: '2h',
                    local: 'Sala Principal',
                    tipo: 'reuniao',
                    participantes: ['João', 'Maria', 'Pedro']
                },
                {
                    id: 2,
                    titulo: 'Almoço com investidores',
                    horario: '12:30',
                    duracao: '1h30',
                    local: 'Restaurante Fasano',
                    tipo: 'almoco',
                    observacoes: 'Mesa reservada em nome da empresa'
                }
            ])

            setContatosVIP([
                {
                    id: 1,
                    nome: 'Dr. Ricardo Silva',
                    cargo: 'Diretor Médico',
                    empresa: 'Hospital Premier',
                    telefone: '+55 11 99999-9999',
                    email: 'ricardo@premier.com.br',
                    categoria: 'saude',
                    preferencias: 'Prefere WhatsApp'
                }
            ])

            setLembretesPessoais([
                {
                    id: 1,
                    tipo: 'aniversario',
                    titulo: 'Aniversário da esposa',
                    data: '2025-08-15',
                    observacoes: 'Reservar Oro - mesa romântica'
                }
            ])
        } finally {
            setIsLoading(false)
        }
    }

    const agendarReserva = async () => {
        try {
            const token = localStorage.getItem('token')

            if (!token) {
                alert('Token não encontrado')
                return
            }

            const response = await fetch('/api/secretaria/reserva', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(novaReserva)
            })

            const data = await response.json()

            if (data.success) {
                alert(`Reserva agendada com sucesso!\nNúmero: ${data.reserva.numero_reserva}\nLocal: ${data.reserva.local}\nData: ${data.reserva.data} às ${data.reserva.horario}`)

                setNovaReserva({
                    tipo: 'restaurante',
                    local: '',
                    data: '',
                    horario: '',
                    pessoas: 2,
                    observacoes: ''
                })

                // Recarregar dados
                await carregarDadosExecutivos()
            } else {
                alert(`Erro ao agendar reserva: ${data.error}`)
            }

        } catch (error) {
            console.error('Erro ao agendar reserva:', error)
            alert('Erro ao agendar reserva')
        }
    }

    const organizarViagem = async () => {
        try {
            const token = localStorage.getItem('token')

            if (!token) {
                alert('Token não encontrado')
                return
            }

            const response = await fetch('/api/secretaria/viagem', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(novaViagem)
            })

            const data = await response.json()

            if (data.success) {
                alert(`Viagem organizada com sucesso!\nNúmero: ${data.viagem.numero_viagem}\nDestino: ${data.viagem.destino}\nPeríodo: ${data.viagem.data_ida} até ${data.viagem.data_volta}\n\nItinerário:\n- ${data.viagem.itinerario.voo_ida}\n- ${data.viagem.itinerario.hospedagem}\n- ${data.viagem.itinerario.voo_volta}\n- ${data.viagem.itinerario.transfer}`)

                setNovaViagem({
                    destino: '',
                    data_ida: '',
                    data_volta: '',
                    tipo_hospedagem: 'hotel',
                    classe_voo: 'executiva',
                    observacoes: ''
                })

                await carregarDadosExecutivos()
            } else {
                alert(`Erro ao organizar viagem: ${data.error}`)
            }

        } catch (error) {
            console.error('Erro ao organizar viagem:', error)
            alert('Erro ao organizar viagem')
        }
    }

    const marcarTarefaConcluida = async (tarefaId) => {
        try {
            const token = localStorage.getItem('token')

            if (!token) {
                alert('Token não encontrado')
                return
            }

            const response = await fetch(`/api/secretaria/tarefa-urgente/${tarefaId}/concluir`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            })

            const data = await response.json()

            if (data.success) {
                // Atualizar estado local
                setTarefasUrgentes(prev =>
                    prev.map(tarefa =>
                        tarefa.id === tarefaId
                            ? { ...tarefa, status: 'concluida' }
                            : tarefa
                    )
                )
            } else {
                alert(`Erro ao concluir tarefa: ${data.error}`)
            }

        } catch (error) {
            console.error('Erro ao concluir tarefa:', error)
            alert('Erro ao concluir tarefa')
        }
    }

    const iconesTipoCompromisso = {
        reuniao: Users,
        almoco: Coffee,
        viagem: Plane,
        evento: Star,
        ligacao: Phone
    }

    const coresPrioridade = {
        alta: 'bg-red-100 text-red-800 border-red-200',
        media: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        baixa: 'bg-green-100 text-green-800 border-green-200'
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <Briefcase className="w-16 h-16 mx-auto text-blue-500 animate-pulse mb-4" />
                    <p className="text-gray-600">Preparando sua secretária executiva...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg border">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <Briefcase className="w-12 h-12 text-blue-600" />
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Secretária Executiva</h1>
                            <p className="text-gray-600">Assistência pessoal de alto nível para {executivo.nome}</p>
                        </div>
                    </div>
                    <Badge variant="outline" className="bg-blue-100 text-blue-800 text-lg px-4 py-2">
                        <Star className="w-5 h-5 mr-2" />
                        Premium Executive
                    </Badge>
                </div>
            </div>

            {/* Dashboard Rápido */}
            <div className="grid md:grid-cols-5 gap-4">
                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Compromissos Hoje</p>
                                <p className="text-2xl font-bold text-blue-600">{compromissosHoje.length}</p>
                            </div>
                            <Calendar className="w-8 h-8 text-blue-500" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Tarefas Urgentes</p>
                                <p className="text-2xl font-bold text-red-600">
                                    {tarefasUrgentes.filter(t => t.status === 'pendente').length}
                                </p>
                            </div>
                            <AlertCircle className="w-8 h-8 text-red-500" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Saúde</p>
                                <p className="text-2xl font-bold text-green-600">Normal</p>
                            </div>
                            <div className="relative">
                                <Heart className="w-8 h-8 text-green-500" />
                                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Contatos VIP</p>
                                <p className="text-2xl font-bold text-purple-600">{contatosVIP.length}</p>
                            </div>
                            <Users className="w-8 h-8 text-purple-500" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Lembretes Pessoais</p>
                                <p className="text-2xl font-bold text-green-600">{lembretesPessoais.length}</p>
                            </div>
                            <Gift className="w-8 h-8 text-green-500" />
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Tabs defaultValue="agenda" className="space-y-6">
                <TabsList className="grid w-full grid-cols-7">
                    <TabsTrigger value="agenda">📅 Agenda</TabsTrigger>
                    <TabsTrigger value="tarefas">⚡ Urgente</TabsTrigger>
                    <TabsTrigger value="saude">💓 Saúde</TabsTrigger>
                    <TabsTrigger value="medico">🩺 Médico IA</TabsTrigger>
                    <TabsTrigger value="reservas">🍽️ Reservas</TabsTrigger>
                    <TabsTrigger value="viagens">✈️ Viagens</TabsTrigger>
                    <TabsTrigger value="contatos">👥 VIP</TabsTrigger>
                </TabsList>

                {/* Agenda Executiva */}
                <TabsContent value="agenda" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <Calendar className="w-5 h-5 mr-2" />
                                Agenda de Hoje - {new Date().toLocaleDateString('pt-BR')}
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {compromissosHoje.map((compromisso) => {
                                    const IconeCompromisso = iconesTipoCompromisso[compromisso.tipo] || Calendar

                                    return (
                                        <div key={compromisso.id} className="border rounded-lg p-4 hover:bg-gray-50">
                                            <div className="flex items-start justify-between">
                                                <div className="flex items-start space-x-3">
                                                    <IconeCompromisso className="w-6 h-6 text-blue-500 mt-1" />
                                                    <div>
                                                        <h4 className="font-semibold text-lg">{compromisso.titulo}</h4>
                                                        <div className="text-sm text-gray-600 space-y-1">
                                                            <p className="flex items-center">
                                                                <Clock className="w-4 h-4 mr-1" />
                                                                {compromisso.horario} ({compromisso.duracao})
                                                            </p>
                                                            <p className="flex items-center">
                                                                <MapPin className="w-4 h-4 mr-1" />
                                                                {compromisso.local}
                                                            </p>
                                                            {compromisso.participantes && (
                                                                <p className="flex items-center">
                                                                    <Users className="w-4 h-4 mr-1" />
                                                                    {compromisso.participantes.join(', ')}
                                                                </p>
                                                            )}
                                                            {compromisso.observacoes && (
                                                                <p className="text-blue-600 font-medium">
                                                                    💡 {compromisso.observacoes}
                                                                </p>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                                <Badge variant="outline" className="ml-2">
                                                    {compromisso.tipo}
                                                </Badge>
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Tarefas Urgentes */}
                <TabsContent value="tarefas" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center text-red-600">
                                <AlertCircle className="w-5 h-5 mr-2" />
                                Tarefas Urgentes & Importantes
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {tarefasUrgentes.map((tarefa) => (
                                    <div key={tarefa.id} className={`p-4 rounded-lg border-2 ${coresPrioridade[tarefa.prioridade]}`}>
                                        <div className="flex items-center justify-between">
                                            <div className="flex-1">
                                                <h4 className="font-semibold">{tarefa.titulo}</h4>
                                                <div className="text-sm mt-1">
                                                    <span className="font-medium">Prazo: </span>
                                                    {tarefa.prazo}
                                                </div>
                                            </div>
                                            <div className="flex items-center space-x-2">
                                                <Badge variant={tarefa.prioridade === 'alta' ? 'destructive' : 'secondary'}>
                                                    {tarefa.prioridade}
                                                </Badge>
                                                {tarefa.status === 'pendente' ? (
                                                    <Button
                                                        size="sm"
                                                        onClick={() => marcarTarefaConcluida(tarefa.id)}
                                                        variant="outline"
                                                    >
                                                        <CheckCircle className="w-4 h-4 mr-1" />
                                                        Concluir
                                                    </Button>
                                                ) : (
                                                    <Badge variant="outline" className="bg-green-50 text-green-700">
                                                        ✅ Concluída
                                                    </Badge>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Monitoramento de Saúde */}
                <TabsContent value="saude" className="space-y-4">
                    <SmartWatchHealth user={user} />
                </TabsContent>

                {/* Sistema Médico Completo */}
                <TabsContent value="medico" className="space-y-4">
                    <SistemaMedicoCompleto user={user} />
                </TabsContent>

                {/* Sistema de Reservas */}
                <TabsContent value="reservas" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <Coffee className="w-5 h-5 mr-2" />
                                Agendar Reservas
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Tipo de Reserva</label>
                                    <select
                                        value={novaReserva.tipo}
                                        onChange={(e) => setNovaReserva(prev => ({ ...prev, tipo: e.target.value }))}
                                        className="w-full p-2 border rounded-md"
                                    >
                                        <option value="restaurante">Restaurante</option>
                                        <option value="spa">Spa/Wellness</option>
                                        <option value="teatro">Teatro/Espetáculo</option>
                                        <option value="evento">Evento Corporativo</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Local</label>
                                    <Input
                                        value={novaReserva.local}
                                        onChange={(e) => setNovaReserva(prev => ({ ...prev, local: e.target.value }))}
                                        placeholder="Nome do estabelecimento"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Data</label>
                                    <Input
                                        type="date"
                                        value={novaReserva.data}
                                        onChange={(e) => setNovaReserva(prev => ({ ...prev, data: e.target.value }))}
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Horário</label>
                                    <Input
                                        type="time"
                                        value={novaReserva.horario}
                                        onChange={(e) => setNovaReserva(prev => ({ ...prev, horario: e.target.value }))}
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Número de Pessoas</label>
                                    <Input
                                        type="number"
                                        value={novaReserva.pessoas}
                                        onChange={(e) => setNovaReserva(prev => ({ ...prev, pessoas: parseInt(e.target.value) }))}
                                        min="1"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-1">Observações Especiais</label>
                                <Textarea
                                    value={novaReserva.observacoes}
                                    onChange={(e) => setNovaReserva(prev => ({ ...prev, observacoes: e.target.value }))}
                                    placeholder="Preferências, restrições alimentares, ocasião especial..."
                                    rows={3}
                                />
                            </div>

                            <Button onClick={agendarReserva} className="w-full">
                                <Coffee className="w-4 h-4 mr-2" />
                                Agendar Reserva
                            </Button>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Organização de Viagens */}
                <TabsContent value="viagens" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <Plane className="w-5 h-5 mr-2" />
                                Organizar Viagem Executiva
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Destino</label>
                                    <Input
                                        value={novaViagem.destino}
                                        onChange={(e) => setNovaViagem(prev => ({ ...prev, destino: e.target.value }))}
                                        placeholder="Cidade/País de destino"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Classe do Voo</label>
                                    <select
                                        value={novaViagem.classe_voo}
                                        onChange={(e) => setNovaViagem(prev => ({ ...prev, classe_voo: e.target.value }))}
                                        className="w-full p-2 border rounded-md"
                                    >
                                        <option value="primeira">Primeira Classe</option>
                                        <option value="executiva">Executiva</option>
                                        <option value="economica_premium">Econômica Premium</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Data de Ida</label>
                                    <Input
                                        type="date"
                                        value={novaViagem.data_ida}
                                        onChange={(e) => setNovaViagem(prev => ({ ...prev, data_ida: e.target.value }))}
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Data de Volta</label>
                                    <Input
                                        type="date"
                                        value={novaViagem.data_volta}
                                        onChange={(e) => setNovaViagem(prev => ({ ...prev, data_volta: e.target.value }))}
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Tipo de Hospedagem</label>
                                    <select
                                        value={novaViagem.tipo_hospedagem}
                                        onChange={(e) => setNovaViagem(prev => ({ ...prev, tipo_hospedagem: e.target.value }))}
                                        className="w-full p-2 border rounded-md"
                                    >
                                        <option value="hotel_5_estrelas">Hotel 5 Estrelas</option>
                                        <option value="resort_luxury">Resort Luxury</option>
                                        <option value="apart_hotel">Apart Hotel</option>
                                        <option value="casa_empresarial">Casa Empresarial</option>
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-1">Observações da Viagem</label>
                                <Textarea
                                    value={novaViagem.observacoes}
                                    onChange={(e) => setNovaViagem(prev => ({ ...prev, observacoes: e.target.value }))}
                                    placeholder="Preferências de hotel, transfer, reuniões agendadas..."
                                    rows={3}
                                />
                            </div>

                            <Button onClick={organizarViagem} className="w-full">
                                <Plane className="w-4 h-4 mr-2" />
                                Organizar Viagem Completa
                            </Button>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Contatos VIP */}
                <TabsContent value="contatos" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <Users className="w-5 h-5 mr-2" />
                                Contatos VIP e Importantes
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {contatosVIP.map((contato) => (
                                    <div key={contato.id} className="border rounded-lg p-4 hover:bg-gray-50">
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <h4 className="font-semibold text-lg">{contato.nome}</h4>
                                                <p className="text-gray-600">{contato.cargo} - {contato.empresa}</p>
                                                <div className="text-sm text-gray-500 mt-2 space-y-1">
                                                    <p className="flex items-center">
                                                        <Phone className="w-4 h-4 mr-2" />
                                                        {contato.telefone}
                                                    </p>
                                                    <p className="flex items-center">
                                                        <Mail className="w-4 h-4 mr-2" />
                                                        {contato.email}
                                                    </p>
                                                    {contato.preferencias && (
                                                        <p className="text-blue-600 font-medium">
                                                            💡 {contato.preferencias}
                                                        </p>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="flex flex-col space-y-2">
                                                <Badge variant="outline">{contato.categoria}</Badge>
                                                <div className="flex space-x-1">
                                                    <Button size="sm" variant="outline">
                                                        <Phone className="w-4 h-4" />
                                                    </Button>
                                                    <Button size="sm" variant="outline">
                                                        <Mail className="w-4 h-4" />
                                                    </Button>
                                                    <Button size="sm" variant="outline">
                                                        <MessageSquare className="w-4 h-4" />
                                                    </Button>
                                                </div>
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

export default SecretariaExecutiva
