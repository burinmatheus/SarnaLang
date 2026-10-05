from __future__ import annotations

from dataclasses import asdict, is_dataclass
from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .codegen_c import CCodeGenerator


class TranspileResult:
    def __init__(self, tokens, ast, semantic, c_code):
        self.tokens = tokens
        self.ast = ast
        self.semantic = semantic
        self.c_code = c_code


def transpile(source: str) -> TranspileResult:
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    semantic = SemanticAnalyzer().analyze(ast)
    c_code = CCodeGenerator(semantic).generate(ast)
    return TranspileResult(tokens, ast, semantic, c_code)


def ast_to_dict(node):
    if is_dataclass(node):
        result = {"node": type(node).__name__}
        for field_name in node.__dataclass_fields__:
            value = getattr(node, field_name)
            if isinstance(value, list):
                result[field_name] = [ast_to_dict(v) for v in value]
            elif is_dataclass(value):
                result[field_name] = ast_to_dict(value)
            else:
                result[field_name] = value
        return result
    return node
