import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';
import { ApiError, request } from '../src/api/client.js';

const originalFetch = globalThis.fetch;
afterEach(() => {
  globalThis.fetch = originalFetch;
});

test('sends the authenticated JSON request and preserves decimal response values', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/cart/items');
    assert.equal(options.method, 'POST');
    assert.equal(options.headers.Authorization, 'Bearer demo-token');
    assert.equal(options.headers['Content-Type'], 'application/json');
    assert.deepEqual(JSON.parse(options.body), { product_id: 1, quantity: 2 });
    return new Response(JSON.stringify({ total: '98.00' }));
  };
  assert.deepEqual(
    await request('/api/cart/items', {
      method: 'POST',
      token: 'demo-token',
      body: { product_id: 1, quantity: 2 },
    }),
    { total: '98.00' },
  );
});

test('retains API status and safe business error messages', async () => {
  globalThis.fetch = async () =>
    new Response(
      JSON.stringify({
        detail: 'Insufficient stock.',
        code: 'insufficient_stock',
        params: { stock: 2, product: 'K2' },
      }),
      { status: 409 },
    );
  await assert.rejects(
    request('/api/orders'),
    (error) =>
      error instanceof ApiError &&
      error.status === 409 &&
      error.message === 'Insufficient stock.' &&
      error.code === 'insufficient_stock' &&
      error.params.stock === 2,
  );
});

test('validation errors hide raw server validation details', async () => {
  globalThis.fetch = async () =>
    new Response(JSON.stringify({ detail: [{ input: 'private value' }] }), { status: 422 });
  await assert.rejects(
    request('/api/auth/register'),
    (error) =>
      error.status === 422 && error.message === 'Please check the information you entered.',
  );
});

test('non-JSON server failures produce a useful retry message', async () => {
  globalThis.fetch = async () => new Response('upstream stack trace', { status: 503 });
  await assert.rejects(
    request('/api/products'),
    (error) =>
      error.status === 503 &&
      !error.message.includes('stack trace') &&
      error.message.includes('try again'),
  );
});

test('network failures give a connection message', async () => {
  globalThis.fetch = async () => {
    throw new TypeError('fetch failed');
  };
  await assert.rejects(
    request('/api/products'),
    (error) => error.status === 0 && error.message.includes('connection'),
  );
});

test('timeouts give a retry message', async () => {
  globalThis.fetch = async () => {
    throw new DOMException('timed out', 'TimeoutError');
  };
  await assert.rejects(
    request('/api/products'),
    (error) => error.status === 0 && error.message.includes('longer than expected'),
  );
});

test('aborted navigation remains an abort rather than a visible connection error', async () => {
  const controller = new AbortController();
  controller.abort();
  globalThis.fetch = async (_, options) => {
    assert.equal(options.signal.aborted, true);
    throw new DOMException('navigation changed', 'AbortError');
  };
  await assert.rejects(request('/api/products', { signal: controller.signal }), {
    name: 'AbortError',
  });
});
