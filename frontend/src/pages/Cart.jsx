import { errorMessage } from '../i18n';
import { useTranslation } from 'react-i18next';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import CartItem from '../components/CartItem';
import OrderSummary from '../components/OrderSummary';
import ShoppingEmpty from '../components/ShoppingEmpty';
import { ErrorState, LoadingState } from '../components/States';
import { useCart } from '../context/cart-context';
export default function Cart() {
  const { t } = useTranslation();
  const { cart, loading, error, refresh, change, remove } = useCart();
  useEffect(() => refresh(), [refresh]);
  const [busy, setBusy] = useState(false);
  const [mutationError, setMutationError] = useState('');
  async function mutate(action) {
    setBusy(true);
    setMutationError('');
    try {
      await action();
    } catch (err) {
      setMutationError(err);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="container shopping-page">
      <p className="eyebrow">{t('ui.your_next_workspace_upgrade')}</p>
      <h1>{t('ui.your_cart')}</h1>
      {loading ? (
        <LoadingState label={t('ui.loading_your_cart')} />
      ) : error ? (
        <ErrorState error={error} onRetry={refresh} />
      ) : !cart?.items.length ? (
        <ShoppingEmpty title={t('ui.your_cart_is_empty')}>
          {t('ui.find_the_tools_that_make_your_workday_better')}
        </ShoppingEmpty>
      ) : (
        <>
          <p className="shopping-subtitle">{t('cart.count', { count: cart.item_count })}</p>
          {mutationError && (
            <p role="alert" className="form-error">
              {errorMessage(mutationError)}{' '}
              <button className="text-button" onClick={refresh}>
                {t('ui.refresh_cart')}
              </button>
            </p>
          )}
          <div className="shopping-layout">
            <div>
              {cart.items.map((item) => (
                <CartItem
                  key={item.id}
                  item={item}
                  busy={busy}
                  onChange={(quantity) => mutate(() => change(item.id, quantity))}
                  onRemove={() => mutate(() => remove(item.id))}
                />
              ))}
              <Link className="text-link continue-shopping" to="/products">
                {t('ui.continue_shopping')}
              </Link>
            </div>
            <OrderSummary summary={cart}>
              {cart.items.every((item) => item.available) ? (
                <Link className="button button-primary" to="/checkout">
                  {t('ui.continue_to_checkout')}
                </Link>
              ) : (
                <p className="stock-warning">
                  {t('ui.review_unavailable_items_before_checking_out')}
                </p>
              )}
            </OrderSummary>
          </div>
        </>
      )}
    </section>
  );
}
