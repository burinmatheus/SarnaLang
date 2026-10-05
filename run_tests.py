"""Executa testes de fases, CLI, exemplos e compilação/execução em C."""
import argparse
import shlex
import unittest
from tests import support


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cc', help='Compilador C (padrão: cc, gcc ou clang disponível).')
    parser.add_argument('--skip-c', action='store_true', help='Verificação parcial, sem compilar/executar C.')
    args = parser.parse_args()
    if args.cc:
        support.COMPILER = shlex.split(args.cc)
    support.SKIP_C = args.skip_c
    if not support.COMPILER and not args.skip_c:
        parser.error('GCC/Clang não encontrado. Instale um compilador ou use --skip-c para verificação parcial.')
    suite = unittest.defaultTestLoader.discover(str(support.ROOT / 'tests'), top_level_dir=str(support.ROOT))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
