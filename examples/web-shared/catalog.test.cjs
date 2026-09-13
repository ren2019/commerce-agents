const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');

function harness(load) {
  let locale = 'en', state = {}, effect, cleanup;
  const sandbox = { exports: {}, require(name) {
    if (name === 'react') return {
      useState: () => [state, (next) => { state = next; }],
      useEffect: (callback) => { effect = callback; },
    };
    if (name === './language') return { useDemoLanguage: () => ({ language: locale }) };
    throw Error(name);
  } };
  vm.runInNewContext(ts.transpileModule(fs.readFileSync(`${__dirname}/catalog.ts`, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS },
  }).outputText, sandbox);
  return {
    async show(language) {
      cleanup?.(); locale = language;
      sandbox.exports.useCatalogIndex(load); cleanup = effect();
      await new Promise(setImmediate);
      return state;
    },
    state: () => state,
  };
}

test('failed English refresh retains products and is retried rather than cached empty', async () => {
  let calls = 0;
  const zh = { product_id: 'A', title: '中文', labels: ['bestseller'] };
  const en = { ...zh, title: 'English' };
  const responses = [[zh], null, [en]];
  const h = harness(async () => responses[calls++]);
  assert.equal((await h.show('zh')).A.title, '中文');
  assert.equal((await h.show('en')).A.title, '中文');
  await h.show('zh');
  assert.equal((await h.show('en')).A.title, 'English');
  assert.equal(calls, 3);
});

test('initial failure is retriable but a genuine empty catalog is cached', async () => {
  let calls = 0;
  const h = harness(async () => ++calls === 1 ? null : []);
  await h.show('en'); await h.show('en'); await h.show('en');
  assert.equal(calls, 2);
  assert.equal(Object.keys(h.state()).length, 0);
});

test('an older language response cannot overwrite the currently selected language', async () => {
  let finish;
  let calls = 0;
  const h = harness(() => ++calls === 1 ? new Promise(resolve => { finish = resolve; }) : Promise.resolve([{ product_id: 'A', title: '中文' }]));
  await h.show('en'); await h.show('zh');
  finish([{ product_id: 'A', title: 'English' }]);
  await new Promise(setImmediate);
  assert.equal(h.state().A.title, '中文');
});
