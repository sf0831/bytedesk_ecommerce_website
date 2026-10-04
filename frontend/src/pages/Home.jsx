import { language, categoryName } from '../i18n';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { getProducts } from '../api/products';
import Icon from '../components/Icon';
import ProductGrid from '../components/ProductGrid';
import { ErrorState, LoadingState } from '../components/States';
import useResource from '../hooks/useResource';
import { categoryImages } from '../utils/format';
export default function Home({ categories, brands }) {
  const { t } = useTranslation();
  const { data, error, loading, retry } = useResource(
    (signal) =>
      getProducts(
        {
          page_size: 4,
          sort: 'price_desc',
        },
        signal,
      ),
    language(),
  );
  return (
    <>
      <section className="hero container">
        <div className="hero-copy">
          <span className="eyebrow">{t('ui.a_little_upgrade_a_big_difference')}</span>
          <h1>
            {t('ui.make_room_for')}
            <br />
            {t('ui.better_work')}
            <span>.</span>
          </h1>
          <p>
            {t(
              'ui.keyboards_that_feel_right_sound_that_keeps_you_focused_tools_that_make_your_everyday_',
            )}
          </p>
          <Link className="button" to="/products">
            {t('ui.explore_the_collection_3')}
            <Icon name="arrow" size={18} />
          </Link>
          <div className="hero-footnote">
            <span className="tiny-square" />
            {t('ui.good_design_meets_everyday_function')}
          </div>
        </div>
        <div className="hero-art">
          <img
            src="/images/workspace.svg"
            alt={t(
              'ui.illustration_of_a_thoughtfully_arranged_desk_with_a_monitor_keyboard_headphones_and_d',
            )}
            fetchPriority="high"
          />
          <span className="hero-art-label">{t('ui.your_space_reconsidered')}</span>
        </div>
      </section>
      <section className="container category-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">{t('ui.build_your_setup')}</span>
            <h2>{t('ui.find_your_kind_of_upgrade')}</h2>
          </div>
          <Link className="text-link" to="/products">
            {t('ui.shop_everything')}
            <Icon name="arrow" size={17} />
          </Link>
        </div>
        <div className="category-grid">
          {categories.map((category) => (
            <Link
              className="category-tile"
              key={category.id}
              to={`/products?category=${category.slug}`}
            >
              <img src={categoryImages[category.slug] || '/images/accessories.svg'} alt="" />
              <span>
                {categoryName(category)}
                <Icon name="arrow" size={16} />
              </span>
            </Link>
          ))}
        </div>
      </section>
      <section className="featured-section">
        <div className="container">
          <div className="section-heading">
            <div>
              <span className="eyebrow">{t('ui.a_closer_look')}</span>
              <h2>{t('ui.upgrade_your_daily_essentials')}</h2>
            </div>
            <Link className="text-link" to="/products">
              {t('ui.view_the_collection')}
              <Icon name="arrow" size={17} />
            </Link>
          </div>
          {loading ? (
            <LoadingState cards />
          ) : error ? (
            <ErrorState error={error} onRetry={retry} />
          ) : data?.items.length ? (
            <ProductGrid products={data.items} />
          ) : (
            <p className="state-block">
              {t('ui.the_collection_is_being_prepared_check_back_soon')}
            </p>
          )}
        </div>
      </section>
      <section className="container brand-section">
        <p>{t('ui.familiar_names_thoughtful_choices')}</p>
        <div className="brand-wordmarks">
          {brands.map((brand) => (
            <span key={brand.id}>{brand.name}</span>
          ))}
        </div>
        <p className="brand-disclaimer">
          {t('ui.independent_sample_catalog_brand_names_identify_sample_products')}
        </p>
      </section>
      <section className="container editorial-section">
        <div className="editorial-visual">
          <img
            src="/images/keyboard.svg"
            alt={t('ui.mechanical_keyboard_illustration')}
            loading="lazy"
          />
        </div>
        <div>
          <span className="eyebrow">{t('ui.your_desk_your_rhythm')}</span>
          <h2>
            {t('ui.small_details')}
            <br />
            {t('ui.better_workdays')}
          </h2>
          <p>
            {t(
              'ui.from_your_first_morning_keystroke_to_the_last_call_of_the_day_the_right_equipment_mak',
            )}
          </p>
          <Link className="text-link" to="/products?category=keyboards">
            {t('ui.find_your_next_keyboard')}
            <Icon name="arrow" size={18} />
          </Link>
        </div>
      </section>
    </>
  );
}
