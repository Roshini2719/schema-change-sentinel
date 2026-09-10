import React, { useEffect, useState } from 'react';
import { Header } from './components/Header';
import { Dashboard } from './components/Dashboard';
import { SchemasTab } from './components/SchemasTab';
import { PipelineRunsTab } from './components/PipelineRunsTab';
import { LineageTab } from './components/LineageTab';
import { AuditTab } from './components/AuditTab';
import { LoginPage } from './components/LoginPage';
import { fetchMetrics, fetchPipelineRuns, mockDataSources } from './services/api';
import { PipelineMetric, PipelineRun } from './types';

export function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [metrics, setMetrics] = useState<PipelineMetric | null>(null);
  const [pipelineRuns, setPipelineRuns] = useState<PipelineRun[]>([]);
  const [backendConnected, setBackendConnected] = useState(false);

  const loadData = async () => {
    const metricsData = await fetchMetrics();
    const runsData = await fetchPipelineRuns();
    setMetrics(metricsData);
    setPipelineRuns(runsData);

    try {
      const res = await fetch('/health');
      if (res.ok) setBackendConnected(true);
    } catch {
      setBackendConnected(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadData();
    }
  }, [isAuthenticated]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <LoginPage onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans flex flex-col">
      <Header 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        backendStatus={backendConnected} 
        onOpenAuth={handleLogout}
        isAuthenticated={isAuthenticated}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
        {activeTab === 'dashboard' && metrics && (
          <Dashboard 
            metrics={metrics} 
            pipelineRuns={pipelineRuns} 
            dataSources={mockDataSources} 
            onNavigateToRuns={() => setActiveTab('runs')}
          />
        )}
        {activeTab === 'schemas' && <SchemasTab />}
        {activeTab === 'runs' && <PipelineRunsTab />}
        {activeTab === 'lineage' && <LineageTab />}
        {activeTab === 'audit' && <AuditTab />}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950/60 py-4 px-6 text-center text-xs text-slate-500">
        Schema Sentinel Dashboard • Integrated with FastAPI Backend (`/Users/muthamilroshini/Desktop/COE-project/backend`)
      </footer>
    </div>
  );
}

export default App;
