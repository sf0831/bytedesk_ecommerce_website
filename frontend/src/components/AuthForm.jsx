import { errorMessage } from '../i18n';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/auth-context';
export default function AuthForm({ register = false }) {
  const { t } = useTranslation();
  const { user, authenticate } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const location = useLocation();
  const from = location.state?.from;
  const destination =
    typeof from === 'string' &&
    /^\/(?:profile|cart|wishlist|checkout|orders(?:\/\d+)?|products\/[^/?#]+)$/.test(from)
      ? from
      : '/profile';
  if (user) return <Navigate to={destination} replace />;
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError('');
    const values = Object.fromEntries(new FormData(event.currentTarget));
    try {
      await authenticate(register ? 'register' : 'login', values);
      navigate(destination, {
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
        <p className="eyebrow">{t('ui.your_bytedesk_account')}</p>
        <h1>{register ? t('ui.make_yourself_at_home') : t('ui.welcome_back')}</h1>
        <p>
          {register
            ? t('ui.create_an_account_for_a_workspace_that_works_for_you')
            : t('ui.sign_in_to_your_account_and_keep_exploring_your_next_workspace_upgrade')}
        </p>
        <Link className="text-link" to="/products">
          {t('ui.explore_the_collection')}
        </Link>
      </div>
      <div className="account-panel">
        <h2>{register ? t('ui.create_an_account') : t('ui.sign_in')}</h2>
        <p>
          {register
            ? t('ui.a_few_details_and_you_re_all_set')
            : t('ui.enter_your_email_and_password_to_continue')}
        </p>
        <form onSubmit={submit} className="account-form">
          {register && (
            <>
              <div className="form-row">
                <label>
                  {t('ui.first_name')}
                  <input name="first_name" autoComplete="given-name" maxLength={150} />
                </label>
                <label>
                  {t('ui.last_name')}
                  <input name="last_name" autoComplete="family-name" maxLength={150} />
                </label>
              </div>
              <label>
                {t('ui.username')}
                <input
                  name="username"
                  autoComplete="username"
                  required
                  minLength={3}
                  maxLength={150}
                  pattern="[a-zA-Z0-9_.@+\-]+"
                />
                <small>{t('ui.at_least_3_characters_letters_numbers_and')}</small>
              </label>
            </>
          )}
          <label>
            {t('ui.email_address')}
            <input
              type="email"
              name="email"
              autoComplete={register ? 'email' : 'username'}
              required
              maxLength={254}
            />
          </label>
          <label>
            {t('ui.password')}
            <input
              type="password"
              name="password"
              autoComplete={register ? 'new-password' : 'current-password'}
              required
              minLength={register ? 10 : 1}
              maxLength={128}
            />
            {register && <small>{t('ui.use_at_least_10_characters')}</small>}
          </label>
          {error && (
            <p role="alert" className="form-error">
              {errorMessage(error)}
            </p>
          )}
          <button className="button button-primary" disabled={busy}>
            {busy ? t('ui.please_wait') : register ? t('ui.create_account') : t('ui.sign_in')}
          </button>
        </form>
        <p className="account-switch">
          {register ? t('ui.already_have_an_account') : t('ui.new_to_bytedesk')}{' '}
          <Link
            to={register ? '/login' : '/register'}
            state={{
              from: destination,
            }}
          >
            {register ? t('ui.sign_in') : t('ui.create_an_account')}
          </Link>
        </p>
      </div>
    </section>
  );
}
