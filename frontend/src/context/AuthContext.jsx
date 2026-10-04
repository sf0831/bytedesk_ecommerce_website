import { useCallback, useEffect, useState } from 'react';
import { request } from '../api/client';
import { AuthContext } from './auth-context';
const KEY = 'bytedesk-session';
const readToken = () => {
  try {
    return sessionStorage.getItem(KEY);
  } catch {
    return null;
  }
};
const saveToken = (token) => {
  try {
    if (token) sessionStorage.setItem(KEY, token);
    else sessionStorage.removeItem(KEY);
  } catch {
    /* Session remains usable in memory. */
  }
};
export function AuthProvider({ children }) {
  const [token, setToken] = useState(readToken);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(token));
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    if (!token) return;
    const controller = new AbortController();
    request('/api/users/me', { token, signal: controller.signal })
      .then((data) => {
        setUser(data);
        setError('');
        setLoading(false);
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;
        if (err.status === 401) {
          saveToken(null);
          setToken(null);
          setUser(null);
          setError('');
        } else setError(err);
        setLoading(false);
      });
    return () => controller.abort();
  }, [token, attempt]);
  useEffect(() => {
    if (!token) return;
    let active = true;
    // Check expiry using the server; no client-side JWT claims are trusted.
    const check = () =>
      request('/api/users/me', { token }).catch((err) => {
        if (active && err.status === 401) {
          saveToken(null);
          setToken(null);
          setUser(null);
          setError('');
        }
      });
    window.addEventListener('focus', check);
    const timer = window.setInterval(check, 60000);
    return () => {
      active = false;
      window.removeEventListener('focus', check);
      window.clearInterval(timer);
    };
  }, [token]);
  const apiRequest = useCallback(
    async (path, options = {}) => {
      try {
        return await request(path, { ...options, token });
      } catch (err) {
        if (err.status === 401) {
          saveToken(null);
          setToken(null);
          setUser(null);
          setError('');
        }
        throw err;
      }
    },
    [token],
  );
  async function authenticate(kind, values) {
    const data = await request(`/api/auth/${kind}`, { method: 'POST', body: values });
    saveToken(data.access_token);
    setToken(data.access_token);
    setUser(data.user);
    setError('');
    setLoading(false);
  }
  async function logout() {
    try {
      await request('/api/auth/logout', { method: 'POST', token });
    } catch (err) {
      if (err.status !== 401) throw err;
    }
    saveToken(null);
    setToken(null);
    setUser(null);
    setError('');
  }
  return (
    <AuthContext.Provider
      value={{
        user,
        apiRequest,
        loading,
        error,
        authenticate,
        logout,
        retry: () => {
          setLoading(true);
          setAttempt((n) => n + 1);
        },
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
