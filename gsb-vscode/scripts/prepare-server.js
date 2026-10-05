// Executado antes de empacotar: a extensão inclui a mesma implementação Python.
const fs = require('node:fs');
const path = require('node:path');
const source = path.resolve(__dirname, '../../sarnalang');
const destination = path.resolve(__dirname, '../server/sarnalang');
fs.mkdirSync(destination, { recursive: true });
for (const name of fs.readdirSync(source)) {
  if (name.endsWith('.py')) fs.copyFileSync(path.join(source, name), path.join(destination, name));
}
console.log('Analisador SarnaLang copiado para o pacote da extensão.');
