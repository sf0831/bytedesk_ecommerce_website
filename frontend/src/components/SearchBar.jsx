import { useTranslation } from 'react-i18next';
import { useEffect, useId, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Icon from './Icon';
export default function SearchBar({ onSearch }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const id = useId();
  const search = new URLSearchParams(location.search).get('search') || '';
  const [value, setValue] = useState(search);
  useEffect(() => setValue(search), [search]);
  function submit(event) {
    event.preventDefault();
    const params = new URLSearchParams();
    if (value.trim()) params.set('search', value.trim());
    navigate(`/products${params.size ? `?${params}` : ''}`);
    onSearch?.();
  }
  return (
    <form className="search-bar" role="search" onSubmit={submit}>
      <label className="sr-only" htmlFor={id}>
        {t('ui.search_the_store')}
      </label>
      <input
        id={id}
        type="search"
        maxLength={200}
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder={t('ui.search_your_next_desk_upgrade')}
      />
      <button aria-label={t('ui.search_products')} type="submit">
        <Icon name="search" />
      </button>
    </form>
  );
}
