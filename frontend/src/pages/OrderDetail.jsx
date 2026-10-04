import { errorMessage, locale } from '../i18n';
import { useTranslation } from 'react-i18next';
import { Link, useLocation, useParams } from 'react-router-dom';
import { getOrder } from '../api/orders';
import OrderSummary from '../components/OrderSummary';
import { ErrorState, LoadingState } from '../components/States';
import { useAuth } from '../context/auth-context';
import useResource from '../hooks/useResource';
import { formatPrice } from '../utils/format';
export default function OrderDetail() {
  const { t } = useTranslation();
  const { id } = useParams();
  const { apiRequest, user } = useAuth();
  const location = useLocation();
  const {
    data: order,
    error,
    loading,
    retry,
  } = useResource((signal) => getOrder(apiRequest, id, signal), `${user.id}-${id}`);
  if (loading)
    return (
      <div className="container shopping-page">
        <LoadingState label={t('ui.loading_your_order')} />
      </div>
    );
  if (error)
    return (
      <div className="container shopping-page">
        <div className="state-block" role="alert">
          <h1>
            {error.status === 404 ? t('ui.order_not_found') : t('ui.unable_to_load_your_order')}
          </h1>
          <p>{errorMessage(error)}</p>
          {error.status !== 404 && (
            <button className="button button-primary" onClick={retry}>
              {t('ui.try_again')}
            </button>
          )}
          <Link className="text-link" to="/orders">
            {t('ui.back_to_your_orders')}
          </Link>
        </div>
      </div>
    );
  return (
    <section className="container shopping-page">
      {location.state?.placed && (
        <div className="order-confirmation" role="status">
          <strong>{t('ui.thank_you_your_demo_order_is_placed')}</strong>
          <p>{t('ui.no_payment_has_been_collected_you_can_follow_its_status_here')}</p>
        </div>
      )}
      <p className="eyebrow">{t('ui.order_details')}</p>
      <h1>
        {t('ui.order_value', {
          value1: order.id,
        })}
      </h1>
      <p className="shopping-subtitle">
        {t('ui.placed_value', {
          value1: new Date(order.created_at).toLocaleDateString(locale()),
        })}
        <span className={`order-status status-${order.status}`}>{t(`status.${order.status}`)}</span>
      </p>
      <div className="shopping-layout">
        <div>
          <h2>{t('ui.items_ordered')}</h2>
          <div className="order-items">
            {order.items.map((item) => (
              <article key={item.id}>
                <div>
                  <h3>{item.product_name}</h3>
                  <p>
                    {t('ui.value_each_quantity_value', {
                      value1: formatPrice(item.unit_price),
                      value2: item.quantity,
                    })}
                  </p>
                </div>
                <strong>{formatPrice(item.subtotal)}</strong>
              </article>
            ))}
          </div>
          <section className="shipping-address">
            <h2>{t('ui.shipping_address')}</h2>
            <address>
              {order.shipping_name}
              <br />
              {order.shipping_address}
              <br />
              {order.shipping_city}, {order.shipping_postal_code}
              <br />
              {order.shipping_country}
            </address>
          </section>
          <Link className="text-link" to="/orders">
            {t('ui.all_your_orders')}
          </Link>
        </div>
        <OrderSummary summary={order} />
      </div>
    </section>
  );
}
