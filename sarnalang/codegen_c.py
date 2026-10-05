from __future__ import annotations

import json
from .ast_nodes import *


class CodegenError(Exception):
    pass


class CCodeGenerator:
    """
    Gera C a partir da AST já validada semanticamente.
    Não realiza substituição textual de keywords.
    """

    def __init__(self, semantic):
        self.semantic = semantic
        self.lines: list[str] = []
        self.indent = 0

    def generate(self, program: Program) -> str:
        self.lines = [
            "#include <stdio.h>",
            "#include <string.h>",
            "",
            "int main(void) {",
        ]
        self.indent = 1

        for stmt in program.statements:
            self._stmt(stmt)

        self._emit("return 0;")
        self.indent = 0
        self.lines.append("}")
        self.lines.append("")
        return "\n".join(self.lines)

    def _emit(self, text=""):
        self.lines.append("    " * self.indent + text)

    def _stmt(self, node):
        if isinstance(node, VarDecl):
            self._var_decl(node)
            return

        if isinstance(node, Assign):
            self._assign(node)
            return

        if isinstance(node, PrintStmt):
            self._print(node)
            return

        if isinstance(node, InputStmt):
            self._input(node)
            return

        if isinstance(node, IfStmt):
            self._emit(f"if ({self._expr(node.condition)}) {{")
            self.indent += 1
            for stmt in node.then_branch.statements:
                self._stmt(stmt)
            self.indent -= 1

            if node.else_branch is None:
                self._emit("}")
            else:
                self._emit("} else {")
                self.indent += 1
                for stmt in node.else_branch.statements:
                    self._stmt(stmt)
                self.indent -= 1
                self._emit("}")
            return

        if isinstance(node, WhileStmt):
            self._emit(f"while ({self._expr(node.condition)}) {{")
            self.indent += 1
            for stmt in node.body.statements:
                self._stmt(stmt)
            self.indent -= 1
            self._emit("}")
            return

        raise CodegenError(
            f"Nó não suportado na geração C: {type(node).__name__}"
        )

    def _var_decl(self, node: VarDecl):
        name = self._c_name(node)

        if node.type_name == "int":
            value = (
                self._expr(node.initializer)
                if node.initializer is not None
                else "0"
            )
            self._emit(f"int {name} = {value};")
            return

        if node.type_name == "float":
            value = (
                self._expr(node.initializer)
                if node.initializer is not None
                else "0.0"
            )
            self._emit(f"double {name} = {value};")
            return

        if node.type_name == "bool":
            value = (
                self._expr(node.initializer)
                if node.initializer is not None
                else "0"
            )
            self._emit(f"int {name} = {value};")
            return

        if node.type_name == "string":
            self._emit(f"char {name}[256] = \"\";")
            if node.initializer is not None:
                rhs = self._expr(node.initializer)
                self._emit(
                    f"strncpy({name}, {rhs}, sizeof({name}) - 1);"
                )
                self._emit(
                    f"{name}[sizeof({name}) - 1] = '\\0';"
                )
            return

        raise CodegenError(f"Tipo desconhecido: {node.type_name}")

    def _assign(self, node: Assign):
        name = self._c_name(node)
        target = self.semantic.statement_target_types[id(node)]

        if target == "string":
            # x = x preserva o valor; strncpy com buffers sobrepostos é inválido.
            if isinstance(node.value, Variable) and self._c_name(node.value) == name:
                return
            rhs = self._expr(node.value)
            self._emit(
                f"strncpy({name}, {rhs}, sizeof({name}) - 1);"
            )
            self._emit(f"{name}[sizeof({name}) - 1] = '\\0';")
        else:
            self._emit(f"{name} = {self._expr(node.value)};")

    def _print(self, node: PrintStmt):
        for index, value in enumerate(node.values):
            typ = self.semantic.expr_types[id(value)]
            expr = self._expr(value)

            if typ == "int":
                self._emit(f'printf("%d", {expr});')
            elif typ == "float":
                self._emit(f'printf("%g", {expr});')
            elif typ == "string":
                self._emit(f'printf("%s", {expr});')
            elif typ == "bool":
                self._emit(
                    f'printf("%s", ({expr}) ? "SHOW" : "NAO SHOW");'
                )
            else:
                raise CodegenError(f"Tipo de saída não suportado: {typ}")

            if index < len(node.values) - 1:
                self._emit('printf(" ");')

        self._emit('printf("\\n");')

    def _input(self, node: InputStmt):
        typ = self.semantic.statement_target_types[id(node)]
        name = self._c_name(node)

        if typ == "int":
            self._emit(f'scanf("%d", &{name});')
        elif typ == "float":
            self._emit(f'scanf("%lf", &{name});')
        elif typ == "string":
            self._emit(f'scanf("%255s", {name});')
        elif typ == "bool":
            # bool é lido como 0 ou 1 para manter C simples.
            self._emit(f'scanf("%d", &{name});')
        else:
            raise CodegenError(f"Tipo de entrada não suportado: {typ}")

    def _expr(self, node) -> str:
        if isinstance(node, Literal):
            if node.literal_type == "string":
                return json.dumps(
                    node.value,
                    ensure_ascii=False
                )
            if node.literal_type == "bool":
                return "1" if node.value else "0"
            if node.literal_type == "float":
                return repr(float(node.value))
            return str(node.value)

        if isinstance(node, Variable):
            return self._c_name(node)

        if isinstance(node, Unary):
            op = {
                "MINUS": "-",
                "NOT": "!",
            }[node.operator]
            return f"({op}{self._expr(node.operand)})"

        if isinstance(node, Binary):
            left_type = self.semantic.expr_types[id(node.left)]
            right_type = self.semantic.expr_types[id(node.right)]

            # == / != entre strings vira strcmp.
            if (
                node.operator in {"EQ", "NE"}
                and left_type == "string"
                and right_type == "string"
            ):
                cmp_op = "==" if node.operator == "EQ" else "!="
                return (
                    f"(strcmp({self._expr(node.left)}, "
                    f"{self._expr(node.right)}) {cmp_op} 0)"
                )

            op = {
                "PLUS": "+",
                "MINUS": "-",
                "STAR": "*",
                "SLASH": "/",
                "EQ": "==",
                "NE": "!=",
                "LT": "<",
                "LE": "<=",
                "GT": ">",
                "GE": ">=",
                "AND": "&&",
                "OR": "||",
            }[node.operator]

            return (
                f"({self._expr(node.left)} {op} "
                f"{self._expr(node.right)})"
            )

        raise CodegenError(
            f"Expressão não suportada: {type(node).__name__}"
        )

    def _c_name(self, node) -> str:
        return self.semantic.bindings[id(node)].c_name
