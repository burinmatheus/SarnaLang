const assert = require('node:assert/strict');
const { test } = require('node:test');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const Module = require('node:module');
const { validateSource } = require('../compiler-client');
const root = path.resolve(__dirname, '../..');
const options = { pythonPath: process.env.SARNA_TEST_PYTHON || (process.platform === 'win32' ? 'python' : 'python3'), compilerDirectory: root };
const wrap = body => `E AÍ MARCELO, É O QUÊ?\n${body}\nSHOW DE BOLA, VALEU!`;
const read = file => fs.readFileSync(path.join(root, file), 'utf8');

test('ponte Python valida exemplos e retorna as três categorias de erro', async () => {
  for (const file of ['tests/casos/01_valido_basico.sarna', 'tests/casos/02_valido_completo.sarna', 'tests/casos/08_valido_escopos.sarna', 'gsb-vscode/examples/exemplo.sarna', 'gsb-vscode/examples/ola_mundo.sarna']) {
    const result = await validateSource(read(file), options).promise;
    assert.deepEqual(result.diagnostics, [], file);
  }
  for (const [file, category] of [['03_erro_lexico', 'LexerError'], ['04_erro_sintatico', 'ParserError'], ['05_erro_semantico', 'SemanticError']]) {
    const result = await validateSource(read(`tests/casos/${file}.sarna`), options).promise;
    assert.equal(result.diagnostics[0].category, category);
    assert.ok(result.diagnostics[0].line > 0);
  }
});

test('backend empacotado funciona fora do repositório e em caminho com espaços', async () => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'sarna extension '));
  try {
    fs.cpSync(path.join(root, 'gsb-vscode/server/sarnalang'), path.join(temporary, 'sarnalang'), { recursive: true });
    const result = await validateSource(wrap('E AÍ MARCELO, MOSTRA AÍ("cafe\u0301 😀");').normalize('NFD'), { ...options, compilerDirectory: temporary }).promise;
    assert.deepEqual(result.diagnostics, []);
    for (const name of fs.readdirSync(path.join(root, 'sarnalang')).filter(name => name.endsWith('.py'))) {
      assert.equal(fs.readFileSync(path.join(temporary, 'sarnalang', name), 'utf8'), read(`sarnalang/${name}`), name);
    }
  } finally {
    fs.rmSync(temporary, { recursive: true, force: true });
  }
});

test('falha de Python é reportada sem se passar por erro da linguagem', async () => {
  await assert.rejects(validateSource(wrap(''), { ...options, pythonPath: path.join(root, 'python-inexistente') }).promise, /Não foi possível validar com Python/);
});

test('realce reconhece frases completas antes de SHOW e as formas NFC/NFD', () => {
  const grammar = JSON.parse(read('gsb-vscode/syntaxes/gsb.tmLanguage.json'));
  const patterns = grammar.patterns.filter(p => p.match).map(p => ({ ...p, regex: new RegExp(p.match.replace('(?i)', ''), p.match.includes('(?i)') ? 'iu' : 'u') }));
  const phrases = [
    ['E AÍ MARCELO, É O QUÊ?', 'keyword.control.gsb'], ['SHOW DE BOLA, VALEU!', 'keyword.control.gsb'],
    ['ABRE O PORTÃO', 'keyword.control.gsb'], ['FECHA O PORTÃO', 'keyword.control.gsb'],
    ['PORTÃOZÃO', 'storage.type.gsb'], ['CASONA', 'storage.type.gsb'], ['NENEZINHO', 'storage.type.gsb'], ['GRAXA VÉIA', 'storage.type.gsb'],
    ['E AÍ MARCELO, MOSTRA AÍ', 'keyword.control.gsb'], ['ME DIZ AÍ', 'keyword.control.gsb'],
    ['MAS TU É SARNA NÉ?', 'keyword.control.gsb'], ['NÃO É SARNA NÃO', 'keyword.control.gsb'], ['DE NOVO MARCELO', 'keyword.control.gsb'],
    ['SHOW', 'constant.language.boolean.gsb'], ['NÃO SHOW', 'constant.language.boolean.gsb'],
    ['E MAIS', 'keyword.operator.gsb'], ['OU O QUÊ?', 'keyword.operator.gsb'], ['NEM A PAU', 'keyword.operator.gsb']
  ];
  for (const [phrase, scope] of phrases) {
    for (const text of [phrase, phrase.normalize('NFD'), phrase.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase()]) {
      const matched = patterns.find(p => p.regex.exec(text)?.index === 0);
      assert.equal(matched.name, scope, text);
      assert.equal(matched.regex.exec(text)[0], text);
    }
  }
});

test('extensão atualiza Problems com fonte não salva e converte colunas UTF-16', async () => {
  const listeners = {};
  const noOpDisposable = { dispose() {} };
  let source = wrap('E AÍ MARCELO, MOSTRA AÍ("😀"); @');
  const uri = { toString: () => 'untitled:teste', fsPath: '' };
  const document = { languageId: 'gsb', uri, isClosed: false, version: 1,
    getText: () => source,
    get lineCount() { return source.split('\n').length; },
    lineAt: line => ({ text: source.split('\n')[line], range: { line } })
  };
  let receive;
  const nextDiagnostics = () => new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('diagnóstico não recebido')), 5000);
    receive = issues => { clearTimeout(timeout); resolve(issues); };
  });
  const mock = {
    Range: class { constructor(line, start, endLine, end) { Object.assign(this, { line, start, endLine, end }); } },
    Diagnostic: class { constructor(range, message, severity) { Object.assign(this, { range, message, severity }); } },
    DiagnosticSeverity: { Error: 0, Warning: 1 },
    languages: {
      createDiagnosticCollection: () => ({ set: (uri, issues) => receive(issues), delete() {}, dispose() {} }),
      registerCompletionItemProvider: () => noOpDisposable,
      registerHoverProvider: () => noOpDisposable
    },
    workspace: {
      isTrusted: true, textDocuments: [document],
      getWorkspaceFolder: () => undefined,
      getConfiguration: () => ({ get: (name, fallback) => name === 'pythonPath' ? options.pythonPath : fallback }),
      onDidOpenTextDocument: () => noOpDisposable,
      onDidSaveTextDocument: () => noOpDisposable,
      onDidChangeTextDocument: fn => { listeners.change = fn; return noOpDisposable; },
      onDidCloseTextDocument: fn => { listeners.close = fn; return noOpDisposable; },
      onDidChangeConfiguration: () => noOpDisposable
    },
    commands: { registerCommand: () => noOpDisposable }, window: {}
  };
  const originalLoad = Module._load;
  let extension;
  try {
    Module._load = function (name, ...args) { return name === 'vscode' ? mock : originalLoad.call(this, name, ...args); };
    extension = require('../extension');
  } finally {
    Module._load = originalLoad;
  }
  const context = { subscriptions: [] };
  try {
    let waiting = nextDiagnostics();
    extension.activate(context);
    let issues = await waiting;
    assert.equal(issues[0].code, 'LexerError');
    assert.equal(issues[0].range.start, source.split('\n')[1].indexOf('@'));
    waiting = nextDiagnostics();
    // Dois eventos antes do debounce: somente a versão atual deve prevalecer.
    source = wrap('PORTÃOZÃO x = ;'); document.version++;
    listeners.change({ document });
    source = wrap('PORTÃOZÃO x = 2 + 3 * 4;'); document.version++;
    listeners.change({ document });
    issues = await waiting;
    assert.deepEqual(issues, []);
    listeners.close(document);
  } finally {
    for (const disposable of context.subscriptions) disposable.dispose();
  }
});
