import test from 'node:test';
import assert from 'node:assert/strict';
import {submitContact} from '../contact-submission.mjs';
import {prepareContactData, CONTACT_METHODS} from '../contact-preferences.mjs';

const endpoint = 'https://formsubmit.co/ajax/info@lumirize.co';
const data = new FormData();
data.set('message', 'test-only content that must not appear in diagnostics');

for (const success of [true, 'true']) {
  test(`accept explicit acknowledgement: ${typeof success}`, async () => {
    let calls = 0;
    const result = await submitContact(endpoint, data, {fetchImpl: async (url, init) => {
      calls++;
      assert.equal(url, endpoint);
      assert.equal(init.method, 'POST');
      assert.equal(init.body, data);
      assert.deepEqual(init.headers, {Accept: 'application/json'});
      return {ok: true, json: async () => ({success})};
    }});
    assert.deepEqual(result, {confirmed: true, reason: 'accepted'});
    assert.equal(calls, 1);
  });
}

for (const payload of [{success: false}, {success: 'false'}, {}, null, {success: 'TRUE'}]) {
  test(`do not claim success for ${JSON.stringify(payload)}`, async () => {
    const result = await submitContact(endpoint, data, {fetchImpl: async () => ({
      ok: true, json: async () => payload
    })});
    assert.deepEqual(result, {confirmed: false, reason: 'not-confirmed'});
  });
}

test('HTTP failure remains unconfirmed even with a success-looking body', async () => {
  const result = await submitContact(endpoint, data, {fetchImpl: async () => ({
    ok: false, json: async () => ({success: true})
  })});
  assert.deepEqual(result, {confirmed: false, reason: 'http-response'});
});

test('unreadable response remains unconfirmed and exposes no response text', async () => {
  const result = await submitContact(endpoint, data, {fetchImpl: async () => ({
    ok: true, json: async () => { throw new SyntaxError('private response body'); }
  })});
  assert.deepEqual(result, {confirmed: false, reason: 'unreadable-response'});
});

test('network failure does not retry or expose submitted content', async () => {
  let calls = 0;
  const result = await submitContact(endpoint, data, {fetchImpl: async () => {
    calls++;
    throw new TypeError(data.get('message'));
  }});
  assert.deepEqual(result, {confirmed: false, reason: 'network'});
  assert.equal(calls, 1);
});

test('timeout is an unknown delivery outcome, with one request only', async () => {
  let calls = 0;
  const result = await submitContact(endpoint, data, {
    timeoutMs: 10,
    fetchImpl: async (_url, {signal}) => {
      calls++;
      return new Promise((_resolve, reject) => signal.addEventListener('abort',
        () => reject(new DOMException('aborted', 'AbortError')), {once: true}));
    }
  });
  assert.deepEqual(result, {confirmed: false, reason: 'timeout'});
  assert.equal(calls, 1);
});

test('accept a response after the former 20-second deadline without resending', async t => {
  t.mock.timers.enable({apis: ['setTimeout']});
  let calls = 0;
  const resultPromise = submitContact(endpoint, data, {fetchImpl: (_url, {signal}) => {
    calls++;
    return new Promise((resolve, reject) => {
      signal.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')));
      setTimeout(() => resolve({ok: true, json: async () => ({success: true})}), 45000);
    });
  }});
  t.mock.timers.tick(45000);
  assert.deepEqual(await resultPromise, {confirmed: true, reason: 'accepted'});
  assert.equal(calls, 1);
});

test('no-reply preference preserves the notification but strips reply destinations', () => {
  const input = new FormData();
  input.set('連絡方法', CONTACT_METHODS.none);
  input.set('email', 'test@example.invalid');
  input.set('phone', '0000000000');
  input.set('_replyto', 'test@example.invalid');
  input.set('_autoresponse', 'should not be sent');
  input.set('message', 'no-reply test');
  const prepared = prepareContactData(input);
  for (const name of ['email', 'phone', '_replyto', '_autoresponse']) assert.equal(prepared.has(name), false);
  assert.equal(prepared.get('message'), 'no-reply test');
  assert.equal(prepared.get('電話連絡'), '不可');
  assert.equal(prepared.get('メール返信'), '不可');
  assert.equal(prepared.get('留守電'), '電話・留守電ともに不可');
});
