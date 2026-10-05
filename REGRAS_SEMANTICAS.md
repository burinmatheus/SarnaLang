# Regras Semânticas — SarnaLang 1.0

A análise semântica é executada somente depois de o parser produzir uma AST
válida.

## Tabela de símbolos

Cada entrada registra:

- nome;
- tipo;
- linha de declaração;
- nome C único por declaração (`sl_<número>_<nome>`).

Existe uma pilha de escopos. Blocos de `if`, `else` e `while` criam escopos
internos.

## Regras

1. Uma variável deve ser declarada antes de ser usada.
2. Uma variável não pode ser redeclarada no mesmo escopo.
3. Shadowing em bloco interno é permitido. O novo símbolo só entra no escopo
   após a análise de seu inicializador, que ainda pode consultar um homônimo externo.
4. Uma atribuição deve respeitar os tipos.
5. `int -> float` é a única promoção implícita permitida.
6. Operações `+ - * /` aceitam apenas `int` e `float`.
7. Se uma operação numérica tiver um operando `float`, seu resultado é `float`.
8. `< <= > >=` aceitam somente operandos numéricos e retornam `bool`.
9. `== !=` aceitam tipos iguais ou a comparação mista `int/float`.
10. `E MAIS` e `OU O QUÊ?` exigem dois operandos `bool`.
11. `NEM A PAU` exige operando `bool`.
12. A condição de `MAS TU É SARNA NÉ?` deve ser `bool`.
13. A condição de `DE NOVO MARCELO` deve ser `bool`.
14. Entrada só pode referenciar variável já declarada.
15. Saída pode receber expressões de qualquer tipo primitivo.

## Exemplos inválidos

Uso antes da declaração:

```text
x = 10;
PORTÃOZÃO x;
```

Redeclaração:

```text
PORTÃOZÃO x;
CASONA x;
```

Tipos incompatíveis:

```text
PORTÃOZÃO x = 10;
NENEZINHO texto = "sarna";
x = texto;
```

## Preservação de escopos no C

O analisador associa declarações, leituras, atribuições e referências na AST
ao objeto `Symbol` encontrado na pilha de escopos. O gerador consulta essas
associações mesmo depois de os escopos internos terem sido desempilhados.

```text
PORTÃOZÃO x = 5;
MAS TU É SARNA NÉ? (SHOW)
ABRE O PORTÃO
    PORTÃOZÃO x = x + 1;
    E AÍ MARCELO, MOSTRA AÍ(x);
FECHA O PORTÃO
E AÍ MARCELO, MOSTRA AÍ(x);
```

O trecho imprime `6` e depois `5`. As declarações viram `sl_1_x` e `sl_2_x`;
o inicializador interno usa `sl_1_x + 1`. Sem uma declaração externa,
`PORTÃOZÃO x = x + 1;` é rejeitado por uso antes da declaração.

## Valores, texto e entrada/saída

- Declarações sem inicializador recebem `0`, `0.0`, texto vazio ou falso.
- A divisão entre inteiros é inteira, com truncamento em direção a zero;
  com pelo menos um operando real, é divisão real: `5 / 2` é `2`,
  enquanto `5 / 2.0` é `2.5`.
- `E MAIS` e `OU O QUÊ?` usam curto-circuito, como `&&` e `||` em C.
- Igualdade de textos compara o conteúdo por `strcmp`.
- Variáveis de texto armazenam até 255 bytes, mais o terminador. Cópias
  maiores são truncadas nesse limite; a contagem é em bytes UTF-8.
- A entrada usa `scanf`: inteiro, real, uma palavra de texto sem espaços
  (até 255 bytes), ou `0`/`1` para lógico. Os exemplos pressupõem entrada
  no formato do tipo solicitado.
- A saída insere um espaço entre expressões e uma quebra de linha ao final.
  Lógicos são impressos como `SHOW` e `NAO SHOW`; saída vazia imprime uma linha.
