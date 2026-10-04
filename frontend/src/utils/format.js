import { locale } from '../i18n';
export const formatPrice = (price) =>
  new Intl.NumberFormat(locale(), { style: 'currency', currency: 'USD' }).format(Number(price));
export const categoryImages = {
  keyboards: '/images/keyboard.svg',
  mice: '/images/mouse.svg',
  audio: '/images/headphones.svg',
  monitors: '/images/monitor.svg',
  'desk-accessories': '/images/accessories.svg',
};

export const formatNumber = (value, options = {}) =>
  new Intl.NumberFormat(locale(), options).format(Number(value));
