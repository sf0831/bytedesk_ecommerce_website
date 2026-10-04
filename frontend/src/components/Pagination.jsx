import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
export default function Pagination({ page, totalPages, params }) {
  const { t } = useTranslation();
  if (totalPages < 2) return null;
  function url(target) {
    const next = new URLSearchParams(params);
    next.set('page', target);
    return `/products?${next}`;
  }
  const current = Math.min(page, totalPages);
  const start = Math.max(1, Math.min(current - 2, totalPages - 4));
  const pages = Array.from(
    {
      length: Math.min(totalPages, 5),
    },
    (_, index) => start + index,
  );
  return (
    <nav className="pagination" aria-label={t('ui.product_pagination')}>
      {page > 1 ? (
        <Link to={url(page - 1)} aria-label={t('ui.previous_page')}>
          ←
        </Link>
      ) : (
        <span className="disabled" aria-hidden="true">
          ←
        </span>
      )}
      {pages.map((number) => (
        <Link key={number} to={url(number)} aria-current={number === page ? 'page' : undefined}>
          {number}
        </Link>
      ))}
      {page < totalPages ? (
        <Link to={url(page + 1)} aria-label={t('ui.next_page')}>
          →
        </Link>
      ) : (
        <span className="disabled" aria-hidden="true">
          →
        </span>
      )}
    </nav>
  );
}
