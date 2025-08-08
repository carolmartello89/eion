from src.models.user import db
from src.models.subscription import PlanoAssinatura, CupomDesconto
from datetime import datetime, timedelta

def criar_planos_iniciais():
    """Cria planos iniciais para o sistema"""
    
    # Verifica se já existem planos
    if PlanoAssinatura.query.first():
        print("Planos já existem!")
        return
    
    planos = [
        {
            'nome': 'Gratuito',
            'descricao': 'Perfeito para começar a organizar sua vida pessoal',
            'preco_mensal': 0,
            'preco_anual': 0,
            'max_usuarios': 1,
            'max_transacoes_mes': 50,
            'max_reunioes_mes': 5,
            'max_storage_gb': 0.5,
            'tem_voice_auth': False,
            'tem_speaker_diarization': False,
            'tem_ai_avancada': False,
            'tem_relatorios_excel': False,
            'tem_automacao': False,
            'tem_api_access': False,
            'tem_suporte_prioritario': False,
            'ordem_exibicao': 1
        },
        {
            'nome': 'Pessoal',
            'descricao': 'Para quem quer mais produtividade e recursos avançados',
            'preco_mensal': 29.90,
            'preco_anual': 299.00,  # 2 meses grátis
            'max_usuarios': 1,
            'max_transacoes_mes': 500,
            'max_reunioes_mes': 20,
            'max_storage_gb': 5.0,
            'tem_voice_auth': True,
            'tem_speaker_diarization': True,
            'tem_ai_avancada': True,
            'tem_relatorios_excel': True,
            'tem_automacao': True,
            'tem_api_access': False,
            'tem_suporte_prioritario': True,
            'ordem_exibicao': 2
        },
        {
            'nome': 'Profissional',
            'descricao': 'Para profissionais que precisam de recursos empresariais',
            'preco_mensal': 59.90,
            'preco_anual': 599.00,  # 2 meses grátis
            'max_usuarios': 3,
            'max_transacoes_mes': 2000,
            'max_reunioes_mes': 100,
            'max_storage_gb': 20.0,
            'tem_voice_auth': True,
            'tem_speaker_diarization': True,
            'tem_ai_avancada': True,
            'tem_relatorios_excel': True,
            'tem_automacao': True,
            'tem_api_access': True,
            'tem_suporte_prioritario': True,
            'ordem_exibicao': 3
        },
        {
            'nome': 'Empresarial',
            'descricao': 'Para equipes e empresas que precisam do máximo',
            'preco_mensal': 99.90,
            'preco_anual': 999.00,  # 2 meses grátis
            'max_usuarios': 10,
            'max_transacoes_mes': 10000,
            'max_reunioes_mes': 500,
            'max_storage_gb': 100.0,
            'tem_voice_auth': True,
            'tem_speaker_diarization': True,
            'tem_ai_avancada': True,
            'tem_relatorios_excel': True,
            'tem_automacao': True,
            'tem_api_access': True,
            'tem_suporte_prioritario': True,
            'ordem_exibicao': 4
        }
    ]
    
    for plano_data in planos:
        plano = PlanoAssinatura(**plano_data)
        db.session.add(plano)
    
    db.session.commit()
    print(f"Criados {len(planos)} planos iniciais!")

def criar_cupons_iniciais():
    """Cria cupons promocionais iniciais"""
    
    cupons = [
        {
            'codigo': 'WELCOME30',
            'nome': 'Desconto de Boas-vindas',
            'descricao': '30% de desconto na primeira assinatura',
            'tipo_desconto': 'percentual',
            'valor_desconto': 30,
            'data_inicio': datetime.utcnow(),
            'data_fim': datetime.utcnow() + timedelta(days=365),
            'max_usos_total': 1000,
            'max_usos_por_usuario': 1,
            'ativo': True
        },
        {
            'codigo': 'TESTE7DIAS',
            'nome': 'Teste Gratuito 7 Dias',
            'descricao': '7 dias gratuitos do plano Pessoal',
            'tipo_desconto': 'gratuito',
            'data_inicio': datetime.utcnow(),
            'data_fim': datetime.utcnow() + timedelta(days=365),
            'max_usos_total': 500,
            'max_usos_por_usuario': 1,
            'ativo': True
        },
        {
            'codigo': 'BLACKFRIDAY50',
            'nome': 'Black Friday',
            'descricao': '50% de desconto - oferta especial',
            'tipo_desconto': 'percentual',
            'valor_desconto': 50,
            'data_inicio': datetime.utcnow(),
            'data_fim': datetime.utcnow() + timedelta(days=30),
            'max_usos_total': 100,
            'max_usos_por_usuario': 1,
            'ativo': True
        },
        {
            'codigo': 'PRIMEIROANO',
            'nome': 'Primeiro Ano Grátis',
            'descricao': 'Primeiro ano gratuito para usuários selecionados',
            'tipo_desconto': 'gratuito',
            'data_inicio': datetime.utcnow(),
            'data_fim': datetime.utcnow() + timedelta(days=365),
            'max_usos_total': 50,
            'max_usos_por_usuario': 1,
            'uso_interno': True,
            'ativo': True
        }
    ]
    
    for cupom_data in cupons:
        # Verifica se cupom já existe
        if not CupomDesconto.query.filter_by(codigo=cupom_data['codigo']).first():
            cupom = CupomDesconto(**cupom_data)
            db.session.add(cupom)
    
    db.session.commit()
    print(f"Cupons promocionais criados!")

def inicializar_sistema_comercial():
    """Inicializa todo o sistema comercial"""
    try:
        criar_planos_iniciais()
        criar_cupons_iniciais()
        print("✅ Sistema comercial inicializado com sucesso!")
        
        # Mostra resumo
        total_planos = PlanoAssinatura.query.count()
        total_cupons = CupomDesconto.query.count()
        
        print(f"📊 Resumo:")
        print(f"   • {total_planos} planos criados")
        print(f"   • {total_cupons} cupons disponíveis")
        print(f"")
        print(f"🎫 Cupons disponíveis:")
        cupons = CupomDesconto.query.filter_by(ativo=True).all()
        for cupom in cupons:
            print(f"   • {cupom.codigo}: {cupom.nome}")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar sistema comercial: {e}")

if __name__ == '__main__':
    from src.models.user import db
    from flask import Flask
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        inicializar_sistema_comercial()
