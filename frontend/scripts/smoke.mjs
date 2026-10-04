import assert from 'node:assert/strict';

const base = process.env.STOREFRONT_URL || 'http://127.0.0.1:5173';
async function json(path) {
  const response = await fetch(`${base}${path}`);
  assert.equal(response.status, 200, path);
  return response.json();
}
const health = await json('/api/health');
assert.equal(health.database, 'connected');
const products = await json('/api/products?page_size=1');
assert.ok(products.total > 0, 'Seed the catalog before verification');
assert.equal(products.items.length, 1);
assert.equal(typeof products.items[0].price, 'string');
assert.ok((await json('/api/categories')).length > 0);
assert.ok((await json('/api/brands')).length > 0);
for (const path of [
  '/',
  '/products',
  `/products/${products.items[0].slug}`,
  '/login',
  '/register',
  '/profile',
  '/cart',
  '/wishlist',
  '/checkout',
  '/orders',
  '/orders/1',
]) {
  const response = await fetch(`${base}${path}`);
  assert.equal(response.status, 200, path);
  assert.match(await response.text(), /id="root"/, `SPA route: ${path}`);
}
const detail = await json(`/api/products/${products.items[0].slug}`);
assert.ok(Array.isArray(detail.specifications));
assert.ok(Array.isArray(detail.images));
assert.equal((await fetch(`${base}/api/users/me`)).status, 401, 'Profile requires a bearer token');
for (const path of ['/api/cart', '/api/wishlist', '/api/orders']) {
  assert.equal((await fetch(`${base}${path}`)).status, 401, `Protected shopping API: ${path}`);
}
const reviews = await json(`/api/reviews?product_id=${products.items[0].id}`);
assert.ok(Array.isArray(reviews.items));
assert.equal(typeof reviews.total, 'number');
assert.equal(
  (await fetch(`${base}/api/reviews/me?product_id=${products.items[0].id}`)).status,
  401,
);
console.log(
  'Storefront HTTP checks passed: routes, FastAPI proxy, catalog, taxonomies and detail.',
);
