import { errorMessage } from '../i18n';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';
import { createReview } from '../api/reviews';
import { useAuth } from '../context/auth-context';
export default function ReviewForm({ productId, onSubmitted }) {
  const { t } = useTranslation();
  const { apiRequest } = useAuth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function submit(event) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError('');
    const values = Object.fromEntries(new FormData(event.currentTarget));
    try {
      const review = await createReview(apiRequest, {
        ...values,
        product_id: productId,
        rating: Number(values.rating),
      });
      onSubmitted(review);
    } catch (err) {
      setError(err);
      setBusy(false);
    }
  }
  return (
    <form className="account-form review-form" onSubmit={submit}>
      <h3>{t('ui.write_a_review')}</h3>
      <p>
        {t(
          'ui.share_what_it_s_like_to_use_this_product_reviews_are_checked_before_they_appear_publi',
        )}
      </p>
      <label>
        {t('ui.rating')}
        <select name="rating" required defaultValue="">
          <option value="" disabled>
            {t('ui.select_a_rating')}
          </option>
          {[5, 4, 3, 2, 1].map((value) => (
            <option key={value} value={value}>
              {t('reviews.stars', { count: value })}
            </option>
          ))}
        </select>
      </label>
      <label>
        {t('ui.review_title')}
        <input
          name="title"
          required
          minLength={3}
          maxLength={160}
          placeholder={t('ui.sum_up_your_experience')}
        />
      </label>
      <label>
        {t('ui.your_review')}
        <textarea
          name="body"
          required
          minLength={10}
          maxLength={5000}
          rows={5}
          placeholder={t('ui.what_worked_well_what_could_be_better')}
        />
      </label>
      {error && (
        <p role="alert" className="form-error">
          {errorMessage(error)}
        </p>
      )}
      <button className="button button-primary" disabled={busy}>
        {busy ? t('ui.submitting') : t('ui.submit_review')}
      </button>
    </form>
  );
}
