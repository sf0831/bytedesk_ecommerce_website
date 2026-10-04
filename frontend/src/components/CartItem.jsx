import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import ProductImage from './ProductImage';
import { formatPrice } from '../utils/format';
export default function CartItem({ item, busy, onChange, onRemove }) {
  const { t } = useTranslation();
  return (
    <article className="cart-line">
      <Link className="cart-line-image" to={`/products/${item.product.slug}`}>
        <ProductImage product={item.product} />
      </Link>
      <div className="cart-line-copy">
        <p className="product-brand">{item.product.brand.name}</p>
        <h2>
          <Link to={`/products/${item.product.slug}`}>{item.product.name}</Link>
        </h2>
        <p>
          {t('ui.value_each', {
            value1: formatPrice(item.product.price),
          })}
        </p>
        {!item.available && (
          <p className="stock-warning">
            {t('ui.availability_changed_reduce_the_quantity_or_remove_this_item_before_checkout')}
          </p>
        )}
        <button className="text-button" disabled={busy} onClick={onRemove}>
          {t('ui.remove')}
          <span className="sr-only">{item.product.name}</span>
        </button>
      </div>
      <div className="cart-line-controls">
        <div
          className="quantity-control"
          aria-label={t('ui.quantity_for_value', {
            value1: item.product.name,
          })}
        >
          <button
            disabled={busy || item.quantity <= 1 || item.product.stock_quantity === 0}
            aria-label={t('ui.decrease_value_quantity', {
              value1: item.product.name,
            })}
            onClick={() =>
              onChange(Math.min(item.quantity - 1, Math.max(1, item.product.stock_quantity)))
            }
          >
            −
          </button>
          <span aria-live="polite">{item.quantity}</span>
          <button
            disabled={busy || item.quantity >= item.product.stock_quantity}
            aria-label={t('ui.increase_value_quantity', {
              value1: item.product.name,
            })}
            onClick={() => onChange(item.quantity + 1)}
          >
            +
          </button>
        </div>
        <strong>{formatPrice(item.subtotal)}</strong>
      </div>
    </article>
  );
}
