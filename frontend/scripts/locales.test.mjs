import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import i18next from 'i18next';
const en = JSON.parse(await readFile(new URL('../src/locales/en.json', import.meta.url)));
const tr = JSON.parse(await readFile(new URL('../src/locales/tr.json', import.meta.url)));
const flatten = (obj, prefix = '') =>
  Object.fromEntries(
    Object.entries(obj).flatMap(([key, value]) =>
      typeof value === 'object'
        ? Object.entries(flatten(value, `${prefix}${key}.`))
        : [[`${prefix}${key}`, value]],
    ),
  );
const english = flatten(en),
  turkish = flatten(tr);
const placeholders = (text) =>
  [...text.matchAll(/{{\s*([^}]+)\s*}}/g)].map((match) => match[1]).sort();

test('English and Turkish catalogs have matching keys and interpolations', () => {
  assert.deepEqual(Object.keys(turkish).sort(), Object.keys(english).sort());
  for (const key of Object.keys(english)) {
    assert.ok(turkish[key].trim(), `Empty Turkish message: ${key}`);
    assert.deepEqual(placeholders(turkish[key]), placeholders(english[key]), key);
  }
});
test('Every literal translation key used by the storefront exists', async () => {
  for (const folder of ['pages', 'components', '']) {
    const directory = new URL(`../src/${folder}/`, import.meta.url);
    for (const name of await readdir(directory)) {
      if (!name.endsWith('.jsx')) continue;
      const source = await readFile(new URL(name, directory), 'utf8');
      for (const match of source.matchAll(/\bt\(['"]([^'"]+)['"]/g)) {
        assert.ok(english[match[1]] || english[`${match[1]}_one`], `${name}: ${match[1]}`);
      }
    }
  }
});
test('Whole-message plurals work in both languages and missing Turkish falls back', async () => {
  const instance = i18next.createInstance();
  await instance.init({
    lng: 'en',
    fallbackLng: 'en',
    resources: { en: { translation: en }, tr: { translation: tr } },
  });
  assert.equal(instance.t('catalog.productCount', { count: 1 }), '1 product');
  assert.equal(instance.t('catalog.productCount', { count: 2 }), '2 products');
  await instance.changeLanguage('tr');
  assert.equal(instance.t('catalog.productCount', { count: 1 }), '1 ürün');
  assert.equal(instance.t('catalog.productCount', { count: 2 }), '2 ürün');
  assert.equal(
    instance.t('errors.insufficient_stock', { stock: 3, product: 'K2' }),
    'K2 için stokta yalnızca 3 adet var.',
  );
  instance.addResource('en', 'translation', 'testFallback', 'English fallback');
  assert.equal(instance.t('testFallback'), 'English fallback');
});
