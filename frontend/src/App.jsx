import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import './index.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-primary-600 text-white shadow-lg">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                  <span className="text-primary-600 font-bold text-xl">HQ</span>
                </div>
                <h1 className="text-2xl font-bold">comp-HQ</h1>
              </div>
              <p className="text-primary-100">AI-Powered Component Sourcing Assistant</p>
            </div>
          </div>
        </header>
        
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
          </Routes>
        </main>
        
        <footer className="bg-secondary-800 text-white mt-12">
          <div className="container mx-auto px-4 py-6">
            <div className="text-center">
              <p>&copy; 2024 comp-HQ. AI-Powered Component Sourcing Assistant.</p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
