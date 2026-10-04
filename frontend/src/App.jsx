import { useTranslation } from 'react-i18next';
import Cart from './pages/Cart';
import Wishlist from './pages/Wishlist';
import Checkout from './pages/Checkout';
import Orders from './pages/Orders';
import OrderDetail from './pages/OrderDetail';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import ProtectedRoute from './components/ProtectedRoute';
import { useEffect } from 'react';
import { Route, Routes, useLocation } from 'react-router-dom';
import { getBrands, getCategories } from './api/products';
import Footer from './components/Footer';
import Navbar from './components/Navbar';
import useResource from './hooks/useResource';
import Home from './pages/Home';
import NotFound from './pages/NotFound';
import ProductDetail from './pages/ProductDetail';
import Products from './pages/Products';

export default function App() {
  const { t, i18n } = useTranslation();
  const currentLanguage = i18n.resolvedLanguage;
  const location = useLocation();
  const { data, error, retry } = useResource(
    (signal) => Promise.all([getCategories(signal), getBrands(signal)]),
    currentLanguage,
  );
  const [categories, brands] = data || [[], []];
  useEffect(() => {
    window.scrollTo(0, 0);
    const page = location.pathname.split('/')[1];
    const title =
      location.pathname === '/'
        ? t('extra.homeTitle')
        : location.pathname.startsWith('/products/')
          ? t('extra.productTitle')
          : location.pathname.startsWith('/orders/')
            ? t('extra.orderTitle')
            : {
                login: t('ui.sign_in'),
                register: t('ui.create_account'),
                profile: t('ui.my_account'),
                cart: t('ui.your_cart'),
                wishlist: t('ui.wishlist'),
                checkout: t('ui.checkout'),
                orders: t('ui.your_orders'),
                products: t('ui.the_collection'),
              }[page] || t('extra.notFound');
    document.title = `${title} | ByteDesk`;
  }, [location.pathname, location.search, currentLanguage, t]);
  return (
    <>
      <a href="#main-content" className="skip-link">
        {t('extra.skip')}
      </a>
      <Navbar categories={categories} />
      <main id="main-content">
        {error && (
          <div className="taxonomy-error container" role="alert">
            {t('extra.navigationError')}{' '}
            <button className="text-button" onClick={retry}>
              {t('ui.try_again')}
            </button>
          </div>
        )}
        <Routes>
          <Route path="/" element={<Home categories={categories} brands={brands} />} />
          <Route path="/products" element={<Products categories={categories} brands={brands} />} />
          <Route path="/products/:slug" element={<ProductDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/cart"
            element={
              <ProtectedRoute>
                <Cart />
              </ProtectedRoute>
            }
          />
          <Route
            path="/wishlist"
            element={
              <ProtectedRoute>
                <Wishlist />
              </ProtectedRoute>
            }
          />
          <Route
            path="/checkout"
            element={
              <ProtectedRoute>
                <Checkout />
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders"
            element={
              <ProtectedRoute>
                <Orders />
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders/:id"
            element={
              <ProtectedRoute>
                <OrderDetail />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer categories={categories} />
    </>
  );
}
