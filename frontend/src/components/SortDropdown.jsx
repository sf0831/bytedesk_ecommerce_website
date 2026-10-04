import { useTranslation } from 'react-i18next';
export default function SortDropdown({ value, onChange }) {
  const { t } = useTranslation();
  return (
    <label className="sort-control">
      {t('ui.sort_by')}
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="name_asc">{t('ui.name_a_to_z')}</option>
        <option value="name_desc">{t('ui.name_z_to_a')}</option>
        <option value="price_asc">{t('ui.price_low_to_high')}</option>
        <option value="price_desc">{t('ui.price_high_to_low')}</option>
        <option value="newest">{t('ui.newest_arrivals')}</option>
      </select>
    </label>
  );
}
