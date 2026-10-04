import { useTranslation } from 'react-i18next';
import { formatPrice } from '../utils/format';
export default function OrderSummary({ summary, children }) {
  const { t } = useTranslation();
  return (
    <aside className="order-summary">
      <h2>{t('ui.order_summary')}</h2>
      <dl>
        <div>
          <dt>{t('ui.subtotal')}</dt>
          <dd>{formatPrice(summary.subtotal)}</dd>
        </div>
        <div>
          <dt>{t('ui.shipping')}</dt>
          <dd>{Number(summary.shipping) === 0 ? t('ui.free') : formatPrice(summary.shipping)}</dd>
        </div>
        <div className="summary-total">
          <dt>{t('ui.total')}</dt>
          <dd>{formatPrice(summary.total)}</dd>
        </div>
      </dl>
      {summary.free_shipping_threshold && (
        <p className="shipping-note">
          {t('ui.free_shipping_on_orders_of_value_or_more', {
            value1: formatPrice(summary.free_shipping_threshold),
          })}
        </p>
      )}
      {children}
      <p className="demo-note">{t('ui.demo_store_no_payment_is_collected')}</p>
    </aside>
  );
}
