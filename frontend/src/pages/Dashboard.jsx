import React, { useState, useEffect } from 'react';
import ComponentInput from '../components/ComponentInput';
import ProductOptions from '../components/ProductOptions';
import ReportView from '../components/ReportView';
import { componentAPI } from '../api';

const Dashboard = () => {
  const [currentStep, setCurrentStep] = useState('input'); // input, selection, report
  const [sessionId, setSessionId] = useState(null);
  const [components, setComponents] = useState([]);
  const [currentComponentIndex, setCurrentComponentIndex] = useState(0);
  const [currentComponentData, setCurrentComponentData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [completedComponents, setCompletedComponents] = useState([]);

  useEffect(() => {
    // Reset session when starting new
    if (currentStep === 'input') {
      resetSession();
    }
  }, [currentStep]);

  // Auto-load first component when entering selection step
  useEffect(() => {
    if (currentStep === 'selection' && sessionId && components.length > 0 && currentComponentIndex === 0) {
      loadNextComponent();
    }
  }, [currentStep, sessionId, components, currentComponentIndex]);

  const resetSession = () => {
    setSessionId(null);
    setComponents([]);
    setCurrentComponentIndex(0);
    setCurrentComponentData(null);
    setCompletedComponents([]);
    setError('');
  };

  const handleComponentsSubmit = async (response) => {
    console.log('Component submission response:', response);
    setSessionId(response.session_id);
    setComponents(response.components);
    setCurrentStep('selection');
    // Don't call loadNextComponent immediately - let the component mount first
  };

  const loadNextComponent = async () => {
    if (currentComponentIndex >= components.length) {
      // All components processed
      setCurrentStep('report');
      return;
    }

    console.log('Loading component:', {
      currentComponentIndex,
      componentsLength: components.length,
      sessionId,
      component: components[currentComponentIndex]
    });

    setLoading(true);
    setError('');

    try {
      const component = components[currentComponentIndex];
      console.log('Making API call for component:', component.name);
      const productData = await componentAPI.getRankedProducts(
        component.name,
        sessionId
      );
      console.log('Received product data:', productData);
      
      setCurrentComponentData(productData);
    } catch (err) {
      console.error('Error loading component products:', err);
      setError(err.response?.data?.detail || 'Failed to load component products');
    } finally {
      setLoading(false);
    }
  };

  const handleProductSelected = (selection) => {
    setCompletedComponents([...completedComponents, selection]);
  };

  const handleNextComponent = () => {
    setCurrentComponentIndex(currentComponentIndex + 1);
    setCurrentComponentData(null);
    loadNextComponent();
  };

  const handleStartNew = () => {
    setCurrentStep('input');
  };

  const renderProgressBar = () => {
    if (components.length === 0) return null;

    const progress = (completedComponents.length / components.length) * 100;

    return (
      <div className="mb-8">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Progress: {completedComponents.length} of {components.length} components</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-primary-600 h-3 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>
    );
  };

  const renderStepIndicator = () => {
    const steps = [
      { id: 'input', label: 'Enter Components', icon: '📝' },
      { id: 'selection', label: 'Select Products', icon: '🛒' },
      { id: 'report', label: 'Generate Report', icon: '📊' }
    ];

    const currentStepIndex = steps.findIndex(step => step.id === currentStep);

    return (
      <div className="flex justify-center mb-8">
        <div className="flex items-center space-x-4">
          {steps.map((step, index) => (
            <React.Fragment key={step.id}>
              <div className="flex items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
                    index <= currentStepIndex
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {step.icon}
                </div>
                <span
                  className={`ml-2 text-sm font-medium ${
                    index <= currentStepIndex
                      ? 'text-primary-600'
                      : 'text-gray-500'
                  }`}
                >
                  {step.label}
                </span>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`w-8 h-1 ${
                    index < currentStepIndex ? 'bg-primary-600' : 'bg-gray-200'
                  }`}
                ></div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div>
      {renderStepIndicator()}
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {currentStep === 'input' && (
        <ComponentInput onComponentsSubmit={handleComponentsSubmit} />
      )}

      {currentStep === 'selection' && (
        <div>
          {renderProgressBar()}
          
          {loading ? (
            <div className="card max-w-4xl mx-auto text-center py-12">
              <div className="loading-spinner mx-auto mb-4"></div>
              <p className="text-gray-600">Searching for the best products...</p>
              <p className="text-sm text-gray-500 mt-2">
                This may take a few moments as we search multiple retailers
              </p>
            </div>
          ) : currentComponentData ? (
            <ProductOptions
              component={currentComponentData}
              sessionId={sessionId}
              onProductSelected={handleProductSelected}
              onNextComponent={handleNextComponent}
            />
          ) : null}
        </div>
      )}

      {currentStep === 'report' && (
        <ReportView
          sessionId={sessionId}
          onStartNew={handleStartNew}
        />
      )}
    </div>
  );
};

export default Dashboard;
