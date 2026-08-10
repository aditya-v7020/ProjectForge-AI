import React, { useState, useEffect } from 'react';
import { Activity, ShieldCheck, Zap, Cpu, Clock, AlertTriangle, ChevronRight } from 'lucide-react';
import api from '../services/api';

export default function ProjectHealthScoreCard({ projectId, compact = false }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (projectId) {
      fetchHealthScore();
    }
  }, [projectId]);

  const fetchHealthScore = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/api/projects/${projectId}/health-score`);
      setData(res.data);
    } catch (err) {
      console.error('Failed to load health score:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="skeleton" style={{ height: compact ? '90px' : '220px', borderRadius: '16px', marginBottom: '24px' }} />;
  }

  if (!data) return null;

  const { overall_score, grade, factors } = data;

  const factorIcons = {
    complexity: Activity,
    security: ShieldCheck,
    scalability: Zap,
    technology_fit: Cpu,
    timeline_feasibility: Clock,
    risk_level: AlertTriangle,
  };

  const getScoreColor = (score) => {
    if (score >= 90) return '#34D399';
    if (score >= 80) return '#38BDF8';
    if (score >= 70) return '#FBBF24';
    return '#F87171';
  };

  return (
    <div className="glass-card" style={{ padding: compact ? '16px 20px' : '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Activity size={20} color="var(--accent-cyan)" />
          <h3 style={{ margin: 0, fontSize: compact ? '1.05rem' : '1.2rem', color: '#FFF' }}>Project Health & Feasibility Matrix</h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Overall Grade:</span>
          <span
            className="badge"
            style={{
              fontSize: '1rem',
              fontWeight: 800,
              padding: '4px 12px',
              backgroundColor: 'rgba(59, 130, 246, 0.2)',
              border: '1px solid rgba(59, 130, 246, 0.4)',
              color: getScoreColor(overall_score),
            }}
          >
            {grade} ({overall_score}/100)
          </span>
        </div>
      </div>

      {/* Breakdown Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
        {Object.entries(factors || {}).map(([key, item]) => {
          const Icon = factorIcons[key] || Activity;
          const label = key.replace('_', ' ').toUpperCase();
          const color = getScoreColor(item.score);

          return (
            <div
              key={key}
              style={{
                padding: '12px 14px',
                borderRadius: '10px',
                backgroundColor: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255, 255, 255, 0.07)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)' }}>{label}</span>
                <Icon size={14} color={color} />
              </div>

              <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginBottom: '6px' }}>
                <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFF' }}>{item.score}</span>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: color }}>{item.level}</span>
              </div>

              {/* Progress mini bar */}
              <div style={{ height: '4px', backgroundColor: 'rgba(255, 255, 255, 0.08)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${item.score}%`, backgroundColor: color, borderRadius: '4px' }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
