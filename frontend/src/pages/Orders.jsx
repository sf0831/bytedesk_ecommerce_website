import { locale } from '../i18n';
import { useTranslation } from 'react-i18next';
import { Link, useSearchParams } from 'react-router-dom';
import { getOrders } from '../api/orders';
import ShoppingEmpty from '../components/ShoppingEmpty';
import { ErrorState, LoadingState } from '../components/States';
import { useAuth } from '../context/auth-context';
import useResource from '../hooks/useResource';
import { formatPrice } from '../utils/format';
export default function Orders() {
  const { t } = useTranslation();
  const { apiRequest, user } = useAuth();
  const [params] = useSearchParams();
  const raw = Number(params.get('page') || 1);
  const page = Number.isInteger(raw) && raw > 0 && raw <= 2147483647 ? raw : 1;
  const { data, error, loading, retry } = useResource(
    (signal) => getOrders(apiRequest, page, signal),
    `${user.id}-${page}`,
  );
  return (
    <section className="container shopping-page">
      <p className="eyebrow">{t('ui.your_workspace_journey')}</p>
      <h1>{t('ui.your_orders')}</h1>
      {loading ? (
        <LoadingState label={t('ui.loading_your_orders')} />
      ) : error ? (
        <ErrorState error={error} onRetry={retry} />
      ) : !data?.items.length ? (
        <>
          <ShoppingEmpty title={page > 1 ? t('ui.no_orders_on_this_page') : t('ui.no_orders_yet')}>
            {t('ui.your_demo_orders_will_appear_here_after_checkout')}
          </ShoppingEmpty>
          {page > 1 && (
            <Link className="text-link" to="/orders">
              {t('ui.back_to_the_first_page')}
            </Link>
          )}
        </>
      ) : (
        <>
          <div className="orders-list">
            {data.items.map((order) => (
              <article className="order-row" key={order.id}>
                <div>
                  <h2>
                    <Link to={`/orders/${order.id}`}>
                      {t('ui.order_value', {
                        value1: order.id,
                      })}
                    </Link>
                  </h2>
                  <p>
                    {t('orders.itemCount', {
                      date: new Date(order.created_at).toLocaleDateString(locale(), {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      }),
                      count: order.items.reduce((sum, item) => sum + item.quantity, 0),
                    })}
                  </p>
                </div>
                <span className={`order-status status-${order.status}`}>
                  {t(`status.${order.status}`)}
                </span>
                <strong>{formatPrice(order.total)}</strong>
                <Link className="text-link" to={`/orders/${order.id}`}>
                  {t('ui.view_order')}
                </Link>
              </article>
            ))}
          </div>
          {data.total_pages > 1 && (
            <nav className="pagination" aria-label={t('ui.order_pagination')}>
              {page > 1 && <Link to={`/orders?page=${page - 1}`}>{t('ui.previous')}</Link>}
              <span>
                {t('ui.page_value_of_value', {
                  value1: page,
                  value2: data.total_pages,
                })}
              </span>
              {page < data.total_pages && (
                <Link to={`/orders?page=${page + 1}`}>{t('ui.next')}</Link>
              )}
            </nav>
          )}
        </>
      )}
    </section>
  );
}
