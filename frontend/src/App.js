import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [apiStatus, setApiStatus] = useState('Loading...');

  useEffect(() => {
    // Test API connection
    fetch('/api/health')
      .then(response => response.json())
      .then(data => setApiStatus(data.status))
      .catch(() => setApiStatus('API not available'));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>MemoryGraph</h1>
        <p>API Status: {apiStatus}</p>
        <p>Welcome to MemoryGraph - A full-stack application</p>
      </header>
    </div>
  );
}

export default App;