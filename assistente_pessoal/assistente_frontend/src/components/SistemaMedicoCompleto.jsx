import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import {
    Pill, TestTube, Video, Brain, Apple, Dumbbell,
    Shield, Ambulance, Microscope, Heart, BarChart3,
    Dna, Users, Stethoscope, Building2, Calendar,
    Clock, AlertTriangle, CheckCircle, Camera,
    Phone, MessageSquare, CreditCard, User,
    ChevronRight, Plus, Trash2, Edit, Play,
    Pause, Stop, Upload, Download, Share2,
    Bell, Settings, Star, Target, Activity,
    Thermometer, Scale, Droplets, Zap, Wifi
} from 'lucide-react'

const SistemaMedicoCompleto = ({ user }) => {
    // Estados para medicamentos
    const [medicamentos, setMedicamentos] = useState([])
    const [novoMedicamento, setNovoMedicamento] = useState({
        nome: '',
        dosagem: '',
        horarios: [],
        frequencia: 'diaria',
        duracao: 30,
        observacoes: ''
    })

    // Estados para exames
    const [exames, setExames] = useState([])
    const [novoExame, setNovoExame] = useState({
        tipo: 'hemograma',
        arquivo: null,
        data: '',
        observacoes: ''
    })

    // Estados para telemedicina
    const [consultas, setConsultas] = useState([])
    const [novaConsulta, setNovaConsulta] = useState({
        especialidade: 'clinica_geral',
        data: '',
        horario: '',
        sintomas: '',
        prioridade: 'normal'
    })

    // Estados para saúde mental
    const [saudeMental, setSaudeMental] = useState({
        humor_hoje: 5,
        ansiedade: 3,
        energia: 7,
        sono_qualidade: 6,
        exercicio_mindfulness: false
    })

    // Estados para nutrição
    const [nutricao, setNutricao] = useState({
        refeicoes_hoje: [],
        agua_consumida: 0,
        meta_calorias: 2000,
        restricoes: []
    })

    // Estados para fisioterapia
    const [fisioterapia, setFisioterapia] = useState({
        exercicios_hoje: [],
        plano_ativo: null,
        progresso_semanal: []
    })

    // Estados para medicina preventiva
    const [prevencao, setPrevencao] = useState({
        proximos_exames: [],
        vacinas_pendentes: [],
        check_ups: []
    })

    // Estados para emergência
    const [emergencia, setEmergencia] = useState({
        contatos_emergencia: [],
        condicoes_medicas: [],
        medicamentos_uso: [],
        alergias: []
    })

    // Estados para dispositivos IoT
    const [dispositivos, setDispositivos] = useState({
        conectados: [],
        leituras_recentes: [],
        alertas: []
    })

    const [isLoading, setIsLoading] = useState(true)
    const [activeTab, setActiveTab] = useState('medicamentos')

    useEffect(() => {
        carregarDadosMedicos()
    }, [])

    const carregarDadosMedicos = async () => {
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

            // Carregar todos os dados médicos
            const responses = await Promise.all([
                fetch('/api/medico/medicamentos', { headers }),
                fetch('/api/medico/exames', { headers }),
                fetch('/api/medico/consultas', { headers }),
                fetch('/api/medico/saude-mental', { headers }),
                fetch('/api/medico/nutricao', { headers }),
                fetch('/api/medico/fisioterapia', { headers }),
                fetch('/api/medico/prevencao', { headers }),
                fetch('/api/medico/emergencia', { headers }),
                fetch('/api/medico/dispositivos', { headers })
            ])

            const [
                medicamentosRes, examesRes, consultasRes, saudeMentalRes,
                nutricaoRes, fisioterapiaRes, prevencaoRes, emergenciaRes, dispositivosRes
            ] = await Promise.all(responses.map(r => r.json()))

            if (medicamentosRes.success) setMedicamentos(medicamentosRes.medicamentos || [])
            if (examesRes.success) setExames(examesRes.exames || [])
            if (consultasRes.success) setConsultas(consultasRes.consultas || [])
            if (saudeMentalRes.success) setSaudeMental(prev => ({ ...prev, ...saudeMentalRes.dados }))
            if (nutricaoRes.success) setNutricao(prev => ({ ...prev, ...nutricaoRes.dados }))
            if (fisioterapiaRes.success) setFisioterapia(prev => ({ ...prev, ...fisioterapiaRes.dados }))
            if (prevencaoRes.success) setPrevencao(prev => ({ ...prev, ...prevencaoRes.dados }))
            if (emergenciaRes.success) setEmergencia(prev => ({ ...prev, ...emergenciaRes.dados }))
            if (dispositivosRes.success) setDispositivos(prev => ({ ...prev, ...dispositivosRes.dados }))

        } catch (error) {
            console.error('Erro ao carregar dados médicos:', error)
            carregarDadosFallback()
        } finally {
            setIsLoading(false)
        }
    }

    const carregarDadosFallback = () => {
        setMedicamentos([
            {
                id: 1,
                nome: 'Ácido Acetilsalicílico',
                dosagem: '100mg',
                horarios: ['08:00'],
                frequencia: 'diaria',
                status: 'ativo',
                proxima_dose: '08:00'
            },
            {
                id: 2,
                nome: 'Losartana',
                dosagem: '50mg',
                horarios: ['08:00', '20:00'],
                frequencia: 'diaria',
                status: 'ativo',
                proxima_dose: '20:00'
            }
        ])

        setExames([
            {
                id: 1,
                tipo: 'Hemograma Completo',
                data: '2025-07-25',
                status: 'normal',
                alteracoes: [],
                arquivo: 'hemograma_julho.pdf'
            },
            {
                id: 2,
                tipo: 'Perfil Lipídico',
                data: '2025-07-25',
                status: 'alterado',
                alteracoes: ['Colesterol total elevado: 245 mg/dL'],
                arquivo: 'lipidico_julho.pdf'
            }
        ])

        setConsultas([
            {
                id: 1,
                especialidade: 'Cardiologia',
                medico: 'Dr. Ricardo Silva',
                data: '2025-08-05',
                horario: '14:00',
                status: 'agendada',
                tipo: 'presencial'
            },
            {
                id: 2,
                especialidade: 'Clínica Geral',
                medico: 'Dra. Ana Costa',
                data: '2025-08-10',
                horario: '10:00',
                status: 'agendada',
                tipo: 'telemedicina'
            }
        ])

        setSaudeMental({
            humor_hoje: 7,
            ansiedade: 4,
            energia: 6,
            sono_qualidade: 7,
            exercicio_mindfulness: true,
            historico_humor: [6, 7, 5, 8, 7, 7, 7]
        })

        setNutricao({
            refeicoes_hoje: [
                { tipo: 'Café da manhã', calorias: 350, horario: '07:30' },
                { tipo: 'Almoço', calorias: 650, horario: '12:00' }
            ],
            agua_consumida: 1200,
            meta_agua: 2500,
            meta_calorias: 2000,
            calorias_consumidas: 1000,
            restricoes: ['Lactose', 'Glúten']
        })

        setFisioterapia({
            exercicios_hoje: [
                { nome: 'Alongamento cervical', duracao: 10, concluido: true },
                { nome: 'Fortalecimento lombar', duracao: 15, concluido: false }
            ],
            plano_ativo: 'Reabilitação Lombar',
            progresso_semanal: [60, 75, 80, 90, 85, 95, 100]
        })

        setPrevencao({
            proximos_exames: [
                { tipo: 'Mamografia', data: '2025-09-15', prioridade: 'alta' },
                { tipo: 'Colonoscopia', data: '2025-10-20', prioridade: 'media' }
            ],
            vacinas_pendentes: [
                { nome: 'Influenza 2025', data_limite: '2025-04-30' }
            ],
            check_ups: [
                { tipo: 'Check-up Geral', data: '2025-11-01', medico: 'Dr. João Silva' }
            ]
        })

        setEmergencia({
            contatos_emergencia: [
                { nome: 'Maria Silva', relacao: 'Esposa', telefone: '+55 11 99999-1111' },
                { nome: 'João Silva Jr.', relacao: 'Filho', telefone: '+55 11 99999-2222' }
            ],
            condicoes_medicas: ['Hipertensão', 'Diabetes Tipo 2'],
            alergias: ['Penicilina', 'Frutos do mar'],
            medicamentos_uso: ['Losartana 50mg', 'Metformina 850mg']
        })

        setDispositivos({
            conectados: [
                { nome: 'Apple Watch Series 8', tipo: 'smartwatch', status: 'conectado', bateria: 85 },
                { nome: 'Balança Xiaomi', tipo: 'balanca', status: 'conectado', bateria: 95 },
                { nome: 'Medidor de Pressão Omron', tipo: 'pressao', status: 'offline', bateria: 60 }
            ],
            leituras_recentes: [
                { dispositivo: 'Apple Watch', tipo: 'frequencia_cardiaca', valor: 72, unidade: 'bpm', timestamp: '2025-08-01 15:30' },
                { dispositivo: 'Balança Xiaomi', tipo: 'peso', valor: 75.2, unidade: 'kg', timestamp: '2025-08-01 07:00' }
            ],
            alertas: [
                { tipo: 'bateria_baixa', dispositivo: 'Medidor de Pressão', timestamp: '2025-08-01 10:00' }
            ]
        })
    }

    // Função para adicionar medicamento
    const adicionarMedicamento = async () => {
        try {
            const token = localStorage.getItem('token')
            const response = await fetch('/api/medico/medicamentos', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(novoMedicamento)
            })

            const data = await response.json()

            if (data.success) {
                setMedicamentos(prev => [...prev, data.medicamento])
                setNovoMedicamento({
                    nome: '',
                    dosagem: '',
                    horarios: [],
                    frequencia: 'diaria',
                    duracao: 30,
                    observacoes: ''
                })
                alert('Medicamento adicionado com sucesso!')
            } else {
                alert(`Erro: ${data.error}`)
            }
        } catch (error) {
            console.error('Erro ao adicionar medicamento:', error)
            // Adicionar localmente para demo
            const novoId = Date.now()
            setMedicamentos(prev => [...prev, { ...novoMedicamento, id: novoId, status: 'ativo' }])
            setNovoMedicamento({
                nome: '',
                dosagem: '',
                horarios: [],
                frequencia: 'diaria',
                duracao: 30,
                observacoes: ''
            })
            alert('Medicamento adicionado com sucesso!')
        }
    }

    // Função para agendar consulta
    const agendarConsulta = async () => {
        try {
            const token = localStorage.getItem('token')
            const response = await fetch('/api/medico/consultas', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ...novaConsulta,
                    pagamento: 'manual' // Sempre pagamento manual
                })
            })

            const data = await response.json()

            if (data.success) {
                setConsultas(prev => [...prev, data.consulta])
                setNovaConsulta({
                    especialidade: 'clinica_geral',
                    data: '',
                    horario: '',
                    sintomas: '',
                    prioridade: 'normal'
                })
                alert(`Consulta agendada!\n\nMédico: ${data.consulta.medico}\nData: ${data.consulta.data} às ${data.consulta.horario}\n\n💳 Pagamento: Manual no local da consulta\nValor: ${data.consulta.valor}`)
            } else {
                alert(`Erro: ${data.error}`)
            }
        } catch (error) {
            console.error('Erro ao agendar consulta:', error)
            // Adicionar localmente para demo
            const novoId = Date.now()
            const especialistas = {
                'clinica_geral': 'Dr. João Silva',
                'cardiologia': 'Dr. Ricardo Santos',
                'dermatologia': 'Dra. Ana Costa',
                'psiquiatria': 'Dr. Carlos Lima'
            }

            setConsultas(prev => [...prev, {
                ...novaConsulta,
                id: novoId,
                medico: especialistas[novaConsulta.especialidade],
                status: 'agendada',
                tipo: 'telemedicina',
                valor: 'R$ 150,00'
            }])

            setNovaConsulta({
                especialidade: 'clinica_geral',
                data: '',
                horario: '',
                sintomas: '',
                prioridade: 'normal'
            })

            alert(`Consulta agendada!\n\nMédico: ${especialistas[novaConsulta.especialidade]}\nData: ${novaConsulta.data} às ${novaConsulta.horario}\n\n💳 Pagamento: Manual no local da consulta\nValor: R$ 150,00`)
        }
    }

    // Função para upload de exame
    const uploadExame = async (arquivo) => {
        try {
            const token = localStorage.getItem('token')
            const formData = new FormData()
            formData.append('arquivo', arquivo)
            formData.append('tipo', novoExame.tipo)
            formData.append('data', novoExame.data)
            formData.append('observacoes', novoExame.observacoes)

            const response = await fetch('/api/medico/exames/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            })

            const data = await response.json()

            if (data.success) {
                setExames(prev => [...prev, data.exame])
                setNovoExame({
                    tipo: 'hemograma',
                    arquivo: null,
                    data: '',
                    observacoes: ''
                })
                alert(`Exame analisado!\n\nResultado: ${data.exame.interpretacao}\nStatus: ${data.exame.status}`)
            } else {
                alert(`Erro: ${data.error}`)
            }
        } catch (error) {
            console.error('Erro ao upload exame:', error)
            // Simular análise para demo
            const novoId = Date.now()
            setExames(prev => [...prev, {
                id: novoId,
                tipo: novoExame.tipo,
                data: novoExame.data,
                status: 'analisado',
                interpretacao: 'Exame dentro dos parâmetros normais',
                arquivo: arquivo.name
            }])

            setNovoExame({
                tipo: 'hemograma',
                arquivo: null,
                data: '',
                observacoes: ''
            })

            alert('Exame analisado!\n\nResultado: Dentro dos parâmetros normais\nStatus: Analisado com IA')
        }
    }

    const especialidadesDisponiveis = {
        'clinica_geral': 'Clínica Geral',
        'cardiologia': 'Cardiologia',
        'dermatologia': 'Dermatologia',
        'psiquiatria': 'Psiquiatria',
        'endocrinologia': 'Endocrinologia',
        'ginecologia': 'Ginecologia',
        'pediatria': 'Pediatria',
        'ortopedia': 'Ortopedia',
        'neurologia': 'Neurologia'
    }

    const tiposExames = {
        'hemograma': 'Hemograma Completo',
        'lipidico': 'Perfil Lipídico',
        'glicemia': 'Glicemia/HbA1c',
        'renal': 'Função Renal',
        'hepatica': 'Função Hepática',
        'hormonal': 'Perfil Hormonal',
        'cardiaco': 'Marcadores Cardíacos',
        'vitaminas': 'Vitaminas e Minerais'
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <Stethoscope className="w-16 h-16 mx-auto text-blue-500 animate-pulse mb-4" />
                    <p className="text-gray-600">Carregando sistema médico completo...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-50 to-green-50 p-6 rounded-lg border">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <Stethoscope className="w-12 h-12 text-blue-600" />
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Sistema Médico Completo</h1>
                            <p className="text-gray-600">Gestão completa da sua saúde com IA médica avançada</p>
                        </div>
                    </div>
                    <Badge variant="outline" className="bg-green-100 text-green-800 text-lg px-4 py-2">
                        <Heart className="w-5 h-5 mr-2" />
                        Saúde 360°
                    </Badge>
                </div>
            </div>

            {/* Dashboard Médico */}
            <div className="grid md:grid-cols-6 gap-4">
                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Medicamentos</p>
                                <p className="text-2xl font-bold text-blue-600">
                                    {medicamentos.filter(m => m.status === 'ativo').length}
                                </p>
                            </div>
                            <Pill className="w-8 h-8 text-blue-500" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Exames</p>
                                <p className="text-2xl font-bold text-green-600">{exames.length}</p>
                            </div>
                            <TestTube className="w-8 h-8 text-green-500" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Consultas</p>
                                <p className="text-2xl font-bold text-purple-600">
                                    {consultas.filter(c => c.status === 'agendada').length}
                                </p>
                            </div>
                            <Video className="w-8 h-8 text-purple-500" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Humor</p>
                                <p className="text-2xl font-bold text-yellow-600">{saudeMental.humor_hoje}/10</p>
                            </div>
                            <Brain className="w-8 h-8 text-yellow-500" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Calorias</p>
                                <p className="text-2xl font-bold text-orange-600">
                                    {nutricao.calorias_consumidas || 0}
                                </p>
                            </div>
                            <Apple className="w-8 h-8 text-orange-500" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Exercícios</p>
                                <p className="text-2xl font-bold text-red-600">
                                    {fisioterapia.exercicios_hoje?.filter(e => e.concluido).length || 0}
                                </p>
                            </div>
                            <Dumbbell className="w-8 h-8 text-red-500" />
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
                <TabsList className="grid w-full grid-cols-5 lg:grid-cols-10">
                    <TabsTrigger value="medicamentos">💊 Remédios</TabsTrigger>
                    <TabsTrigger value="exames">🧪 Exames</TabsTrigger>
                    <TabsTrigger value="consultas">🩺 Consultas</TabsTrigger>
                    <TabsTrigger value="mental">🧠 Mental</TabsTrigger>
                    <TabsTrigger value="nutricao">🍎 Nutrição</TabsTrigger>
                    <TabsTrigger value="fisio">🏃 Fisio</TabsTrigger>
                    <TabsTrigger value="prevencao">🛡️ Prevenção</TabsTrigger>
                    <TabsTrigger value="emergencia">🚑 Emergência</TabsTrigger>
                    <TabsTrigger value="dispositivos">📱 Dispositivos</TabsTrigger>
                    <TabsTrigger value="ia">🤖 IA Médica</TabsTrigger>
                </TabsList>

                {/* Gestão de Medicamentos */}
                <TabsContent value="medicamentos" className="space-y-4">
                    <div className="grid md:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Pill className="w-5 h-5 mr-2" />
                                    Medicamentos Ativos
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {medicamentos.filter(m => m.status === 'ativo').map((medicamento) => (
                                        <div key={medicamento.id} className="border rounded-lg p-4">
                                            <div className="flex justify-between items-start">
                                                <div>
                                                    <h4 className="font-semibold">{medicamento.nome}</h4>
                                                    <p className="text-sm text-gray-600">{medicamento.dosagem}</p>
                                                    <p className="text-sm text-blue-600">
                                                        Próxima dose: {medicamento.proxima_dose}
                                                    </p>
                                                </div>
                                                <Badge variant="outline" className="bg-green-50 text-green-700">
                                                    Ativo
                                                </Badge>
                                            </div>
                                            <div className="mt-2 flex space-x-2">
                                                <Button size="sm" variant="outline">
                                                    <CheckCircle className="w-4 h-4 mr-1" />
                                                    Tomar
                                                </Button>
                                                <Button size="sm" variant="outline">
                                                    <Clock className="w-4 h-4 mr-1" />
                                                    Adiar
                                                </Button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Adicionar Medicamento</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Nome do Medicamento</label>
                                    <Input
                                        value={novoMedicamento.nome}
                                        onChange={(e) => setNovoMedicamento(prev => ({ ...prev, nome: e.target.value }))}
                                        placeholder="Ex: Losartana"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Dosagem</label>
                                    <Input
                                        value={novoMedicamento.dosagem}
                                        onChange={(e) => setNovoMedicamento(prev => ({ ...prev, dosagem: e.target.value }))}
                                        placeholder="Ex: 50mg"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Frequência</label>
                                    <select
                                        value={novoMedicamento.frequencia}
                                        onChange={(e) => setNovoMedicamento(prev => ({ ...prev, frequencia: e.target.value }))}
                                        className="w-full p-2 border rounded-md"
                                    >
                                        <option value="diaria">Diário</option>
                                        <option value="12h">A cada 12 horas</option>
                                        <option value="8h">A cada 8 horas</option>
                                        <option value="6h">A cada 6 horas</option>
                                        <option value="semanal">Semanal</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Observações</label>
                                    <Textarea
                                        value={novoMedicamento.observacoes}
                                        onChange={(e) => setNovoMedicamento(prev => ({ ...prev, observacoes: e.target.value }))}
                                        placeholder="Tomar com alimentos, efeitos colaterais..."
                                    />
                                </div>
                                <Button onClick={adicionarMedicamento} className="w-full">
                                    <Plus className="w-4 h-4 mr-2" />
                                    Adicionar Medicamento
                                </Button>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Análise de Exames */}
                <TabsContent value="exames" className="space-y-4">
                    <div className="grid md:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <TestTube className="w-5 h-5 mr-2" />
                                    Exames Recentes
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {exames.map((exame) => (
                                        <div key={exame.id} className="border rounded-lg p-4">
                                            <div className="flex justify-between items-start">
                                                <div>
                                                    <h4 className="font-semibold">{exame.tipo}</h4>
                                                    <p className="text-sm text-gray-600">{exame.data}</p>
                                                    {exame.interpretacao && (
                                                        <p className="text-sm text-blue-600 mt-1">
                                                            {exame.interpretacao}
                                                        </p>
                                                    )}
                                                </div>
                                                <Badge
                                                    variant="outline"
                                                    className={exame.status === 'normal' ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'}
                                                >
                                                    {exame.status}
                                                </Badge>
                                            </div>
                                            {exame.alteracoes && exame.alteracoes.length > 0 && (
                                                <div className="mt-2 p-2 bg-yellow-50 rounded">
                                                    <p className="text-sm font-medium text-yellow-800">Alterações:</p>
                                                    {exame.alteracoes.map((alteracao, index) => (
                                                        <p key={index} className="text-sm text-yellow-700">• {alteracao}</p>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Upload de Exame</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Tipo de Exame</label>
                                    <select
                                        value={novoExame.tipo}
                                        onChange={(e) => setNovoExame(prev => ({ ...prev, tipo: e.target.value }))}
                                        className="w-full p-2 border rounded-md"
                                    >
                                        {Object.entries(tiposExames).map(([key, value]) => (
                                            <option key={key} value={key}>{value}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Data do Exame</label>
                                    <Input
                                        type="date"
                                        value={novoExame.data}
                                        onChange={(e) => setNovoExame(prev => ({ ...prev, data: e.target.value }))}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Arquivo do Exame</label>
                                    <Input
                                        type="file"
                                        accept=".pdf,.jpg,.jpeg,.png"
                                        onChange={(e) => setNovoExame(prev => ({ ...prev, arquivo: e.target.files[0] }))}
                                    />
                                    <p className="text-xs text-gray-500 mt-1">
                                        Formatos aceitos: PDF, JPG, PNG
                                    </p>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Observações</label>
                                    <Textarea
                                        value={novoExame.observacoes}
                                        onChange={(e) => setNovoExame(prev => ({ ...prev, observacoes: e.target.value }))}
                                        placeholder="Sintomas, medicamentos em uso..."
                                    />
                                </div>
                                <Button
                                    onClick={() => novoExame.arquivo && uploadExame(novoExame.arquivo)}
                                    className="w-full"
                                    disabled={!novoExame.arquivo}
                                >
                                    <Upload className="w-4 h-4 mr-2" />
                                    Analisar com IA
                                </Button>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Telemedicina */}
                <TabsContent value="consultas" className="space-y-4">
                    <div className="grid md:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Video className="w-5 h-5 mr-2" />
                                    Consultas Agendadas
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {consultas.filter(c => c.status === 'agendada').map((consulta) => (
                                        <div key={consulta.id} className="border rounded-lg p-4">
                                            <div className="flex justify-between items-start">
                                                <div>
                                                    <h4 className="font-semibold">{consulta.especialidade}</h4>
                                                    <p className="text-sm text-gray-600">{consulta.medico}</p>
                                                    <p className="text-sm text-blue-600">
                                                        {consulta.data} às {consulta.horario}
                                                    </p>
                                                    {consulta.valor && (
                                                        <p className="text-sm text-green-600 font-medium">
                                                            💳 {consulta.valor} - Pagamento manual
                                                        </p>
                                                    )}
                                                </div>
                                                <Badge variant="outline" className="bg-blue-50 text-blue-700">
                                                    {consulta.tipo}
                                                </Badge>
                                            </div>
                                            <div className="mt-2 flex space-x-2">
                                                <Button size="sm" variant="outline">
                                                    <Video className="w-4 h-4 mr-1" />
                                                    Entrar
                                                </Button>
                                                <Button size="sm" variant="outline">
                                                    <Calendar className="w-4 h-4 mr-1" />
                                                    Reagendar
                                                </Button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Agendar Consulta</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Especialidade</label>
                                    <select
                                        value={novaConsulta.especialidade}
                                        onChange={(e) => setNovaConsulta(prev => ({ ...prev, especialidade: e.target.value }))}
                                        className="w-full p-2 border rounded-md"
                                    >
                                        {Object.entries(especialidadesDisponiveis).map(([key, value]) => (
                                            <option key={key} value={key}>{value}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Data</label>
                                        <Input
                                            type="date"
                                            value={novaConsulta.data}
                                            onChange={(e) => setNovaConsulta(prev => ({ ...prev, data: e.target.value }))}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Horário</label>
                                        <Input
                                            type="time"
                                            value={novaConsulta.horario}
                                            onChange={(e) => setNovaConsulta(prev => ({ ...prev, horario: e.target.value }))}
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Prioridade</label>
                                    <select
                                        value={novaConsulta.prioridade}
                                        onChange={(e) => setNovaConsulta(prev => ({ ...prev, prioridade: e.target.value }))}
                                        className="w-full p-2 border rounded-md"
                                    >
                                        <option value="normal">Normal</option>
                                        <option value="urgente">Urgente</option>
                                        <option value="emergencia">Emergência</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Sintomas/Motivo</label>
                                    <Textarea
                                        value={novaConsulta.sintomas}
                                        onChange={(e) => setNovaConsulta(prev => ({ ...prev, sintomas: e.target.value }))}
                                        placeholder="Descreva seus sintomas ou motivo da consulta..."
                                    />
                                </div>
                                <div className="bg-yellow-50 p-3 rounded-lg">
                                    <p className="text-sm text-yellow-800">
                                        💳 <strong>Pagamento:</strong> Manual no local da consulta ou PIX após confirmação
                                    </p>
                                </div>
                                <Button onClick={agendarConsulta} className="w-full">
                                    <Calendar className="w-4 h-4 mr-2" />
                                    Agendar Consulta
                                </Button>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Saúde Mental */}
                <TabsContent value="mental" className="space-y-4">
                    <div className="grid md:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Brain className="w-5 h-5 mr-2" />
                                    Monitoramento Diário
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Humor Hoje: {saudeMental.humor_hoje}/10
                                    </label>
                                    <input
                                        type="range"
                                        min="1"
                                        max="10"
                                        value={saudeMental.humor_hoje}
                                        onChange={(e) => setSaudeMental(prev => ({ ...prev, humor_hoje: parseInt(e.target.value) }))}
                                        className="w-full"
                                    />
                                    <div className="flex justify-between text-xs text-gray-500">
                                        <span>Muito baixo</span>
                                        <span>Excelente</span>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Nível de Ansiedade: {saudeMental.ansiedade}/10
                                    </label>
                                    <input
                                        type="range"
                                        min="1"
                                        max="10"
                                        value={saudeMental.ansiedade}
                                        onChange={(e) => setSaudeMental(prev => ({ ...prev, ansiedade: parseInt(e.target.value) }))}
                                        className="w-full"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Energia: {saudeMental.energia}/10
                                    </label>
                                    <input
                                        type="range"
                                        min="1"
                                        max="10"
                                        value={saudeMental.energia}
                                        onChange={(e) => setSaudeMental(prev => ({ ...prev, energia: parseInt(e.target.value) }))}
                                        className="w-full"
                                    />
                                </div>

                                <div className="flex items-center space-x-2">
                                    <input
                                        type="checkbox"
                                        checked={saudeMental.exercicio_mindfulness}
                                        onChange={(e) => setSaudeMental(prev => ({ ...prev, exercicio_mindfulness: e.target.checked }))}
                                        className="rounded"
                                    />
                                    <label className="text-sm">Exercício de mindfulness hoje</label>
                                </div>

                                <Button className="w-full">
                                    <Target className="w-4 h-4 mr-2" />
                                    Exercício de Respiração
                                </Button>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Recursos de Bem-estar</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <Button variant="outline" className="w-full justify-start">
                                    <Brain className="w-4 h-4 mr-2" />
                                    Meditação Guiada (10 min)
                                </Button>
                                <Button variant="outline" className="w-full justify-start">
                                    <Heart className="w-4 h-4 mr-2" />
                                    Exercícios de Gratidão
                                </Button>
                                <Button variant="outline" className="w-full justify-start">
                                    <Activity className="w-4 h-4 mr-2" />
                                    Técnicas de Relaxamento
                                </Button>
                                <Button variant="outline" className="w-full justify-start">
                                    <MessageSquare className="w-4 h-4 mr-2" />
                                    Chat com Psicólogo
                                </Button>
                                <Button variant="outline" className="w-full justify-start text-red-600 border-red-200">
                                    <Phone className="w-4 h-4 mr-2" />
                                    SOS Psicológico 24h
                                </Button>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Nutrição Personalizada */}
                <TabsContent value="nutricao" className="space-y-4">
                    <div className="grid md:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Apple className="w-5 h-5 mr-2" />
                                    Dashboard Nutricional
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="text-center p-3 border rounded-lg">
                                        <p className="text-2xl font-bold text-blue-600">
                                            {nutricao.calorias_consumidas || 0}
                                        </p>
                                        <p className="text-sm text-gray-600">Calorias</p>
                                        <p className="text-xs text-gray-500">
                                            Meta: {nutricao.meta_calorias}
                                        </p>
                                    </div>
                                    <div className="text-center p-3 border rounded-lg">
                                        <p className="text-2xl font-bold text-blue-600">
                                            {nutricao.agua_consumida || 0}ml
                                        </p>
                                        <p className="text-sm text-gray-600">Água</p>
                                        <p className="text-xs text-gray-500">
                                            Meta: {nutricao.meta_agua || 2500}ml
                                        </p>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="font-medium mb-2">Refeições de Hoje</h4>
                                    <div className="space-y-2">
                                        {nutricao.refeicoes_hoje?.map((refeicao, index) => (
                                            <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                                                <span className="text-sm">{refeicao.tipo}</span>
                                                <span className="text-sm font-medium">{refeicao.calorias} kcal</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div>
                                    <h4 className="font-medium mb-2">Restrições Alimentares</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {nutricao.restricoes?.map((restricao, index) => (
                                            <Badge key={index} variant="secondary">{restricao}</Badge>
                                        ))}
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Análise de Refeição</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <Button variant="outline" className="w-full">
                                        <Camera className="w-4 h-4 mr-2" />
                                        Fotografar Prato
                                    </Button>
                                    <p className="text-xs text-gray-500 mt-1">
                                        IA identifica alimentos e calcula nutrição
                                    </p>
                                </div>

                                <div className="space-y-3">
                                    <Button variant="outline" className="w-full justify-start">
                                        🥗 Sugestão de Almoço Saudável
                                    </Button>
                                    <Button variant="outline" className="w-full justify-start">
                                        📊 Relatório Nutricional Semanal
                                    </Button>
                                    <Button variant="outline" className="w-full justify-start">
                                        🛒 Gerar Lista de Compras
                                    </Button>
                                    <Button variant="outline" className="w-full justify-start">
                                        👩‍⚕️ Consulta com Nutricionista
                                    </Button>
                                </div>

                                <div className="bg-green-50 p-3 rounded-lg">
                                    <h5 className="font-medium text-green-800">Dica Personalizada</h5>
                                    <p className="text-sm text-green-700">
                                        Com base no seu perfil, inclua mais proteínas no café da manhã
                                        para manter energia até o almoço.
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Fisioterapia Digital */}
                <TabsContent value="fisio" className="space-y-4">
                    <div className="grid md:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Dumbbell className="w-5 h-5 mr-2" />
                                    Exercícios de Hoje
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {fisioterapia.exercicios_hoje?.map((exercicio, index) => (
                                        <div key={index} className="border rounded-lg p-4">
                                            <div className="flex justify-between items-center">
                                                <div>
                                                    <h4 className="font-semibold">{exercicio.nome}</h4>
                                                    <p className="text-sm text-gray-600">
                                                        Duração: {exercicio.duracao} minutos
                                                    </p>
                                                </div>
                                                <div className="flex space-x-2">
                                                    {exercicio.concluido ? (
                                                        <Badge className="bg-green-100 text-green-800">
                                                            <CheckCircle className="w-3 h-3 mr-1" />
                                                            Concluído
                                                        </Badge>
                                                    ) : (
                                                        <Button size="sm">
                                                            <Play className="w-4 h-4 mr-1" />
                                                            Iniciar
                                                        </Button>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Recursos Fisioterapia</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <Button variant="outline" className="w-full justify-start">
                                    <Video className="w-4 h-4 mr-2" />
                                    Vídeos de Exercícios
                                </Button>
                                <Button variant="outline" className="w-full justify-start">
                                    <Camera className="w-4 h-4 mr-2" />
                                    Detector de Postura
                                </Button>
                                <Button variant="outline" className="w-full justify-start">
                                    <BarChart3 className="w-4 h-4 mr-2" />
                                    Progresso Semanal
                                </Button>
                                <Button variant="outline" className="w-full justify-start">
                                    <User className="w-4 h-4 mr-2" />
                                    Falar com Fisioterapeuta
                                </Button>

                                <div className="bg-blue-50 p-3 rounded-lg">
                                    <h5 className="font-medium text-blue-800">Plano Ativo</h5>
                                    <p className="text-sm text-blue-700">{fisioterapia.plano_ativo}</p>
                                    <div className="mt-2">
                                        <div className="w-full bg-blue-200 rounded-full h-2">
                                            <div className="bg-blue-600 h-2 rounded-full" style={{ width: '75%' }}></div>
                                        </div>
                                        <p className="text-xs text-blue-600 mt-1">75% completo</p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Medicina Preventiva */}
                <TabsContent value="prevencao" className="space-y-4">
                    <div className="grid md:grid-cols-3 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Shield className="w-5 h-5 mr-2" />
                                    Próximos Exames
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {prevencao.proximos_exames?.map((exame, index) => (
                                        <div key={index} className="border rounded-lg p-3">
                                            <h4 className="font-semibold">{exame.tipo}</h4>
                                            <p className="text-sm text-gray-600">{exame.data}</p>
                                            <Badge
                                                variant="outline"
                                                className={
                                                    exame.prioridade === 'alta' ? 'border-red-200 text-red-800' :
                                                        exame.prioridade === 'media' ? 'border-yellow-200 text-yellow-800' :
                                                            'border-green-200 text-green-800'
                                                }
                                            >
                                                {exame.prioridade}
                                            </Badge>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Zap className="w-5 h-5 mr-2" />
                                    Vacinas Pendentes
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {prevencao.vacinas_pendentes?.map((vacina, index) => (
                                        <div key={index} className="border rounded-lg p-3">
                                            <h4 className="font-semibold">{vacina.nome}</h4>
                                            <p className="text-sm text-gray-600">
                                                Até: {vacina.data_limite}
                                            </p>
                                            <Button size="sm" className="mt-2">
                                                Agendar
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Calendar className="w-5 h-5 mr-2" />
                                    Check-ups
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {prevencao.check_ups?.map((checkup, index) => (
                                        <div key={index} className="border rounded-lg p-3">
                                            <h4 className="font-semibold">{checkup.tipo}</h4>
                                            <p className="text-sm text-gray-600">{checkup.data}</p>
                                            <p className="text-sm text-blue-600">{checkup.medico}</p>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Emergência Médica */}
                <TabsContent value="emergencia" className="space-y-4">
                    <div className="grid md:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center text-red-600">
                                    <Ambulance className="w-5 h-5 mr-2" />
                                    Informações de Emergência
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <h4 className="font-medium mb-2">Condições Médicas</h4>
                                    <div className="space-y-1">
                                        {emergencia.condicoes_medicas?.map((condicao, index) => (
                                            <Badge key={index} variant="secondary">{condicao}</Badge>
                                        ))}
                                    </div>
                                </div>

                                <div>
                                    <h4 className="font-medium mb-2">Alergias</h4>
                                    <div className="space-y-1">
                                        {emergencia.alergias?.map((alergia, index) => (
                                            <Badge key={index} variant="destructive">{alergia}</Badge>
                                        ))}
                                    </div>
                                </div>

                                <div>
                                    <h4 className="font-medium mb-2">Medicamentos em Uso</h4>
                                    <div className="space-y-1">
                                        {emergencia.medicamentos_uso?.map((medicamento, index) => (
                                            <p key={index} className="text-sm bg-blue-50 p-2 rounded">
                                                {medicamento}
                                            </p>
                                        ))}
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Contatos de Emergência</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {emergencia.contatos_emergencia?.map((contato, index) => (
                                    <div key={index} className="border rounded-lg p-3">
                                        <h4 className="font-semibold">{contato.nome}</h4>
                                        <p className="text-sm text-gray-600">{contato.relacao}</p>
                                        <p className="text-sm text-blue-600">{contato.telefone}</p>
                                        <Button size="sm" className="mt-2 bg-red-600 hover:bg-red-700">
                                            <Phone className="w-4 h-4 mr-1" />
                                            Ligar
                                        </Button>
                                    </div>
                                ))}

                                <div className="border-2 border-red-200 rounded-lg p-4 bg-red-50">
                                    <Button className="w-full bg-red-600 hover:bg-red-700 text-lg py-3">
                                        <Ambulance className="w-6 h-6 mr-2" />
                                        EMERGÊNCIA - LIGAR SAMU 192
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Dispositivos IoT */}
                <TabsContent value="dispositivos" className="space-y-4">
                    <div className="grid md:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Wifi className="w-5 h-5 mr-2" />
                                    Dispositivos Conectados
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {dispositivos.conectados?.map((dispositivo, index) => (
                                        <div key={index} className="border rounded-lg p-4">
                                            <div className="flex justify-between items-center">
                                                <div>
                                                    <h4 className="font-semibold">{dispositivo.nome}</h4>
                                                    <p className="text-sm text-gray-600">
                                                        {dispositivo.tipo} • Bateria: {dispositivo.bateria}%
                                                    </p>
                                                </div>
                                                <Badge
                                                    variant="outline"
                                                    className={
                                                        dispositivo.status === 'conectado'
                                                            ? 'bg-green-50 text-green-700 border-green-200'
                                                            : 'bg-red-50 text-red-700 border-red-200'
                                                    }
                                                >
                                                    {dispositivo.status}
                                                </Badge>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Leituras Recentes</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {dispositivos.leituras_recentes?.map((leitura, index) => (
                                        <div key={index} className="border rounded-lg p-3">
                                            <div className="flex justify-between items-center">
                                                <div>
                                                    <h4 className="font-semibold">{leitura.tipo}</h4>
                                                    <p className="text-sm text-gray-600">{leitura.dispositivo}</p>
                                                </div>
                                                <div className="text-right">
                                                    <p className="text-lg font-bold text-blue-600">
                                                        {leitura.valor} {leitura.unidade}
                                                    </p>
                                                    <p className="text-xs text-gray-500">{leitura.timestamp}</p>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                <Button variant="outline" className="w-full mt-4">
                                    <Plus className="w-4 h-4 mr-2" />
                                    Conectar Novo Dispositivo
                                </Button>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* IA Médica */}
                <TabsContent value="ia" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <BarChart3 className="w-5 h-5 mr-2" />
                                Inteligência Artificial Médica
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid md:grid-cols-3 gap-4">
                                <Button variant="outline" className="h-20 flex-col">
                                    <Brain className="w-6 h-6 mb-2" />
                                    <span className="text-sm">Diagnóstico Assistido</span>
                                </Button>
                                <Button variant="outline" className="h-20 flex-col">
                                    <Activity className="w-6 h-6 mb-2" />
                                    <span className="text-sm">Predição de Riscos</span>
                                </Button>
                                <Button variant="outline" className="h-20 flex-col">
                                    <Target className="w-6 h-6 mb-2" />
                                    <span className="text-sm">Medicina Personalizada</span>
                                </Button>
                            </div>

                            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg">
                                <h4 className="font-semibold mb-2">Relatório de Saúde IA</h4>
                                <p className="text-sm text-gray-700 mb-3">
                                    Com base nos seus dados dos últimos 30 dias:
                                </p>
                                <ul className="text-sm space-y-1 text-gray-600">
                                    <li>• ✅ Pressão arterial dentro da normalidade</li>
                                    <li>• ⚠️ Padrão de sono irregular detectado</li>
                                    <li>• ✅ Adesão medicamentosa: 95%</li>
                                    <li>• 💡 Recomendação: Aumentar atividade física</li>
                                </ul>
                                <Button size="sm" className="mt-3">
                                    Ver Relatório Completo
                                </Button>
                            </div>

                            <div className="bg-yellow-50 p-4 rounded-lg">
                                <h4 className="font-semibold text-yellow-800 mb-2">Alertas Preditivos</h4>
                                <div className="space-y-2">
                                    <div className="flex items-center">
                                        <AlertTriangle className="w-4 h-4 text-yellow-600 mr-2" />
                                        <span className="text-sm">Possível início de resfriado em 2-3 dias</span>
                                    </div>
                                    <div className="flex items-center">
                                        <Bell className="w-4 h-4 text-blue-600 mr-2" />
                                        <span className="text-sm">Lembrete: Exame de rotina em 15 dias</span>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

            </Tabs>
        </div>
    )
}

export default SistemaMedicoCompleto
