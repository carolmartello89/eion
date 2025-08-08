from src.models.user import db
from src.models.auth import AuthUser

def init_auth_user():
    """Inicializa o usuário de autenticação padrão"""
    
    # Verifica se já existe um usuário com este email
    existing_user = AuthUser.query.filter_by(email='fuda.julio@gmail.com').first()
    
    if existing_user:
        print("Usuário já existe!")
        return existing_user
    
    # Cria novo usuário
    user = AuthUser(email='fuda.julio@gmail.com')
    user.set_password('assistente2025')  # Senha padrão
    
    db.session.add(user)
    db.session.commit()
    
    print(f"Usuário criado com sucesso!")
    print(f"Email: fuda.julio@gmail.com")
    print(f"Senha: assistente2025")
    
    return user

if __name__ == '__main__':
    init_auth_user()

