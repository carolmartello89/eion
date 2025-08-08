import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { useTheme } from './ThemeProvider.jsx'
import { 
  Settings as SettingsIcon, 
  Moon, 
  Sun, 
  Monitor,
  Bell,
  Shield,
  User,
  Palette,
  Volume2,
  Smartphone,
  Download,
  Upload,
  Trash2,
  Save,
  RefreshCw
} from 'lucide-react'

const Settings = () => {
  const { theme, setTheme, effectiveTheme } = useTheme()
  const [settings, setSettings] = useState({
    notifications: {
      enabled: true,
      sound: true,
      desktop: true,
      email: false,
      reminderMinutes: 15
    },
    privacy: {
      shareAnalytics: false,
      saveHistory: true,
      autoBackup: true
    },
    appearance: {
      compactMode: false,
      animations: true,
      fontSize: 'medium'
    },
    voice: {
      enabled: true,
      language: 'pt-BR',
      speed: 1.0,
      pitch: 1.0
    },
    account: {
      name: '',
      email: '',
      timezone: 'America/Sao_Paulo'
    }
  })
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const response = await fetch('/api/settings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setSettings(data.settings)
      }
    } catch (error) {
      console.error('Erro ao carregar configurações:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const saveSettings = async () => {
    setIsSaving(true)
    try {
      const response = await fetch('/api/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({ settings })
      })

      if (response.ok) {
        alert('Configurações salvas com sucesso!')
      } else {
        throw new Error('Erro ao salvar configurações')
      }
    } catch (error) {
      console.error('Erro ao salvar configurações:', error)
      alert('Erro ao salvar configurações')
    } finally {
      setIsSaving(false)
    }
  }

  const updateSetting = (section, key, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }))
  }

  const exportData = async () => {
    try {
      const response = await fetch('/api/export', {
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
        a.download = `assistente_backup_${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Erro ao exportar dados:', error)
      alert('Erro ao exportar dados')
    }
  }

  const importData = (event) => {
    const file = event.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = async (e) => {
      try {
        const data = JSON.parse(e.target.result)
        
        const response = await fetch('/api/import', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: JSON.stringify(data)
        })

        if (response.ok) {
          alert('Dados importados com sucesso! Recarregue a página.')
        } else {
          throw new Error('Erro ao importar dados')
        }
      } catch (error) {
        console.error('Erro ao importar dados:', error)
        alert('Erro ao importar dados. Verifique o arquivo.')
      }
    }
    reader.readAsText(file)
  }

  const clearAllData = async () => {
    if (!confirm('Tem certeza que deseja apagar todos os dados? Esta ação não pode ser desfeita.')) {
      return
    }

    try {
      const response = await fetch('/api/clear-data', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (response.ok) {
        alert('Todos os dados foram apagados.')
        window.location.reload()
      }
    } catch (error) {
      console.error('Erro ao apagar dados:', error)
      alert('Erro ao apagar dados')
    }
  }

  const getThemeIcon = () => {
    switch (theme) {
      case 'light': return <Sun className="w-4 h-4" />
      case 'dark': return <Moon className="w-4 h-4" />
      case 'system': return <Monitor className="w-4 h-4" />
      default: return <Monitor className="w-4 h-4" />
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin" />
        <span className="ml-2">Carregando configurações...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Configurações</h2>
          <p className="text-muted-foreground">
            Personalize sua experiência com o assistente
          </p>
        </div>
        
        <Button onClick={saveSettings} disabled={isSaving}>
          {isSaving ? (
            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Save className="w-4 h-4 mr-2" />
          )}
          Salvar
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Aparência */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Palette className="w-5 h-5" />
              <span>Aparência</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Tema</Label>
              <div className="flex items-center space-x-2 mt-2">
                {[
                  { value: 'light', label: 'Claro', icon: <Sun className="w-4 h-4" /> },
                  { value: 'dark', label: 'Escuro', icon: <Moon className="w-4 h-4" /> },
                  { value: 'system', label: 'Sistema', icon: <Monitor className="w-4 h-4" /> }
                ].map((themeOption) => (
                  <Button
                    key={themeOption.value}
                    variant={theme === themeOption.value ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setTheme(themeOption.value)}
                    className="flex items-center space-x-2"
                  >
                    {themeOption.icon}
                    <span>{themeOption.label}</span>
                  </Button>
                ))}
              </div>
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div>
                <Label>Modo Compacto</Label>
                <p className="text-sm text-muted-foreground">
                  Interface mais densa com menos espaçamento
                </p>
              </div>
              <Switch
                checked={settings.appearance.compactMode}
                onCheckedChange={(value) => updateSetting('appearance', 'compactMode', value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Animações</Label>
                <p className="text-sm text-muted-foreground">
                  Transições e efeitos visuais
                </p>
              </div>
              <Switch
                checked={settings.appearance.animations}
                onCheckedChange={(value) => updateSetting('appearance', 'animations', value)}
              />
            </div>

            <div>
              <Label>Tamanho da Fonte</Label>
              <select 
                className="w-full p-2 border rounded mt-2"
                value={settings.appearance.fontSize}
                onChange={(e) => updateSetting('appearance', 'fontSize', e.target.value)}
              >
                <option value="small">Pequena</option>
                <option value="medium">Média</option>
                <option value="large">Grande</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Notificações */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Bell className="w-5 h-5" />
              <span>Notificações</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Notificações Ativadas</Label>
                <p className="text-sm text-muted-foreground">
                  Receber notificações do assistente
                </p>
              </div>
              <Switch
                checked={settings.notifications.enabled}
                onCheckedChange={(value) => updateSetting('notifications', 'enabled', value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Som</Label>
                <p className="text-sm text-muted-foreground">
                  Reproduzir som nas notificações
                </p>
              </div>
              <Switch
                checked={settings.notifications.sound}
                onCheckedChange={(value) => updateSetting('notifications', 'sound', value)}
                disabled={!settings.notifications.enabled}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Notificações Desktop</Label>
                <p className="text-sm text-muted-foreground">
                  Mostrar notificações na área de trabalho
                </p>
              </div>
              <Switch
                checked={settings.notifications.desktop}
                onCheckedChange={(value) => updateSetting('notifications', 'desktop', value)}
                disabled={!settings.notifications.enabled}
              />
            </div>

            <div>
              <Label>Antecedência dos Lembretes (minutos)</Label>
              <Input
                type="number"
                min="1"
                max="60"
                value={settings.notifications.reminderMinutes}
                onChange={(e) => updateSetting('notifications', 'reminderMinutes', parseInt(e.target.value))}
                className="mt-2"
              />
            </div>
          </CardContent>
        </Card>

        {/* Assistente de Voz */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Volume2 className="w-5 h-5" />
              <span>Assistente de Voz</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Assistente de Voz Ativado</Label>
                <p className="text-sm text-muted-foreground">
                  Habilitar comandos e respostas por voz
                </p>
              </div>
              <Switch
                checked={settings.voice.enabled}
                onCheckedChange={(value) => updateSetting('voice', 'enabled', value)}
              />
            </div>

            <div>
              <Label>Idioma</Label>
              <select 
                className="w-full p-2 border rounded mt-2"
                value={settings.voice.language}
                onChange={(e) => updateSetting('voice', 'language', e.target.value)}
                disabled={!settings.voice.enabled}
              >
                <option value="pt-BR">Português (Brasil)</option>
                <option value="en-US">English (US)</option>
                <option value="es-ES">Español</option>
              </select>
            </div>

            <div>
              <Label>Velocidade da Fala</Label>
              <input
                type="range"
                min="0.5"
                max="2"
                step="0.1"
                value={settings.voice.speed}
                onChange={(e) => updateSetting('voice', 'speed', parseFloat(e.target.value))}
                className="w-full mt-2"
                disabled={!settings.voice.enabled}
              />
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Lenta</span>
                <span>{settings.voice.speed}x</span>
                <span>Rápida</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Privacidade */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="w-5 h-5" />
              <span>Privacidade</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Salvar Histórico</Label>
                <p className="text-sm text-muted-foreground">
                  Manter histórico de atividades para analytics
                </p>
              </div>
              <Switch
                checked={settings.privacy.saveHistory}
                onCheckedChange={(value) => updateSetting('privacy', 'saveHistory', value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Backup Automático</Label>
                <p className="text-sm text-muted-foreground">
                  Fazer backup dos dados automaticamente
                </p>
              </div>
              <Switch
                checked={settings.privacy.autoBackup}
                onCheckedChange={(value) => updateSetting('privacy', 'autoBackup', value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Compartilhar Analytics</Label>
                <p className="text-sm text-muted-foreground">
                  Ajudar a melhorar o produto com dados anônimos
                </p>
              </div>
              <Switch
                checked={settings.privacy.shareAnalytics}
                onCheckedChange={(value) => updateSetting('privacy', 'shareAnalytics', value)}
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Dados e Backup */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Smartphone className="w-5 h-5" />
            <span>Dados e Backup</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" onClick={exportData}>
              <Download className="w-4 h-4 mr-2" />
              Exportar Dados
            </Button>
            
            <div>
              <input
                type="file"
                accept=".json"
                onChange={importData}
                className="hidden"
                id="import-file"
              />
              <Button 
                variant="outline" 
                onClick={() => document.getElementById('import-file').click()}
              >
                <Upload className="w-4 h-4 mr-2" />
                Importar Dados
              </Button>
            </div>
            
            <Button variant="destructive" onClick={clearAllData}>
              <Trash2 className="w-4 h-4 mr-2" />
              Apagar Tudo
            </Button>
          </div>
          
          <p className="text-sm text-muted-foreground mt-4">
            Use essas opções para fazer backup dos seus dados ou transferir para outro dispositivo.
            A opção "Apagar Tudo" remove permanentemente todos os dados.
          </p>
        </CardContent>
      </Card>

      {/* Informações da Conta */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <User className="w-5 h-5" />
            <span>Informações da Conta</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Nome</Label>
            <Input
              value={settings.account.name}
              onChange={(e) => updateSetting('account', 'name', e.target.value)}
              placeholder="Seu nome"
              className="mt-2"
            />
          </div>
          
          <div>
            <Label>Email</Label>
            <Input
              value={settings.account.email}
              onChange={(e) => updateSetting('account', 'email', e.target.value)}
              placeholder="seu@email.com"
              type="email"
              className="mt-2"
            />
          </div>
          
          <div>
            <Label>Fuso Horário</Label>
            <select 
              className="w-full p-2 border rounded mt-2"
              value={settings.account.timezone}
              onChange={(e) => updateSetting('account', 'timezone', e.target.value)}
            >
              <option value="America/Sao_Paulo">São Paulo (GMT-3)</option>
              <option value="America/New_York">New York (GMT-5)</option>
              <option value="Europe/London">London (GMT+0)</option>
            </select>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Settings

