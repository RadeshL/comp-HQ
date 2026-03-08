import React, { useState } from 'react';
import { componentAPI } from '../api';

const ProductOptions = ({ component, sessionId, onProductSelected, onNextComponent }) => {
  const [selectedProductId, setSelectedProductId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showReasoning, setShowReasoning] = useState({});

  const handleSelectProduct = async (productId) => {
    setSelectedProductId(productId);
    setLoading(true);
    setError('');

    try {
      await componentAPI.selectProduct(component.component_name, productId, sessionId);
      
      // Notify parent component
      onProductSelected({
        component_name: component.component_name,
        product_id: productId
      });
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to select product');
    } finally {
      setLoading(false);
    }
  };

  const toggleReasoning = (productId) => {
    setShowReasoning(prev => ({
      ...prev,
      [productId]: !prev[productId]
    }));
  };

  const renderStars = (rating) => {
    if (!rating) return <span className="text-gray-400">No rating</span>;
    
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5 ? 1 : 0;
    const emptyStars = 5 - fullStars - halfStar;
    
    return (
      <div className="flex items-center">
        {[...Array(fullStars)].map((_, i) => (
          <span key={`full-${i}`} className="text-yellow-400">★</span>
        ))}
        {halfStar === 1 && <span className="text-yellow-400">☆</span>}
        {[...Array(emptyStars)].map((_, i) => (
          <span key={`empty-${i}`} className="text-gray-300">☆</span>
        ))}
        <span className="ml-1 text-sm text-gray-600">({rating}/5)</span>
      </div>
    );
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const formatReviews = (count) => {
    if (!count) return 'No reviews';
    if (count >= 1000) return `${(count / 1000).toFixed(1)}k reviews`;
    return `${count} reviews`;
  };

  if (!component || !component.top_products || component.top_products.length === 0) {
    return (
      <div className="card max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          {component.component_name}
        </h2>
        <div className="text-center py-8">
          <p className="text-gray-600">No products found for this component.</p>
        </div>
        <div className="flex justify-end">
          <button
            onClick={onNextComponent}
            className="btn-secondary"
          >
            Skip Component
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          {component.component_name}
        </h2>
        <span className="bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm font-medium">
          {component.top_products.length} options found
        </span>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {component.top_products.map((product, index) => (
          <div key={product.id} className="product-card relative">
            {/* Ranking Badge */}
            <div className="absolute top-2 right-2 bg-primary-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm">
              {index + 1}
            </div>

            {/* Product Info */}
            <div className="mb-4">
              <h3 className="font-semibold text-gray-900 mb-2 pr-8">{product.name}</h3>
              <div className="text-sm text-gray-600 space-y-1">
                <div className="flex items-center">
                  <span className="font-medium">Seller:</span>
                  <span className="ml-2">{product.seller}</span>
                </div>
                <div className="flex items-center">
                  <span className="font-medium">Price:</span>
                  <span className="ml-2 text-lg font-bold text-green-600">
                    {formatPrice(product.price)}
                  </span>
                </div>
                <div className="rating-stars">
                  <span className="font-medium">Rating:</span>
                  <span className="ml-2">{renderStars(product.rating)}</span>
                </div>
                <div className="flex items-center">
                  <span className="font-medium">Reviews:</span>
                  <span className="ml-2">{formatReviews(product.review_count)}</span>
                </div>
                {product.score && (
                  <div className="flex items-center">
                    <span className="font-medium">Score:</span>
                    <span className="ml-2 text-primary-600 font-bold">
                      {product.score.toFixed(3)}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Product Link */}
            {product.product_link && (
              <div className="mb-4">
                <a
                  href={product.product_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:text-primary-800 text-sm underline"
                >
                  View Product →
                </a>
              </div>
            )}

            {/* Reasoning Toggle */}
            {product.reasoning && (
              <div className="mb-4">
                <button
                  onClick={() => toggleReasoning(product.id)}
                  className="text-sm text-primary-600 hover:text-primary-800 underline"
                >
                  {showReasoning[product.id] ? 'Hide' : 'Show'} Ranking Reasoning
                </button>
                {showReasoning[product.id] && (
                  <div className="mt-2 p-3 bg-gray-50 rounded text-sm text-gray-700 whitespace-pre-line">
                    {product.reasoning}
                  </div>
                )}
              </div>
            )}

            {/* Select Button */}
            <button
              onClick={() => handleSelectProduct(product.id)}
              disabled={loading || selectedProductId === product.id}
              className={`w-full py-2 px-4 rounded-lg font-medium transition-colors duration-200 ${
                selectedProductId === product.id
                  ? 'bg-green-600 text-white'
                  : 'btn-primary'
              } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {selectedProductId === product.id ? (
                <span className="flex items-center justify-center">
                  ✓ Selected
                </span>
              ) : loading ? (
                <span className="flex items-center justify-center">
                  <div className="loading-spinner mr-2"></div>
                  Selecting...
                </span>
              ) : (
                'Select This Product'
              )}
            </button>
          </div>
        ))}
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center mt-8">
        <button
          onClick={onNextComponent}
          disabled={loading}
          className="btn-secondary"
        >
          Skip Component
        </button>
        
        {selectedProductId && (
          <div className="text-green-600 font-medium">
            ✓ Product selected successfully
          </div>
        )}
        
        <button
          onClick={onNextComponent}
          disabled={loading || !selectedProductId}
          className="btn-primary"
        >
          Next Component →
        </button>
      </div>
    </div>
  );
};

export default ProductOptions;
