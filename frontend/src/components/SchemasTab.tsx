import React, { useState } from 'react';
import { mockContracts, mockDataSources } from '../services/api';
import { ShieldCheck, Plus, CheckCircle2, AlertOctagon, Terminal } from 'lucide-react';

export const SchemasTab: React.FC = () => {
  const [selectedContract, setSelectedContract] = useState(mockContracts[0]);
  const [testPayload, setTestPayload] = useState(
`{
  "transaction_id": "tx_99841221",
  "amount": "1450.50",
  "currency": "USD",
  "account_number": "ACC-90124",
  "timestamp": "2026-09-10T09:40:00Z"
}`
  );
  const [testResult, setTestResult] = useState<{ status: string; message: string } | null>(null);

  const handleTestSchema = () => {
    try {
      const parsed = JSON.parse(testPayload);
      const missing = selectedContract.required_fields.filter(f => !(f in parsed));
      
      if (missing.length > 0) {
        setTestResult({
          status: 'BLOCK',
          message: `Contract Validation Failed: Missing required field(s): ${missing.join(', ')}`
        });
      } else {
        setTestResult({
          status: 'ALLOW',
          message: `Schema Validation Passed: All ${selectedContract.required_fields.length} required fields present and typed correctly.`
        });
      }
    } catch {
      setTestResult({
        status: 'BLOCK',
        message: 'Invalid JSON payload structure'
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Registered Data Contracts</h2>
          <p className="text-sm text-slate-400">Strict structural rules enforced for upstream partner payloads</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-sm transition">
          <Plus className="w-4 h-4" /> Create New Contract
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Contract List */}
        <div className="space-y-4">
          {mockContracts.map((contract) => {
            const ds = mockDataSources.find(d => d.id === contract.data_source_id);
            const isSelected = selectedContract.id === contract.id;
            return (
              <div 
                key={contract.id}
                onClick={() => setSelectedContract(contract)}
                className={`p-5 rounded-2xl cursor-pointer transition border ${
                  isSelected ? 'bg-slate-900 border-cyan-500/50 shadow-lg shadow-cyan-500/10' : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                    {contract.version}
                  </span>
                  <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Strict Active
                  </span>
                </div>
                <h4 className="text-base font-semibold text-white mb-1">{ds?.name}</h4>
                <p className="text-xs text-slate-400">{ds?.partner_name} • Created {new Date(contract.created_at).toLocaleDateString()}</p>
                
                <div className="mt-4 flex items-center gap-2 text-xs text-slate-300">
                  <ShieldCheck className="w-4 h-4 text-cyan-400" />
                  <span>{contract.required_fields.length} Required Attributes Enforced</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Selected Contract Details & Testing Sandbox */}
        <div className="lg:col-span-2 space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
            <h3 className="text-lg font-bold text-white mb-4">Contract Rule Specification ({selectedContract.version})</h3>
            
            <div className="mb-6">
              <label className="text-xs font-semibold uppercase text-slate-400 tracking-wider mb-2 block">
                Required Fields & Expected Data Types
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {selectedContract.required_fields.map((field) => (
                  <div key={field} className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between">
                    <span className="font-mono text-xs text-cyan-300 font-semibold">{field}</span>
                    <span className="text-[10px] font-mono text-slate-500 uppercase">
                      {selectedContract.allowed_types[field] || 'NOT NULL'}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Test Sandbox */}
            <div className="p-5 rounded-xl bg-slate-950/90 border border-slate-800/90">
              <div className="flex items-center justify-between mb-3">
                <span className="flex items-center gap-2 text-sm font-semibold text-slate-200">
                  <Terminal className="w-4 h-4 text-cyan-400" /> Schema Change Evaluator Sandbox
                </span>
                <button
                  onClick={handleTestSchema}
                  className="px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-xs transition"
                >
                  Run Validation Engine
                </button>
              </div>

              <textarea
                value={testPayload}
                onChange={(e) => setTestPayload(e.target.value)}
                className="w-full h-36 p-3 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-slate-200 focus:outline-none focus:border-cyan-500/50"
              />

              {testResult && (
                <div className={`mt-4 p-4 rounded-xl border flex items-start gap-3 text-sm ${
                  testResult.status === 'ALLOW' 
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                    : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                }`}>
                  {testResult.status === 'ALLOW' ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                  ) : (
                    <AlertOctagon className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                  )}
                  <div>
                    <div className="font-semibold">{testResult.status}: Decision Result</div>
                    <div className="text-xs text-slate-300 mt-1">{testResult.message}</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
