import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
export default function ShoppingEmpty({ title, children }) {
  const { t } = useTranslation();
  return (
    <div className="shopping-empty">
      <h2>{title}</h2>
      <p>{children}</p>
      <Link className="button button-primary" to="/products">
        {t('ui.explore_the_collection_2')}
      </Link>
    </div>
  );
}
