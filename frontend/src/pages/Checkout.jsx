import { errorMessage } from '../i18n';
import { useTranslation } from 'react-i18next';
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { createOrder } from '../api/orders';
import OrderSummary from '../components/OrderSummary';
import ShoppingEmpty from '../components/ShoppingEmpty';
import { ErrorState, LoadingState } from '../components/States';
import { useAuth } from '../context/auth-context';
import { useCart } from '../context/cart-context';
import { formatPrice } from '../utils/format';
export default function Checkout() {
  const { t } = useTranslation();
  const { user, apiRequest } = useAuth();
  const { cart, loading, error, refresh } = useCart();
  const navigate = useNavigate();
  const [key] = useState(() => crypto.randomUUID());
  useEffect(() => refresh(), [refresh]);
  const [busy, setBusy] = useState(false);
  const [submitError, setSubmitError] = useState('');
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setSubmitError('');
    const shipping = {
      ...Object.fromEntries(new FormData(event.currentTarget)),
      checkout_key: key,
    };
    try {
      const order = await createOrder(apiRequest, shipping);
      refresh();
      navigate(`/orders/${order.id}`, {
        replace: true,
        state: {
          placed: true,
        },
      });
    } catch (err) {
      setSubmitError(err);
      setBusy(false);
    }
  }
  return (
    <section className="container shopping-page">
      <p className="eyebrow">{t('ui.one_last_step')}</p>
      <h1>{t('ui.checkout')}</h1>
      <p className="shopping-subtitle">
        {t('ui.this_is_a_demo_checkout_no_card_details_or_payment_are_required')}
      </p>
      {loading ? (
        <LoadingState label={t('ui.checking_your_cart')} />
      ) : error ? (
        <ErrorState error={error} onRetry={refresh} />
      ) : !cart?.items.length ? (
        <ShoppingEmpty title={t('ui.there_s_nothing_to_check_out')}>
          {t('ui.add_a_product_to_your_cart_to_get_started')}
        </ShoppingEmpty>
      ) : (
        <div className="shopping-layout">
          <div className="checkout-content">
            <h2>{t('ui.shipping_information')}</h2>
            <form id="checkout-form" className="account-form" onSubmit={submit}>
              <label>
                {t('ui.full_name')}
                <input
                  name="shipping_name"
                  autoComplete="name"
                  defaultValue={
                    [user.first_name, user.last_name].filter(Boolean).join(' ') || user.username
                  }
                  required
                  minLength={2}
                  maxLength={200}
                />
              </label>
              <label>
                {t('ui.street_address')}
                <input
                  name="shipping_address"
                  autoComplete="street-address"
                  required
                  minLength={5}
                  maxLength={300}
                />
              </label>
              <div className="form-row">
                <label>
                  {t('ui.city')}
                  <input
                    name="shipping_city"
                    autoComplete="address-level2"
                    required
                    minLength={2}
                    maxLength={100}
                  />
                </label>
                <label>
                  {t('ui.postal_code')}
                  <input
                    name="shipping_postal_code"
                    autoComplete="postal-code"
                    required
                    minLength={2}
                    maxLength={20}
                  />
                </label>
              </div>
              <label>
                {t('ui.country')}
                <input
                  name="shipping_country"
                  autoComplete="country-name"
                  required
                  minLength={2}
                  maxLength={100}
                />
              </label>
              {submitError && (
                <p role="alert" className="form-error">
                  {errorMessage(submitError)} <Link to="/cart">{t('ui.review_your_cart')}</Link>
                </p>
              )}
            </form>
            <h2 className="checkout-review-title">{t('ui.review_your_items')}</h2>
            <ul className="checkout-review">
              {cart.items.map((item) => (
                <li key={item.id}>
                  <span>
                    {item.product.name} <small>× {item.quantity}</small>
                  </span>
                  <strong>{formatPrice(item.subtotal)}</strong>
                </li>
              ))}
            </ul>
            <Link className="text-link" to="/cart">
              {t('ui.back_to_cart')}
            </Link>
          </div>
          <OrderSummary summary={cart}>
            {!cart.items.every((item) => item.available) && (
              <p className="stock-warning">
                {t('ui.availability_changed_review_your_cart_before_placing_your_order')}
              </p>
            )}
            <button
              className="button button-primary"
              type="submit"
              form="checkout-form"
              disabled={busy || !cart.items.every((item) => item.available)}
            >
              {busy ? t('ui.placing_your_order') : t('ui.place_demo_order')}
            </button>
            <p className="checkout-explanation">
              {t(
                'ui.we_ll_reserve_the_items_and_create_an_order_in_your_account_no_money_will_be_charged',
              )}
            </p>
          </OrderSummary>
        </div>
      )}
    </section>
  );
}
