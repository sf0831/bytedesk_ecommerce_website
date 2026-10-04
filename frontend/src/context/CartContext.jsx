import { useCallback, useEffect, useState } from 'react';
import { addCartItem, getCart, removeCartItem, setCartQuantity } from '../api/cart';
import { useAuth } from './auth-context';
import { CartContext } from './cart-context';
export function CartProvider({ children }) {
  const { user, apiRequest } = useAuth();
  const userId = user?.id;
  const [state, setState] = useState({ userId: null, cart: null, loading: false, error: null });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    if (!userId) {
      setState({ userId: null, cart: null, loading: false, error: null });
      return;
    }
    const controller = new AbortController();
    setState({ userId, cart: null, loading: true, error: null });
    getCart(apiRequest, controller.signal)
      .then((cart) => {
        if (!controller.signal.aborted) setState({ userId, cart, loading: false, error: null });
      })
      .catch((error) => {
        if (!controller.signal.aborted) setState({ userId, cart: null, loading: false, error });
      });
    return () => controller.abort();
  }, [userId, apiRequest, attempt]);
  const acceptCart = useCallback(
    (cart) => setState({ userId, cart, loading: false, error: null }),
    [userId],
  );
  const refresh = useCallback(() => setAttempt((value) => value + 1), []);
  async function add(productId, quantity) {
    const cart = await addCartItem(apiRequest, productId, quantity);
    acceptCart(cart);
    return cart;
  }
  async function change(itemId, quantity) {
    acceptCart(await setCartQuantity(apiRequest, itemId, quantity));
  }
  async function remove(itemId) {
    acceptCart(await removeCartItem(apiRequest, itemId));
  }
  const current =
    state.userId === userId ? state : { cart: null, loading: Boolean(userId), error: null };
  return (
    <CartContext.Provider value={{ ...current, add, change, remove, refresh, acceptCart }}>
      {children}
    </CartContext.Provider>
  );
}
