import { categoryName } from '../i18n';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { formatPrice } from '../utils/format';
import Icon from './Icon';
import ProductImage from './ProductImage';
export default function ProductCard({ product, illustrationsOnly = false }) {
  const { t } = useTranslation();
  return (
    <article className="product-card">
      <Link
        className={`product-card-image${!illustrationsOnly && product.images?.length ? ' has-photo' : ''}`}
        to={`/products/${product.slug}`}
        tabIndex={-1}
        aria-hidden="true"
      >
        <ProductImage product={product} illustrationsOnly={illustrationsOnly} />
        {!product.in_stock && <span className="stock-badge">{t('ui.out_of_stock')}</span>}
      </Link>
      <div className="product-card-copy">
        <span className="product-brand">{product.brand.name}</span>
        <h3>
          <Link to={`/products/${product.slug}`}>{product.name}</Link>
        </h3>
        <p className="product-category">
          {categoryName(product.category)}
          {!product.in_stock && <span className="sr-only">{t('ui.out_of_stock_2')}</span>}
        </p>
        <div className="product-card-bottom">
          <span className="price">{formatPrice(product.price)}</span>
          <Link
            className="product-view"
            to={`/products/${product.slug}`}
            aria-label={t('ui.view_value_2', {
              value1: product.name,
            })}
          >
            <Icon name="arrow" size={18} />
          </Link>
        </div>
      </div>
    </article>
  );
}
