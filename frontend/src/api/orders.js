export const getOrders = (client, page, signal) =>
  client(`/api/orders?page=${page}&page_size=10`, { signal });
export const getOrder = (client, id, signal) => client(`/api/orders/${id}`, { signal });
export const createOrder = (client, shipping) =>
  client('/api/orders', { method: 'POST', body: shipping });
