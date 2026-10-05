"""Validação para editores: fonte UTF-8 em stdin, diagnóstico JSON em stdout.

Usa as mesmas três fases do transpilador e nunca grava código C.
"""
from __future__ import annotations

import json
import re
import sys

from .lexer import Lexer, LexerError
from .parser import Parser, ParserError, TYPE_MAP
from .semantic import SemanticAnalyzer, SemanticError


def inspect_source(source: str) -> dict:
    lexer = Lexer(source)
    diagnostics = []
    try:
        tokens = lexer.tokenize()
        ast = Parser(tokens).parse()
        SemanticAnalyzer().analyze(ast)
    except (LexerError, ParserError, SemanticError) as exc:
        message = str(exc)
        position = re.search(r"linha (\d+)(?:, coluna (\d+))?", message)
        diagnostics.append({
            "message": message,
            "line": int(position[1]) if position else 1,
            "column": int(position[2]) if position and position[2] else None,
            "category": type(exc).__name__,
        })

    declarations = []
    for previous, token in zip(lexer.tokens, lexer.tokens[1:]):
        if previous.type in TYPE_MAP and token.type == "IDENT":
            declarations.append({
                "name": token.lexeme,
                "type": TYPE_MAP[previous.type],
                "line": token.line,
                "column": token.column,
            })
    return {"diagnostics": diagnostics, "declarations": declarations}


def main():
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(inspect_source(sys.stdin.read()), ensure_ascii=True))


if __name__ == "__main__":
    main()
