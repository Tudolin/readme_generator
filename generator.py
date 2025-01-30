import ast
import os
import re

DIRECTORY = '.'

README_TEMPLATE = """
{status_badge}
{language_badges}

# Índice

* [Introdução](#introdução)
* [Instalação de Dependências](#instalação-de-dependências)
* [Estrutura do Código](#estrutura-do-código)
* [Funções e Classes](#funções-e-classes){toc_routes}
* [Execução da Aplicação](#execução-da-aplicação)

# Introdução

{introduction}

# Instalação de Dependências

Para instalar as dependências, utilize o seguinte comando:

```bash
pip install -r requirements.txt
```
# Estrutura do Código

O código está organizado da seguinte forma:

{code_structure}

# Funções e Classes

{functions_doc}

{classes_doc}

{routes_section}

# Execução da Aplicação

{execution_section}
"""


def extract_functions_classes_routes(file_path):
    """
    Extrai funções, classes, rotas do Flask, e verifica se o arquivo contém 'app.run()'.

    Args:
    file_path (str): Caminho para o arquivo Python a ser analisado.

Returns:
    tuple: Contém listas de funções, classes, rotas, um booleano indicando se 'app.run()' está presente,
           e um booleano indicando se Flask está sendo utilizado.
"""
    with open(file_path, 'r', encoding='utf-8') as file:
        node = ast.parse(file.read(), filename=file_path)

    functions = []
    classes = []
    routes = []
    has_app_run = False
    is_flask_app = False

    # Verifica as importações para identificar se Flask está sendo usado
    for n in node.body:
        if isinstance(n, ast.Import):
            for alias in n.names:
                if alias.name == 'flask' or 'Flask':
                    is_flask_app = True
        elif isinstance(n, ast.ImportFrom):
            if n.module == 'flask' or 'Flask':
                is_flask_app = True

    # Itera sobre os elementos do nó AST para extrair informações
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            docstring = ast.get_docstring(item)
            functions.append({
                'name': item.name,
                'docstring': docstring
            })

        elif isinstance(item, ast.ClassDef):
            class_doc = ast.get_docstring(item)
            methods = []
            for elem in item.body:
                if isinstance(elem, ast.FunctionDef):
                    method_doc = ast.get_docstring(elem)
                    methods.append({
                        'name': elem.name,
                        'docstring': method_doc
                    })
            classes.append({
                'name': item.name,
                'docstring': class_doc,
                'methods': methods
            })

        elif isinstance(item, ast.Expr) and isinstance(item.value, ast.Call):
            if isinstance(item.value.func, ast.Attribute):
                if item.value.func.attr == 'route':
                    is_flask_app = True  # O uso de rotas indica que é um aplicativo Flask
                    route_path = item.value.args[0].s if item.value.args else ''
                    methods = ''
                    for keyword in item.value.keywords:
                        if keyword.arg == 'methods':
                            methods = ', '.join([method.s for method in keyword.value.elts])
                    routes.append({
                        'route': route_path,
                        'methods': methods
                    })
                if item.value.func.attr == 'run':
                    has_app_run = True

    return functions, classes, routes, has_app_run, is_flask_app


def generate_code_structure(directory, exclude_files):
    """
    Gera a estrutura de diretórios e arquivos Python, excluindo arquivos especificados.

    Args:
    directory (str): Diretório raiz para a geração da estrutura.
    exclude_files (list): Lista de nomes de arquivos a serem excluídos.

    Returns:
        str: Representação em Markdown da estrutura de código.
    """
    structure_lines = []

    for root, dirs, files in os.walk(directory):
        rel_dir = os.path.relpath(root, directory)
        if any(part.startswith('.') for part in rel_dir.split(os.sep)):
            continue
        level = rel_dir.count(os.sep)
        indent = ' ' * 4 * level
        if rel_dir != '.':
            structure_lines.append(f"{indent}- **{os.path.basename(root)}/**")
        sub_indent = ' ' * 4 * (level + 1)
        for name in files:
            if name.endswith('.py') and name not in exclude_files and not name.startswith('.'):
                structure_lines.append(f"{sub_indent}- `{name}`")

    return '\n'.join(structure_lines)


def generate_functions_doc(functions):
    """
    Gera a documentação em Markdown para as funções extraídas.

    Args:
    functions (list): Lista de dicionários contendo informações sobre as funções.

    Returns:
        str: Documentação em Markdown das funções.
    """
    doc = ''
    for func in functions:
        doc += f"### `{func['name']}`\n\n"
        if func['docstring']:
            doc += f"{func['docstring']}\n\n"
        else:
            doc += "Sem descrição disponível.\n\n"
    return doc


def generate_classes_doc(classes):
    """
    Gera a documentação em Markdown para as classes e seus métodos.

    Args:
    classes (list): Lista de dicionários contendo informações sobre as classes e métodos.

    Returns:
        str: Documentação em Markdown das classes e métodos.
    """
    doc = ''
    for cls in classes:
        doc += f"### Classe `{cls['name']}`\n\n"
        if cls['docstring']:
            doc += f"{cls['docstring']}\n\n"
        else:
            doc += "Sem descrição disponível.\n\n"
        if cls['methods']:
            doc += f"#### Métodos:\n\n"
            for method in cls['methods']:
                doc += f"- **`{method['name']}()`**\n"
                if method['docstring']:
                    doc += f"  {method['docstring']}\n\n"
                else:
                    doc += "  Sem descrição disponível.\n\n"
    return doc


def generate_routes_doc(routes):
    """
    Gera a documentação em Markdown para as rotas do Flask.

    Args:
    routes (list): Lista de dicionários contendo informações sobre as rotas.

    Returns:
        str: Documentação em Markdown das rotas.
    """
    doc = ''
    for route in routes:
        methods = f" ({route['methods']})" if route['methods'] else ''
        doc += f"- `{route['route']}`{methods}\n"
    return doc


def find_app_entry(directory, exclude_files):
    """
    Encontra o arquivo de entrada principal da aplicação Flask, se existir.

    Args:
    directory (str): Diretório raiz para a busca.
    exclude_files (list): Lista de nomes de arquivos a serem excluídos.

    Returns:
        tuple: Nome do arquivo de entrada e número da porta, se encontrado.
    """
    app_file = None
    app_port = None
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name.endswith('.py') and name not in exclude_files:
                file_path = os.path.join(root, name)
                _, _, has_app_run, _ = extract_functions_classes_routes(file_path)[:4]
                if has_app_run:
                    app_file = name
                    # Tenta extrair o número da porta usando regex
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        match = re.search(r'app\.run\(.*port\s*=\s*(\d+)', content)
                        if match:
                            app_port = match.group(1)
                    return app_file, app_port
    return app_file, app_port

def detect_languages(directory, exclude_files):
    """_summary_

    Args:
    directory (str): Diretório raiz para a varredura.
    exclude_files (list): Lista de nomes de arquivos a serem excluídos.

    Returns:
    list: Lista de linguagens de programação detectadas.
    """
    extensions_to_languages = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.html': 'HTML',
        '.css': 'CSS',
        '.java': 'Java',
    }

    languages = set()

    for root, dirs, files in os.walk(directory):
        for name in files:
            if name not in exclude_files:
                _, ext = os.path.splitext(name)
                language = extensions_to_languages.get(ext.lower())
                if language:
                    languages.add(language)

    return list(languages)

def generate_language_badges(languages):
    badges = ''
    for lang in languages:
        lang_encoded = lang.replace(' ', '%20')
        badge = f"![{lang}](https://img.shields.io/badge/Code-{lang_encoded}-blue.svg)"
        badges += badge + ' '
    return badges.strip()

def main():
    """
    Função principal que orquestra a geração do README.md.
    """
    print("Bem-vindo ao Gerador de README.md!")
    
    # Pergunta o idioma do README
    print("\nSelecione o idioma do README:")
    print("1 - Português")
    print("2 - English")
    language_choice = input("Escolha uma opção (1, 2): ").strip()
    
    if language_choice == '2':
        language = 'en'
    else:
        language = 'pt'

    # Pergunta o status do projeto
    print("\nSelecione o status do projeto:")
    print("1 - Em desenvolvimento")
    print("2 - Concluído")
    print("3 - Descontinuado")
    status_choice = input("Escolha uma opção (1, 2, 3): ").strip()
    objetivo = input("Insira o objetivo do projeto: ").strip()
    funcionalidade = input("Insira uma descrição breve da funcionalidade: ").strip()

    # Formata a introdução com as entradas do usuário
    if language == 'en':
        introduction = f"""This project aims to **{objetivo}**.
It was developed to **{funcionalidade}**."""
    else:
        introduction = f"""Este projeto tem como objetivo **{objetivo}**.
Ele foi desenvolvido para **{funcionalidade}**."""

    status_dict = {
        '1': 'Em Desenvolvimento' if language == 'pt' else 'In Development',
        '2': 'Concluído' if language == 'pt' else 'Completed',
        '3': 'Descontinuado' if language == 'pt' else 'Discontinued'
    }

    status = status_dict.get(status_choice, 'Em Desenvolvimento' if language == 'pt' else 'In Development')

    # Prepara o badge com base na escolha
    badge_color_dict = {
        'Em Desenvolvimento': 'yellow',
        'In Development': 'yellow',
        'Concluído': 'brightgreen',
        'Completed': 'brightgreen',
        'Descontinuado': 'red',
        'Discontinued': 'red'
    }

    badge_color = badge_color_dict.get(status, 'yellow')

    status_badge = f"![Status](https://img.shields.io/badge/STATUS-{status.replace(' ', '%20').upper()}-{badge_color}?style=for-the-badge)"

    exclude_files = [os.path.basename(__file__)]
    languages = detect_languages(DIRECTORY, exclude_files)
    language_badges = generate_language_badges(languages)

    all_functions = []
    all_classes = []
    all_routes = []
    is_flask_app = False

    app_file, app_port = find_app_entry(DIRECTORY, exclude_files)

    for root, dirs, files in os.walk(DIRECTORY):
        for name in files:
            if name.endswith('.py') and name not in exclude_files:
                file_path = os.path.join(root, name)
                functions, classes, routes, _, is_flask = extract_functions_classes_routes(file_path)
                all_functions.extend(functions)
                all_classes.extend(classes)
                all_routes.extend(routes)
                if is_flask:
                    is_flask_app = True

    code_structure = generate_code_structure(DIRECTORY, exclude_files)
    functions_doc = generate_functions_doc(all_functions)
    classes_doc = generate_classes_doc(all_classes)

    if is_flask_app and all_routes:
        routes_doc = generate_routes_doc(all_routes)
        toc_routes = '\n* [Rotas da Aplicação](#rotas-da-aplicação)' if language == 'pt' else '\n* [Application Routes](#application-routes)'
        routes_section = f"\n# Rotas da Aplicação\n\nAs rotas da aplicação Flask são definidas para interagir com as diversas funcionalidades do projeto.\n\n{routes_doc}" if language == 'pt' else f"\n# Application Routes\n\nThe Flask application routes are defined to interact with the various functionalities of the project.\n\n{routes_doc}"
        if app_file:
            execution_section = f"Para executar a aplicação Flask, utilize o seguinte comando:\n\n```bash\npython {app_file}\n```\n" if language == 'pt' else f"To run the Flask application, use the following command:\n\n```bash\npython {app_file}\n```\n"
            if app_port:
                execution_section += f"A aplicação será executada por padrão em `http://0.0.0.0:{app_port}`." if language == 'pt' else f"The application will run by default at `http://0.0.0.0:{app_port}`."
            else:
                execution_section += "A aplicação será executada por padrão em `http://0.0.0.0:5000`." if language == 'pt' else "The application will run by default at `http://0.0.0.0:5000`."
        else:
            execution_section = "Para executar a aplicação Flask, utilize o comando apropriado, especificando o arquivo principal." if language == 'pt' else "To run the Flask application, use the appropriate command, specifying the main file."
    else:
        toc_routes = ''
        routes_section = ''
        if app_file:
            execution_section = f"Para executar a aplicação, utilize o seguinte comando:\n\n```bash\npython {app_file}\n```\n" if language == 'pt' else f"To run the application, use the following command:\n\n```bash\npython {app_file}\n```\n"
        else:
            execution_section = "Para executar a aplicação, utilize o comando apropriado, especificando o arquivo principal." if language == 'pt' else "To run the application, use the appropriate command, specifying the main file."

    readme_content = README_TEMPLATE.format(
        status_badge=status_badge,
        language_badges=language_badges,
        introduction=introduction,
        code_structure=code_structure,
        functions_doc=functions_doc,
        classes_doc=classes_doc,
        toc_routes=toc_routes,
        routes_section=routes_section,
        execution_section=execution_section
    )

    with open('README.md', 'w', encoding='utf-8') as readme_file:
        readme_file.write(readme_content)

    print("README.md gerado com sucesso!" if language == 'pt' else "README.md generated successfully!")


if __name__ == '__main__':
    main()
