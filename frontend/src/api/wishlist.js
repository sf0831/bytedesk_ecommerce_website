export const getWishlist = (client, signal) => client('/api/wishlist', { signal });
export const addWishlistItem = (client, productId) =>
  client('/api/wishlist/items', { method: 'POST', body: { product_id: productId } });
export const removeWishlistItem = (client, productId) =>
  client(`/api/wishlist/items/${productId}`, { method: 'DELETE' });
export const moveWishlistItem = (client, productId) =>
  client(`/api/wishlist/items/${productId}/move-to-cart`, { method: 'POST' });
