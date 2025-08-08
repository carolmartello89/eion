# Assistente Pessoal

Assistente Pessoal é um sistema web completo (backend + frontend) para organização de compromissos, reuniões, contatos e automação de tarefas, com assistente de voz e notificações inteligentes. Ideal para uso pessoal ou profissional, com interface responsiva e instalação como PWA no iPhone.

## Funcionalidades Principais
- Gerenciamento de compromissos e agenda
- Agendamento e gravação de reuniões
- Cadastro e organização de contatos
- Assistente de voz com comandos inteligentes
- Notificações push e lembretes
- Instalação como app (PWA) no iOS

## Estrutura do Projeto
```
assistente_pessoal/
├── assistente_backend/   # Backend Python (Flask)
│   └── src/             # Models, rotas, serviços, utils
├── assistente_frontend/ # Frontend React (Vite)
│   └── src/             # Componentes, hooks, assets
├── INSTRUCOES_INSTALACAO.md # Manual de instalação e uso
├── requirements.txt     # Dependências do backend
├── .gitignore           # Arquivos ignorados no Git
└── README.md            # Este arquivo
```

## Instalação e Uso

### 1. Backend (Python)
1. Acesse a pasta `assistente_backend`
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o backend:
   ```bash
   python src/main.py
   ```

### 2. Frontend (React)
1. Acesse a pasta `assistente_frontend`
2. Instale as dependências:
   ```bash
   pnpm install
   # ou npm install
   ```
3. Inicie o frontend:
   ```bash
   pnpm dev
   # ou npm run dev
   ```

### 3. Instalação no iPhone (PWA)
- Siga o passo a passo detalhado no arquivo `INSTRUCOES_INSTALACAO.md`.

## Deploy
- O sistema pode ser publicado facilmente no Vercel (frontend) e em qualquer serviço de backend Python (Heroku, Render, etc).
- Para deploy local, basta rodar backend e frontend conforme instruções acima.

## Licença
MIT License. Sinta-se livre para usar, modificar e compartilhar!

## Suporte
Dúvidas ou problemas? Consulte o `INSTRUCOES_INSTALACAO.md` ou abra uma issue.

---
Desenvolvido com ❤️ para otimizar sua produtividade pessoal!
