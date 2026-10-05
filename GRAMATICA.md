# Gramática Livre de Contexto — SarnaLang 1.0

## Definição formal G = (V, T, P, S)

### V — não terminais

```text
V = {
  Programa, ListaComandos, Comando, Declaracao, Tipo, Atribuicao,
  Entrada, Saida, ListaSaida, Condicional, Repeticao,
  Bloco, Expressao, ExprOu, ExprE, Igualdade, Comparacao,
  ExpressaoArit, Termo, Unario, Primario
}
```

### T — terminais

```text
T = {
  START, END, BLOCK_OPEN, BLOCK_CLOSE,
  TYPE_INT, TYPE_FLOAT, TYPE_STRING, TYPE_BOOL,
  PRINT, INPUT, IF, ELSE, WHILE,
  TRUE, FALSE, AND, OR, NOT,
  id, int_lit, float_lit, string_lit,
  +, -, *, /, =, ==, !=, <, <=, >, >=,
  (, ), ,, ;
}
```

### S — símbolo inicial

```text
S = Programa
```

Os terminais `id`, `int_lit`, `float_lit` e `string_lit` correspondem aos
tokens `IDENT`, `INT`, `FLOAT` e `STRING` da tabela léxica. `EOF` é uma sentinela
do parser: depois de `END`, nenhum outro token de programa é permitido.

## Produções P em EBNF

```ebnf
Programa ::=
    START ListaComandos END ;

ListaComandos ::=
    { Comando } ;

Comando ::=
      Declaracao
    | Atribuicao
    | Entrada
    | Saida
    | Condicional
    | Repeticao ;

Tipo ::=
      TYPE_INT
    | TYPE_FLOAT
    | TYPE_STRING
    | TYPE_BOOL ;

Declaracao ::=
    Tipo id [ "=" Expressao ] ";" ;

Atribuicao ::=
    id "=" Expressao ";" ;

Entrada ::=
    INPUT "(" id ")" ";" ;

Saida ::=
    PRINT "(" [ ListaSaida ] ")" ";" ;

ListaSaida ::=
    Expressao { "," Expressao } ;

Condicional ::=
    IF "(" Expressao ")" Bloco
    [ ELSE Bloco ] ;

Repeticao ::=
    WHILE "(" Expressao ")" Bloco ;

Bloco ::=
    BLOCK_OPEN ListaComandos BLOCK_CLOSE ;

Expressao ::=
    ExprOu ;

ExprOu ::=
    ExprE { OR ExprE } ;

ExprE ::=
    Igualdade { AND Igualdade } ;

Igualdade ::=
    Comparacao { ( "==" | "!=" ) Comparacao } ;

Comparacao ::=
    ExpressaoArit
    { ( "<" | "<=" | ">" | ">=" ) ExpressaoArit } ;

ExpressaoArit ::=
    Termo { ( "+" | "-" ) Termo } ;

Termo ::=
    Unario { ( "*" | "/" ) Unario } ;

Unario ::=
      ( "-" | NOT ) Unario
    | Primario ;

Primario ::=
      id
    | int_lit
    | float_lit
    | string_lit
    | TRUE
    | FALSE
    | "(" Expressao ")" ;
```

## Precedência

Da maior para a menor:

1. agrupamento `( )`;
2. operadores unários `-` e `NEM A PAU`;
3. multiplicação e divisão `* /`;
4. soma e subtração `+ -`;
5. relações `< <= > >=`;
6. igualdade `== !=`;
7. `E MAIS`;
8. `OU O QUÊ?`.

Logo:

```text
2 + 3 * 4
```

é representado como:

```text
2 + (3 * 4)
```

na AST, e não corrigido posteriormente pelo gerador.

## Ausência de recursão à esquerda

As produções foram fatoradas em níveis de precedência e utilizam repetição
EBNF, permitindo implementação por parser preditivo de descida recursiva.

## Correspondência entre produções e parser

| Produção | Método em `sarnalang/parser.py` |
|---|---|
| Programa | `parse` |
| ListaComandos | laços em `parse` e `_block` |
| Comando | `_statement` |
| Tipo | `TYPE_MAP` e `_var_decl` |
| Declaracao / Atribuicao | `_var_decl` / `_assignment` |
| Entrada / Saida / ListaSaida | `_input_stmt` / `_print_stmt` |
| Condicional / Repeticao / Bloco | `_if_stmt` / `_while_stmt` / `_block` |
| Expressao / ExprOu / ExprE | `_expression` / `_or` / `_and` |
| Igualdade / Comparacao | `_equality` / `_comparison` |
| ExpressaoArit / Termo | `_term` / `_factor` |
| Unario / Primario | `_unary` / `_primary` |

As repetições de operadores binários constroem nós associados à esquerda:
`8 - 3 - 1` significa `(8 - 3) - 1`. A GLC aceita comparações encadeadas,
mas a semântica rejeita `1 < 2 < 3`, pois o resultado de `1 < 2` é lógico
e não pode ser operando numérico do segundo `<`.
