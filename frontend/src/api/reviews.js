import { request } from './client';
export const getReviews = (productId, page, signal) =>
  request(`/api/reviews?product_id=${productId}&page=${page}&page_size=5`, { signal });
export const getOwnReview = (client, productId, signal) =>
  client(`/api/reviews/me?product_id=${productId}`, { signal });
export const createReview = (client, values) =>
  client('/api/reviews', { method: 'POST', body: values });
