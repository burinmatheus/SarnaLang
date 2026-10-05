from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional


class Node:
    line: int


@dataclass
class Program(Node):
    statements: list[Node]
    line: int = 1


@dataclass
class Block(Node):
    statements: list[Node]
    line: int


@dataclass
class VarDecl(Node):
    type_name: str
    name: str
    initializer: Optional[Node]
    line: int


@dataclass
class Assign(Node):
    name: str
    value: Node
    line: int


@dataclass
class PrintStmt(Node):
    values: list[Node]
    line: int


@dataclass
class InputStmt(Node):
    name: str
    line: int


@dataclass
class IfStmt(Node):
    condition: Node
    then_branch: Block
    else_branch: Optional[Block]
    line: int


@dataclass
class WhileStmt(Node):
    condition: Node
    body: Block
    line: int


@dataclass
class Binary(Node):
    left: Node
    operator: str
    right: Node
    line: int


@dataclass
class Unary(Node):
    operator: str
    operand: Node
    line: int


@dataclass
class Literal(Node):
    value: Any
    literal_type: str
    line: int


@dataclass
class Variable(Node):
    name: str
    line: int
