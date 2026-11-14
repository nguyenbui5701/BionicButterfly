// Independent ECMAScript/V8 comparison harness, tests only. RFC 8785 sections
// 3.2.2 and 3.2.3: native number/string encoding and recursive UTF-16 key sorting.
'use strict';
const fs = require('node:fs');
function canonical(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}';
}
process.stdout.write(JSON.stringify(JSON.parse(fs.readFileSync(0, 'utf8')).map(canonical)));
