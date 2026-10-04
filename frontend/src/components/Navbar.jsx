import LanguageSwitcher from './LanguageSwitcher';
import { useTranslation } from 'react-i18next';
import { useCart } from '../context/cart-context';
import { useAuth } from '../context/auth-context';
import { useState } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import Icon from './Icon';
import SearchBar from './SearchBar';
export default function Navbar({ categories }) {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { cart } = useCart();
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const category = new URLSearchParams(location.search).get('category');
  function close() {
    setOpen(false);
  }
  return (
    <>
      <div className="announcement">
        {t('ui.good_tools_better_workdays')}
        <span>{t('ui.welcome_to_bytedesk')}</span>
        <LanguageSwitcher />
      </div>
      <header className="site-header">
        <div className="container header-main">
          <Link to="/" className="logo" onClick={close} aria-label={t('ui.bytedesk_home')}>
            <span className="logo-mark">
              {t('ui.b')}
              <span />
            </span>
            {t('ui.bytedesk_2')}
            <span className="logo-dot">.</span>
          </Link>
          <div className="desktop-search">
            <SearchBar />
          </div>
          <NavLink className="shop-link" to="/products" onClick={close}>
            {t('ui.explore_the_store')}
            <Icon name="arrow" size={17} />
          </NavLink>
          <NavLink
            className="account-link header-account"
            to={user ? '/profile' : '/login'}
            onClick={close}
          >
            {user ? t('ui.my_account') : t('ui.sign_in')}
          </NavLink>
          <NavLink className="cart-link" to="/cart" onClick={close}>
            {t('ui.cartvalue', {
              value1:
                user && cart
                  ? t('ui.value', {
                      value1: cart.item_count,
                    })
                  : '',
            })}
          </NavLink>
          <button
            type="button"
            className="menu-toggle"
            aria-label={open ? t('ui.close_navigation') : t('ui.open_navigation')}
            aria-expanded={open}
            aria-controls="store-navigation"
            onClick={() => setOpen(!open)}
          >
            <Icon name={open ? 'close' : 'menu'} />
          </button>
        </div>
        <nav
          id="store-navigation"
          className={`category-nav ${open ? 'is-open' : ''}`}
          aria-label={t('ui.store_navigation')}
        >
          <div className="container nav-inner">
            <div className="mobile-search">
              <SearchBar onSearch={close} />
            </div>
            <Link
              className={location.pathname === '/products' && !category ? 'active' : ''}
              to="/products"
              onClick={close}
            >
              {t('ui.all_products')}
            </Link>
            {categories.map((item) => (
              <Link
                key={item.id}
                className={category === item.slug ? 'active' : ''}
                to={`/products?category=${item.slug}`}
                onClick={close}
              >
                {item.name}
              </Link>
            ))}
            <Link to="/wishlist" onClick={close}>
              {t('ui.wishlist')}
            </Link>
            <Link className="mobile-account-link" to={user ? '/profile' : '/login'} onClick={close}>
              {user ? t('ui.my_account') : t('ui.sign_in')}
            </Link>
            <span className="nav-note">{t('ui.made_for_your_workspace')}</span>
          </div>
        </nav>
      </header>
    </>
  );
}
