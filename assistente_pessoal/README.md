# 🤖 Assistente Pessoal Inteligente

Um assistente pessoal completo com IA, desenvolvido em Python (Flask) + React, otimizado para iPhone e dispositivos móveis.

## 🌟 Funcionalidades Principais

### 🎤 **Assistente de Voz Avançado**
- Comandos de voz inteligentes com IA integrada
- Síntese de voz em português brasileiro
- Reconhecimento de fala nativo do navegador
- Comandos personalizáveis e contextuais

### 📅 **Gerenciamento de Compromissos**
- Agenda inteligente com visualização por dia/semana/mês
- Criação rápida de compromissos por voz
- Alertas e notificações personalizáveis
- Sincronização em tempo real

### 👥 **Sistema de Reuniões**
- Gravação de reuniões com transcrição automática
- Resumos gerados por IA
- Acompanhamento de participantes
- Histórico completo de reuniões

### 📞 **Gerenciamento de Contatos**
- Lista de contatos organizada
- Ligações diretas via comando de voz
- Categorização automática
- Busca inteligente

### 📊 **Analytics e Relatórios**
- Dashboard com métricas de produtividade
- Gráficos interativos de atividades
- Relatórios em PDF exportáveis
- Insights personalizados

### 🔔 **Lembretes Inteligentes**
- Sugestões automáticas baseadas em padrões
- Lembretes recorrentes
- Priorização inteligente
- Notificações push

### ⚡ **Centro de Automação**
- Templates de automação prontos
- Regras personalizáveis
- Estatísticas de execução
- Integração com todas as funcionalidades

### 🎨 **Interface Moderna**
- Modo escuro/claro/sistema
- Design responsivo para mobile
- PWA (Progressive Web App)
- Animações suaves e micro-interações

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11+
- Node.js 20+
- npm ou yarn

### 1. Backend (Flask)
```bash
cd assistente_backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
python src/main.py
```

### 2. Frontend (React) - Para desenvolvimento
```bash
cd assistente_frontend
npm install
npm run dev
```

### 3. Deploy Completo
O projeto já está configurado para deploy. O frontend é servido pelo Flask:
```bash
cd assistente_backend
source venv/bin/activate
python src/main.py
```

## 📱 Instalação no iPhone

1. Acesse a URL do aplicativo no Safari
2. Toque no botão "Compartilhar" (quadrado com seta)
3. Selecione "Adicionar à Tela de Início"
4. Permita notificações quando solicitado

## 🔐 Credenciais de Acesso

- **Email:** fuda.julio@gmail.com
- **Senha:** assistente2025

## 🛠️ Estrutura do Projeto

```
assistente_pessoal/
├── assistente_backend/          # Backend Flask
│   ├── src/
│   │   ├── models/             # Modelos de dados
│   │   ├── routes/             # APIs REST
│   │   ├── utils/              # Utilitários
│   │   └── static/             # Frontend buildado
│   ├── requirements.txt
│   └── README.md
├── assistente_frontend/         # Frontend React
│   ├── src/
│   │   ├── components/         # Componentes React
│   │   ├── hooks/              # Hooks customizados
│   │   └── App.jsx
│   ├── package.json
│   └── dist/                   # Build de produção
└── README.md
```

## 🔧 Adicionando Novas Funcionalidades

### Backend (Python/Flask)
1. **Criar novo modelo** em `src/models/`:
```python
# src/models/nova_funcionalidade.py
from src.models.user import db

class NovaFuncionalidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    # ... outros campos
```

2. **Criar novas rotas** em `src/routes/`:
```python
# src/routes/nova_funcionalidade.py
from flask import Blueprint, request, jsonify
from src.routes.auth import token_required

nova_bp = Blueprint('nova', __name__)

@nova_bp.route('/nova-rota', methods=['GET'])
@token_required
def nova_rota(current_user):
    # Sua lógica aqui
    return jsonify({'message': 'Sucesso'})
```

3. **Registrar no main.py**:
```python
from src.routes.nova_funcionalidade import nova_bp
app.register_blueprint(nova_bp, url_prefix='/api')
```

### Frontend (React)
1. **Criar novo componente** em `src/components/`:
```jsx
// src/components/NovoComponente.jsx
import { useState, useEffect } from 'react'

const NovoComponente = () => {
  const [dados, setDados] = useState([])
  
  // Sua lógica aqui
  
  return (
    <div>
      {/* Sua interface aqui */}
    </div>
  )
}

export default NovoComponente
```

2. **Adicionar ao App.jsx**:
```jsx
import NovoComponente from './components/NovoComponente.jsx'

// Adicionar na navegação e no renderView()
```

## 🎯 Comandos de Voz Disponíveis

- "Próximos compromissos"
- "Criar compromisso"
- "Ligar para [nome]"
- "Mostrar agenda"
- "Que horas são?"
- "Iniciar reunião"
- "Parar gravação"
- E muitos outros...

## 🔒 Segurança

- Autenticação JWT
- Senhas criptografadas
- CORS configurado
- Validação de dados
- Proteção contra ataques comuns

## 📈 Performance

- PWA com cache offline
- Lazy loading de componentes
- Otimização de bundle
- Compressão de assets
- API otimizada

## 🌐 Compatibilidade

- ✅ iPhone (Safari)
- ✅ Android (Chrome)
- ✅ Desktop (Chrome, Firefox, Safari, Edge)
- ✅ Tablets
- ✅ Modo offline (PWA)

## 🔄 Atualizações Futuras

O projeto está estruturado para fácil expansão:
- Integração com calendários externos
- Sincronização com contatos do telefone
- IA mais avançada
- Mais automações
- Integração com APIs externas

## 📞 Suporte

Para adicionar novas funcionalidades ou fazer modificações:
1. Use VS Code com extensões Python e React
2. Siga a estrutura modular existente
3. Teste localmente antes do deploy
4. Use as APIs existentes como referência

## 🎉 Pronto para Usar!

O assistente está completamente funcional e pronto para uso profissional. Todas as funcionalidades foram testadas e otimizadas para a melhor experiência do usuário.

