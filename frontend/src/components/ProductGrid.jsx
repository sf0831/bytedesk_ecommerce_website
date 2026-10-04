import ProductCard from './ProductCard';

export default function ProductGrid({ products, illustrationsOnly = false }) {
  return (
    <div className="product-grid">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} illustrationsOnly={illustrationsOnly} />
      ))}
    </div>
  );
}
