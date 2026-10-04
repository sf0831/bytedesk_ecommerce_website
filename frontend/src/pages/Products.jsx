import { formatPrice } from '../utils/format';
import { language, categoryName } from '../i18n';
import { useTranslation } from 'react-i18next';
import { useEffect, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { getProducts } from '../api/products';
import Icon from '../components/Icon';
import Pagination from '../components/Pagination';
import ProductFilters from '../components/ProductFilters';
import ProductGrid from '../components/ProductGrid';
import SortDropdown from '../components/SortDropdown';
import { EmptyState, ErrorState, LoadingState } from '../components/States';
import useResource from '../hooks/useResource';
const queryKeys = ['search', 'category', 'brand', 'min_price', 'max_price', 'sort', 'page'];
export default function Products({ categories, brands }) {
  const { t } = useTranslation();
  const [params, setParams] = useSearchParams();
  const pendingParams = useRef(params);
  useEffect(() => {
    pendingParams.current = params;
  }, [params]);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const values = Object.fromEntries(queryKeys.map((key) => [key, params.get(key) || '']));
  const key = `${params.toString()}-${language()}`;
  const { data, error, loading, retry } = useResource(
    (signal) =>
      getProducts(
        {
          ...values,
          page_size: 12,
        },
        signal,
      ),
    key,
  );
  const category = categories.find((item) => item.slug === values.category);
  function update(changes) {
    const next = new URLSearchParams(pendingParams.current);
    Object.entries(changes).forEach(([name, value]) => {
      if (value) next.set(name, value);
      else next.delete(name);
    });
    next.delete('page');
    pendingParams.current = next;
    setParams(next);
  }
  function clear() {
    pendingParams.current = new URLSearchParams();
    setParams({});
  }
  const activeFilters = ['search', 'category', 'brand', 'min_price', 'max_price'].filter(
    (name) => values[name],
  );
  const page = data?.page || 1;
  return (
    <div className="container catalog-page">
      <div className="breadcrumbs">
        <Link to="/">{t('ui.home')}</Link>
        <span>/</span>
        <span>{t('ui.shop')}</span>
        {category && (
          <>
            <span>/</span>
            <span>{categoryName(category)}</span>
          </>
        )}
      </div>
      <div className="catalog-heading">
        <span className="eyebrow">{t('ui.find_your_everyday_essentials')}</span>
        <h1>
          {category?.name || t('ui.the_collection')}
          <span>.</span>
        </h1>
        <p>
          {values.search
            ? t('ui.search_results_for_value', {
                value1: values.search,
              })
            : t('ui.practical_equipment_familiar_brands_a_workspace_that_works_for_you')}
        </p>
      </div>
      <div className="catalog-layout">
        <aside className={`filter-panel ${filtersOpen ? 'filters-open' : ''}`} id="product-filters">
          <ProductFilters
            key={`${values.min_price}:${values.max_price}`}
            categories={categories}
            brands={brands}
            values={values}
            onChange={update}
            onClear={clear}
          />
        </aside>
        <section className="catalog-results" aria-label={t('ui.catalog_results')}>
          <div className="catalog-toolbar">
            <span className="result-count" aria-live="polite">
              {loading
                ? t('ui.finding_your_next_upgrade')
                : data
                  ? t('catalog.productCount', { count: data.total })
                  : t('ui.collection')}
            </span>
            <button
              className="mobile-filter-button"
              onClick={() => setFiltersOpen(!filtersOpen)}
              aria-expanded={filtersOpen}
              aria-controls="product-filters"
            >
              <Icon name="filter" size={16} />
              {t('ui.filters')}
            </button>
            <SortDropdown
              value={values.sort || 'name_asc'}
              onChange={(sort) =>
                update({
                  sort,
                })
              }
            />
          </div>
          {activeFilters.length > 0 && (
            <div className="active-filters">
              {activeFilters.map((name) => (
                <button
                  key={name}
                  onClick={() =>
                    update({
                      [name]: '',
                    })
                  }
                  aria-label={t('ui.remove_value_filter', {
                    value1: t(`filterNames.${name}`),
                  })}
                >
                  <span>
                    {name === 'category'
                      ? category?.name || values[name]
                      : name === 'brand'
                        ? brands.find((brand) => brand.slug === values[name])?.name || values[name]
                        : name === 'min_price'
                          ? t('ui.from_value', {
                              value1: formatPrice(values[name]),
                            })
                          : name === 'max_price'
                            ? t('ui.up_to_value', {
                                value1: formatPrice(values[name]),
                              })
                            : values[name]}
                  </span>
                  <Icon name="close" size={12} />
                </button>
              ))}
            </div>
          )}
          {loading ? (
            <LoadingState cards />
          ) : error ? (
            <ErrorState error={error} onRetry={retry} />
          ) : data?.items.length ? (
            <>
              <ProductGrid products={data.items} />
              <div className="pagination-row">
                <span>
                  {t('ui.showing_value_value_of_value', {
                    value1: (page - 1) * data.page_size + 1,
                    value2: Math.min(page * data.page_size, data.total),
                    value3: data.total,
                  })}
                </span>
                <Pagination page={page} totalPages={data.total_pages} params={params} />
              </div>
            </>
          ) : (
            <EmptyState onReset={clear} />
          )}
        </section>
      </div>
    </div>
  );
}
