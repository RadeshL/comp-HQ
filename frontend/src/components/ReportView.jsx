import React, { useState, useEffect } from 'react';
import { componentAPI, reportAPI } from '../api';

const ReportView = ({ sessionId, onStartNew }) => {
  const [selections, setSelections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [error, setError] = useState('');
  const [reportInfo, setReportInfo] = useState(null);

  useEffect(() => {
    loadSelections();
  }, [sessionId]);

  const loadSelections = async () => {
    setLoading(true);
    try {
      const data = await componentAPI.getSessionSelections(sessionId);
      setSelections(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load selections');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    setGeneratingReport(true);
    setError('');
    
    try {
      const response = await reportAPI.generateReport(sessionId);
      setReportInfo(response);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate report');
    } finally {
      setGeneratingReport(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!reportInfo?.download_url) return;
    
    try {
      const response = await reportAPI.downloadReport(
        reportInfo.download_url.split('/').pop()
      );
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', reportInfo.filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download report');
    }
  };

  const calculateTotalCost = () => {
    return selections.reduce((total, selection) => total + (selection.price || 0), 0);
  };

  const calculateAverageRating = () => {
    const ratedSelections = selections.filter(s => s.rating);
    if (ratedSelections.length === 0) return 0;
    const sum = ratedSelections.reduce((total, s) => total + s.rating, 0);
    return (sum / ratedSelections.length).toFixed(1);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
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
      </div>
    );
  };

  if (loading) {
    return (
      <div className="card max-w-4xl mx-auto text-center py-12">
        <div className="loading-spinner mx-auto mb-4"></div>
        <p className="text-gray-600">Loading your selections...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Procurement Report</h2>
        <p className="text-gray-600">Review your component selections and generate a detailed report</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card text-center">
          <div className="text-3xl font-bold text-primary-600 mb-2">{selections.length}</div>
          <div className="text-gray-600">Components Selected</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-green-600 mb-2">{formatPrice(calculateTotalCost())}</div>
          <div className="text-gray-600">Total Cost</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-yellow-600 mb-2">{calculateAverageRating()}/5</div>
          <div className="text-gray-600">Average Rating</div>
        </div>
      </div>

      {/* Selections Table */}
      <div className="card mb-8">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Selected Components</h3>
        
        {selections.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-600">No components selected yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Component
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Product
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Seller
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rating
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Link
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {selections.map((selection, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {selection.component_name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {selection.product_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {selection.seller}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                      {formatPrice(selection.price)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {renderStars(selection.rating)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {selection.product_link ? (
                        <a
                          href={selection.product_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary-600 hover:text-primary-800 underline"
                        >
                          View
                        </a>
                      ) : (
                        <span className="text-gray-400">N/A</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Report Generation */}
      <div className="card">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Generate Report</h3>
        
        <div className="space-y-4">
          <p className="text-gray-600">
            Generate a comprehensive Word document with all your component selections, 
            including cost analysis, recommendations, and detailed product information.
          </p>

          {reportInfo ? (
            <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-green-800">Report Generated Successfully!</h4>
                  <p className="text-green-700 text-sm mt-1">{reportInfo.message}</p>
                </div>
                <button
                  onClick={handleDownloadReport}
                  className="btn-primary"
                >
                  Download Report
                </button>
              </div>
            </div>
          ) : (
            <div className="flex space-x-3">
              <button
                onClick={handleGenerateReport}
                disabled={generatingReport || selections.length === 0}
                className="btn-primary flex-1"
              >
                {generatingReport ? (
                  <span className="flex items-center justify-center">
                    <div className="loading-spinner mr-2"></div>
                    Generating Report...
                  </span>
                ) : (
                  'Generate Word Report'
                )}
              </button>
              
              <button
                onClick={onStartNew}
                className="btn-secondary"
              >
                Start New Session
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportView;
