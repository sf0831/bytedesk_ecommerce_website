export const getCart = (client, signal) => client('/api/cart', { signal });
export const addCartItem = (client, productId, quantity = 1) =>
  client('/api/cart/items', { method: 'POST', body: { product_id: productId, quantity } });
export const setCartQuantity = (client, itemId, quantity) =>
  client(`/api/cart/items/${itemId}`, { method: 'PATCH', body: { quantity } });
export const removeCartItem = (client, itemId) =>
  client(`/api/cart/items/${itemId}`, { method: 'DELETE' });
