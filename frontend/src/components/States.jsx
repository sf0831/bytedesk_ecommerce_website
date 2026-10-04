import { errorMessage } from '../i18n';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
export function LoadingState({ label, cards = false }) {
  const { t } = useTranslation();
  label = label || t('extra.loading');
  return cards ? (
    <div className="product-grid skeleton-grid" role="status" aria-label={label}>
      {Array.from(
        {
          length: 4,
        },
        (_, index) => (
          <div key={index} className="skeleton-card">
            <div />
            <span />
            <span />
          </div>
        ),
      )}
      <span className="sr-only">{label}</span>
    </div>
  ) : (
    <div className="state-block" role="status">
      <span className="loading-dot" />
      {label}
    </div>
  );
}
export function ErrorState({ error, onRetry }) {
  const { t } = useTranslation();
  return (
    <div className="state-block error-state" role="alert">
      <h2>
        {error?.status === 404
          ? t('ui.we_couldn_t_find_that_page')
          : t('ui.something_interrupted_your_visit')}
      </h2>
      <p>{errorMessage(error) || t('ui.please_try_again_in_a_moment')}</p>
      <div className="state-actions">
        {onRetry && error?.status !== 404 && (
          <button className="button" onClick={onRetry}>
            {t('ui.try_again')}
          </button>
        )}
        <Link className="text-link" to="/products">
          {t('ui.browse_the_catalog')}
        </Link>
      </div>
    </div>
  );
}
export function EmptyState({ onReset }) {
  const { t } = useTranslation();
  return (
    <div className="state-block">
      <h2>{t('ui.no_products_found')}</h2>
      <p>{t('ui.try_another_search_or_clear_a_filter_to_see_more_of_the_collection')}</p>
      <button className="button button-outline" onClick={onReset}>
        {t('ui.clear_all_filters')}
      </button>
    </div>
  );
}
