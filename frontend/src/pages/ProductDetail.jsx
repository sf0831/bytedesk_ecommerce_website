import { language, categoryName } from '../i18n';
import { useTranslation } from 'react-i18next';
import ReviewList from '../components/ReviewList';
import ProductActions from '../components/ProductActions';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getProduct } from '../api/products';
import Icon from '../components/Icon';
import ProductImage from '../components/ProductImage';
import { ErrorState, LoadingState } from '../components/States';
import useResource from '../hooks/useResource';
import { formatPrice } from '../utils/format';
export default function ProductDetail() {
  const { t } = useTranslation();
  const { slug } = useParams();
  const {
    data: product,
    error,
    loading,
    retry,
  } = useResource((signal) => getProduct(slug, signal), `${slug}-${language()}`, slug);
  const [selected, setSelected] = useState(0);
  useEffect(() => setSelected(0), [slug]);
  if (loading)
    return (
      <div className="container detail-page">
        <LoadingState label={t('ui.loading_product_details')} />
      </div>
    );
  if (error)
    return (
      <div className="container detail-page">
        <ErrorState error={error} onRetry={retry} />
      </div>
    );
  return (
    <div className="container detail-page">
      <nav className="breadcrumbs" aria-label={t('ui.breadcrumb')}>
        <Link to="/">{t('ui.home')}</Link>
        <span>/</span>
        <Link to="/products">{t('ui.shop')}</Link>
        <span>/</span>
        <Link to={`/products?category=${product.category.slug}`}>
          {categoryName(product.category)}
        </Link>
      </nav>
      <div className="detail-layout">
        <div className="product-gallery">
          <div className="detail-image">
            <ProductImage product={product} image={product.images[selected]} eager />
          </div>
          {product.images.length > 1 && (
            <div className="gallery-thumbnails">
              {product.images.map((image, index) => (
                <button
                  className={selected === index ? 'selected' : ''}
                  key={image.id}
                  onClick={() => setSelected(index)}
                  aria-label={t('ui.view_image_value', {
                    value1: index + 1,
                  })}
                  aria-pressed={selected === index}
                >
                  <ProductImage product={product} image={image} />
                </button>
              ))}
            </div>
          )}
          {product.images.length === 0 && (
            <p className="image-note">{t('ui.illustrative_product_image')}</p>
          )}
        </div>
        <div className="detail-copy">
          <Link className="product-brand" to={`/products?brand=${product.brand.slug}`}>
            {product.brand.name}
          </Link>
          <h1>{product.name}</h1>
          <span className="detail-sku">
            {t('ui.sku_value', {
              value1: product.sku,
            })}
          </span>
          <p className="detail-price">{formatPrice(product.price)}</p>
          <p className={`stock-label ${product.in_stock ? '' : 'out-of-stock'}`}>
            <Icon name={product.in_stock ? 'check' : 'close'} size={16} />
            {product.in_stock
              ? t('ui.in_stock_value_available', {
                  value1: product.stock_quantity,
                })
              : t('ui.currently_out_of_stock')}
          </p>
          <p className="detail-description">{product.description}</p>
          <ProductActions key={product.id} product={product} />
          <div className="detail-facts">
            <span>{t('ui.category')}</span>
            <Link to={`/products?category=${product.category.slug}`}>
              {categoryName(product.category)}
            </Link>
            <span>{t('ui.brand')}</span>
            <Link to={`/products?brand=${product.brand.slug}`}>{product.brand.name}</Link>
          </div>
          <Link
            className="button button-outline"
            to={`/products?category=${product.category.slug}`}
          >
            {t('ui.explore_more_value', {
              value1: categoryName(product.category),
            })}
            <Icon name="arrow" size={17} />
          </Link>
        </div>
      </div>
      <section className="specifications">
        <div>
          <span className="eyebrow">{t('ui.the_details_that_matter')}</span>
          <h2>{t('ui.specifications')}</h2>
          <p>{t('ui.a_closer_look_at_what_s_on_your_desk')}</p>
        </div>
        {product.specifications.length ? (
          <dl>
            {product.specifications.map((specification) => (
              <div key={specification.key}>
                <dt>{specification.key}</dt>
                <dd>{specification.value}</dd>
              </div>
            ))}
          </dl>
        ) : (
          <p>{t('ui.specifications_haven_t_been_added_for_this_product_yet')}</p>
        )}
      </section>
      <ReviewList key={product.id} product={product} />
    </div>
  );
}
