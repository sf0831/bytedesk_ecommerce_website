import { locale, errorMessage } from '../i18n';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/auth-context';
export default function Profile() {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  async function signOut() {
    setBusy(true);
    setError('');
    try {
      await logout();
      navigate('/login', {
        replace: true,
      });
    } catch (err) {
      setError(err);
      setBusy(false);
    }
  }
  return (
    <section className="container account-layout">
      <div className="account-intro">
        <p className="eyebrow">{t('ui.my_account_2')}</p>
        <h1>
          {t('ui.hello_value', {
            value1: user.first_name || user.username,
          })}
        </h1>
        <p>{t('ui.your_everyday_workspace_starts_here')}</p>
        <Link className="button button-primary" to="/products">
          {t('ui.browse_the_collection')}
        </Link>
      </div>
      <div className="account-panel">
        <h2>{t('ui.your_profile')}</h2>
        <nav className="account-shopping-links" aria-label={t('ui.account_shopping')}>
          <Link to="/orders">{t('ui.your_orders_2')}</Link>
          <Link to="/wishlist">{t('ui.wishlist_3')}</Link>
          <Link to="/cart">{t('ui.cart_2')}</Link>
        </nav>
        <dl className="profile-details">
          <div>
            <dt>{t('ui.username')}</dt>
            <dd>{user.username}</dd>
          </div>
          <div>
            <dt>{t('ui.name')}</dt>
            <dd>
              {[user.first_name, user.last_name].filter(Boolean).join(' ') || t('ui.not_provided')}
            </dd>
          </div>
          <div>
            <dt>{t('ui.email_address')}</dt>
            <dd>{user.email}</dd>
          </div>
          <div>
            <dt>{t('ui.member_since')}</dt>
            <dd>
              {new Date(user.date_joined).toLocaleDateString(locale(), {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </dd>
          </div>
        </dl>
        {error && (
          <p className="form-error" role="alert">
            {errorMessage(error)}
          </p>
        )}
        <button className="button button-secondary" disabled={busy} onClick={signOut}>
          {busy ? t('ui.signing_out') : t('ui.sign_out')}
        </button>
        <p className="account-note">
          {t('ui.signing_out_ends_all_active_sessions_for_your_account')}
        </p>
      </div>
    </section>
  );
}
