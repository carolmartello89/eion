import os
import sys
from flask import Flask, jsonify, send_from_directory, render_template_string
from flask_cors import CORS

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações básicas
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Inicializar CORS
CORS(app, origins="*")

@app.route('/api/health')
def health_check():
    """Endpoint de verificação de saúde"""
    return {'status': 'ok', 'message': 'IAON Backend funcionando!'}

@app.route('/api/status')
def status():
    """Status do sistema"""
    return {
        'status': 'running',
        'version': '1.0.0',
        'modules': ['IA Avançada', 'Telemedicina', 'Gestão Financeira', 'Agenda', 'Automação']
    }

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve a interface principal do IAON"""
    html_template = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IAON - Sistema de IA Completo</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #581c87 100%);
                min-height: 100vh;
                color: white;
                overflow-x: hidden;
            }
            
            .header {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(20px);
                padding: 1rem 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .logo {
                display: flex;
                align-items: center;
                gap: 15px;
                font-size: 1.8em;
                font-weight: 700;
            }
            
            .logo i {
                background: linear-gradient(45deg, #ffd700, #ffed4e);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 2em;
            }
            
            .nav {
                display: flex;
                gap: 2rem;
            }
            
            .nav-item {
                padding: 0.5rem 1rem;
                border-radius: 25px;
                background: rgba(255, 255, 255, 0.1);
                cursor: pointer;
                transition: all 0.3s ease;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .nav-item:hover, .nav-item.active {
                background: rgba(255, 255, 255, 0.2);
                transform: translateY(-2px);
            }
            
            .main-content {
                padding: 2rem;
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .welcome-section {
                text-align: center;
                margin-bottom: 3rem;
                padding: 2rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            
            .welcome-title {
                font-size: 3rem;
                margin-bottom: 1rem;
                background: linear-gradient(45deg, #ffd700, #ffed4e, #ffa500);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .modules-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
                margin-bottom: 3rem;
            }
            
            .module-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 2rem;
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .module-card:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.15);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            }
            
            .module-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
                color: #ffd700;
            }
            
            .module-title {
                font-size: 1.5rem;
                margin-bottom: 1rem;
                font-weight: 600;
            }
            
            .module-description {
                opacity: 0.8;
                line-height: 1.6;
                margin-bottom: 1.5rem;
            }
            
            .module-btn {
                background: linear-gradient(45deg, #ffd700, #ffed4e);
                color: #333;
                border: none;
                padding: 0.8rem 1.5rem;
                border-radius: 25px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
            }
            
            .module-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(255, 215, 0, 0.4);
            }
            
            .status-bar {
                background: rgba(34, 197, 94, 0.2);
                border: 1px solid rgba(34, 197, 94, 0.3);
                border-radius: 10px;
                padding: 1rem;
                text-align: center;
                margin-bottom: 2rem;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            
            .status-indicator {
                width: 12px;
                height: 12px;
                background: #22c55e;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .quick-actions {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 2rem;
                margin-bottom: 2rem;
            }
            
            .quick-actions h3 {
                margin-bottom: 1.5rem;
                font-size: 1.5rem;
                text-align: center;
            }
            
            .actions-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
            }
            
            .action-btn {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                padding: 1rem;
                color: white;
                text-decoration: none;
                transition: all 0.3s ease;
                text-align: center;
                cursor: pointer;
            }
            
            .action-btn:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: translateY(-2px);
            }
            
            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                z-index: 1000;
                align-items: center;
                justify-content: center;
            }
            
            .modal-content {
                background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
                border-radius: 20px;
                padding: 2rem;
                max-width: 600px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .modal-close {
                float: right;
                font-size: 2rem;
                cursor: pointer;
                color: #ffd700;
            }
            
            @media (max-width: 768px) {
                .header { flex-direction: column; gap: 1rem; }
                .nav { flex-wrap: wrap; }
                .welcome-title { font-size: 2rem; }
                .modules-grid { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">
                <i class="fas fa-brain"></i>
                <span>IAON</span>
            </div>
            <div class="nav">
                <div class="nav-item active" onclick="showSection('dashboard')">
                    <i class="fas fa-home"></i> Dashboard
                </div>
                <div class="nav-item" onclick="showSection('ia')">
                    <i class="fas fa-robot"></i> IA
                </div>
                <div class="nav-item" onclick="showSection('medicina')">
                    <i class="fas fa-stethoscope"></i> Medicina
                </div>
                <div class="nav-item" onclick="showSection('agenda')">
                    <i class="fas fa-calendar"></i> Agenda
                </div>
                <div class="nav-item" onclick="showSection('financeiro')">
                    <i class="fas fa-chart-line"></i> Financeiro
                </div>
            </div>
        </div>

        <div class="main-content">
            <div class="status-bar">
                <div class="status-indicator"></div>
                <span><strong>Sistema IAON Online</strong> - Todos os módulos funcionando</span>
            </div>

            <div class="welcome-section">
                <h1 class="welcome-title">🚀 Bem-vindo ao IAON</h1>
                <p style="font-size: 1.3rem; opacity: 0.9;">
                    Sistema Inteligente de Assistência Organizacional com Neurociência
                </p>
                <p style="margin-top: 1rem; opacity: 0.8;">
                    Versão 2.0 - Integração completa com IA, Telemedicina e Automação
                </p>
            </div>

            <div class="modules-grid">
                <div class="module-card" onclick="openModule('ia')">
                    <div class="module-icon">
                        <i class="fas fa-brain"></i>
                    </div>
                    <h3 class="module-title">IA Avançada</h3>
                    <p class="module-description">
                        Processamento de linguagem natural, análise de sentimentos e automação inteligente baseada em neurociência.
                    </p>
                    <button class="module-btn">Acessar IA</button>
                </div>

                <div class="module-card" onclick="openModule('medicina')">
                    <div class="module-icon">
                        <i class="fas fa-user-md"></i>
                    </div>
                    <h3 class="module-title">Telemedicina</h3>
                    <p class="module-description">
                        Sistema completo de consultas online, prontuários digitais e acompanhamento médico remoto.
                    </p>
                    <button class="module-btn">Acessar Medicina</button>
                </div>

                <div class="module-card" onclick="openModule('financeiro')">
                    <div class="module-icon">
                        <i class="fas fa-chart-pie"></i>
                    </div>
                    <h3 class="module-title">Gestão Financeira</h3>
                    <p class="module-description">
                        Controle completo de finanças pessoais e empresariais com análise preditiva e relatórios inteligentes.
                    </p>
                    <button class="module-btn">Acessar Financeiro</button>
                </div>

                <div class="module-card" onclick="openModule('agenda')">
                    <div class="module-icon">
                        <i class="fas fa-calendar-check"></i>
                    </div>
                    <h3 class="module-title">Agenda Inteligente</h3>
                    <p class="module-description">
                        Organização automática de compromissos, lembretes inteligentes e sincronização com todos os dispositivos.
                    </p>
                    <button class="module-btn">Acessar Agenda</button>
                </div>

                <div class="module-card" onclick="openModule('reunioes')">
                    <div class="module-icon">
                        <i class="fas fa-video"></i>
                    </div>
                    <h3 class="module-title">Centro de Reuniões</h3>
                    <p class="module-description">
                        Gravação automática, transcrição em tempo real e análise de reuniões com IA.
                    </p>
                    <button class="module-btn">Acessar Reuniões</button>
                </div>

                <div class="module-card" onclick="openModule('automacao')">
                    <div class="module-icon">
                        <i class="fas fa-cogs"></i>
                    </div>
                    <h3 class="module-title">Automação</h3>
                    <p class="module-description">
                        Automatização de tarefas repetitivas, integração com sistemas externos e workflows inteligentes.
                    </p>
                    <button class="module-btn">Acessar Automação</button>
                </div>
            </div>

            <div class="quick-actions">
                <h3><i class="fas fa-bolt"></i> Ações Rápidas</h3>
                <div class="actions-grid">
                    <div class="action-btn" onclick="quickAction('nova-consulta')">
                        <i class="fas fa-plus-circle"></i><br>Nova Consulta
                    </div>
                    <div class="action-btn" onclick="quickAction('analise-financeira')">
                        <i class="fas fa-chart-bar"></i><br>Análise Financeira
                    </div>
                    <div class="action-btn" onclick="quickAction('reuniao-urgente')">
                        <i class="fas fa-phone"></i><br>Reunião Urgente
                    </div>
                    <div class="action-btn" onclick="quickAction('relatorio-ia')">
                        <i class="fas fa-file-alt"></i><br>Relatório IA
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal para módulos -->
        <div id="moduleModal" class="modal">
            <div class="modal-content">
                <span class="modal-close" onclick="closeModal()">&times;</span>
                <div id="modalContent">
                    <!-- Conteúdo do módulo será carregado aqui -->
                </div>
            </div>
        </div>

        <script>
            function showSection(section) {
                // Remover classe active de todos os nav-items
                document.querySelectorAll('.nav-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Adicionar classe active ao item clicado
                event.target.classList.add('active');
                
                // Aqui você pode implementar a lógica para mostrar diferentes seções
                console.log('Mostrando seção:', section);
            }

            function openModule(module) {
                const modal = document.getElementById('moduleModal');
                const modalContent = document.getElementById('modalContent');
                
                let content = '';
                
                switch(module) {
                    case 'ia':
                        content = `
                            <h2><i class="fas fa-brain"></i> Módulo IA Avançada</h2>
                            <p>Sistema de Inteligência Artificial com capacidades avançadas:</p>
                            <ul style="margin: 1rem 0; padding-left: 2rem;">
                                <li>Processamento de Linguagem Natural</li>
                                <li>Análise de Sentimentos</li>
                                <li>Reconhecimento de Voz</li>
                                <li>Automação Inteligente</li>
                                <li>Aprendizado de Máquina</li>
                            </ul>
                            <div style="margin-top: 2rem;">
                                <button class="module-btn" style="margin: 0.5rem;">Iniciar Chat IA</button>
                                <button class="module-btn" style="margin: 0.5rem;">Análise de Documentos</button>
                                <button class="module-btn" style="margin: 0.5rem;">Configurações IA</button>
                            </div>
                        `;
                        break;
                        
                    case 'medicina':
                        content = `
                            <h2><i class="fas fa-user-md"></i> Módulo Telemedicina</h2>
                            <p>Sistema completo de atendimento médico digital:</p>
                            <ul style="margin: 1rem 0; padding-left: 2rem;">
                                <li>Consultas Online</li>
                                <li>Prontuário Eletrônico</li>
                                <li>Prescrições Digitais</li>
                                <li>Agendamento de Consultas</li>
                                <li>Histórico Médico</li>
                            </ul>
                            <div style="margin-top: 2rem;">
                                <button class="module-btn" style="margin: 0.5rem;">Nova Consulta</button>
                                <button class="module-btn" style="margin: 0.5rem;">Prontuários</button>
                                <button class="module-btn" style="margin: 0.5rem;">Agenda Médica</button>
                            </div>
                        `;
                        break;
                        
                    case 'financeiro':
                        content = `
                            <h2><i class="fas fa-chart-pie"></i> Módulo Financeiro</h2>
                            <p>Gestão completa das suas finanças:</p>
                            <ul style="margin: 1rem 0; padding-left: 2rem;">
                                <li>Controle de Receitas e Despesas</li>
                                <li>Análise de Investimentos</li>
                                <li>Relatórios Financeiros</li>
                                <li>Planejamento Orçamentário</li>
                                <li>Integração Bancária</li>
                            </ul>
                            <div style="margin-top: 2rem;">
                                <button class="module-btn" style="margin: 0.5rem;">Dashboard Financeiro</button>
                                <button class="module-btn" style="margin: 0.5rem;">Nova Transação</button>
                                <button class="module-btn" style="margin: 0.5rem;">Relatórios</button>
                            </div>
                        `;
                        break;
                        
                    case 'agenda':
                        content = `
                            <h2><i class="fas fa-calendar-check"></i> Agenda Inteligente</h2>
                            <p>Organização inteligente de compromissos:</p>
                            <ul style="margin: 1rem 0; padding-left: 2rem;">
                                <li>Agendamento Automático</li>
                                <li>Lembretes Inteligentes</li>
                                <li>Sincronização Multi-dispositivos</li>
                                <li>Análise de Produtividade</li>
                                <li>Integração com Email</li>
                            </ul>
                            <div style="margin-top: 2rem;">
                                <button class="module-btn" style="margin: 0.5rem;">Ver Agenda</button>
                                <button class="module-btn" style="margin: 0.5rem;">Novo Compromisso</button>
                                <button class="module-btn" style="margin: 0.5rem;">Configurações</button>
                            </div>
                        `;
                        break;
                        
                    case 'reunioes':
                        content = `
                            <h2><i class="fas fa-video"></i> Centro de Reuniões</h2>
                            <p>Gestão completa de reuniões e videoconferências:</p>
                            <ul style="margin: 1rem 0; padding-left: 2rem;">
                                <li>Gravação Automática</li>
                                <li>Transcrição em Tempo Real</li>
                                <li>Análise de Participação</li>
                                <li>Resumos Automáticos</li>
                                <li>Compartilhamento de Tela</li>
                            </ul>
                            <div style="margin-top: 2rem;">
                                <button class="module-btn" style="margin: 0.5rem;">Iniciar Reunião</button>
                                <button class="module-btn" style="margin: 0.5rem;">Reuniões Gravadas</button>
                                <button class="module-btn" style="margin: 0.5rem;">Agendar Reunião</button>
                            </div>
                        `;
                        break;
                        
                    case 'automacao':
                        content = `
                            <h2><i class="fas fa-cogs"></i> Centro de Automação</h2>
                            <p>Automatização inteligente de processos:</p>
                            <ul style="margin: 1rem 0; padding-left: 2rem;">
                                <li>Workflows Personalizados</li>
                                <li>Integração com APIs</li>
                                <li>Automação de Emails</li>
                                <li>Processamento de Documentos</li>
                                <li>Triggers Inteligentes</li>
                            </ul>
                            <div style="margin-top: 2rem;">
                                <button class="module-btn" style="margin: 0.5rem;">Criar Automação</button>
                                <button class="module-btn" style="margin: 0.5rem;">Automações Ativas</button>
                                <button class="module-btn" style="margin: 0.5rem;">Templates</button>
                            </div>
                        `;
                        break;
                }
                
                modalContent.innerHTML = content;
                modal.style.display = 'flex';
            }

            function closeModal() {
                document.getElementById('moduleModal').style.display = 'none';
            }

            function quickAction(action) {
                alert(`Executando ação: ${action}\\n\\nEsta funcionalidade será implementada em breve!`);
            }

            // Fechar modal ao clicar fora dele
            window.onclick = function(event) {
                const modal = document.getElementById('moduleModal');
                if (event.target == modal) {
                    modal.style.display = 'none';
                }
            }

            // Animação de entrada
            window.onload = function() {
                console.log('🚀 IAON Sistema carregado com sucesso!');
                
                // Simular loading dos módulos
                setTimeout(() => {
                    document.querySelectorAll('.module-card').forEach((card, index) => {
                        setTimeout(() => {
                            card.style.opacity = '0';
                            card.style.transform = 'translateY(20px)';
                            setTimeout(() => {
                                card.style.transition = 'all 0.5s ease';
                                card.style.opacity = '1';
                                card.style.transform = 'translateY(0)';
                            }, 50);
                        }, index * 100);
                    });
                }, 500);
            }
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html_template)

if __name__ == '__main__':
    print("🚀 Iniciando IAON - Sistema de IA...")
    print("🌐 Servidor rodando em: http://localhost:5000")
    print("📊 Health Check: http://localhost:5000/api/health")
    print("✨ Interface: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
