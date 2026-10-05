from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


@dataclass(frozen=True)
class Token:
    type: str
    lexeme: str
    literal: object
    line: int
    column: int


class LexerError(Exception):
    pass


def normalize(text: str) -> str:
    """Remove acentos para comparação das palavras reservadas."""
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(
        ch for ch in decomposed
        if unicodedata.category(ch) != "Mn"
    )


def phrase_pattern(text: str) -> str:
    normalized = normalize(text)
    escaped = re.escape(normalized)
    return escaped.replace(r"\ ", r"[ \t\r\n]+")


class Lexer:
    """
    Analisador léxico da SarnaLang.

    Estratégia:
    1. ignora espaços/quebras/comentários;
    2. reconhece string;
    3. reconhece palavras reservadas compostas;
    4. reconhece operadores pelo maior casamento;
    5. reconhece números e identificadores;
    6. qualquer outro caractere produz erro léxico.

    A normalização permite escrever keywords com ou sem acento.
    """

    PHRASES = [
        # Delimitação
        ("START", "E AÍ MARCELO, É O QUÊ?"),
        ("END", "SHOW DE BOLA, VALEU!"),
        ("BLOCK_OPEN", "ABRE O PORTÃO"),
        ("BLOCK_CLOSE", "FECHA O PORTÃO"),

        # Tipos
        ("TYPE_INT", "PORTÃOZÃO"),
        ("TYPE_FLOAT", "CASONA"),
        ("TYPE_STRING", "NENEZINHO"),
        ("TYPE_BOOL", "GRAXA VÉIA"),

        # Comandos
        ("PRINT", "E AÍ MARCELO, MOSTRA AÍ"),
        ("INPUT", "ME DIZ AÍ"),
        ("IF", "MAS TU É SARNA NÉ?"),
        ("ELSE", "NÃO É SARNA NÃO"),
        ("WHILE", "DE NOVO MARCELO"),

        # Booleanos e operadores lógicos
        ("TRUE", "SHOW"),
        ("FALSE", "NÃO SHOW"),
        ("AND", "E MAIS"),
        ("OR", "OU O QUÊ?"),
        ("NOT", "NEM A PAU"),
    ]

    # Ordem é importante para longest match.
    SIMPLE = [
        ("EQ", r"=="),
        ("NE", r"!="),
        ("LE", r"<="),
        ("GE", r">="),
        ("ASSIGN", r"="),
        ("LT", r"<"),
        ("GT", r">"),
        ("PLUS", r"\+"),
        ("MINUS", r"-"),
        ("STAR", r"\*"),
        ("SLASH", r"/"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("COMMA", r","),
        ("SEMICOLON", r";"),
    ]

    def __init__(self, source: str):
        self.source = source
        # Só keywords consultam esta visão. Os dois mapas preservam posições
        # do texto original mesmo quando NFD remove marcas combinantes.
        folded = []
        self.keyword_offsets = []
        self.source_ends = [0]
        for index, ch in enumerate(source):
            self.keyword_offsets.append(len(folded))
            normalized = normalize(ch)
            if normalized:
                folded.extend(normalized)
                self.source_ends.extend([index + 1] * len(normalized))
            else:
                self.source_ends[-1] = index + 1
        self.keyword_offsets.append(len(folded))
        self.normalized = "".join(folded)
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

        # Frases mais longas têm prioridade.
        phrases = sorted(self.PHRASES, key=lambda p: len(p[1]), reverse=True)
        self.phrase_patterns = [
            (typ, re.compile(phrase_pattern(phrase), re.IGNORECASE | re.ASCII))
            for typ, phrase in phrases
        ]
        self.simple_patterns = [
            (typ, re.compile(pattern))
            for typ, pattern in self.SIMPLE
        ]

        self.float_re = re.compile(r"[0-9]+\.[0-9]+")
        self.int_re = re.compile(r"[0-9]+")
        self.ident_re = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

    def tokenize(self) -> list[Token]:
        while not self._at_end():
            if self._skip_ignored():
                continue

            line, col = self.line, self.column

            if self._peek() == '"':
                self.tokens.append(self._string())
                continue

            matched = False

            # Keywords compostas
            for typ, pattern in self.phrase_patterns:
                if unicodedata.category(self._peek()) == "Mn":
                    break
                m = pattern.match(self.normalized, self.keyword_offsets[self.pos])
                end = self.source_ends[m.end()] if m else self.pos
                if m and self._keyword_boundary(end):
                    length = end - self.pos
                    lexeme = self.source[self.pos:self.pos + length]
                    self.tokens.append(Token(typ, lexeme, None, line, col))
                    self._advance_count(length)
                    matched = True
                    break
            if matched:
                continue

            # Operadores/delimitadores - longest match
            for typ, pattern in self.simple_patterns:
                m = pattern.match(self.source, self.pos)
                if m:
                    length = m.end() - self.pos
                    lexeme = self.source[self.pos:self.pos + length]
                    self.tokens.append(Token(typ, lexeme, None, line, col))
                    self._advance_count(length)
                    matched = True
                    break
            if matched:
                continue

            # Float antes de int
            m = self.float_re.match(self.source, self.pos)
            if m:
                length = m.end() - self.pos
                lexeme = self.source[self.pos:self.pos + length]
                self.tokens.append(
                    Token("FLOAT", lexeme, float(lexeme), line, col)
                )
                self._advance_count(length)
                continue

            m = self.int_re.match(self.source, self.pos)
            if m:
                length = m.end() - self.pos
                lexeme = self.source[self.pos:self.pos + length]
                self.tokens.append(
                    Token("INT", lexeme, int(lexeme), line, col)
                )
                self._advance_count(length)
                continue

            m = self.ident_re.match(self.source, self.pos)
            if m:
                length = m.end() - self.pos
                lexeme = self.source[self.pos:self.pos + length]
                self.tokens.append(
                    Token("IDENT", lexeme, None, line, col)
                )
                self._advance_count(length)
                continue

            invalid = self._peek()
            raise LexerError(
                f"[ERRO LÉXICO] linha {self.line}, coluna {self.column}: "
                f"caractere/lexema inválido {invalid!r}. "
                f"Mas tu é sarna né?"
            )

        self.tokens.append(
            Token("EOF", "", None, self.line, self.column)
        )
        return self.tokens

    def _skip_ignored(self) -> bool:
        consumed = False

        while not self._at_end():
            ch = self._peek()

            if ch in " \t\r\n":
                self._advance_count(1)
                consumed = True
                continue

            # comentário tradicional
            if self.source.startswith("//", self.pos):
                while not self._at_end() and self._peek() not in "\r\n":
                    self._advance_count(1)
                consumed = True
                continue

            # comentário temático: BAH: comentário
            fragment = self.source[self.pos:self.pos + 4].upper()
            if fragment == "BAH:":
                while not self._at_end() and self._peek() not in "\r\n":
                    self._advance_count(1)
                consumed = True
                continue

            break

        return consumed

    def _string(self) -> Token:
        line, col = self.line, self.column
        start = self.pos
        self._advance_count(1)  # abre aspas
        chars = []

        while not self._at_end() and self._peek() != '"':
            ch = self._peek()

            if ch in "\r\n":
                raise LexerError(
                    f"[ERRO LÉXICO] linha {line}, coluna {col}: literal de texto "
                    "não pode atravessar quebra de linha."
                )

            if ch == "\\":
                self._advance_count(1)
                if self._at_end():
                    raise LexerError(
                        f"[ERRO LÉXICO] linha {line}, coluna {col}: escape incompleto."
                    )
                esc = self._peek()
                escapes = {
                    "n": "\n",
                    "t": "\t",
                    '"': '"',
                    "\\": "\\",
                }
                if esc not in escapes:
                    raise LexerError(
                        f"[ERRO LÉXICO] linha {self.line}, coluna {self.column}: "
                        f"escape inválido {chr(92) + esc!r}."
                    )
                chars.append(escapes[esc])
                self._advance_count(1)
            else:
                if not ch.isprintable():
                    raise LexerError(
                        f"[ERRO LÉXICO] linha {self.line}, coluna {self.column}: "
                        f"caractere não imprimível {ch!r} no texto."
                    )
                chars.append(ch)
                self._advance_count(1)

        if self._at_end():
            raise LexerError(
                f"[ERRO LÉXICO] linha {line}, coluna {col}: string não terminada."
            )

        self._advance_count(1)
        value = "".join(chars)
        return Token("STRING", self.source[start:self.pos], value, line, col)

    def _keyword_boundary(self, end: int) -> bool:
        if end >= len(self.source):
            return True
        ch = self.source[end]
        return not (ch.isalnum() or ch == "_")

    def _advance_count(self, count: int):
        for _ in range(count):
            ch = self.source[self.pos]
            self.pos += 1
            if ch == "\r" or (ch == "\n" and (self.pos < 2 or self.source[self.pos - 2] != "\r")):
                self.line += 1
                self.column = 1
            elif ch == "\n":
                self.column = 1
            else:
                self.column += 1

    def _peek(self) -> str:
        return self.source[self.pos]

    def _at_end(self) -> bool:
        return self.pos >= len(self.source)
