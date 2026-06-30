import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [loading, setLoading] = useState(true);
  const [systemData, setSystemData] = useState(null);
  const [offline, setOffline] = useState(false);
  const [lastUpdated, setLastUpdated] = useState('');

  const fetchSystemStatus = async () => {
    setLoading(true);
    setOffline(false);
    try {
      // Query the API Gateway health endpoint
      const response = await fetch('http://localhost:4000/api/health');
      const payload = await response.json();

      if (payload && payload.status === 'success') {
        setSystemData(payload.data);
      } else {
        // Fallback for bad JSON structure
        setOffline(true);
      }
    } catch (err) {
      // Connection failure to API Gateway (Node.js down)
      setOffline(true);
    } finally {
      setLoading(false);
      setLastUpdated(new Date().toLocaleTimeString());
    }
  };

  useEffect(() => {
    fetchSystemStatus();
  }, []);

  // Determine overall status based on systemData or offline state
  const getOverallStatus = () => {
    if (offline) return 'offline';
    if (!systemData) return 'loading';
    return systemData.status; // 'healthy' or 'degraded'
  };

  const overallStatus = getOverallStatus();

  return (
    <div className="status-container">
      <h1>
        Maven System Status
        <span className={`system-status-indicator status-${overallStatus}`}>
          {overallStatus}
        </span>
      </h1>

      {loading ? (
        <div className="loading-text">Loading system diagnostics...</div>
      ) : (
        <div className="service-list">
          {/* 1. Frontend Status (Self-reported) */}
          <div className="service-card">
            <div className="service-header">
              <span className="service-name">Frontend</span>
              <span className="status-badge status-healthy">healthy</span>
            </div>
            <div className="metadata-grid">
              <div className="metadata-item">
                <span className="metadata-label">Language</span>
                <span className="metadata-value">React / JS</span>
              </div>
              <div className="metadata-item">
                <span className="metadata-label">Runtime</span>
                <span className="metadata-value">Vite / Browser</span>
              </div>
            </div>
          </div>

          {/* 2. Backend Status */}
          <div className="service-card">
            <div className="service-header">
              <span className="service-name">Backend (API Gateway)</span>
              <span className={`status-badge status-${offline ? 'offline' : systemData?.services?.backend?.status}`}>
                {offline ? 'offline' : systemData?.services?.backend?.status}
              </span>
            </div>
            {!offline && systemData?.services?.backend ? (
              <div className="metadata-grid">
                <div className="metadata-item">
                  <span className="metadata-label">Version</span>
                  <span className="metadata-value">{systemData.services.backend.version}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Uptime</span>
                  <span className="metadata-value">{systemData.services.backend.uptime}s</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Timestamp</span>
                  <span className="metadata-value">{new Date(systemData.services.backend.timestamp).toLocaleTimeString()}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Runtime</span>
                  <span className="metadata-value">Node.js</span>
                </div>
              </div>
            ) : (
              <div className="metadata-grid">
                <div className="error-reason">
                  Failed to connect to Node.js backend. Port 4000 may be inactive.
                </div>
              </div>
            )}
          </div>

          {/* 3. Python AI Service Status */}
          <div className="service-card">
            <div className="service-header">
              <span className="service-name">AI Service (Python)</span>
              <span className={`status-badge status-${offline ? 'offline' : systemData?.services?.aiService?.status}`}>
                {offline ? 'offline' : systemData?.services?.aiService?.status}
              </span>
            </div>
            {!offline && systemData?.services?.aiService ? (
              systemData.services.aiService.status === 'healthy' ? (
                <div className="metadata-grid">
                  <div className="metadata-item">
                    <span className="metadata-label">Version</span>
                    <span className="metadata-value">{systemData.services.aiService.version}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="metadata-label">Uptime</span>
                    <span className="metadata-value">{systemData.services.aiService.uptime}s</span>
                  </div>
                  <div className="metadata-item">
                    <span className="metadata-label">Timestamp</span>
                    <span className="metadata-value">{new Date(systemData.services.aiService.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="metadata-label">Runtime</span>
                    <span className="metadata-value">FastAPI / Python</span>
                  </div>
                </div>
              ) : (
                <div className="metadata-grid">
                  <div className="error-reason">
                    AI Service Degradation: {systemData.services.aiService.reason}
                  </div>
                </div>
              )
            ) : (
              <div className="metadata-grid">
                <div className="error-reason">
                  Unreachable. The backend is offline, preventing downstream status retrieval.
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="refresh-container">
        <span>Last Updated: {lastUpdated || 'Never'}</span>
        <button className="refresh-button" onClick={fetchSystemStatus} disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh Status'}
        </button>
      </div>
    </div>
  );
}

export default App;
