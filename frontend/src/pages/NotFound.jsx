import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
export default function NotFound() {
  const { t } = useTranslation();
  return (
    <div className="container state-block not-found">
      <span className="eyebrow">404</span>
      <h1>{t('ui.this_page_has_moved_off_the_desk')}</h1>
      <p>{t('ui.let_s_get_you_back_to_the_collection')}</p>
      <Link className="button" to="/products">
        {t('ui.browse_products')}
      </Link>
    </div>
  );
}
