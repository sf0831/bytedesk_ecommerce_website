import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
export default function Footer({ categories }) {
  const { t } = useTranslation();
  return (
    <footer className="site-footer" id="about">
      <div className="container footer-grid">
        <div>
          <Link to="/" className="footer-logo">
            {t('ui.bytedesk')}
          </Link>
          <p>{t('ui.thoughtful_tools_for_the_place_you_do_your_best_work')}</p>
          <span className="footer-small">{t('ui.a_workspace_equipment_portfolio_store')}</span>
        </div>
        <div>
          <h2>{t('ui.find_your_next_upgrade')}</h2>
          <div className="footer-links">
            {categories.map((item) => (
              <Link key={item.id} to={`/products?category=${item.slug}`}>
                {item.name}
              </Link>
            ))}
          </div>
        </div>
        <div>
          <h2>{t('ui.a_straightforward_store')}</h2>
          <p>
            {t(
              'ui.explore_a_sample_catalog_of_familiar_brands_and_practical_equipment_product_illustrat',
            )}
          </p>
          <Link className="footer-browse" to="/products">
            {t('ui.browse_all_products')}
          </Link>
        </div>
      </div>
      <div className="container footer-bottom">
        <span>
          {t('ui.value_bytedesk', {
            value1: new Date().getFullYear(),
          })}
        </span>
        <span>{t('ui.built_for_a_better_everyday_workspace')}</span>
      </div>
    </footer>
  );
}
