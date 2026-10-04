import { useCallback, useEffect, useRef, useState } from 'react';

export default function useResource(loader, key = '', keepPreviousFor = null) {
  const loaderRef = useRef(loader);
  loaderRef.current = loader;
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState({ key: null, data: null, error: null, loading: true });
  useEffect(() => {
    const controller = new AbortController();
    setState((previous) => {
      const data =
        keepPreviousFor !== null && previous.keepPreviousFor === keepPreviousFor
          ? previous.data
          : null;
      return { key, keepPreviousFor, data, error: null, loading: !data };
    });
    loaderRef.current(controller.signal).then(
      (data) => {
        if (!controller.signal.aborted)
          setState({ key, keepPreviousFor, data, error: null, loading: false });
      },
      (error) => {
        if (!controller.signal.aborted)
          setState({ key, keepPreviousFor, data: null, error, loading: false });
      },
    );
    return () => controller.abort();
  }, [key, attempt, keepPreviousFor]);
  const retry = useCallback(() => setAttempt((value) => value + 1), []);
  const retained =
    keepPreviousFor !== null && state.keepPreviousFor === keepPreviousFor ? state.data : null;
  return {
    ...(state.key === key ? state : { data: retained, error: null, loading: !retained }),
    retry,
  };
}
