import { useTranslation } from 'react-i18next';
export default function LanguageSwitcher() {
  const { i18n, t } = useTranslation();
  return (
    <select
      className="language-switcher"
      aria-label={t('settings.language')}
      value={i18n.resolvedLanguage}
      onChange={(event) => i18n.changeLanguage(event.target.value)}
    >
      <option value="en">English</option>
      <option value="tr">Türkçe</option>
    </select>
  );
}
