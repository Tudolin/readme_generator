# Gerador de Documentação Automática Python

Este projeto inclui um script Python chamado `generator.py` que automatiza a criação do arquivo `README.md`. A seguir, apresentamos uma descrição detalhada da funcionalidade e como utilizá-lo.

# OBS: Para que o script funcione seus arquivos .py devem estar documentados utilizando docstrings. Recomendamos a utilização da extensão do VSCODE [autoDocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring).

Exemplo:
```
    """
    Sumary: 
        breve explicação de funcionamento.

    Args:
        arqumento_passado_na_execução (str): descrição do argumento.

    Returns:
        tipo_de_dado: Descrição do retorno.
    """
```

## Funcionalidade

O `generator.py` realiza as seguintes tarefas:

1. **Análise de Arquivos Python:**
   - Percorre todos os arquivos `.py` no diretório especificado.
   - Exclui automaticamente o próprio script da documentação para evitar redundâncias.

2. **Extração de Informações:**
   - **Funções:** Identifica e documenta todas as funções presentes nos arquivos analisados, incluindo suas docstrings.
   - **Classes e Métodos:** Identifica classes e seus métodos, documentando também as respectivas docstrings.
   - **Rotas Flask:** Se a aplicação utiliza o framework Flask, o script detecta as rotas definidas e as documenta, incluindo os métodos HTTP associados.

3. **Geração da Estrutura do Código:**
   - Cria uma representação hierárquica dos diretórios e arquivos Python presentes no projeto.

4. **Interação com o Usuário:**
   - Solicita ao usuário informações básicas sobre o projeto, como o objetivo e uma descrição breve da funcionalidade, que são inseridas na seção de introdução do `README.md`.

5. **Geração do `README.md`:**
   - Compila todas as informações extraídas e formatadas em um arquivo `README.md` estruturado, contendo seções como Introdução, Instalação de Dependências, Estrutura do Código, Funções e Classes, Rotas da Aplicação (se aplicável) e Execução da Aplicação.

## Como Utilizar

1. **Preparação:**
   - Certifique-se de que o script `generator.py` está localizado na raiz do seu projeto Python ou ajuste a variável `DIRECTORY` dentro do script para apontar para o diretório correto.

2. **Execução:**
   - Abra o terminal e navegue até o diretório onde o script está localizado.
   - Execute o script com o seguinte comando:
     ```bash
     python generator.py
     ```

3. **Inserção de Informações:**
   - Durante a execução, o script solicitará que você insira o objetivo do projeto e uma descrição breve da funcionalidade. Forneça as informações conforme solicitado.

4. **Resultado:**
   - Após a conclusão, um arquivo `README.md` será gerado na raiz do seu projeto com toda a documentação estruturada automaticamente.

## Benefícios

- **Economia de Tempo:** Automatiza o processo de documentação, evitando a necessidade de escrever manualmente o `README.md`.
- **Consistência:** Garante que todas as funções, classes e rotas estejam devidamente documentadas de forma consistente.
- **Atualização Fácil:** Facilita a atualização da documentação conforme o projeto evolui, bastando executar o script novamente.

## Considerações Finais

O `generator.py` é uma ferramenta poderosa para desenvolvedores que desejam manter a documentação de seus projetos Python sempre atualizada de forma rápida e eficiente. Ao automatizar a geração do `README.md`, ele contribui para a manutenção de projetos bem documentados, facilitando a compreensão e colaboração.

---

Caso tenha dúvidas ou precise de assistência adicional para configurar ou utilizar o script, sinta-se à vontade para entrar em contato ou abrir uma issue no repositório.

