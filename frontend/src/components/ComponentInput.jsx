import React, { useState } from 'react';
import { componentAPI } from '../api';

const ComponentInput = ({ onComponentsSubmit }) => {
  const [components, setComponents] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    console.log('Form submitted with components:', components);
    
    if (!components.trim()) {
      setError('Please enter at least one component');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Parse components (split by new lines or commas)
      const componentList = components
        .split(/[\n,]+/)
        .map(comp => comp.trim())
        .filter(comp => comp.length > 0);

      console.log('Parsed component list:', componentList);

      if (componentList.length === 0) {
        setError('Please enter valid component names');
        return;
      }

      // Submit to backend
      console.log('Making API call to submit components...');
      const response = await componentAPI.submitComponents(componentList);
      console.log('Received response from backend:', response);
      
      setSuccess(`Successfully processed ${componentList.length} components`);
      onComponentsSubmit(response);
      
      // Clear form
      setComponents('');
      
    } catch (err) {
      console.error('Error submitting components:', err);
      setError(err.response?.data?.detail || 'Failed to submit components');
    } finally {
      setLoading(false);
    }
  };

  const handleSampleComponents = () => {
    setComponents('Arduino Uno\nESP32\nUltrasonic Sensor\nLED Strip\nBreadboard');
  };

  return (
    <div className="card max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Enter Components</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="components" className="block text-sm font-medium text-gray-700 mb-2">
            Component List (one per line or comma-separated)
          </label>
          <textarea
            id="components"
            value={components}
            onChange={(e) => setComponents(e.target.value)}
            className="input-field w-full h-32 resize-none"
            placeholder="Arduino Uno&#10;ESP32&#10;Ultrasonic Sensor&#10;LED Strip&#10;Breadboard"
            disabled={loading}
          />
          <p className="text-sm text-gray-500 mt-1">
            Enter each component on a new line or separate with commas
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {success}
          </div>
        )}

        <div className="flex space-x-3">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex-1"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <div className="loading-spinner mr-2"></div>
                Processing...
              </span>
            ) : (
              'Submit Components'
            )}
          </button>
          
          <button
            type="button"
            onClick={handleSampleComponents}
            disabled={loading}
            className="btn-secondary"
          >
            Load Sample
          </button>
        </div>
      </form>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold text-blue-900 mb-2">💡 Tips:</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Be specific with component names (e.g., "Arduino Uno R3" instead of just "Arduino")</li>
          <li>• Include common variations like "ESP32 DevKit" or "HC-SR04 Ultrasonic Sensor"</li>
          <li>• The system will search across multiple retailers for the best options</li>
          <li>• Each component will be ranked based on price, rating, and reviews</li>
        </ul>
      </div>
    </div>
  );
};

export default ComponentInput;
