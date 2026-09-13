const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const ts = require(process.cwd() + '/examples/node_modules/typescript');
const source = fs.readFileSync('examples/web-shared/portal/merchant.ts', 'utf8');
async function scenario(name, postResult, ledger, expected) {
  const calls = []; let refreshed = 0; let updated = 0;
  const sandbox = {exports: {}, require(id) {
    if (id === 'react') return {useCallback: fn => fn, useRef: value => ({current:value})};
    if (id === '../turn') return {useAgentTurn: () => ({setItems: () => updated++})};
    throw Error(id);
  }};
  vm.runInNewContext(ts.transpileModule(source, {compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText, sandbox);
  const api = {post: async path => {calls.push(['POST',path]); return postResult;}, get: async path => {calls.push(['GET',path]); return ledger;}};
  const chat = sandbox.exports.useMerchantChat(api, {sessionId:'test',unreachable:'offline',onPortalRefresh:()=>refreshed++});
  const result = await chat.actOnChange('chg-1','apply');
  assert.equal(result?.status ?? null, expected);
  assert.equal(calls.filter(c=>c[0]==='POST').length,1,'never retry a write');
  assert.equal(refreshed,expected ? 1:0); assert.equal(updated,expected ? 1:0);
  assert.equal(calls.length,postResult ? 1:2);
  console.log('PASS', name);
}
(async()=>{
 await scenario('normal approval',{change:{change_id:'chg-1',status:'applied'}},null,'applied');
 await scenario('lost response after successful write',null,{recent_changes:[{change_id:'chg-1',status:'applied'}]},'applied');
 await scenario('different change cannot prove success',null,{recent_changes:[{change_id:'chg-2',status:'applied'}]},null);
 await scenario('wrong final state cannot prove success',null,{recent_changes:[{change_id:'chg-1',status:'discarded'}]},null);
 await scenario('unreachable read cannot prove success',null,null,null);
})();
