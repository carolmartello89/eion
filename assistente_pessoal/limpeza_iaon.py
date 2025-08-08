import os
import shutil

# Pastas e arquivos ORIGINAIS do sistema manus.ia que devem ser mantidos
MANTER_PASTAS = [
    'assistente_backend',
    'assistente_frontend'
]
MANTER_ARQUIVOS = [
    'requirements.txt',
    'vercel.json',
    'INSTRUCOES_INSTALACAO.md',
    'README.md'
]

# Função para deletar tudo que não está na lista de manter
def limpar_pasta(base_path):
    for item in os.listdir(base_path):
        if item in MANTER_PASTAS or item in MANTER_ARQUIVOS:
            continue
        caminho = os.path.join(base_path, item)
        try:
            if os.path.isdir(caminho):
                shutil.rmtree(caminho)
                print(f'Pasta removida: {caminho}')
            else:
                os.remove(caminho)
                print(f'Arquivo removido: {caminho}')
        except Exception as e:
            print(f'Erro ao remover {caminho}: {e}')

if __name__ == '__main__':
    pasta_base = os.path.dirname(os.path.abspath(__file__))
    limpar_pasta(pasta_base)
    print('\nLimpeza concluída! Só os arquivos originais manus.ia foram mantidos.')
