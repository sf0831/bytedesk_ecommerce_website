import { errorMessage } from '../i18n';
import { useTranslation } from 'react-i18next';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/auth-context';
export default function ProtectedRoute({ children }) {
  const { t } = useTranslation();
  const { user, loading, error, retry } = useAuth();
  const location = useLocation();
  if (loading)
    return (
      <div className="container account-state" role="status">
        {t('ui.loading_your_account')}
      </div>
    );
  if (error)
    return (
      <div className="container account-state" role="alert">
        <p>{errorMessage(error)}</p>
        <button className="button button-primary" onClick={retry}>
          {t('ui.try_again')}
        </button>
      </div>
    );
  if (!user)
    return (
      <Navigate
        to="/login"
        state={{
          from: location.pathname,
        }}
        replace
      />
    );
  return children;
}
