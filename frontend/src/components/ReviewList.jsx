import { formatNumber } from '../utils/format';
import { locale } from '../i18n';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { getOwnReview, getReviews } from '../api/reviews';
import { useAuth } from '../context/auth-context';
import useResource from '../hooks/useResource';
import ReviewForm from './ReviewForm';
import { ErrorState, LoadingState } from './States';
export default function ReviewList({ product }) {
  const { t } = useTranslation();
  const { user, apiRequest, loading: authLoading } = useAuth();
  const location = useLocation();
  const [page, setPage] = useState(1);
  const [submitted, setSubmitted] = useState(null);
  const publicReviews = useResource(
    (signal) => getReviews(product.id, page, signal),
    `${product.id}-${page}`,
  );
  const own = useResource(
    (signal) => (user ? getOwnReview(apiRequest, product.id, signal) : Promise.resolve(null)),
    `${product.id}-${user?.id || 'guest'}`,
  );
  const submittedReview = submitted && submitted.userId === user?.id ? submitted.review : null;
  const existing = submittedReview || own.data;
  return (
    <section className="reviews-section" aria-labelledby="reviews-title">
      <div className="reviews-heading">
        <div>
          <p className="eyebrow">{t('ui.from_the_workspace')}</p>
          <h2 id="reviews-title">{t('ui.customer_reviews')}</h2>
        </div>
        {publicReviews.data && (
          <div className="rating-summary">
            <strong>
              {publicReviews.data.average_rating === null
                ? '—'
                : formatNumber(publicReviews.data.average_rating, {
                    minimumFractionDigits: 1,
                    maximumFractionDigits: 1,
                  })}
              <span> / 5</span>
            </strong>
            <span>{t('reviews.count', { count: publicReviews.data.total })}</span>
          </div>
        )}
      </div>
      <div className="reviews-layout">
        <div>
          {publicReviews.loading ? (
            <LoadingState label={t('ui.loading_reviews')} />
          ) : publicReviews.error ? (
            <ErrorState error={publicReviews.error} onRetry={publicReviews.retry} />
          ) : publicReviews.data.total === 0 ? (
            <div className="review-empty">
              <h3>{t('ui.no_reviews_yet')}</h3>
              <p>{t('ui.be_the_first_to_share_your_experience_with_this_product')}</p>
            </div>
          ) : publicReviews.data.items.length === 0 ? (
            <div className="review-empty">
              <h3>{t('ui.no_reviews_on_this_page')}</h3>
              <button className="text-button" onClick={() => setPage(1)}>
                {t('ui.back_to_the_first_page')}
              </button>
            </div>
          ) : (
            <>
              <div className="review-list">
                {publicReviews.data.items.map((review) => (
                  <article key={review.id} className="review-entry">
                    <div className="review-meta">
                      <span
                        className="review-stars"
                        aria-label={t('ui.value_out_of_5_stars', {
                          value1: review.rating,
                        })}
                      >
                        {'★'.repeat(review.rating)}
                        <span aria-hidden="true">{'☆'.repeat(5 - review.rating)}</span>
                      </span>
                      <time dateTime={review.created_at}>
                        {new Date(review.created_at).toLocaleDateString(locale())}
                      </time>
                    </div>
                    <h3>{review.title}</h3>
                    <p className="review-body">{review.body}</p>
                    <span className="review-author">{review.author}</span>
                  </article>
                ))}
              </div>
              {publicReviews.data.total_pages > 1 && (
                <nav className="pagination" aria-label={t('ui.review_pagination')}>
                  <button
                    className="button button-outline"
                    disabled={page <= 1}
                    onClick={() => setPage((value) => value - 1)}
                  >
                    {t('ui.previous')}
                  </button>
                  <span>
                    {t('ui.page_value_of_value', {
                      value1: page,
                      value2: publicReviews.data.total_pages,
                    })}
                  </span>
                  <button
                    className="button button-outline"
                    disabled={page >= publicReviews.data.total_pages}
                    onClick={() => setPage((value) => value + 1)}
                  >
                    {t('ui.next')}
                  </button>
                </nav>
              )}
            </>
          )}
        </div>
        <aside className="review-compose">
          {authLoading ? (
            <LoadingState label={t('ui.checking_your_account')} />
          ) : !user ? (
            <>
              <h3>{t('ui.have_something_to_share')}</h3>
              <p>{t('ui.sign_in_to_leave_a_review_each_customer_can_review_a_product_once')}</p>
              <Link
                className="button button-outline"
                to="/login"
                state={{
                  from: location.pathname,
                }}
              >
                {t('ui.sign_in_to_review')}
              </Link>
            </>
          ) : own.loading && !submittedReview ? (
            <LoadingState label={t('ui.checking_your_reviews')} />
          ) : own.error && !submittedReview ? (
            <ErrorState error={own.error} onRetry={own.retry} />
          ) : existing ? (
            <div className="own-review" role="status">
              <h3>
                {existing.is_approved
                  ? t('ui.your_review_is_published')
                  : t('ui.your_review_is_awaiting_approval')}
              </h3>
              <p>
                {existing.is_approved
                  ? t('ui.thank_you_for_sharing_your_experience')
                  : t('ui.thank_you_your_review_will_appear_after_an_administrator_approves_it')}
              </p>
              <strong>{existing.title}</strong>
              <p>
                {t('ui.value_out_of_5_stars', {
                  value1: existing.rating,
                })}
              </p>
              <p className="review-body">{existing.body}</p>
            </div>
          ) : (
            <ReviewForm
              productId={product.id}
              onSubmitted={(review) =>
                setSubmitted({
                  userId: user.id,
                  review,
                })
              }
            />
          )}
        </aside>
      </div>
    </section>
  );
}
