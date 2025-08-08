import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { 
  Phone, 
  Mail, 
  Building, 
  Plus, 
  Edit, 
  Trash2, 
  Star,
  Search,
  X,
  User,
  Heart
} from 'lucide-react'

const Contatos = () => {
  const [contatos, setContatos] = useState([])
  const [filtro, setFiltro] = useState('todos') // todos, favoritos, trabalho, pessoal, familia
  const [busca, setBusca] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [formData, setFormData] = useState({
    nome: '',
    telefone: '',
    email: '',
    empresa: '',
    cargo: '',
    categoria: 'geral',
    notas: ''
  })

  // Carrega contatos
  useEffect(() => {
    loadContatos()
  }, [])

  const loadContatos = async () => {
    try {
      // Simula dados enquanto a API não está disponível
      const mockContatos = [
        {
          id: '1',
          nome: 'João Silva',
          telefone: '(11) 99999-1234',
          email: 'joao.silva@empresa.com',
          empresa: 'Tech Solutions',
          cargo: 'Desenvolvedor Senior',
          categoria: 'trabalho',
          favorito: true,
          notas: 'Especialista em React e Node.js'
        },
        {
          id: '2',
          nome: 'Maria Santos',
          telefone: '(11) 98888-5678',
          email: 'maria.santos@gmail.com',
          empresa: '',
          cargo: '',
          categoria: 'pessoal',
          favorito: false,
          notas: 'Amiga da faculdade'
        },
        {
          id: '3',
          nome: 'Dr. Pedro Costa',
          telefone: '(11) 3333-4567',
          email: 'pedro.costa@clinica.com',
          empresa: 'Clínica Saúde Total',
          cargo: 'Médico Cardiologista',
          categoria: 'profissional',
          favorito: true,
          notas: 'Consultas às terças-feiras'
        },
        {
          id: '4',
          nome: 'Ana Oliveira',
          telefone: '(11) 97777-9999',
          email: 'ana@startup.com',
          empresa: 'StartupXYZ',
          cargo: 'CEO',
          categoria: 'trabalho',
          favorito: false,
          notas: 'Cliente importante - projeto mobile'
        }
      ]
      
      setContatos(mockContatos)
    } catch (error) {
      console.error('Erro ao carregar contatos:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      if (editingId) {
        // Atualizar contato existente
        setContatos(prev => prev.map(contato => 
          contato.id === editingId ? { ...contato, ...formData } : contato
        ))
      } else {
        // Criar novo contato
        const novoContato = {
          id: Date.now().toString(),
          ...formData,
          favorito: false,
          criado_em: new Date().toISOString()
        }
        setContatos(prev => [...prev, novoContato])
      }
      
      resetForm()
    } catch (error) {
      console.error('Erro ao salvar contato:', error)
    }
  }

  const resetForm = () => {
    setFormData({
      nome: '',
      telefone: '',
      email: '',
      empresa: '',
      cargo: '',
      categoria: 'geral',
      notas: ''
    })
    setShowForm(false)
    setEditingId(null)
  }

  const handleEdit = (contato) => {
    setFormData({
      nome: contato.nome,
      telefone: contato.telefone,
      email: contato.email,
      empresa: contato.empresa,
      cargo: contato.cargo,
      categoria: contato.categoria,
      notas: contato.notas
    })
    setEditingId(contato.id)
    setShowForm(true)
  }

  const handleDelete = async (id) => {
    if (confirm('Tem certeza que deseja excluir este contato?')) {
      setContatos(prev => prev.filter(contato => contato.id !== id))
    }
  }

  const toggleFavorito = async (id) => {
    setContatos(prev => prev.map(contato => 
      contato.id === id ? { ...contato, favorito: !contato.favorito } : contato
    ))
  }

  const iniciarLigacao = (telefone, nome) => {
    if (!telefone) {
      alert('Telefone não cadastrado para este contato')
      return
    }
    
    // Remove caracteres especiais do telefone
    const telefoneNumeros = telefone.replace(/\D/g, '')
    
    // Cria URL para ligação
    const urlLigacao = `tel:${telefoneNumeros}`
    
    // Confirma antes de iniciar ligação
    if (confirm(`Ligar para ${nome}?`)) {
      window.location.href = urlLigacao
    }
  }

  const enviarEmail = (email, nome) => {
    if (!email) {
      alert('Email não cadastrado para este contato')
      return
    }
    
    const urlEmail = `mailto:${email}?subject=Contato via Assistente Pessoal`
    window.location.href = urlEmail
  }

  const getCategoriaColor = (categoria) => {
    switch (categoria) {
      case 'trabalho': return 'bg-blue-100 text-blue-800'
      case 'pessoal': return 'bg-green-100 text-green-800'
      case 'familia': return 'bg-purple-100 text-purple-800'
      case 'profissional': return 'bg-orange-100 text-orange-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getCategoriaIcon = (categoria) => {
    switch (categoria) {
      case 'trabalho': return '💼'
      case 'pessoal': return '👤'
      case 'familia': return '👨‍👩‍👧‍👦'
      case 'profissional': return '🏥'
      default: return '📋'
    }
  }

  const filteredContatos = contatos.filter(contato => {
    const matchesBusca = contato.nome.toLowerCase().includes(busca.toLowerCase()) ||
                        contato.empresa.toLowerCase().includes(busca.toLowerCase()) ||
                        contato.telefone.includes(busca) ||
                        contato.email.toLowerCase().includes(busca.toLowerCase())
    
    if (!matchesBusca) return false
    
    switch (filtro) {
      case 'favoritos':
        return contato.favorito
      case 'trabalho':
        return contato.categoria === 'trabalho'
      case 'pessoal':
        return contato.categoria === 'pessoal'
      case 'familia':
        return contato.categoria === 'familia'
      case 'profissional':
        return contato.categoria === 'profissional'
      default:
        return true
    }
  })

  // Ordena contatos: favoritos primeiro, depois alfabético
  const sortedContatos = filteredContatos.sort((a, b) => {
    if (a.favorito && !b.favorito) return -1
    if (!a.favorito && b.favorito) return 1
    return a.nome.localeCompare(b.nome)
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Contatos</h2>
          <p className="text-muted-foreground">Gerencie seus contatos pessoais e profissionais</p>
        </div>
        <Button onClick={() => setShowForm(true)} className="touch-target">
          <Plus className="w-4 h-4 mr-2" />
          Novo
        </Button>
      </div>

      {/* Filtros e busca */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Buscar contatos..."
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <div className="flex space-x-2 overflow-x-auto pb-2">
          {[
            { key: 'todos', label: 'Todos' },
            { key: 'favoritos', label: 'Favoritos' },
            { key: 'trabalho', label: 'Trabalho' },
            { key: 'pessoal', label: 'Pessoal' },
            { key: 'familia', label: 'Família' },
            { key: 'profissional', label: 'Profissional' }
          ].map(({ key, label }) => (
            <Button
              key={key}
              variant={filtro === key ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFiltro(key)}
              className="whitespace-nowrap"
            >
              {label}
            </Button>
          ))}
        </div>
      </div>

      {/* Lista de contatos */}
      <div className="space-y-3">
        {sortedContatos.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <User className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">
                {busca ? 'Nenhum contato encontrado' : 'Nenhum contato cadastrado'}
              </p>
            </CardContent>
          </Card>
        ) : (
          sortedContatos.map((contato) => (
            <Card key={contato.id} className={contato.favorito ? 'ring-1 ring-yellow-200' : ''}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1 min-w-0">
                    {/* Avatar */}
                    <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-lg font-semibold text-primary">
                        {contato.nome.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    
                    {/* Informações do contato */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className="font-semibold truncate">{contato.nome}</h3>
                        {contato.favorito && (
                          <Star className="w-4 h-4 text-yellow-500 fill-current" />
                        )}
                        <Badge className={getCategoriaColor(contato.categoria)}>
                          {getCategoriaIcon(contato.categoria)} {contato.categoria}
                        </Badge>
                      </div>
                      
                      {contato.empresa && (
                        <div className="flex items-center space-x-1 text-sm text-muted-foreground mb-1">
                          <Building className="w-3 h-3" />
                          <span className="truncate">
                            {contato.cargo ? `${contato.cargo} • ${contato.empresa}` : contato.empresa}
                          </span>
                        </div>
                      )}
                      
                      <div className="space-y-1">
                        {contato.telefone && (
                          <div className="flex items-center space-x-1 text-sm">
                            <Phone className="w-3 h-3 text-muted-foreground" />
                            <span>{contato.telefone}</span>
                          </div>
                        )}
                        
                        {contato.email && (
                          <div className="flex items-center space-x-1 text-sm">
                            <Mail className="w-3 h-3 text-muted-foreground" />
                            <span className="truncate">{contato.email}</span>
                          </div>
                        )}
                      </div>
                      
                      {contato.notas && (
                        <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                          {contato.notas}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  {/* Ações */}
                  <div className="flex flex-col space-y-1 ml-4">
                    <div className="flex space-x-1">
                      {contato.telefone && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => iniciarLigacao(contato.telefone, contato.nome)}
                          className="touch-target text-green-600"
                        >
                          <Phone className="w-4 h-4" />
                        </Button>
                      )}
                      
                      {contato.email && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => enviarEmail(contato.email, contato.nome)}
                          className="touch-target text-blue-600"
                        >
                          <Mail className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                    
                    <div className="flex space-x-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleFavorito(contato.id)}
                        className="touch-target"
                      >
                        {contato.favorito ? (
                          <Star className="w-4 h-4 text-yellow-500 fill-current" />
                        ) : (
                          <Star className="w-4 h-4" />
                        )}
                      </Button>
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(contato)}
                        className="touch-target"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(contato.id)}
                        className="touch-target text-destructive"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Modal de formulário */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-end justify-center p-4">
          <Card className="w-full max-w-md max-h-[90vh] overflow-hidden">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>
                    {editingId ? 'Editar Contato' : 'Novo Contato'}
                  </CardTitle>
                  <CardDescription>
                    Preencha as informações do contato
                  </CardDescription>
                </div>
                <Button variant="ghost" size="sm" onClick={resetForm}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="overflow-y-auto">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Nome *</label>
                  <Input
                    value={formData.nome}
                    onChange={(e) => setFormData(prev => ({ ...prev, nome: e.target.value }))}
                    placeholder="Ex: João Silva"
                    required
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Telefone</label>
                    <Input
                      value={formData.telefone}
                      onChange={(e) => setFormData(prev => ({ ...prev, telefone: e.target.value }))}
                      placeholder="(11) 99999-9999"
                      type="tel"
                    />
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Categoria</label>
                    <select
                      value={formData.categoria}
                      onChange={(e) => setFormData(prev => ({ ...prev, categoria: e.target.value }))}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="geral">Geral</option>
                      <option value="trabalho">Trabalho</option>
                      <option value="pessoal">Pessoal</option>
                      <option value="familia">Família</option>
                      <option value="profissional">Profissional</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium">Email</label>
                  <Input
                    value={formData.email}
                    onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="joao@exemplo.com"
                    type="email"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Empresa</label>
                    <Input
                      value={formData.empresa}
                      onChange={(e) => setFormData(prev => ({ ...prev, empresa: e.target.value }))}
                      placeholder="Nome da empresa"
                    />
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Cargo</label>
                    <Input
                      value={formData.cargo}
                      onChange={(e) => setFormData(prev => ({ ...prev, cargo: e.target.value }))}
                      placeholder="Ex: Desenvolvedor"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium">Notas</label>
                  <Textarea
                    value={formData.notas}
                    onChange={(e) => setFormData(prev => ({ ...prev, notas: e.target.value }))}
                    placeholder="Informações adicionais..."
                    rows={3}
                  />
                </div>
                
                <div className="flex space-x-3 pt-4">
                  <Button type="submit" className="flex-1">
                    {editingId ? 'Atualizar' : 'Criar'}
                  </Button>
                  <Button type="button" variant="outline" onClick={resetForm}>
                    Cancelar
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

export default Contatos

