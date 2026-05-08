import React, { useState, useEffect } from 'react';
import { TrendingUp, AlertCircle, Target, Zap, BarChart3, Shield, FileText, Network } from 'lucide-react';

export default function FinanceAgentDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [dataFlow, setDataFlow] = useState([]);
  const [portfolio, setPortfolio] = useState({
    totalValue: 487250.50,
    dayChange: 2145.75,
    dayChangePercent: 0.44,
    lastUpdate: new Date().toLocaleTimeString()
  });

  // Simulate real-time data flow animation
  useEffect(() => {
    const interval = setInterval(() => {
      const flows = [
        { id: 1, source: 'Email Parser', target: 'Data Ingestion', status: 'active' },
        { id: 2, source: 'Receipt OCR', target: 'Data Ingestion', status: 'active' },
        { id: 3, source: 'Banking API', target: 'Data Ingestion', status: 'idle' },
      ];
      setDataFlow(flows.filter(() => Math.random() > 0.3));
      
      setPortfolio(prev => ({
        ...prev,
        totalValue: prev.totalValue + (Math.random() - 0.5) * 100,
        dayChange: prev.dayChange + (Math.random() - 0.5) * 50,
        lastUpdate: new Date().toLocaleTimeString()
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const agents = [
    {
      name: 'Data Ingestion Agent',
      role: 'Chief Data Officer',
      icon: '🔄',
      status: 'active',
      description: 'Multi-source data collection & validation',
      tasks: ['Email parsing', 'Receipt OCR', 'API integration', 'Data validation'],
      connections: ['Gmail', 'Banking APIs', 'Brokerage APIs']
    },
    {
      name: 'Expense Categorizer',
      role: 'Financial Analyst',
      icon: '📊',
      status: 'active',
      description: 'Transaction analysis & categorization',
      tasks: ['Auto-categorization', 'Anomaly detection', 'Budget tracking', 'Pattern analysis'],
      connections: ['Data Warehouse', 'ML Models']
    },
    {
      name: 'Portfolio Manager',
      role: 'Chief Investment Officer',
      icon: '💼',
      status: 'active',
      description: 'Portfolio tracking & rebalancing',
      tasks: ['Holdings aggregation', 'Performance tracking', 'Diversification analysis', 'Tax planning'],
      connections: ['Brokerage APIs', 'Benchmarks']
    },
    {
      name: 'Market Research Agent',
      role: 'Senior Analyst',
      icon: '🔬',
      status: 'active',
      description: 'Market data & fundamental analysis',
      tasks: ['Price tracking', 'Financial analysis', 'News sentiment', 'Trend analysis'],
      connections: ['Market APIs', 'Financial Data', 'News Feeds']
    },
    {
      name: 'Investment Recommendation',
      role: 'Investment Strategist',
      icon: '🎯',
      status: 'active',
      description: 'AI-driven stock selection',
      tasks: ['Buy/sell signals', 'Risk scoring', 'Portfolio optimization', 'Backtesting'],
      connections: ['ML Models', 'Market Data', 'Portfolio Data']
    },
    {
      name: 'Risk Assessment',
      role: 'Risk Manager',
      icon: '⚠️',
      status: 'active',
      description: 'Portfolio risk analysis',
      tasks: ['Risk metrics', 'Concentration analysis', 'Stress testing', 'Alerts'],
      connections: ['Portfolio Data', 'Market Data']
    },
    {
      name: 'Reporting & Insights',
      role: 'Communications Officer',
      icon: '📈',
      status: 'active',
      description: 'Synthesis & comprehensive reporting',
      tasks: ['Dashboard generation', 'Report creation', 'Visualizations', 'Notifications'],
      connections: ['All Agents', 'User Dashboard']
    }
  ];

  const portfolioHoldings = [
    { symbol: 'MSFT', name: 'Microsoft', shares: 25, price: 387.42, value: 9685.50, change: 2.34 },
    { symbol: 'AAPL', name: 'Apple', shares: 40, price: 189.35, value: 7574.00, change: 1.45 },
    { symbol: 'NVDA', name: 'NVIDIA', shares: 15, price: 912.50, value: 13687.50, change: 5.12 },
    { symbol: 'TSLA', name: 'Tesla', shares: 20, price: 245.30, value: 4906.00, change: -1.23 },
    { symbol: 'VTI', name: 'Vanguard Total Stock', shares: 150, value: 380000.00, change: 0.56 },
  ];

  const recommendations = [
    { symbol: 'AVGO', action: 'BUY', confidence: 87, reason: 'Strong growth trajectory', target: 145.50 },
    { symbol: 'AMD', action: 'HOLD', confidence: 72, reason: 'Stable with upside potential', target: 165.00 },
    { symbol: 'INTC', action: 'SELL', confidence: 81, reason: 'Declining market share', target: 32.50 },
  ];

  return (
    <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', minHeight: '100vh', color: '#e2e8f0' }}>
      {/* Header */}
      <div style={{ background: 'rgba(15, 23, 42, 0.8)', borderBottom: '1px solid rgba(148, 163, 184, 0.1)', padding: '20px 30px' }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h1 style={{ fontSize: '28px', fontWeight: 'bold', margin: '0 0 8px 0', background: 'linear-gradient(135deg, #60a5fa, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                🏦 Agentic Finance Platform
              </h1>
              <p style={{ margin: 0, fontSize: '14px', color: '#94a3b8' }}>Multi-Agent AI System for Wealth Management</p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#10b981' }}>
                ${portfolio.totalValue.toLocaleString('en-US', { maximumFractionDigits: 2 })}
              </div>
              <div style={{ fontSize: '14px', color: portfolio.dayChange >= 0 ? '#10b981' : '#ef4444' }}>
                {portfolio.dayChange >= 0 ? '+' : ''}{portfolio.dayChange.toFixed(2)} ({portfolio.dayChangePercent.toFixed(2)}%)
              </div>
              <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>Updated: {portfolio.lastUpdate}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div style={{ background: 'rgba(15, 23, 42, 0.5)', borderBottom: '1px solid rgba(148, 163, 184, 0.1)', padding: '0 30px' }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', gap: '30px' }}>
          {['overview', 'agents', 'portfolio', 'recommendations'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                padding: '16px 0',
                border: 'none',
                background: 'none',
                color: activeTab === tab ? '#60a5fa' : '#94a3b8',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: activeTab === tab ? 'bold' : 'normal',
                borderBottom: activeTab === tab ? '2px solid #60a5fa' : 'none',
                transition: 'all 0.3s'
              }}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '30px' }}>
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div>
            <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '20px' }}>System Status & Data Flow</h2>
            
            {/* Agent Status Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '30px' }}>
              {agents.map((agent, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(71, 85, 105, 0.3))',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    borderRadius: '12px',
                    padding: '20px',
                    transition: 'all 0.3s',
                    cursor: 'pointer'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.borderColor = 'rgba(96, 165, 250, 0.5)'}
                  onMouseLeave={(e) => e.currentTarget.style.borderColor = 'rgba(148, 163, 184, 0.2)'}
                >
                  <div style={{ display: 'flex', alignItems: 'start', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ fontSize: '28px', marginBottom: '8px' }}>{agent.icon}</div>
                      <h3 style={{ margin: '0 0 4px 0', fontSize: '16px', fontWeight: 'bold' }}>{agent.name}</h3>
                      <p style={{ margin: '0 0 8px 0', fontSize: '12px', color: '#60a5fa' }}>{agent.role}</p>
                    </div>
                    <div style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      background: 'rgba(16, 185, 129, 0.1)',
                      padding: '4px 12px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      color: '#10b981'
                    }}>
                      <div style={{ width: '8px', height: '8px', background: '#10b981', borderRadius: '50%' }}></div>
                      Active
                    </div>
                  </div>
                  <p style={{ margin: '12px 0', fontSize: '13px', color: '#cbd5e1' }}>{agent.description}</p>
                  <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid rgba(148, 163, 184, 0.1)' }}>
                    <p style={{ margin: '0 0 8px 0', fontSize: '12px', color: '#94a3b8' }}>Key Tasks:</p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {agent.tasks.map((task, tidx) => (
                        <span key={tidx} style={{
                          background: 'rgba(96, 165, 250, 0.1)',
                          color: '#93c5fd',
                          padding: '4px 10px',
                          borderRadius: '4px',
                          fontSize: '11px'
                        }}>
                          {task}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Data Flow Visualization */}
            <div style={{
              background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(71, 85, 105, 0.3))',
              border: '1px solid rgba(148, 163, 184, 0.2)',
              borderRadius: '12px',
              padding: '20px'
            }}>
              <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Network size={18} /> Real-time Data Flow
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {[
                  { from: '📧 Email Parser', to: '🔄 Data Ingestion', rate: '156/hour', color: '#60a5fa' },
                  { from: '📝 Receipt OCR', to: '🔄 Data Ingestion', rate: '89/hour', color: '#a78bfa' },
                  { from: '🔐 Banking APIs', to: '🔄 Data Ingestion', rate: 'Real-time', color: '#10b981' },
                  { from: '📊 Expense Categorizer', to: '📈 Dashboard', rate: 'Instant', color: '#f59e0b' },
                  { from: '💼 Portfolio Manager', to: '📈 Dashboard', rate: 'Live', color: '#ef4444' },
                ].map((flow, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', background: 'rgba(0,0,0,0.2)', borderRadius: '6px' }}>
                    <div style={{ fontSize: '14px', width: '30%' }}>{flow.from}</div>
                    <div style={{ flex: 1, height: '2px', background: `linear-gradient(90deg, ${flow.color}, transparent)`, position: 'relative' }}>
                      <div style={{
                        position: 'absolute',
                        right: 0,
                        top: '-4px',
                        width: '10px',
                        height: '10px',
                        background: flow.color,
                        borderRadius: '50%',
                        animation: 'pulse 2s infinite'
                      }}></div>
                    </div>
                    <div style={{ fontSize: '14px', width: '30%', textAlign: 'right' }}>{flow.to}</div>
                    <div style={{ fontSize: '12px', color: '#94a3b8', width: '15%', textAlign: 'right' }}>{flow.rate}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Agents Tab */}
        {activeTab === 'agents' && (
          <div>
            <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '20px' }}>Agent Team Details</h2>
            <div style={{ display: 'grid', gap: '20px' }}>
              {agents.map((agent, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(71, 85, 105, 0.3))',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    borderRadius: '12px',
                    padding: '24px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'start', justifyContent: 'space-between', marginBottom: '16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <div style={{ fontSize: '40px' }}>{agent.icon}</div>
                      <div>
                        <h3 style={{ margin: '0 0 4px 0', fontSize: '18px', fontWeight: 'bold' }}>{agent.name}</h3>
                        <p style={{ margin: 0, color: '#60a5fa', fontSize: '14px' }}>{agent.role}</p>
                      </div>
                    </div>
                    <div style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', padding: '6px 16px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold' }}>
                      ● ACTIVE
                    </div>
                  </div>

                  <p style={{ margin: '0 0 16px 0', color: '#cbd5e1', fontSize: '14px' }}>{agent.description}</p>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                    <div>
                      <h4 style={{ margin: '0 0 10px 0', fontSize: '12px', fontWeight: 'bold', color: '#94a3b8', textTransform: 'uppercase' }}>
                        Core Responsibilities
                      </h4>
                      <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: '#cbd5e1', lineHeight: '1.8' }}>
                        {agent.tasks.map((task, tidx) => <li key={tidx}>{task}</li>)}
                      </ul>
                    </div>
                    <div>
                      <h4 style={{ margin: '0 0 10px 0', fontSize: '12px', fontWeight: 'bold', color: '#94a3b8', textTransform: 'uppercase' }}>
                        Data Connections
                      </h4>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {agent.connections.map((conn, cidx) => (
                          <span key={cidx} style={{
                            background: 'rgba(96, 165, 250, 0.1)',
                            color: '#93c5fd',
                            padding: '6px 12px',
                            borderRadius: '6px',
                            fontSize: '12px',
                            border: '1px solid rgba(96, 165, 250, 0.2)'
                          }}>
                            {conn}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Portfolio Tab */}
        {activeTab === 'portfolio' && (
          <div>
            <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '20px' }}>Portfolio Holdings & Analysis</h2>
            
            <div style={{
              background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(71, 85, 105, 0.3))',
              border: '1px solid rgba(148, 163, 184, 0.2)',
              borderRadius: '12px',
              overflow: 'hidden'
            }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(148, 163, 184, 0.2)', background: 'rgba(0,0,0,0.2)' }}>
                    {['Symbol', 'Company', 'Shares', 'Price', 'Value', 'Change'].map(header => (
                      <th key={header} style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: 'bold', color: '#94a3b8', textTransform: 'uppercase' }}>
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {portfolioHoldings.map((holding, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid rgba(148, 163, 184, 0.1)' }}>
                      <td style={{ padding: '16px', fontWeight: 'bold', color: '#60a5fa' }}>{holding.symbol}</td>
                      <td style={{ padding: '16px', color: '#cbd5e1' }}>{holding.name}</td>
                      <td style={{ padding: '16px', color: '#cbd5e1' }}>{holding.shares.toLocaleString()}</td>
                      <td style={{ padding: '16px', color: '#cbd5e1' }}>${holding.price.toFixed(2)}</td>
                      <td style={{ padding: '16px', color: '#10b981', fontWeight: 'bold' }}>${holding.value.toLocaleString('en-US', { maximumFractionDigits: 2 })}</td>
                      <td style={{ padding: '16px', color: holding.change >= 0 ? '#10b981' : '#ef4444', fontWeight: 'bold' }}>
                        {holding.change >= 0 ? '+' : ''}{holding.change}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginTop: '20px' }}>
              <div style={{ background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(71, 85, 105, 0.3))', border: '1px solid rgba(148, 163, 184, 0.2)', borderRadius: '12px', padding: '20px' }}>
                <p style={{ margin: '0 0 8px 0', fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase' }}>Total Invested</p>
                <p style={{ margin: '0 0 4px 0', fontSize: '28px', fontWeight: 'bold', color: '#10b981' }}>$416,248.00</p>
                <p style={{ margin: 0, fontSize: '12px', color: '#64748b' }}>87.2% of portfolio</p>
              </div>
              <div style={{ background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(71, 85, 105, 0.3))', border: '1px solid rgba(148, 163, 184, 0.2)', borderRadius: '12px', padding: '20px' }}>
                <p style={{ margin: '0 0 8px 0', fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase' }}>Cash Reserves</p>
                <p style={{ margin: '0 0 4px 0', fontSize: '28px', fontWeight: 'bold', color: '#60a5fa' }}>$71,002.50</p>
                <p style={{ margin: 0, fontSize: '12px', color: '#64748b' }}>12.8% of portfolio</p>
              </div>
              <div style={{ background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(71, 85, 105, 0.3))', border: '1px solid rgba(148, 163, 184, 0.2)', borderRadius: '12px', padding: '20px' }}>
                <p style={{ margin: '0 0 8px 0', fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase' }}>YTD Return</p>
                <p style={{ margin: '0 0 4px 0', fontSize: '28px', fontWeight: 'bold', color: '#10b981' }}>+18.4%</p>
                <p style={{ margin: 0, fontSize: '12px', color: '#64748b' }}>vs S&P +12.1%</p>
              </div>
            </div>
          </div>
        )}

        {/* Recommendations Tab */}
        {activeTab === 'recommendations' && (
          <div>
            <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '20px' }}>AI Investment Recommendations</h2>
            
            <div style={{ display: 'grid', gap: '20px' }}>
              {recommendations.map((rec, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(71, 85, 105, 0.3))',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    borderRadius: '12px',
                    padding: '24px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'start', justifyContent: 'space-between', marginBottom: '16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <div style={{
                        width: '60px',
                        height: '60px',
                        background: rec.action === 'BUY' ? 'rgba(16, 185, 129, 0.1)' : rec.action === 'SELL' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(96, 165, 250, 0.1)',
                        border: `2px solid ${rec.action === 'BUY' ? '#10b981' : rec.action === 'SELL' ? '#ef4444' : '#60a5fa'}`,
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '24px',
                        fontWeight: 'bold',
                        color: rec.action === 'BUY' ? '#10b981' : rec.action === 'SELL' ? '#ef4444' : '#60a5fa'
                      }}>
                        {rec.symbol.substring(0, 2)}
                      </div>
                      <div>
                        <h3 style={{ margin: '0 0 4px 0', fontSize: '18px', fontWeight: 'bold' }}>{rec.symbol}</h3>
                        <p style={{ margin: 0, color: '#cbd5e1', fontSize: '14px' }}>{rec.reason}</p>
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{
                        display: 'inline-block',
                        padding: '8px 16px',
                        borderRadius: '6px',
                        background: rec.action === 'BUY' ? 'rgba(16, 185, 129, 0.2)' : rec.action === 'SELL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(96, 165, 250, 0.2)',
                        color: rec.action === 'BUY' ? '#10b981' : rec.action === 'SELL' ? '#ef4444' : '#60a5fa',
                        fontWeight: 'bold',
                        fontSize: '14px',
                        marginBottom: '8px'
                      }}>
                        {rec.action}
                      </div>
                      <p style={{ margin: '0 0 4px 0', fontSize: '12px', color: '#94a3b8' }}>Confidence</p>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ width: '100px', height: '6px', background: 'rgba(0,0,0,0.3)', borderRadius: '3px' }}>
                          <div style={{ width: `${rec.confidence}%`, height: '100%', background: rec.confidence > 80 ? '#10b981' : rec.confidence > 70 ? '#f59e0b' : '#ef4444', borderRadius: '3px' }}></div>
                        </div>
                        <span style={{ fontSize: '12px', fontWeight: 'bold' }}>{rec.confidence}%</span>
                      </div>
                    </div>
                  </div>

                  <div style={{ paddingTop: '16px', borderTop: '1px solid rgba(148, 163, 184, 0.1)', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
                    <div>
                      <p style={{ margin: '0 0 4px 0', fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase' }}>Target Price</p>
                      <p style={{ margin: 0, fontSize: '18px', fontWeight: 'bold', color: '#60a5fa' }}>${rec.target}</p>
                    </div>
                    <div>
                      <p style={{ margin: '0 0 4px 0', fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase' }}>Time Horizon</p>
                      <p style={{ margin: 0, fontSize: '18px', fontWeight: 'bold', color: '#a78bfa' }}>6-12 months</p>
                    </div>
                    <div>
                      <p style={{ margin: '0 0 4px 0', fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase' }}>Risk Level</p>
                      <p style={{ margin: 0, fontSize: '18px', fontWeight: 'bold', color: '#f59e0b' }}>Medium</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
}
