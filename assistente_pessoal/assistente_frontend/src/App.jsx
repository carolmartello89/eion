import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import {
  Calendar, Users, Phone, Mic, Settings,
  BarChart3, Brain, LogOut, Menu, X,
  Home, DollarSign, FileText, Clock, Shield,
  History, Zap
} from 'lucide-react'

import Login from './components/Login.jsx'
import Dashboard from './components/Dashboard.jsx'
import VoiceAssistant from './components/VoiceAssistant.jsx'
import Compromissos from './components/Compromissos.jsx'
import Reunioes from './components/Reunioes.jsx'
import Contatos from './components/Contatos.jsx'
import Analytics from './components/Analytics.jsx'
import SmartReminders from './components/SmartReminders.jsx'
import AutomationCenter from './components/AutomationCenter.jsx'
import SistemaFinanceiro from './components/SistemaFinanceiro.jsx'
import MemoriaHistorico from './components/MemoriaHistorico.jsx'
import ReconhecimentoVozAvancado from './components/ReconhecimentoVozAvancado.jsx'
import AlwaysActiveIA from './components/AlwaysActiveIA.jsx'
import SetupWizard from './components/SetupWizard.jsx'
import PlanosAssinaturas from './components/PlanosAssinaturas.jsx'
import AdminDashboard from './components/AdminDashboard.jsx'
import SecretariaExecutiva from './components/SecretariaExecutiva.jsx'
import SistemaFinanceiroCompleto from './components/SistemaFinanceiroCompleto.jsx'
import { ThemeProvider } from './components/ThemeProvider.jsx'
import SettingsComponent from './components/Settings.jsx'
import useAuth from './hooks/useAuth.jsx'
import { useNotifications } from './hooks/useNotifications.js'

function App() {
  const { user, login, logout, isAuthenticated, loading } = useAuth()
  const { requestPermission } = useNotifications()

  const [activeTab, setActiveTab] = useState('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showSetup, setShowSetup] = useState(false)
  const [setupCompleted, setSetupCompleted] = useState(false)

  // Verifica se precisa mostrar setup inicial
  useEffect(() => {
    if (isAuthenticated && !loading) {
      const completed = localStorage.getItem('setup_completed')
      if (!completed) {
        setShowSetup(true)
      } else {
        setSetupCompleted(true)
      }
    }
  }, [isAuthenticated, loading])

  // Solicita permissões de notificação
  useEffect(() => {
    if (isAuthenticated && setupCompleted) {
      requestPermission()
    }
  }, [isAuthenticated, setupCompleted, requestPermission])

  const handleLogin = async (credentials) => {
    try {
      await login(credentials)
    } catch (error) {
      console.error('Erro no login:', error)
    }
  }

  const handleLogout = () => {
    logout()
    setActiveTab('dashboard')
    setSetupCompleted(false)
    localStorage.removeItem('setup_completed')
  }

  const handleSetupComplete = (setupData) => {
    setShowSetup(false)
    setSetupCompleted(true)
    console.log('Setup concluído:', setupData)
  }

  const handleVoiceCommand = (action, parameters) => {
    console.log('Comando de voz:', action, parameters)

    // Executa ações baseadas no comando
    switch (action) {
      case 'navigate':
        setActiveTab(parameters.page)
        break
      case 'create_appointment':
        setActiveTab('agenda')
        // Adicionar lógica para criar compromisso
        break
      case 'add_transaction':
        setActiveTab('financeiro')
        // Adicionar lógica para transação financeira
        break
      case 'make_call':
        setActiveTab('contatos')
        // Adicionar lógica para ligação
        break
      default:
        console.log('Ação não reconhecida:', action)
    }
  }

  const handleVoiceAuth = (authResult) => {
    console.log('Autenticação por voz:', authResult)
    // Lógica adicional para autenticação por voz
  }

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'secretaria', label: 'Secretária Executiva', icon: Shield },
    { id: 'agenda', label: 'Agenda', icon: Calendar },
    { id: 'reunioes', label: 'Reuniões', icon: Users },
    { id: 'contatos', label: 'Contatos', icon: Phone },
    { id: 'financeiro', label: 'Financeiro', icon: DollarSign },
    { id: 'financeiro-completo', label: 'Sistema Financeiro', icon: BarChart3 },
    { id: 'memoria', label: 'Memória', icon: History },
    { id: 'voz', label: 'Reconhecimento', icon: Mic },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'lembretes', label: 'Lembretes', icon: Clock },
    { id: 'automacao', label: 'Automação', icon: Zap },
    { id: 'planos', label: 'Planos', icon: Shield },
    ...(user?.email === 'fuda.julio@gmail.com' ? [
      { id: 'admin', label: 'Admin', icon: Settings }
    ] : []),
    { id: 'configuracoes', label: 'Configurações', icon: Settings }
  ]

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard user={user} />
      case 'secretaria':
        return <SecretariaExecutiva user={user} />
      case 'agenda':
        return <Compromissos user={user} />
      case 'reunioes':
        return <Reunioes user={user} />
      case 'contatos':
        return <Contatos user={user} />
      case 'financeiro':
        return <SistemaFinanceiro user={user} />
      case 'financeiro-completo':
        return <SistemaFinanceiroCompleto user={user} />
      case 'memoria':
        return <MemoriaHistorico user={user} />
      case 'voz':
        return <ReconhecimentoVozAvancado user={user} />
      case 'analytics':
        return <Analytics user={user} />
      case 'lembretes':
        return <SmartReminders user={user} />
      case 'automacao':
        return <AutomationCenter user={user} />
      case 'planos':
        return <PlanosAssinaturas user={user} />
      case 'admin':
        return <AdminDashboard user={user} />
      case 'configuracoes':
        return <SettingsComponent user={user} />
      default:
        return <Dashboard user={user} />
    }
  }

  if (loading) {
    return (
      <ThemeProvider>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100 flex items-center justify-center">
          <div className="text-center">
            <Brain className="w-16 h-16 mx-auto text-blue-500 animate-pulse mb-4" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">IA</h2>
            <p className="text-gray-600">Carregando seu assistente pessoal...</p>
          </div>
        </div>
      </ThemeProvider>
    )
  }

  if (!isAuthenticated) {
    return (
      <ThemeProvider>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100">
          <Login onLogin={handleLogin} />
        </div>
      </ThemeProvider>
    )
  }

  if (showSetup) {
    return (
      <ThemeProvider>
        <SetupWizard user={user} onComplete={handleSetupComplete} />
      </ThemeProvider>
    )
  }

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 shadow-sm">
          <div className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="md:hidden"
              >
                {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>

              <div className="flex items-center space-x-2">
                <Brain className="w-8 h-8 text-blue-500" />
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  IA
                </h1>
                <Badge variant="outline" className="text-xs">
                  Assistente Pessoal
                </Badge>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600 hidden sm:block">
                Olá, {user?.preferred_name || user?.email?.split('@')[0] || 'Usuário'}!
              </span>

              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                className="flex items-center space-x-2"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Sair</span>
              </Button>
            </div>
          </div>
        </header>

        <div className="flex">
          {/* Sidebar */}
          <aside className={`bg-white border-r border-gray-200 w-64 min-h-screen transition-transform duration-300 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'
            } md:translate-x-0 fixed md:relative z-30`}>
            <nav className="p-4 space-y-2">
              {menuItems.map((item) => {
                const IconComponent = item.icon
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      setActiveTab(item.id)
                      setSidebarOpen(false)
                    }}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${activeTab === item.id
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'text-gray-600 hover:bg-gray-50'
                      }`}
                  >
                    <IconComponent className="w-5 h-5" />
                    <span>{item.label}</span>
                  </button>
                )
              })}
            </nav>
          </aside>

          {/* Overlay para mobile */}
          {sidebarOpen && (
            <div
              className="fixed inset-0 bg-black bg-opacity-50 z-20 md:hidden"
              onClick={() => setSidebarOpen(false)}
            />
          )}

          {/* Main Content */}
          <main className="flex-1 p-6 overflow-auto">
            {renderContent()}
          </main>
        </div>

        {/* IA Sempre Ativa - Componente flutuante */}
        {setupCompleted && (
          <AlwaysActiveIA
            user={user}
            onCommand={handleVoiceCommand}
            onVoiceAuth={handleVoiceAuth}
          />
        )}

        {/* Assistente de Voz Tradicional - Para compatibilidade */}
        <div className="fixed bottom-4 left-4 z-40">
          <VoiceAssistant user={user} />
        </div>
      </div>
    </ThemeProvider>
  )
}

export default App

