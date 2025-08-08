from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.contato import Contato
from datetime import datetime

contato_bp = Blueprint('contato', __name__)

@contato_bp.route('/contatos', methods=['GET'])
def listar_contatos():
    """Lista todos os contatos"""
    try:
        # Parâmetros de filtro opcionais
        categoria = request.args.get('categoria')
        favoritos = request.args.get('favoritos')
        busca = request.args.get('busca')
        
        query = Contato.query
        
        if categoria:
            query = query.filter(Contato.categoria == categoria)
        if favoritos and favoritos.lower() == 'true':
            query = query.filter(Contato.favorito == True)
        if busca:
            # Busca por nome, empresa ou telefone
            busca_termo = f"%{busca}%"
            query = query.filter(
                db.or_(
                    Contato.nome.ilike(busca_termo),
                    Contato.empresa.ilike(busca_termo),
                    Contato.telefone.ilike(busca_termo),
                    Contato.email.ilike(busca_termo)
                )
            )
        
        contatos = query.order_by(Contato.nome.asc()).all()
        return jsonify([contato.to_dict() for contato in contatos])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@contato_bp.route('/contatos', methods=['POST'])
def criar_contato():
    """Cria um novo contato"""
    try:
        dados = request.get_json()
        
        # Validação básica
        if not dados.get('nome'):
            return jsonify({'erro': 'Nome é obrigatório'}), 400
        
        contato = Contato(
            nome=dados['nome'],
            telefone=dados.get('telefone', ''),
            email=dados.get('email', ''),
            empresa=dados.get('empresa', ''),
            cargo=dados.get('cargo', ''),
            categoria=dados.get('categoria', 'geral'),
            favorito=dados.get('favorito', False),
            notas=dados.get('notas', ''),
            foto_url=dados.get('foto_url', '')
        )
        
        db.session.add(contato)
        db.session.commit()
        
        return jsonify(contato.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@contato_bp.route('/contatos/<contato_id>', methods=['GET'])
def obter_contato(contato_id):
    """Obtém um contato específico"""
    try:
        contato = Contato.query.get_or_404(contato_id)
        return jsonify(contato.to_dict())
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@contato_bp.route('/contatos/<contato_id>', methods=['PUT'])
def atualizar_contato(contato_id):
    """Atualiza um contato"""
    try:
        contato = Contato.query.get_or_404(contato_id)
        dados = request.get_json()
        
        # Atualiza campos se fornecidos
        if 'nome' in dados:
            contato.nome = dados['nome']
        if 'telefone' in dados:
            contato.telefone = dados['telefone']
        if 'email' in dados:
            contato.email = dados['email']
        if 'empresa' in dados:
            contato.empresa = dados['empresa']
        if 'cargo' in dados:
            contato.cargo = dados['cargo']
        if 'categoria' in dados:
            contato.categoria = dados['categoria']
        if 'favorito' in dados:
            contato.favorito = dados['favorito']
        if 'notas' in dados:
            contato.notas = dados['notas']
        if 'foto_url' in dados:
            contato.foto_url = dados['foto_url']
        
        contato.atualizado_em = datetime.utcnow()
        db.session.commit()
        
        return jsonify(contato.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@contato_bp.route('/contatos/<contato_id>', methods=['DELETE'])
def deletar_contato(contato_id):
    """Deleta um contato"""
    try:
        contato = Contato.query.get_or_404(contato_id)
        db.session.delete(contato)
        db.session.commit()
        return jsonify({'mensagem': 'Contato deletado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@contato_bp.route('/contatos/favoritos', methods=['GET'])
def contatos_favoritos():
    """Lista contatos favoritos"""
    try:
        contatos = Contato.query.filter(Contato.favorito == True).order_by(Contato.nome.asc()).all()
        return jsonify([contato.to_dict() for contato in contatos])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@contato_bp.route('/contatos/<contato_id>/favorito', methods=['POST'])
def alternar_favorito(contato_id):
    """Alterna status de favorito do contato"""
    try:
        contato = Contato.query.get_or_404(contato_id)
        contato.favorito = not contato.favorito
        contato.atualizado_em = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'id': contato.id,
            'favorito': contato.favorito,
            'mensagem': f'Contato {"adicionado aos" if contato.favorito else "removido dos"} favoritos'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@contato_bp.route('/contatos/categorias', methods=['GET'])
def listar_categorias():
    """Lista todas as categorias de contatos"""
    try:
        # Busca categorias únicas
        categorias = db.session.query(Contato.categoria).distinct().all()
        categorias_lista = [cat[0] for cat in categorias if cat[0]]
        
        # Adiciona categorias padrão se não existirem
        categorias_padrao = ['trabalho', 'pessoal', 'familia', 'amigos', 'geral']
        for cat in categorias_padrao:
            if cat not in categorias_lista:
                categorias_lista.append(cat)
        
        return jsonify(sorted(categorias_lista))
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@contato_bp.route('/contatos/buscar', methods=['GET'])
def buscar_contatos():
    """Busca contatos por nome, telefone ou empresa"""
    try:
        termo = request.args.get('q', '').strip()
        
        if not termo:
            return jsonify({'erro': 'Termo de busca é obrigatório'}), 400
        
        if len(termo) < 2:
            return jsonify({'erro': 'Termo de busca deve ter pelo menos 2 caracteres'}), 400
        
        busca_termo = f"%{termo}%"
        contatos = Contato.query.filter(
            db.or_(
                Contato.nome.ilike(busca_termo),
                Contato.empresa.ilike(busca_termo),
                Contato.telefone.ilike(busca_termo),
                Contato.email.ilike(busca_termo),
                Contato.cargo.ilike(busca_termo)
            )
        ).order_by(Contato.nome.asc()).limit(20).all()
        
        return jsonify([contato.to_dict() for contato in contatos])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@contato_bp.route('/contatos/ligar/<contato_id>', methods=['POST'])
def iniciar_ligacao(contato_id):
    """Retorna informações para iniciar ligação"""
    try:
        contato = Contato.query.get_or_404(contato_id)
        
        if not contato.telefone:
            return jsonify({'erro': 'Contato não possui telefone cadastrado'}), 400
        
        # Remove caracteres especiais do telefone
        telefone_limpo = ''.join(filter(str.isdigit, contato.telefone))
        
        return jsonify({
            'contato': contato.to_dict(),
            'telefone': contato.telefone,
            'telefone_limpo': telefone_limpo,
            'url_ligacao': f'tel:{telefone_limpo}',
            'mensagem': f'Iniciando ligação para {contato.nome}'
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

