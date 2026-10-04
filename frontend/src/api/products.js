import { language } from '../i18n';
import { request } from './client';

export function getProducts(filters = {}, signal) {
  const params = new URLSearchParams({ lang: language() });
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== '' && value !== undefined && value !== null) params.set(key, value);
  });
  return request(`/api/products?${params}`, { signal });
}

export function getProduct(slug, signal) {
  return request(`/api/products/${encodeURIComponent(slug)}?lang=${language()}`, { signal });
}

export function getCategories(signal) {
  return request(`/api/categories?lang=${language()}`, { signal });
}

export function getBrands(signal) {
  return request('/api/brands', { signal });
}
