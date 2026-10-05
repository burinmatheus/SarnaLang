# Resultados e execução da suíte

| Caso | Resultado esperado |
|---|---|
| `01_valido_basico.sarna` | aceito; gera C |
| `02_valido_completo.sarna` | aceito; gera C; `2 + 3 * 4` resulta em `14` |
| `03_erro_lexico.sarna` | rejeitado por `@` |
| `04_erro_sintatico.sarna` | rejeitado por ausência de expressão após `=` |
| `05_erro_semantico.sarna` | rejeitado por uso de `y` sem declaração |
| `06_erro_redeclaracao.sarna` | rejeitado por redeclaração de `x` |
| `07_erro_tipo.sarna` | rejeitado por atribuição de `string` a `int` |
| `08_valido_escopos.sarna` | aceito; preserva variáveis externas nos inicializadores e em blocos aninhados |
| `09_erro_identificador.sarna` | rejeitado: `café` viola identificadores ASCII |

## Verificação automatizada

```bash
python3 run_tests.py
node gsb-vscode/scripts/prepare-server.js
npm run lint --prefix gsb-vscode
npm test --prefix gsb-vscode
```

Na revisão, passaram **14 testes Python** (com vários subcasos) e **5 testes
Node.js**. A suíte Python exige GCC/Clang, compila C11 com avisos tratados como
erros (exceto variáveis não utilizadas) e compara saídas. Também verifica:

- rejeição por categoria e diagnóstico exibido pelo próprio transpilador;
- ausência de arquivo C quando a CLI rejeita o programa;
- AST de expressões com e sem parênteses;
- sombreamento numérico, textual e lógico, atribuição e entrada em escopo interno;
- Unicode NFC/NFD, preservação de strings e posições após caracteres Unicode;
- precedência lógica, ramo `else`, divisão inteira/real e formatos de entrada;
- exemplos e expansões padrão dos snippets da extensão;
- correspondência dos arquivos C entregues com os fontes de teste válidos.

Os testes Node.js executam a ponte Python real, inclusive com o backend copiado
para um caminho com espaços. O teste dos eventos do editor simula a API do
VS Code; a inspeção visual real deve seguir o roteiro com `F5` no README da extensão.

`python3 run_tests.py --skip-c` executa uma verificação parcial e marca os testes
de execução C como ignorados. Não equivale à validação completa.

## Saída do caso básico

```text
Portão: 15
Casona: 2.5
```

## Saída do caso completo

Usando `Marcelo` como entrada:

```text
Qual teu nome?
Repetição: 3
Repetição: 2
Repetição: 1
Show de bola, Marcelo
2 + 3 * 4 = 14
```

## Saída do caso de escopos

Usando `9` como entrada:

```text
6 externo
9
SHOW
5 externo
```

A primeira linha usa os valores externos nos inicializadores locais. A entrada
altera somente o inteiro interno. A última linha confirma que as variáveis
externas mantiveram seus valores.
