from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from sarnalang.transpiler import transpile

ROOT = Path(__file__).resolve().parent.parent
COMPILER = next(([path] for name in ('cc', 'gcc', 'clang') if (path := shutil.which(name))), None)
SKIP_C = False


def program(body):
    return f'E AÍ MARCELO, É O QUÊ?\n{body}\nSHOW DE BOLA, VALEU!\n'


def execute(source, stdin=''):
    if SKIP_C:
        raise unittest.SkipTest('execução C desativada explicitamente por --skip-c')
    if not COMPILER:
        raise AssertionError('Instale GCC/Clang ou use --skip-c para uma verificação parcial.')
    code = transpile(source).c_code
    with tempfile.TemporaryDirectory(prefix='sarnalang_test_') as folder:
        c_file = Path(folder) / 'programa.c'
        executable = Path(folder) / 'programa.exe'
        c_file.write_text(code, encoding='utf-8')
        result = subprocess.run([
            *COMPILER, '-std=c11', '-Wall', '-Wextra', '-Werror', '-pedantic',
            '-Wno-unused-variable', '-Wno-unused-but-set-variable',
            str(c_file), '-o', str(executable)
        ], capture_output=True, text=True, encoding='utf-8', timeout=20)
        if result.returncode:
            raise AssertionError(f'C não compilou:\n{result.stderr}\n{code}')
        result = subprocess.run([str(executable)], input=stdin, capture_output=True,
                                text=True, encoding='utf-8', timeout=5)
        if result.returncode:
            raise AssertionError(f'Programa C encerrou com {result.returncode}: {result.stderr}')
        return result.stdout
