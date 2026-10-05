const vscode = require('vscode');
const fs = require('node:fs');
const path = require('node:path');
const { validateSource } = require('./compiler-client');
const snippets = require('./snippets.json');

function compilerOptions(document) {
  const config = vscode.workspace.getConfiguration('sarna', document.uri);
  const workspace = vscode.workspace.getWorkspaceFolder(document.uri);
  const configured = config.get('compilerDirectory', '');
  const development = path.resolve(__dirname, '..');
  const bundled = path.join(__dirname, 'server');
  const compilerDirectory = configured
    ? path.resolve(workspace ? workspace.uri.fsPath : __dirname, configured)
    : fs.existsSync(path.join(development, 'sarnalang', 'editor.py')) ? development : bundled;
  return {
    pythonPath: config.get('pythonPath', process.platform === 'win32' ? 'python' : 'python3'),
    compilerDirectory
  };
}

function diagnosticRange(document, issue) {
  const line = Math.max(0, Math.min(document.lineCount - 1, issue.line - 1));
  const text = document.lineAt(line).text;
  if (!issue.column) return document.lineAt(line).range;
  // Python conta pontos de código; o VS Code usa unidades UTF-16.
  const chars = Array.from(text);
  const start = chars.slice(0, issue.column - 1).join('').length;
  const end = chars.slice(0, issue.column).join('').length;
  return new vscode.Range(line, start, line, end);
}

function activate(context) {
  const diagnostics = vscode.languages.createDiagnosticCollection('sarnalang');
  const pending = new Map();
  const declarations = new Map();

  function cancel(key) {
    const state = pending.get(key);
    if (state) {
      clearTimeout(state.timer);
      if (state.job) state.job.cancel();
      pending.delete(key);
    }
  }

  function validate(document, immediate = false) {
    if (document.languageId !== 'gsb' || document.isClosed || !vscode.workspace.isTrusted) return;
    const key = document.uri.toString();
    cancel(key);
    declarations.delete(key);
    const version = document.version;
    const state = {};
    pending.set(key, state);
    const current = () => pending.get(key) === state && !document.isClosed && document.version === version;
    const run = () => {
      state.job = validateSource(document.getText(), compilerOptions(document));
      state.job.promise.then(result => {
        if (!current()) return;
        declarations.set(key, result.declarations);
        diagnostics.set(document.uri, result.diagnostics.map(issue => {
          const diagnostic = new vscode.Diagnostic(diagnosticRange(document, issue), issue.message, vscode.DiagnosticSeverity.Error);
          diagnostic.source = 'SarnaLang';
          diagnostic.code = issue.category;
          return diagnostic;
        }));
        pending.delete(key);
      }).catch(error => {
        if (!current()) return;
        const diagnostic = new vscode.Diagnostic(
          new vscode.Range(0, 0, 0, 0),
          `${error.message}. Verifique sarna.pythonPath e sarna.compilerDirectory nas configurações.`,
          vscode.DiagnosticSeverity.Warning
        );
        diagnostic.source = 'SarnaLang';
        diagnostics.set(document.uri, [diagnostic]);
        pending.delete(key);
      });
    };
    if (immediate) run();
    else state.timer = setTimeout(run, 250);
  }

  context.subscriptions.push(diagnostics, {
    dispose() { for (const key of pending.keys()) cancel(key); }
  });
  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(document => validate(document)),
    vscode.workspace.onDidSaveTextDocument(document => validate(document, true)),
    vscode.workspace.onDidChangeTextDocument(event => validate(event.document)),
    vscode.workspace.onDidCloseTextDocument(document => {
      const key = document.uri.toString();
      cancel(key);
      declarations.delete(key);
      diagnostics.delete(document.uri);
    }),
    vscode.workspace.onDidChangeConfiguration(event => {
      if (event.affectsConfiguration('sarna')) {
        for (const document of vscode.workspace.textDocuments) validate(document, true);
      }
    }),
    vscode.commands.registerCommand('gsb.validateCurrentFile', () => {
      if (vscode.window.activeTextEditor) validate(vscode.window.activeTextEditor.document, true);
    })
  );

  context.subscriptions.push(vscode.languages.registerCompletionItemProvider('gsb', {
    provideCompletionItems(document, position) {
      const items = Object.entries(snippets).map(([label, snippet]) => {
        const item = new vscode.CompletionItem(label, vscode.CompletionItemKind.Snippet);
        item.detail = snippet.description;
        item.insertText = new vscode.SnippetString(snippet.body.join('\n'));
        return item;
      });
      const known = new Map();
      for (const declaration of declarations.get(document.uri.toString()) || []) {
        if (declaration.line - 1 <= position.line) known.set(declaration.name, declaration);
      }
      for (const declaration of known.values()) {
        const item = new vscode.CompletionItem(declaration.name, vscode.CompletionItemKind.Variable);
        item.detail = `${declaration.type} · declaração no documento`;
        items.push(item);
      }
      return items;
    }
  }));

  context.subscriptions.push(vscode.languages.registerHoverProvider('gsb', {
    provideHover(document, position) {
      const range = document.getWordRangeAtPosition(position, /[\p{L}\p{M}_]+/u);
      if (!range) return;
      const word = document.getText(range).normalize('NFD').replace(/\p{M}/gu, '').toUpperCase();
      const docs = {
        PORTAOZAO: '**PORTÃOZÃO** — inteiro (`int` em C).',
        CASONA: '**CASONA** — real (`double` em C).',
        NENEZINHO: '**NENEZINHO** — texto de até 255 bytes UTF-8.',
        GRAXA: '**GRAXA VÉIA** — lógico: `SHOW` ou `NÃO SHOW`.'
      };
      if (docs[word]) return new vscode.Hover(new vscode.MarkdownString(docs[word]), range);
    }
  }));

  for (const document of vscode.workspace.textDocuments) validate(document);
}

module.exports = { activate, diagnosticRange };
