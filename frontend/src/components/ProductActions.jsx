import { errorMessage } from '../i18n';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { addWishlistItem } from '../api/wishlist';
import { useAuth } from '../context/auth-context';
import { useCart } from '../context/cart-context';
export default function ProductActions({ product }) {
  const { t } = useTranslation();
  const { user, apiRequest } = useAuth();
  const { add } = useCart();
  const location = useLocation();
  const navigate = useNavigate();
  const [quantity, setQuantity] = useState(1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  async function act(wishlist) {
    if (!user) {
      navigate('/login', {
        state: {
          from: location.pathname,
        },
      });
      return;
    }
    setBusy(true);
    setError('');
    setMessage('');
    try {
      if (wishlist) {
        await addWishlistItem(apiRequest, product.id);
        setMessage('wishlist');
      } else {
        await add(product.id, quantity);
        setMessage('cart');
      }
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="product-actions">
      <div className="purchase-row">
        <label>
          {t('ui.quantity')}
          <input
            type="number"
            value={quantity}
            min="1"
            max={Math.min(product.stock_quantity, 10000)}
            disabled={busy || !product.in_stock}
            onChange={(event) => setQuantity(Number(event.target.value))}
          />
        </label>
        <button
          className="button button-primary"
          disabled={
            busy ||
            !product.in_stock ||
            !Number.isInteger(quantity) ||
            quantity < 1 ||
            quantity > product.stock_quantity
          }
          onClick={() => act(false)}
        >
          {busy
            ? t('ui.please_wait')
            : product.in_stock
              ? t('ui.add_to_cart')
              : t('ui.out_of_stock')}
        </button>
      </div>
      <button className="text-button save-product" disabled={busy} onClick={() => act(true)}>
        {t('ui.save_to_wishlist')}
      </button>
      {!user && (
        <p className="shopping-hint">{t('ui.sign_in_to_add_items_to_your_cart_or_wishlist')}</p>
      )}
      {error && (
        <p className="form-error" role="alert">
          {errorMessage(error)}
        </p>
      )}
      {message && (
        <p className="shopping-feedback" role="status">
          {t(`feedback.${message}`)}{' '}
          <Link to={message === 'wishlist' ? '/wishlist' : '/cart'}>
            {t('ui.view_value', {
              value1: message === 'wishlist' ? t('ui.wishlist_2') : t('ui.cart'),
            })}
          </Link>
        </p>
      )}
    </div>
  );
}
