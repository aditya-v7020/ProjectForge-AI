import React, { useState, useEffect } from 'react';
import { DollarSign, Server, Users, HardDrive, Cpu, ShieldAlert, CheckCircle2 } from 'lucide-react';
import api from '../services/api';

export default function CostEstimationCard({ projectId }) {
  const [costData, setCostData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (projectId) {
      fetchCostEstimation();
    }
  }, [projectId]);

  const fetchCostEstimation = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/api/projects/${projectId}/cost-estimation`);
      setCostData(res.data);
    } catch (err) {
      console.error('Failed to fetch cost estimation:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="skeleton" style={{ height: '180px', borderRadius: '16px', marginBottom: '24px' }} />;
  }

  if (!costData) return null;

  const { development_labor, cloud_infrastructure, user_budget, budget_status } = costData;

  const formatINR = (val) => (val != null ? `₹${Number(val).toLocaleString('en-IN')}` : '₹0');

  return (
    <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <DollarSign size={22} color="var(--accent-emerald)" />
          <h3 style={{ margin: 0, fontSize: '1.2rem', color: '#FFF' }}>Development & Cloud Cost Estimation (INR)</h3>
        </div>
        {budget_status && (
          <span
            className="badge"
            style={{
              padding: '4px 12px',
              fontSize: '0.8rem',
              fontWeight: 700,
              backgroundColor: budget_status === 'Exceeds Budget' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
              color: budget_status === 'Exceeds Budget' ? '#F87171' : '#34D399',
              border: `1px solid ${budget_status === 'Exceeds Budget' ? 'rgba(239, 68, 68, 0.4)' : 'rgba(16, 185, 129, 0.4)'}`,
            }}
          >
            {budget_status}
          </span>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        {/* Dev Labor Cost Card */}
        <div style={{ padding: '18px', borderRadius: '12px', backgroundColor: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: 'var(--accent-cyan)', fontWeight: 700, fontSize: '0.9rem' }}>
            <Users size={18} /> Development Cost (INR)
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#FFF', marginBottom: '4px' }}>
            {formatINR(development_labor?.estimated_min)} – {formatINR(development_labor?.estimated_max)}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
            Based on {development_labor?.total_estimated_hours} total dev hours across {development_labor?.team_size} team member(s) @ {formatINR(development_labor?.blended_hourly_rate)}/hr blended rate.
          </div>

          <div style={{ display: 'grid', gap: '6px' }}>
            {development_labor?.role_breakdown?.map((r, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-main)' }}>
                <span>{r.role} ({r.allocated_hours}h)</span>
                <strong style={{ color: '#38BDF8' }}>{formatINR(r.cost)}</strong>
              </div>
            ))}
          </div>
        </div>

        {/* Cloud Infra Cost Card */}
        <div style={{ padding: '18px', borderRadius: '12px', backgroundColor: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: '#C084FC', fontWeight: 700, fontSize: '0.9rem' }}>
            <Server size={18} /> Cloud Infrastructure Cost (INR)
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#FFF', marginBottom: '4px' }}>
            {formatINR(cloud_infrastructure?.monthly_total)}/mo <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 500 }}>({formatINR(cloud_infrastructure?.annual_total)}/yr)</span>
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
            Monthly operating costs for production cloud tier services.
          </div>

          <div style={{ display: 'grid', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
              <span>Compute & Web Hosting</span>
              <strong style={{ color: '#C084FC' }}>{formatINR(cloud_infrastructure?.breakdown?.compute_hosting)}/mo</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
              <span>Managed Database Instance</span>
              <strong style={{ color: '#C084FC' }}>{formatINR(cloud_infrastructure?.breakdown?.managed_database)}/mo</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
              <span>AI APIs & Model Inference</span>
              <strong style={{ color: '#C084FC' }}>{formatINR(cloud_infrastructure?.breakdown?.ai_apis_services)}/mo</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
              <span>Storage & CDN Bandwidth</span>
              <strong style={{ color: '#C084FC' }}>{formatINR(cloud_infrastructure?.breakdown?.cdn_storage)}/mo</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
