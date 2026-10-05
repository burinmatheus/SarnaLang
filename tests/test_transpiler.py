import json
import re
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path

from sarnalang.ast_nodes import Binary
from sarnalang.editor import inspect_source
from sarnalang.lexer import Lexer, LexerError
from sarnalang.parser import ParserError
from sarnalang.semantic import SemanticError
from sarnalang.transpiler import transpile
from tests.support import ROOT, execute, program

CASES = ROOT / 'tests/casos'


class LexerTests(unittest.TestCase):
    def test_keywords_nfc_nfd_and_positions(self):
        for form in ('NFC', 'NFD'):
            source = unicodedata.normalize(form, program('PORTÃOZÃO x = 1;'))
            tokens = Lexer(source).tokenize()
            self.assertEqual(tokens[0].lexeme, source.splitlines()[0])
            self.assertEqual(tokens[1].type, 'TYPE_INT')
            self.assertEqual(tokens[2].column, source.splitlines()[1].index('x') + 1)
            transpile(source)

    def test_identifiers_and_digits_are_ascii(self):
        for name in ('café', 'cafe\u0301', 'ação', '١'):
            with self.subTest(name=name), self.assertRaises(LexerError):
                transpile(program(f'PORTÃOZÃO {name} = 1;'))
        with self.assertRaises(LexerError):
            transpile(program('PORTÃOZÃO x = ١;'))
        transpile(program('PORTÃOZÃO SHOWzinho = 1; PORTÃOZÃO CASONA_2 = 2;'))

    def test_original_string_and_following_error_positions(self):
        source = program('E AÍ MARCELO, MOSTRA AÍ("cafe\u0301 😀"); @')
        lexer = Lexer(source)
        with self.assertRaises(LexerError) as error:
            lexer.tokenize()
        column = source.splitlines()[1].index('@') + 1
        self.assertIn(f'linha 2, coluna {column}', str(error.exception))
        token = next(t for t in lexer.tokens if t.type == 'STRING')
        self.assertEqual(token.lexeme, '"cafe\u0301 😀"')
        self.assertEqual(token.literal, 'cafe\u0301 😀')

    def test_escapes_and_unterminated_strings(self):
        token = Lexer(r'"linha\n\t\"\\"').tokenize()[0]
        self.assertEqual(token.literal, 'linha\n\t"\\')
        for source in ('"sem fim', '"linha\nseguinte"', '"linha\rseguinte"', r'"escape\q"', '"\x00"', '"fim\\'):
            with self.subTest(source=source), self.assertRaises(LexerError):
                Lexer(source).tokenize()

    def test_longest_match_and_comments(self):
        types = [t.type for t in Lexer('= == < <= > >= != + - * /').tokenize()]
        self.assertEqual(types, ['ASSIGN', 'EQ', 'LT', 'LE', 'GT', 'GE', 'NE', 'PLUS', 'MINUS', 'STAR', 'SLASH', 'EOF'])
        for newline in ('\n', '\r\n', '\r'):
            source = newline.join(['// cafe\u0301 @', 'bah: comentário @', 'e ai marcelo, e o que?', 'show de bola, valeu!'])
            tokens = Lexer(source).tokenize()
            self.assertEqual(tokens[0].line, 3)
            transpile(source)
        source = program('').replace('E AÍ', 'E\t\nAÍ')
        transpile(source)


class PipelineTests(unittest.TestCase):
    def test_invalid_fixtures_and_editor_diagnostics(self):
        errors = {'03_erro_lexico.sarna': LexerError, '04_erro_sintatico.sarna': ParserError,
                  '05_erro_semantico.sarna': SemanticError, '06_erro_redeclaracao.sarna': SemanticError,
                  '07_erro_tipo.sarna': SemanticError, '09_erro_identificador.sarna': LexerError}
        for name, expected in errors.items():
            source = (CASES / name).read_text(encoding='utf-8')
            with self.subTest(name=name):
                with self.assertRaises(expected) as caught:
                    transpile(source)
                self.assertIn('linha', str(caught.exception))
                diagnostic = inspect_source(source)['diagnostics'][0]
                self.assertEqual(diagnostic['message'], str(caught.exception))
                self.assertEqual(diagnostic['category'], expected.__name__)
                print(f'\n{name}: {caught.exception}')

    def test_cli_errors_never_write_c(self):
        with tempfile.TemporaryDirectory() as folder:
            for name in ('03_erro_lexico', '04_erro_sintatico', '05_erro_semantico'):
                target = Path(folder) / 'resultado.c'
                result = subprocess.run([sys.executable, str(ROOT / 'main.py'), str(CASES / (name + '.sarna')), '-o', str(target)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 1)
                self.assertIn('[ERRO ', result.stderr)
                self.assertFalse(target.exists())

    def test_precedence_is_in_ast(self):
        expression = transpile(program('PORTÃOZÃO x = 2 + 3 * 4;')).ast.statements[0].initializer
        self.assertIsInstance(expression, Binary)
        self.assertEqual(expression.operator, 'PLUS')
        self.assertEqual(expression.right.operator, 'STAR')
        grouped = transpile(program('PORTÃOZÃO x = (2 + 3) * 4;')).ast.statements[0].initializer
        self.assertEqual(grouped.operator, 'STAR')
        self.assertEqual(grouped.left.operator, 'PLUS')

    def test_scope_and_type_errors(self):
        bodies = [
            'PORTÃOZÃO x = x + 1;',
            'MAS TU É SARNA NÉ? (SHOW) ABRE O PORTÃO PORTÃOZÃO x = 1; FECHA O PORTÃO E AÍ MARCELO, MOSTRA AÍ(x);',
            'PORTÃOZÃO x = 1; PORTÃOZÃO x = 2;',
            'MAS TU É SARNA NÉ? (1) ABRE O PORTÃO FECHA O PORTÃO',
            'GRAXA VÉIA x = SHOW E MAIS 1;',
            'PORTÃOZÃO x = 1.5;',
        ]
        for body in bodies:
            with self.subTest(body=body), self.assertRaises(SemanticError):
                transpile(program(body))

    def test_snippet_defaults_are_accepted(self):
        snippets = json.loads((ROOT / 'gsb-vscode/snippets.json').read_text(encoding='utf-8'))
        for label, snippet in snippets.items():
            body = '\n'.join(snippet['body'])
            body = re.sub(r'\$\{\d+:([^}]*)\}', lambda m: m[1], body)
            body = re.sub(r'\$\{\d+\}|\$\d+', '', body)
            if label.startswith('Expressão '):
                body = f'E AÍ MARCELO, MOSTRA AÍ({body});'
            if label == 'ME DIZ AÍ':
                body = 'PORTÃOZÃO variavel = 0;\n' + body
            source = body if label == 'Programa SarnaLang' else program(body)
            with self.subTest(label=label):
                self.assertEqual(inspect_source(source)['diagnostics'], [])


class ExecutionTests(unittest.TestCase):
    def test_required_valid_programs(self):
        fixtures = [
            ('01_valido_basico', '', 'Portão: 15\nCasona: 2.5\n'),
            ('02_valido_completo', 'Marcelo\n', 'Qual teu nome?\nRepetição: 3\nRepetição: 2\nRepetição: 1\nShow de bola, Marcelo\n2 + 3 * 4 = 14\n'),
            ('08_valido_escopos', '9\n', '6 externo\n9\nSHOW\n5 externo\n'),
        ]
        for name, stdin, expected in fixtures:
            with self.subTest(name=name):
                source = (CASES / (name + '.sarna')).read_text(encoding='utf-8')
                self.assertEqual(execute(source, stdin), expected)
                self.assertEqual((ROOT / 'generated' / (name + '.c')).read_text(encoding='utf-8'), transpile(source).c_code)

    def test_unicode_output_preserved(self):
        value = 'cafe\u0301 😀'
        source = program(f'NENEZINHO nome = "{value}"; E AÍ MARCELO, MOSTRA AÍ(nome);')
        self.assertEqual(execute(source), value + '\n')
        self.assertEqual(execute(unicodedata.normalize('NFD', source)), value + '\n')

    def test_arithmetic_logic_else_and_input_types(self):
        body = '''PORTÃOZÃO inteiro; CASONA real; GRAXA VÉIA logico;
ME DIZ AÍ(inteiro); ME DIZ AÍ(real); ME DIZ AÍ(logico);
E AÍ MARCELO, MOSTRA AÍ(inteiro, real, logico);
E AÍ MARCELO, MOSTRA AÍ(2 + 3 * 4, (2 + 3) * 4, 8 - 3 - 1, 8 / 2 * 3, 5 / 2, 5 / 2.0);
E AÍ MARCELO, MOSTRA AÍ(SHOW OU O QUÊ? NÃO SHOW E MAIS NÃO SHOW, NEM A PAU SHOW);
MAS TU É SARNA NÉ? (NÃO SHOW) ABRE O PORTÃO
    E AÍ MARCELO, MOSTRA AÍ("errado");
FECHA O PORTÃO NÃO É SARNA NÃO ABRE O PORTÃO
    E AÍ MARCELO, MOSTRA AÍ("alternativa");
FECHA O PORTÃO'''
        self.assertEqual(execute(program(body), '7 2.5 1\n'), '7 2.5 SHOW\n14 20 4 12 2 2.5\nSHOW NAO SHOW\nalternativa\n')

    def test_extension_examples_and_demo(self):
        fixtures = [
            (ROOT / 'gsb-vscode/examples/ola_mundo.sarna', '', 'Olá, Marcelo!\n'),
            (ROOT / 'gsb-vscode/examples/exemplo.sarna', 'Marcelo\n', 'Qual teu nome?\nRepetição: 3\nRepetição: 2\nRepetição: 1\nShow de bola, Marcelo\n2 + 3 * 4 = 14\n'),
            (ROOT / 'examples/demo_sarnalang.sarna', '', 'Mas tu é sarna né, Marcelo - o portãozão é 12\nPortãozão: 12\nPortãozão: 11\nPortãozão: 10\nSHOW DE BOLA!\n'),
        ]
        for source_file, stdin, expected in fixtures:
            with self.subTest(file=source_file):
                source = source_file.read_text(encoding='utf-8')
                self.assertEqual(inspect_source(source)['diagnostics'], [])
                self.assertEqual(execute(source, stdin), expected)
