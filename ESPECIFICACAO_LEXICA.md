# Especificação Léxica — SarnaLang 1.0

## 1. Alfabeto Σ

O arquivo-fonte é codificado em UTF-8. O alfabeto de entrada é o conjunto
finito de valores escalares Unicode:

```text
Σ = { U+0000 … U+D7FF } ∪ { U+E000 … U+10FFFF }
```

Pertencer a Σ não torna um caractere válido em qualquer contexto. As palavras
da linguagem são sequências de Σ reconhecidas pelos padrões abaixo: fora de
strings e comentários, `@`, por exemplo, não inicia nenhum token válido.

- Identificadores: somente `A-Z`, `a-z`, `_` e, após o primeiro caractere, `0-9`.
  São sensíveis a maiúsculas; `nome` e `Nome` são variáveis diferentes.
- Números: somente dígitos ASCII `0-9`; o sinal negativo é um token separado.
- Palavras reservadas: comparação sem distinção entre maiúsculas/minúsculas
  e sem marcas diacríticas da categoria Unicode `Mn` após decomposição NFD.
  `PORTÃOZÃO`, `portaozao` e a grafia com acentos decompostos reconhecem o
  mesmo token. Letras de identificadores e conteúdo de strings não são normalizados.
- Strings: caracteres Unicode imprimíveis, incluindo marcas combinantes,
  exceto aspas e barra invertida, que precisam de escape.
- Espaçamento: espaço ASCII, tabulação, CR e LF.

A visão normalizada usada para palavras reservadas possui mapas para as posições
originais. Lexemas e linhas/colunas referem-se ao texto original; as colunas
contam pontos de código Unicode, iniciando em 1.

## 2. Tabela de tokens

| Categoria/token | Padrão/ER simplificada | Exemplo | Descrição |
|---|---|---|---|
| `START` | literal `E AÍ MARCELO, É O QUÊ?` | `E AÍ MARCELO, É O QUÊ?` | início do programa |
| `END` | literal `SHOW DE BOLA, VALEU!` | `SHOW DE BOLA, VALEU!` | fim do programa |
| `BLOCK_OPEN` | literal `ABRE O PORTÃO` | `ABRE O PORTÃO` | início de bloco |
| `BLOCK_CLOSE` | literal `FECHA O PORTÃO` | `FECHA O PORTÃO` | fim de bloco |
| `TYPE_INT` | literal `PORTÃOZÃO` | `PORTÃOZÃO` | tipo inteiro |
| `TYPE_FLOAT` | literal `CASONA` | `CASONA` | tipo real |
| `TYPE_STRING` | literal `NENEZINHO` | `NENEZINHO` | tipo texto |
| `TYPE_BOOL` | literal `GRAXA VÉIA` | `GRAXA VÉIA` | tipo lógico |
| `PRINT` | literal `E AÍ MARCELO, MOSTRA AÍ` | idem | saída |
| `INPUT` | literal `ME DIZ AÍ` | idem | entrada |
| `IF` | literal `MAS TU É SARNA NÉ?` | idem | decisão |
| `ELSE` | literal `NÃO É SARNA NÃO` | idem | alternativa |
| `WHILE` | literal `DE NOVO MARCELO` | idem | repetição |
| `TRUE` | literal `SHOW` | `SHOW` | verdadeiro |
| `FALSE` | literal `NÃO SHOW` | `NÃO SHOW` | falso |
| `AND` | literal `E MAIS` | `E MAIS` | conjunção lógica |
| `OR` | literal `OU O QUÊ?` | `OU O QUÊ?` | disjunção lógica |
| `NOT` | literal `NEM A PAU` | `NEM A PAU` | negação lógica |
| `IDENT` | `[A-Za-z_][A-Za-z0-9_]*` | `repeticoes` | identificador |
| `INT` | `[0-9]+` | `42` | literal inteiro |
| `FLOAT` | `[0-9]+\.[0-9]+` | `10.5` | literal real |
| `STRING` | `"(C ∪ ESC)*"` (macros abaixo) | `"Show de bola"` | literal de texto |
| `ASSIGN` | `=` | `=` | atribuição |
| `EQ` | `==` | `==` | igualdade |
| `NE` | `!=` | `!=` | diferença |
| `LT` | `<` | `<` | menor |
| `LE` | `<=` | `<=` | menor ou igual |
| `GT` | `>` | `>` | maior |
| `GE` | `>=` | `>=` | maior ou igual |
| `PLUS` | `\+` | `+` | soma |
| `MINUS` | `-` | `-` | subtração/negativo |
| `STAR` | `\*` | `*` | multiplicação |
| `SLASH` | `/` | `/` | divisão |
| `LPAREN` | `\(` | `(` | abre parênteses |
| `RPAREN` | `\)` | `)` | fecha parênteses |
| `COMMA` | `,` | `,` | separação |
| `SEMICOLON` | `;` | `;` | fim de comando |
| `EOF` | fim da entrada, sem lexema | — | sentinela interna do parser |

### Macros para o literal de texto

`C` é a classe dos caracteres para os quais `str.isprintable()` é verdadeiro,
excluindo `"` e `\`. `ESC` é uma barra invertida seguida por um dos quatro
caracteres `n`, `t`, `"` ou `\`. A ER é a concatenação de aspas, zero ou mais
ocorrências de `C ∪ ESC`, e aspas de fechamento.

| Escape no fonte | Valor |
|---|---|
| `\n` | quebra de linha |
| `\t` | tabulação |
| `\"` | aspas duplas |
| `\\` | barra invertida |

Escapes desconhecidos, caracteres de controle literais e strings não encerradas
produzem erro léxico. Quebras de linha CR/LF dentro de uma string precisam ser
representadas pelo escape `\n`. O token preserva o lexema com aspas e escapes;
seu campo `literal` contém o valor interpretado.

## 3. Espaços e quebras de linha

Fora de strings, espaços, tabs e quebras de linha separam lexemas, mas não
geram tokens.

Nas palavras reservadas compostas, cada espaço do padrão representa a ER
`[ \t\r\n]+`. A pontuação da frase é obrigatória. CR, LF e CRLF contam como
uma quebra de linha cada.

## 4. Comentários

Duas formas são reconhecidas:

```text
// comentário convencional
BAH: comentário temático
```

Os padrões são `//[^\r\n]*` e `(?i:BAH:)[^\r\n]*`. Ambos seguem até
CR, LF ou fim do arquivo e são descartados. O conteúdo pode usar qualquer
caractere de Σ, exceto o terminador de linha.

## 5. Longest match

Operadores de dois caracteres são testados antes dos de um caractere:

```text
== != <= >=
```

antes de:

```text
= < >
```

Frases reservadas mais longas são testadas antes das mais curtas: por exemplo,
`SHOW DE BOLA, VALEU!` antes de `SHOW`. O fim de uma palavra reservada não pode
ser seguido de letra, dígito ou `_`, evitando dividir `SHOWzinho`. Números reais
são reconhecidos antes de inteiros. Identificadores, números e operadores são
reconhecidos diretamente no texto original.

## 6. Erro léxico

Qualquer caractere que não iniciar um token válido produz erro contendo:

- categoria do erro;
- linha;
- coluna;
- caractere/lexema inválido.

Exemplo:

```text
[ERRO LÉXICO] linha 4, coluna 7: caractere/lexema inválido '@'.
```
