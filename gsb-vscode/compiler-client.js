const { execFile } = require('node:child_process');

// Sem shell: caminhos com espaços continuam sendo um único argumento.
function validateSource(source, { pythonPath, compilerDirectory }) {
  let child;
  const promise = new Promise((resolve, reject) => {
    child = execFile(pythonPath, ['-m', 'sarnalang.editor'], {
      cwd: compilerDirectory,
      timeout: 10000,
      maxBuffer: 2 * 1024 * 1024,
      encoding: 'utf8',
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    }, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(`Não foi possível validar com Python: ${stderr.trim() || error.message}`));
        return;
      }
      try {
        const result = JSON.parse(stdout);
        if (!Array.isArray(result.diagnostics) || !Array.isArray(result.declarations)) {
          throw new Error('resposta incompleta');
        }
        resolve(result);
      } catch (error) {
        reject(new Error(`Resposta inválida do analisador: ${error.message}`));
      }
    });
    child.stdin.on('error', () => {}); // A falha do processo é tratada no callback.
    child.stdin.end(source, 'utf8');
  });
  return { promise, cancel: () => child.kill() };
}

module.exports = { validateSource };
