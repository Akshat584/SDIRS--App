import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('SDIRS UI Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-card">
            <h2 className="text-red-600 font-bold mb-2">Something went wrong</h2>
            <p className="text-gray-600 mb-4">The SDIRS dashboard encountered an unexpected UI error.</p>
            <button 
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Reload Dashboard
            </button>
            {process.env.NODE_ENV === 'development' && (
              <pre className="mt-4 p-4 bg-gray-100 rounded overflow-auto text-xs text-left max-h-40">
                {this.state.error && this.state.error.toString()}
              </pre>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
