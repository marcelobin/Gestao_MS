import os

def apagar_migracoes(projeto_path):
    """
    Apaga todos os arquivos de migração em um projeto Django, exceto '__init__.py'.
    Ignora pastas ocultas (ex.: .venv, .git) ao percorrer o diretório.
    :param projeto_path: Caminho absoluto para a pasta principal do projeto.
    """
    migracoes_apagadas = 0

    for root, dirs, files in os.walk(projeto_path):
        # Remover pastas ocultas (as que começam com '.') e .venv/venv
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('.venv', 'venv')]

        # Se o diretório for uma pasta de migrations
        if root.endswith('migrations'):
            for file in files:
                if file != '__init__.py' and file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    migracoes_apagadas += 1
                    print(f"Removido: {file_path}")

    if migracoes_apagadas == 0:
        print("Nenhuma migração encontrada para apagar.")
    else:
        print(f"Todas as {migracoes_apagadas} migrações foram apagadas com sucesso!")


# Exemplo de uso, apontando para o diretório atual:
if __name__ == "__main__":
    caminho_projeto = os.path.abspath('.')  # Use o diretório atual como padrão
    apagar_migracoes(caminho_projeto)
