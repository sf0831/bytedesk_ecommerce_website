import { categoryName, language } from '../i18n';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';
import { categoryImages } from '../utils/format';
export default function ProductImage({
  product,
  image,
  className = '',
  eager = false,
  illustrationsOnly = false,
}) {
  const { t } = useTranslation();
  const source = illustrationsOnly ? null : image || product.images?.[0];
  const [failedSource, setFailedSource] = useState(null);
  const fallback = categoryImages[product.category.slug] || '/images/accessories.svg';
  const useImage = source?.url && source.url !== failedSource;
  return (
    <img
      className={className}
      src={useImage ? source.url : fallback}
      alt={
        useImage
          ? (language() === 'tr' ? source.alt_text_tr || source.alt_text : source.alt_text) ||
            product.name
          : t('ui.value_illustration_for_value', {
              value1: categoryName(product.category),
              value2: product.name,
            })
      }
      loading={eager ? 'eager' : 'lazy'}
      onError={useImage ? () => setFailedSource(source.url) : undefined}
    />
  );
}
