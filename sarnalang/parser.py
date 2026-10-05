from __future__ import annotations
from .lexer import Token
from .ast_nodes import *


class ParserError(Exception):
    pass


TYPE_MAP = {
    "TYPE_INT": "int",
    "TYPE_FLOAT": "float",
    "TYPE_STRING": "string",
    "TYPE_BOOL": "bool",
}


class Parser:
    """Parser preditivo manual por descida recursiva."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Program:
        start = self._consume(
            "START",
            "esperado início do programa: 'E AÍ MARCELO, É O QUÊ?'"
        )

        statements = []
        while not self._check("END") and not self._at_end():
            statements.append(self._statement())

        self._consume(
            "END",
            "esperado fim do programa: 'SHOW DE BOLA, VALEU!'"
        )
        self._consume("EOF", "esperado fim do arquivo")

        return Program(statements, start.line)

    def _statement(self):
        if self._match(*TYPE_MAP.keys()):
            return self._var_decl(self._previous())

        if self._match("PRINT"):
            return self._print_stmt(self._previous())

        if self._match("INPUT"):
            return self._input_stmt(self._previous())

        if self._match("IF"):
            return self._if_stmt(self._previous())

        if self._match("WHILE"):
            return self._while_stmt(self._previous())

        if self._check("IDENT") and self._check_next("ASSIGN"):
            return self._assignment()

        raise self._error(
            self._peek(),
            "esperada declaração, atribuição, entrada, saída, "
            "condicional ou repetição"
        )

    def _var_decl(self, type_token: Token):
        type_name = TYPE_MAP[type_token.type]
        name = self._consume(
            "IDENT",
            "esperado identificador após o tipo"
        )

        initializer = None
        if self._match("ASSIGN"):
            if self._check("SEMICOLON"):
                raise self._error(
                    self._peek(),
                    "esperada expressão após '='"
                )
            initializer = self._expression()

        self._consume(
            "SEMICOLON",
            "esperado ';' ao final da declaração"
        )

        return VarDecl(
            type_name, name.lexeme, initializer, type_token.line
        )

    def _assignment(self):
        name = self._consume("IDENT", "esperado identificador")
        self._consume("ASSIGN", "esperado '=' na atribuição")

        if self._check("SEMICOLON"):
            raise self._error(
                self._peek(),
                "esperada expressão após '='"
            )

        value = self._expression()
        self._consume(
            "SEMICOLON",
            "esperado ';' ao final da atribuição"
        )
        return Assign(name.lexeme, value, name.line)

    def _print_stmt(self, token: Token):
        self._consume(
            "LPAREN",
            "esperado '(' após 'E AÍ MARCELO, MOSTRA AÍ'"
        )

        values = []
        if not self._check("RPAREN"):
            values.append(self._expression())
            while self._match("COMMA"):
                values.append(self._expression())

        self._consume("RPAREN", "esperado ')' no comando de saída")
        self._consume(
            "SEMICOLON",
            "esperado ';' ao final do comando de saída"
        )
        return PrintStmt(values, token.line)

    def _input_stmt(self, token: Token):
        self._consume(
            "LPAREN",
            "esperado '(' após 'ME DIZ AÍ'"
        )
        name = self._consume(
            "IDENT",
            "esperado identificador no comando de entrada"
        )
        self._consume("RPAREN", "esperado ')' no comando de entrada")
        self._consume(
            "SEMICOLON",
            "esperado ';' ao final do comando de entrada"
        )
        return InputStmt(name.lexeme, token.line)

    def _if_stmt(self, token: Token):
        self._consume(
            "LPAREN",
            "esperado '(' após 'MAS TU É SARNA NÉ?'"
        )
        condition = self._expression()
        self._consume("RPAREN", "esperado ')' após condição")

        then_branch = self._block()
        else_branch = None

        if self._match("ELSE"):
            else_branch = self._block()

        return IfStmt(
            condition, then_branch, else_branch, token.line
        )

    def _while_stmt(self, token: Token):
        self._consume(
            "LPAREN",
            "esperado '(' após 'DE NOVO MARCELO'"
        )
        condition = self._expression()
        self._consume("RPAREN", "esperado ')' após condição")
        body = self._block()

        return WhileStmt(condition, body, token.line)

    def _block(self):
        opener = self._consume(
            "BLOCK_OPEN",
            "esperado 'ABRE O PORTÃO' para iniciar bloco"
        )

        statements = []
        while not self._check("BLOCK_CLOSE") and not self._at_end():
            if self._check("END"):
                raise self._error(
                    self._peek(),
                    "esperado 'FECHA O PORTÃO' antes do fim do programa"
                )
            statements.append(self._statement())

        self._consume(
            "BLOCK_CLOSE",
            "esperado 'FECHA O PORTÃO' para terminar bloco"
        )
        return Block(statements, opener.line)

    # -------------------------
    # Expressões sem recursão à esquerda
    # -------------------------

    def _expression(self):
        return self._or()

    def _or(self):
        expr = self._and()
        while self._match("OR"):
            op = self._previous()
            expr = Binary(expr, op.type, self._and(), op.line)
        return expr

    def _and(self):
        expr = self._equality()
        while self._match("AND"):
            op = self._previous()
            expr = Binary(expr, op.type, self._equality(), op.line)
        return expr

    def _equality(self):
        expr = self._comparison()
        while self._match("EQ", "NE"):
            op = self._previous()
            expr = Binary(expr, op.type, self._comparison(), op.line)
        return expr

    def _comparison(self):
        expr = self._term()
        while self._match("LT", "LE", "GT", "GE"):
            op = self._previous()
            expr = Binary(expr, op.type, self._term(), op.line)
        return expr

    def _term(self):
        expr = self._factor()
        while self._match("PLUS", "MINUS"):
            op = self._previous()
            expr = Binary(expr, op.type, self._factor(), op.line)
        return expr

    def _factor(self):
        expr = self._unary()
        while self._match("STAR", "SLASH"):
            op = self._previous()
            expr = Binary(expr, op.type, self._unary(), op.line)
        return expr

    def _unary(self):
        if self._match("MINUS", "NOT"):
            op = self._previous()
            return Unary(op.type, self._unary(), op.line)
        return self._primary()

    def _primary(self):
        if self._match("INT"):
            t = self._previous()
            return Literal(t.literal, "int", t.line)

        if self._match("FLOAT"):
            t = self._previous()
            return Literal(t.literal, "float", t.line)

        if self._match("STRING"):
            t = self._previous()
            return Literal(t.literal, "string", t.line)

        if self._match("TRUE"):
            t = self._previous()
            return Literal(True, "bool", t.line)

        if self._match("FALSE"):
            t = self._previous()
            return Literal(False, "bool", t.line)

        if self._match("IDENT"):
            t = self._previous()
            return Variable(t.lexeme, t.line)

        if self._match("LPAREN"):
            expr = self._expression()
            self._consume(
                "RPAREN",
                "esperado ')' após expressão agrupada"
            )
            return expr

        raise self._error(
            self._peek(),
            "esperado identificador, número, texto, booleano "
            "ou expressão entre parênteses"
        )

    # -------------------------
    # Utilidades
    # -------------------------

    def _match(self, *types):
        for typ in types:
            if self._check(typ):
                self._advance()
                return True
        return False

    def _consume(self, typ, message):
        if self._check(typ):
            return self._advance()
        raise self._error(self._peek(), message)

    def _check(self, typ):
        if self._at_end():
            return typ == "EOF"
        return self._peek().type == typ

    def _check_next(self, typ):
        if self.current + 1 >= len(self.tokens):
            return False
        return self.tokens[self.current + 1].type == typ

    def _advance(self):
        if not self._at_end():
            self.current += 1
        return self._previous()

    def _peek(self):
        return self.tokens[self.current]

    def _previous(self):
        return self.tokens[self.current - 1]

    def _at_end(self):
        return self._peek().type == "EOF"

    def _error(self, token: Token, expected: str):
        found = (
            "fim do arquivo"
            if token.type == "EOF"
            else f"{token.type} {token.lexeme!r}"
        )
        return ParserError(
            f"[ERRO SINTÁTICO] linha {token.line}, coluna {token.column}: "
            f"{expected}; encontrado {found}."
        )
