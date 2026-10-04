import { categoryName, errorMessage } from '../i18n';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';
export default function ProductFilters({ categories, brands, values, onChange, onClear }) {
  const { t } = useTranslation();
  const [min, setMin] = useState(values.min_price || '');
  const [max, setMax] = useState(values.max_price || '');
  const [error, setError] = useState('');
  function clear() {
    setMin('');
    setMax('');
    setError('');
    onClear();
  }
  function applyPrice(event) {
    event.preventDefault();
    if (min !== '' && max !== '' && Number(min) > Number(max)) {
      setError({ code: 'price_range' });
      return;
    }
    setError('');
    onChange({
      min_price: min,
      max_price: max,
    });
  }
  return (
    <div className="filter-content">
      <div className="filter-heading">
        <h2>{t('ui.filters')}</h2>
        <button className="text-button" onClick={clear}>
          {t('ui.clear_all')}
        </button>
      </div>
      <fieldset>
        <legend>{t('ui.category')}</legend>
        <label className="filter-option">
          <input
            type="radio"
            name="category"
            checked={!values.category}
            onChange={() =>
              onChange({
                category: '',
              })
            }
          />
          {t('ui.all_categories')}
        </label>
        {categories.map((category) => (
          <label className="filter-option" key={category.id}>
            <input
              type="radio"
              name="category"
              value={category.slug}
              checked={values.category === category.slug}
              onChange={() =>
                onChange({
                  category: category.slug,
                })
              }
            />
            {categoryName(category)}
          </label>
        ))}
      </fieldset>
      <fieldset>
        <legend>{t('ui.brand')}</legend>
        <label className="filter-option">
          <input
            type="radio"
            name="brand"
            checked={!values.brand}
            onChange={() =>
              onChange({
                brand: '',
              })
            }
          />
          {t('ui.all_brands')}
        </label>
        {brands.map((brand) => (
          <label className="filter-option" key={brand.id}>
            <input
              type="radio"
              name="brand"
              value={brand.slug}
              checked={values.brand === brand.slug}
              onChange={() =>
                onChange({
                  brand: brand.slug,
                })
              }
            />
            {brand.name}
          </label>
        ))}
      </fieldset>
      <form onSubmit={applyPrice}>
        <fieldset>
          <legend>{t('ui.price_range')}</legend>
          <div className="price-inputs">
            <label>
              {t('ui.min')}
              <input
                name="min_price"
                type="number"
                min="0"
                step="0.01"
                max="9999999999.99"
                value={min}
                placeholder="0"
                onChange={(event) => setMin(event.target.value)}
              />
            </label>
            <span>–</span>
            <label>
              {t('ui.max')}
              <input
                name="max_price"
                type="number"
                min="0"
                step="0.01"
                max="9999999999.99"
                value={max}
                placeholder={t('ui.any')}
                onChange={(event) => setMax(event.target.value)}
              />
            </label>
          </div>
          {error && (
            <p className="field-error" role="alert">
              {errorMessage(error)}
            </p>
          )}
          <button className="button button-outline price-apply" type="submit">
            {t('ui.apply_price')}
          </button>
        </fieldset>
      </form>
    </div>
  );
}
