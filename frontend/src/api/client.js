const API_BASE = (import.meta.env?.VITE_API_BASE_URL || '').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(message, status, code = 'unknown', params = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.params = params;
  }
}

export async function request(path, { signal, method = 'GET', body, token } = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      signal: signal
        ? AbortSignal.any([signal, AbortSignal.timeout(12000)])
        : AbortSignal.timeout(12000),
      method,
      body: body === undefined ? undefined : JSON.stringify(body),
      headers: {
        Accept: 'application/json',
        ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    if (error.name === 'TimeoutError')
      throw new ApiError(
        'The store is taking longer than expected. Please try again.',
        0,
        'timeout',
      );
    throw new ApiError(
      'We couldn’t reach the store. Please check your connection and try again.',
      0,
      'network_error',
    );
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const message =
      typeof body.detail === 'string'
        ? body.detail
        : response.status === 422
          ? 'Please check the information you entered.'
          : 'The store is temporarily unavailable. Please try again.';
    throw new ApiError(
      message,
      response.status,
      body.code || (response.status === 422 ? 'validation_error' : 'store_unavailable'),
      body.params,
    );
  }
  return response.json();
}
