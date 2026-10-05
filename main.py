from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from sarnalang.lexer import LexerError
from sarnalang.parser import ParserError
from sarnalang.semantic import SemanticError
from sarnalang.codegen_c import CodegenError
from sarnalang.transpiler import transpile, ast_to_dict


def main():
    ap = argparse.ArgumentParser(
        description="SarnaLang 1.0 - transpilador SarnaLang -> C"
    )
    ap.add_argument("arquivo", help="arquivo-fonte .sarna")
    ap.add_argument(
        "-o", "--output",
        help="arquivo C de saída; padrão: mesmo nome com extensão .c"
    )
    ap.add_argument(
        "--tokens",
        action="store_true",
        help="exibe tokens reconhecidos"
    )
    ap.add_argument(
        "--ast",
        action="store_true",
        help="exibe AST em JSON"
    )
    args = ap.parse_args()

    source_path = Path(args.arquivo)
    if not source_path.exists():
        print(
            f"Arquivo não encontrado: {source_path}",
            file=sys.stderr
        )
        raise SystemExit(2)

    source = source_path.read_text(encoding="utf-8")

    try:
        result = transpile(source)

        if args.tokens:
            print("=== TOKENS ===")
            for t in result.tokens:
                literal = (
                    f" literal={t.literal!r}"
                    if t.literal is not None
                    else ""
                )
                print(
                    f"{t.line:>3}:{t.column:<3} "
                    f"{t.type:<14} {t.lexeme!r}{literal}"
                )

        if args.ast:
            print("=== AST ===")
            print(
                json.dumps(
                    ast_to_dict(result.ast),
                    ensure_ascii=False,
                    indent=2
                )
            )

        output_path = (
            Path(args.output)
            if args.output
            else source_path.with_suffix(".c")
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result.c_code, encoding="utf-8")

        print("Léxico: OK")
        print("Sintaxe: OK")
        print("Semântica: OK")
        print(f"Código C gerado: {output_path}")

    except (LexerError, ParserError, SemanticError, CodegenError) as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
