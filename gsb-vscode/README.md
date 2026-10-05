# SarnaLang Language Support para VS Code

Extensão para **SarnaLang 1.0**, a mesma linguagem implementada pelo
transpilador deste projeto. Reconhece arquivos `.sarna`.

## Recursos

- Realce das palavras reservadas, tipos, textos, números e comentários `//`/`BAH:`.
- Snippets para programa, declarações, entrada/saída, `if/else`, `while` e lógica.
- Sugestões de variáveis declaradas antes da linha do cursor. Essa lista é uma
  conveniência de edição; a validação de visibilidade é feita pela semântica.
- Diagnóstico do primeiro erro léxico, sintático ou semântico no painel **Problems**.
- Validação de alterações não salvas, com espera de 250 ms após a última edição.
- Hover dos tipos primitivos.

Exemplo aceito pela extensão e pelo transpilador:

```text
E AÍ MARCELO, É O QUÊ?

PORTÃOZÃO repeticoes = 3;
DE NOVO MARCELO (repeticoes > 0)
ABRE O PORTÃO
    E AÍ MARCELO, MOSTRA AÍ("Repetição:", repeticoes);
    repeticoes = repeticoes - 1;
FECHA O PORTÃO

SHOW DE BOLA, VALEU!
```

Palavras reservadas aceitam acentos, versões sem acento e variações de caixa.
Identificadores usam somente `[A-Za-z_][A-Za-z0-9_]*`. Os blocos usam
`ABRE O PORTÃO` e `FECHA O PORTÃO`. A linguagem não possui `for`, funções,
`break` ou `continue` nesta versão.

## Pré-requisitos e configurações

- VS Code 1.85 ou posterior.
- Python 3.10 ou posterior, sem dependências externas.
- Workspace confiável, pois a validação executa um processo Python local.

Em Settings, procure **SarnaLang**:

| Configuração | Uso |
|---|---|
| `sarna.pythonPath` | Executável Python; padrão `python3`. No Windows, configure `python` ou o caminho completo de `python.exe`. |
| `sarna.compilerDirectory` | Opcional: pasta que contém `sarnalang/`. Caminhos relativos são resolvidos a partir do workspace. |

No desenvolvimento, a extensão encontra o transpilador na pasta pai. O VSIX
inclui uma cópia do mesmo analisador, preparada automaticamente no empacotamento.
Python continua sendo necessário no computador em que a extensão for instalada.
Se Python estiver ausente ou mal configurado, Problems mostra um aviso de
configuração, separado dos erros da linguagem.

## Testar no VS Code

1. Abra a pasta `gsb-vscode` no VS Code e pressione `F5`.
2. Na janela **Extension Development Host**, abra `examples/exemplo.sarna`.
3. Confira que não há erros; introduza `@` para observar um erro léxico.
4. Remova `@`, deixe uma declaração com `= ;` e observe o erro sintático.
5. Restaure a declaração e atribua a uma variável inexistente para testar a semântica.
6. Digite `programa`, `ifelse`, `while`, `mostra`, `mediz` ou `portaozao` para snippets.

O comando **SarnaLang: Validar arquivo atual** solicita nova validação.
Para compilar e executar o programa, use os comandos do [README do projeto](../README.md).

## Testes automatizados

A partir da raiz do projeto, com Node.js e Python instalados:

```bash
node gsb-vscode/scripts/prepare-server.js
npm run lint --prefix gsb-vscode
npm test --prefix gsb-vscode
```

Os testes verificam exemplos reais, os três tipos de erro, o backend incluído
no pacote em uma pasta independente, realce e a atualização dos diagnósticos
por eventos de edição. A API visual do VS Code é simulada nesse último teste;
o roteiro com `F5` serve para conferir a interface real.

## Empacotar como VSIX

A partir desta pasta:

```bash
npm run package
```

O comando usa `@vscode/vsce` via `npx`; no primeiro uso, pode precisar baixá-lo.
O hook `vscode:prepublish` copia os arquivos `.py` de `../sarnalang` para
`server/sarnalang`. Essa pasta é gerada: edite o analisador na raiz e prepare
novamente o pacote. Instale o VSIX pelo menu **Extensions → … → Install from VSIX…**.

## Arquitetura

```text
Documento .sarna, salvo ou não
  → processo Python: python3 -m sarnalang.editor
  → Lexer → Parser → AST → SemanticAnalyzer
  → JSON com diagnóstico e declarações
  → DiagnosticCollection / autocomplete
```

A validação não cria arquivos C. A extensão cancela processos de análises
substituídas e descarta respostas de versões antigas do documento. Não há um
segundo conjunto de regras semânticas em JavaScript nem necessidade de um
Language Server nesta versão.
