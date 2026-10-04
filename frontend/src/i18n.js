import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import tr from './locales/tr.json';

const preferenceKey = 'bytedesk.language';
function initialLanguage() {
  try {
    const saved = globalThis.localStorage?.getItem(preferenceKey);
    if (['en', 'tr'].includes(saved)) return saved;
  } catch {
    /* Storage can be disabled by the browser. */
  }
  return globalThis.navigator?.language?.toLowerCase().startsWith('tr') ? 'tr' : 'en';
}
i18next.use(initReactI18next).init({
  resources: { en: { translation: en }, tr: { translation: tr } },
  lng: initialLanguage(),
  fallbackLng: 'en',
  supportedLngs: ['en', 'tr'],
  interpolation: { escapeValue: false },
});
export const language = () => i18next.resolvedLanguage || 'en';
export const locale = () => (language() === 'tr' ? 'tr-TR' : 'en-US');
export const t = (...args) => i18next.t(...args);
export const categoryName = (category) =>
  language() === 'tr' ? category.name_tr || category.name : category.name;
export function errorMessage(error) {
  if (!error) return '';
  const key = `errors.${error.code || 'unknown'}`;
  return i18next.exists(key)
    ? t(key, { product: t('extra.product'), ...error.params })
    : language() === 'en' && error.message
      ? error.message
      : t('errors.unknown');
}
function rememberLanguage() {
  if (globalThis.document) document.documentElement.lang = language();
  try {
    globalThis.localStorage?.setItem(preferenceKey, language());
  } catch {
    /* Optional preference persistence. */
  }
}
i18next.on('languageChanged', rememberLanguage);
rememberLanguage();
export default i18next;
