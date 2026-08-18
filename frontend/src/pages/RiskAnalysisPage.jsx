import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShieldAlert, ArrowRight, ArrowLeft, AlertTriangle, ShieldCheck, Filter, CheckCircle2, LayoutDashboard, Award, Sparkles } from 'lucide-react';
import api from '../services/api';
import { getErrorMessage } from '../utils/errors';

export default function RiskAnalysisPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [critique, setCritique] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('all');

  useEffect(() => {
    if (id) {
      localStorage.setItem('active_project_id', id);
      fetchRisks();
    }
  }, [id]);

  const fetchRisks = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get(`/api/projects/${id}/risks`);
      setCritique(res.data || {});
    } catch (err) {
      setError(getErrorMessage(err, 'Risk analysis not generated yet.'));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'grid', gap: '16px', maxWidth: '1280px', margin: '0 auto' }}>
        {[1, 2, 3].map((i) => (
          <div key={i} className="skeleton" style={{ height: '120px', borderRadius: '12px' }} />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card" style={{ padding: '48px', textAlign: 'center', maxWidth: '600px', margin: '40px auto' }}>
        <ShieldAlert size={48} color="var(--accent-rose)" style={{ marginBottom: '16px' }} />
        <h2 style={{ fontSize: '1.4rem', marginBottom: '8px' }}>Risk Analysis Not Ready</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
          {error}
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
          <button onClick={() => navigate(`/projects/${id}/timeline`)} className="btn btn-secondary">
            Go to Timeline
          </button>
          <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
            <LayoutDashboard size={16} /> Dashboard
          </button>
        </div>
      </div>
    );
  }

  const risks = critique?.risks || critique?.identified_risks || [];
  const filteredRisks = filterSeverity === 'all'
    ? risks
    : risks.filter((r) => r.severity?.toLowerCase() === filterSeverity);

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
      {/* Top Banner Navigation */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '32px', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button onClick={() => navigate(`/projects/${id}/timeline`)} className="btn btn-secondary btn-sm" style={{ padding: '8px 14px' }}>
            <ArrowLeft size={16} /> Back: Timeline
          </button>
          <div>
            <div className="badge badge-info" style={{ marginBottom: '6px' }}>
              <ShieldAlert size={12} /> Stage 06 / Risk Audit & Quality Review
            </div>
            <h1 style={{ fontSize: '2rem', margin: 0 }}>
              Risk Analysis <span className="gradient-text-cyan">& Mitigation</span>
            </h1>
          </div>
        </div>

        <button onClick={() => navigate(`/projects/${id}/blueprint`)} className="btn btn-gradient btn-lg">
          Generate Final Blueprint <ArrowRight size={18} />
        </button>
      </div>

      {/* Overall Assessment Summary Card if present */}
      {(critique?.overall_assessment || critique?.decision || critique?.feasibility_score) && (
        <div className="glass-card mb-6" style={{ padding: '24px', marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Award size={22} color="var(--accent-cyan)" />
              <h3 style={{ fontSize: '1.15rem', margin: 0 }}>Critic Agent Review Summary</h3>
            </div>
            {critique?.feasibility_score !== undefined && (
              <span className="badge badge-success" style={{ fontSize: '0.85rem', padding: '6px 12px' }}>
                Feasibility Score: {critique.feasibility_score}/100
              </span>
            )}
          </div>
          {critique?.overall_assessment && (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.5, margin: 0 }}>
              {critique.overall_assessment}
            </p>
          )}
        </div>
      )}

      {/* Severity Filter Controls */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Filter size={16} /> Filter by Severity:
        </span>
        <div style={{ display: 'flex', gap: '8px' }}>
          {['all', 'high', 'medium', 'low'].map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`btn btn-sm ${filterSeverity === sev ? 'btn-primary' : 'btn-secondary'}`}
              style={{ textTransform: 'capitalize' }}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Empty State */}
      {filteredRisks.length === 0 ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center' }}>
          <ShieldCheck size={40} color="#34D399" style={{ marginBottom: '12px' }} />
          <h3 style={{ fontSize: '1.1rem', marginBottom: '6px' }}>No Risks Found for Selected Filter</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
            No risks categorized with severity "{filterSeverity}".
          </p>
        </div>
      ) : (
        /* Risk Cards Matrix */
        <div style={{ display: 'grid', gap: '16px' }}>
          {filteredRisks.map((risk, idx) => {
            const sev = risk.severity?.toLowerCase() || 'medium';
            const isCritical = sev === 'critical';
            const isHigh = sev === 'high' || isCritical;
            const isMed = sev === 'medium';

            const description = risk.explanation || risk.description || risk.risk || 'Risk audit identified potential area requiring mitigation.';
            const mitigation = risk.mitigation || 'Implement standard error handling and validation procedures.';

            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="glass-card"
                style={{
                  padding: '24px',
                  borderLeft: isHigh
                    ? '4px solid var(--accent-rose)'
                    : isMed
                    ? '4px solid var(--accent-amber)'
                    : '4px solid var(--accent-emerald)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px', flexWrap: 'wrap', gap: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <AlertTriangle color={isHigh ? '#FB7185' : isMed ? '#FBBF24' : '#34D399'} size={20} />
                    <h3 style={{ fontSize: '1.1rem', margin: 0 }}>
                      {risk.category ? `Category: ${risk.category}` : risk.title || `Risk Item #${idx + 1}`}
                    </h3>
                  </div>

                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    {risk.probability && (
                      <span className="badge badge-info" style={{ fontSize: '0.75rem' }}>
                        Prob: {risk.probability}
                      </span>
                    )}
                    {risk.impact && (
                      <span className="badge badge-warning" style={{ fontSize: '0.75rem' }}>
                        Impact: {risk.impact}
                      </span>
                    )}
                    <span className={`badge ${isHigh ? 'badge-danger' : isMed ? 'badge-warning' : 'badge-success'}`}>
                      {sev.toUpperCase()} SEVERITY
                    </span>
                  </div>
                </div>

                <p style={{ color: 'var(--text-main)', fontSize: '0.95rem', marginBottom: '16px', lineHeight: 1.5 }}>
                  {description}
                </p>

                <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-dark)', marginBottom: '12px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-cyan)', textTransform: 'uppercase', display: 'block', marginBottom: '4px' }}>
                    Mitigation Strategy:
                  </span>
                  <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
                    {mitigation}
                  </p>
                </div>

                {/* Feature 8: Interactive Risk Suggestion Action */}
                <RiskAiSuggestButton projectId={id} risk={risk} />
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function RiskAiSuggestButton({ projectId, risk }) {
  const [suggestion, setSuggestion] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFetchSuggestion = async () => {
    setLoading(true);
    try {
      const res = await api.post(`/api/projects/${projectId}/risks/suggest`, {
        category: risk.category || 'Technical',
        severity: risk.severity || 'medium',
        explanation: risk.explanation || risk.description || '',
        mitigation: risk.mitigation || '',
      });
      setSuggestion(res.data?.suggestion || 'No suggestion returned.');
    } catch (err) {
      setSuggestion('Failed to generate AI suggestion. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: '12px' }}>
      {!suggestion ? (
        <button
          onClick={handleFetchSuggestion}
          disabled={loading}
          className="btn btn-secondary btn-sm"
          style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem' }}
        >
          <Sparkles size={14} color="var(--accent-cyan)" />
          {loading ? 'Generating AI Mitigation...' : 'Get AI Mitigation Suggestion'}
        </button>
      ) : (
        <div style={{ padding: '14px', borderRadius: '8px', backgroundColor: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38BDF8', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Sparkles size={14} /> AI Tailored Mitigation Strategy:
          </div>
          <div style={{ fontSize: '0.85rem', color: '#E2E8F0', whiteSpace: 'pre-wrap', lineHeight: 1.4 }}>
            {suggestion}
          </div>
        </div>
      )}
    </div>
  );
}
