# Checklist de Conformidade com o Trabalho Prático 1

## Escopo mínimo

- [x] pelo menos dois tipos primitivos
- [x] tipo numérico
- [x] declaração de variáveis
- [x] atribuição
- [x] `+ - * /`
- [x] precedência
- [x] parênteses
- [x] operadores relacionais
- [x] if/else
- [x] repetição por expressão lógica
- [x] entrada
- [x] saída
- [x] delimitação clara do programa
- [x] delimitação clara de blocos

## Léxico

- [x] alfabeto Σ
- [x] tabela de tokens
- [x] ER/padrões
- [x] palavras reservadas
- [x] identificadores
- [x] números
- [x] strings
- [x] operadores
- [x] delimitadores
- [x] whitespace
- [x] comentários formalizados
- [x] longest match
- [x] erro léxico com linha

## Sintaxe

- [x] G = (V,T,P,S)
- [x] EBNF
- [x] todas as estruturas mínimas
- [x] precedência
- [x] agrupamento
- [x] sem recursão à esquerda
- [x] parser por descida recursiva
- [x] erros sintáticos com linha/token/esperado
- [x] AST

## Semântica

- [x] fase separada
- [x] tabela de símbolos
- [x] nome e tipo
- [x] uso antes da declaração
- [x] redeclaração no mesmo escopo
- [x] compatibilidade de tipos
- [x] erro semântico claro

## Geração

- [x] linguagem destino C
- [x] geração após validações
- [x] tipos mapeados
- [x] expressões
- [x] condicional
- [x] repetição
- [x] entrada
- [x] saída
- [x] geração a partir da AST
- [x] sem substituição textual simples

## Testes

- [x] 01_valido_basico
- [x] 02_valido_completo
- [x] 03_erro_lexico
- [x] 04_erro_sintatico
- [x] 05_erro_semantico
- [x] expressão `2 + 3 * 4`
- [x] casos adicionais de redeclaração, tipo, escopos e identificador inválido
- [x] compilação e execução automática do C com saída esperada
- [x] regressões de Unicode, precedência e preservação de escopos
- [x] exemplos e snippets da extensão compatíveis com o transpilador

## Entregáveis

- [x] relatório técnico
- [x] código-fonte completo
- [x] suíte de testes
- [x] código C gerado
- [x] README
- [x] declaração breve de uso de IA no relatório

## Preparação presencial — depende do grupo

- [ ] revisar e confirmar autoria e declaração de uso de IA
- [ ] ensaiar a demonstração no computador que será utilizado
- [ ] conferir visualmente a extensão pelo roteiro `F5`
- [ ] garantir que todos expliquem tokens, produções, AST, semântica e C
- [ ] distribuir a apresentação e praticar perguntas individuais
