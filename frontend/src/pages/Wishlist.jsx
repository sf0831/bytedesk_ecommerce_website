import { errorMessage } from '../i18n';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { getWishlist, moveWishlistItem, removeWishlistItem } from '../api/wishlist';
import ProductImage from '../components/ProductImage';
import ShoppingEmpty from '../components/ShoppingEmpty';
import { ErrorState, LoadingState } from '../components/States';
import { useAuth } from '../context/auth-context';
import { useCart } from '../context/cart-context';
import useResource from '../hooks/useResource';
import { formatPrice } from '../utils/format';
export default function Wishlist() {
  const { t } = useTranslation();
  const { apiRequest, user } = useAuth();
  const { acceptCart } = useCart();
  const { data, error, loading, retry } = useResource(
    (signal) => getWishlist(apiRequest, signal),
    user.id,
  );
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [mutationError, setMutationError] = useState('');
  async function change(productId, move) {
    setBusy(true);
    setMutationError('');
    setMessage('');
    try {
      if (move) {
        acceptCart(await moveWishlistItem(apiRequest, productId));
        setMessage('moved');
      } else {
        await removeWishlistItem(apiRequest, productId);
        setMessage('removed');
      }
      retry();
    } catch (err) {
      setMutationError(err);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="container shopping-page">
      <p className="eyebrow">{t('ui.keep_the_good_finds')}</p>
      <h1>{t('ui.your_wishlist')}</h1>
      <p className="shopping-subtitle">
        {t('ui.save_it_for_later_make_room_for_it_when_you_re_ready')}
      </p>
      {mutationError && (
        <p className="form-error" role="alert">
          {errorMessage(mutationError)}
        </p>
      )}
      {message && (
        <p className="shopping-feedback" role="status">
          {t(`feedback.${message}`)} <Link to="/cart">{t('ui.view_cart')}</Link>
        </p>
      )}
      {loading ? (
        <LoadingState label={t('ui.loading_your_wishlist')} />
      ) : error ? (
        <ErrorState error={error} onRetry={retry} />
      ) : !data?.items.length ? (
        <ShoppingEmpty title={t('ui.your_wishlist_is_empty')}>
          {t('ui.save_products_from_their_detail_page_to_keep_them_here')}
        </ShoppingEmpty>
      ) : (
        <div className="wishlist-grid">
          {data.items.map(({ product, available }) => (
            <article className="wishlist-card" key={product.id}>
              <Link className="wishlist-image" to={`/products/${product.slug}`}>
                <ProductImage product={product} />
              </Link>
              <p className="product-brand">{product.brand.name}</p>
              <h2>
                <Link to={`/products/${product.slug}`}>{product.name}</Link>
              </h2>
              <strong>{formatPrice(product.price)}</strong>
              <p className={available ? 'wishlist-stock' : 'stock-warning'}>
                {available ? t('ui.in_stock') : t('ui.currently_unavailable')}
              </p>
              <button
                className="button button-primary"
                disabled={busy || !available}
                onClick={() => change(product.id, true)}
              >
                {t('ui.move_to_cart')}
              </button>
              <button
                className="text-button"
                disabled={busy}
                onClick={() => change(product.id, false)}
              >
                {t('ui.remove')}
                <span className="sr-only">{product.name}</span>
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
