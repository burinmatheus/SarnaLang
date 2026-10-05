from __future__ import annotations

from dataclasses import dataclass
from .ast_nodes import *


class SemanticError(Exception):
    pass


@dataclass
class Symbol:
    name: str
    type_name: str
    line: int
    c_name: str


class SemanticAnalyzer:
    """
    Análise semântica separada do parser.

    Regras:
    - variável deve ser declarada antes do uso;
    - redeclaração no mesmo escopo é proibida;
    - shadowing em escopo interno é permitido;
    - atribuições devem ser compatíveis;
    - operações aritméticas exigem tipos numéricos;
    - comparações relacionais ordenadas exigem numéricos;
    - == e != aceitam tipos iguais ou numéricos mistos;
    - E MAIS / OU O QUÊ? / NEM A PAU exigem bool;
    - condições de if/while devem resultar em bool.
    """

    NUMERIC = {"int", "float"}

    def __init__(self):
        self.scopes: list[dict[str, Symbol]] = [dict()]
        self.expr_types: dict[int, str] = {}
        # Cada declaração e uso fica ligado ao símbolo resolvido no escopo.
        self.bindings: dict[int, Symbol] = {}
        self.symbol_count = 0
        self.statement_target_types: dict[int, str] = {}

    def analyze(self, program: Program):
        for stmt in program.statements:
            self._stmt(stmt)
        return self

    # -------------------------
    # Escopos / símbolos
    # -------------------------

    def _push_scope(self):
        self.scopes.append({})

    def _pop_scope(self):
        self.scopes.pop()

    def _declare(self, name: str, type_name: str, line: int):
        current = self.scopes[-1]
        if name in current:
            previous = current[name]
            raise SemanticError(
                f"[ERRO SEMÂNTICO] linha {line}: variável '{name}' "
                f"já declarada neste escopo na linha {previous.line}."
            )
        self.symbol_count += 1
        symbol = Symbol(name, type_name, line, f"sl_{self.symbol_count}_{name}")
        current[name] = symbol
        return symbol

    def _lookup(self, name: str, line: int) -> Symbol:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(
            f"[ERRO SEMÂNTICO] linha {line}: variável '{name}' "
            "utilizada antes de sua declaração."
        )

    # -------------------------
    # Statements
    # -------------------------

    def _stmt(self, node):
        if isinstance(node, VarDecl):
            # Regra deliberada: o identificador só passa a existir
            # depois da validação do inicializador.
            if node.initializer is not None:
                rhs = self._expr(node.initializer)
                if not self._assignable(node.type_name, rhs):
                    self._type_error(
                        node.line,
                        f"não é possível inicializar '{node.name}' do tipo "
                        f"{node.type_name} com expressão do tipo {rhs}"
                    )
            self.bindings[id(node)] = self._declare(node.name, node.type_name, node.line)
            return

        if isinstance(node, Assign):
            symbol = self._lookup(node.name, node.line)
            self.bindings[id(node)] = symbol
            self.statement_target_types[id(node)] = symbol.type_name
            rhs = self._expr(node.value)
            if not self._assignable(symbol.type_name, rhs):
                self._type_error(
                    node.line,
                    f"atribuição incompatível: '{node.name}' é "
                    f"{symbol.type_name}, mas a expressão é {rhs}"
                )
            return

        if isinstance(node, InputStmt):
            symbol = self._lookup(node.name, node.line)
            self.bindings[id(node)] = symbol
            self.statement_target_types[id(node)] = symbol.type_name
            return

        if isinstance(node, PrintStmt):
            for value in node.values:
                self._expr(value)
            return

        if isinstance(node, IfStmt):
            cond = self._expr(node.condition)
            if cond != "bool":
                self._type_error(
                    node.line,
                    f"a condição de 'MAS TU É SARNA NÉ?' deve ser bool, "
                    f"mas foi {cond}"
                )
            self._block(node.then_branch)
            if node.else_branch is not None:
                self._block(node.else_branch)
            return

        if isinstance(node, WhileStmt):
            cond = self._expr(node.condition)
            if cond != "bool":
                self._type_error(
                    node.line,
                    f"a condição de 'DE NOVO MARCELO' deve ser bool, "
                    f"mas foi {cond}"
                )
            self._block(node.body)
            return

        raise SemanticError(
            f"[ERRO SEMÂNTICO] linha {getattr(node, 'line', '?')}: "
            f"nó não suportado {type(node).__name__}."
        )

    def _block(self, block: Block):
        self._push_scope()
        try:
            for stmt in block.statements:
                self._stmt(stmt)
        finally:
            self._pop_scope()

    # -------------------------
    # Expressões
    # -------------------------

    def _expr(self, node) -> str:
        if isinstance(node, Literal):
            return self._remember(node, node.literal_type)

        if isinstance(node, Variable):
            symbol = self._lookup(node.name, node.line)
            self.bindings[id(node)] = symbol
            return self._remember(node, symbol.type_name)

        if isinstance(node, Unary):
            operand = self._expr(node.operand)

            if node.operator == "MINUS":
                if operand not in self.NUMERIC:
                    self._type_error(
                        node.line,
                        "operador unário '-' exige operando numérico"
                    )
                return self._remember(node, operand)

            if node.operator == "NOT":
                if operand != "bool":
                    self._type_error(
                        node.line,
                        "'NEM A PAU' exige expressão booleana"
                    )
                return self._remember(node, "bool")

        if isinstance(node, Binary):
            left = self._expr(node.left)
            right = self._expr(node.right)
            op = node.operator

            if op in {"PLUS", "MINUS", "STAR", "SLASH"}:
                if left not in self.NUMERIC or right not in self.NUMERIC:
                    self._type_error(
                        node.line,
                        f"operador aritmético exige operandos numéricos, "
                        f"recebido {left} e {right}"
                    )
                result = (
                    "float"
                    if "float" in {left, right}
                    else "int"
                )
                return self._remember(node, result)

            if op in {"LT", "LE", "GT", "GE"}:
                if left not in self.NUMERIC or right not in self.NUMERIC:
                    self._type_error(
                        node.line,
                        f"comparação relacional exige operandos numéricos, "
                        f"recebido {left} e {right}"
                    )
                return self._remember(node, "bool")

            if op in {"EQ", "NE"}:
                compatible = (
                    left == right
                    or (left in self.NUMERIC and right in self.NUMERIC)
                )
                if not compatible:
                    self._type_error(
                        node.line,
                        f"comparação de igualdade incompatível entre "
                        f"{left} e {right}"
                    )
                return self._remember(node, "bool")

            if op in {"AND", "OR"}:
                if left != "bool" or right != "bool":
                    self._type_error(
                        node.line,
                        f"operador lógico exige bool e bool, "
                        f"recebido {left} e {right}"
                    )
                return self._remember(node, "bool")

        raise SemanticError(
            f"[ERRO SEMÂNTICO] linha {getattr(node, 'line', '?')}: "
            f"expressão não suportada {type(node).__name__}."
        )

    def _remember(self, node, typ: str) -> str:
        self.expr_types[id(node)] = typ
        return typ

    @staticmethod
    def _assignable(target: str, source: str) -> bool:
        if target == source:
            return True
        # promoção segura int -> float
        return target == "float" and source == "int"

    @staticmethod
    def _type_error(line: int, message: str):
        raise SemanticError(
            f"[ERRO SEMÂNTICO] linha {line}: {message}."
        )
