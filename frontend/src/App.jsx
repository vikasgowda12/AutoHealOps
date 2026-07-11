import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [data, setData] = useState(null)

  const fetchDashboardData = () => {
    fetch('http://127.0.0.1:8000/dashboard')
      .then((response) => response.json())
      .then((result) => setData(result))
      .catch((error) => console.error('Error:', error))
  }

  useEffect(() => {
    fetchDashboardData()

    const interval = setInterval(fetchDashboardData, 5000)

    return () => clearInterval(interval)
  }, [])

  if (!data) {
    return <div className="loading">Loading AutoHealOps Dashboard...</div>
  }

  return (
    <div className="dashboard">

      <header className="header">
        <div>
          <h1>AutoHealOps</h1>
          <p>Self-Healing Kubernetes Monitoring Dashboard</p>
        </div>

        <div className="live-status">
          ● Live Monitoring
        </div>
      </header>

      <div className="cards">

        <div className="card">
          <h2>Application Status</h2>
          <p className={data.application_status === 'Healthy' ? 'status' : 'error-status'}>
            {data.application_status}
          </p>
        </div>

        <div className="card">
          <h2>Running Pods</h2>
          <p>{data.running_pods}</p>
        </div>

        <div className="card">
          <h2>Container Restarts</h2>
          <p>{data.container_restarts}</p>
        </div>

        <div className="card">
          <h2>Active Alerts</h2>
          <p>{data.active_alerts}</p>
        </div>

        <div className="card">
          <h2>Prometheus Status</h2>
          <p
            className={
              data.prometheus_status === 'Connected'
                ? 'status'
                : 'error-status'
            }
          >
            {data.prometheus_status}
          </p>
        </div>

      </div>

      <div className="system-info">
        <h2>System Monitoring</h2>
        <p>
          Dashboard automatically updates every 5 seconds using real-time
          Kubernetes and Prometheus metrics.
        </p>
      </div>

    </div>
  )
}

export default App