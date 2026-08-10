import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FileText, ArrowRight, ArrowLeft, CheckCircle2, Users, Clock, ShieldAlert, Sparkles, LayoutDashboard } from 'lucide-react';
import api from '../services/api';

export default function RequirementsPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [reqs, setReqs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      localStorage.setItem('active_project_id', id);
      fetchRequirements();
    }
  }, [id]);

  const fetchRequirements = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get(`/api/projects/${id}/requirements`);
      setReqs(res.data || {});
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load requirements.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'grid', gap: '16px' }}>
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
        <h2 style={{ fontSize: '1.4rem', marginBottom: '8px' }}>Project Not Found</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
          {error}
        </p>
        <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
          <LayoutDashboard size={16} /> Return to Dashboard
        </button>
      </div>
    );
  }

  const rawData = reqs?.raw_data || {};
  const goals = reqs?.goals || rawData.goals || [];
  const features = reqs?.features || rawData.features || [];

  return (
    <div>
      {/* Top Header Banner & Navigation Buttons */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '32px', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button onClick={() => navigate('/dashboard')} className="btn btn-secondary btn-sm" style={{ padding: '8px 14px' }}>
            <ArrowLeft size={16} /> Dashboard
          </button>
          <div>
            <div className="badge badge-info" style={{ marginBottom: '6px' }}>
              <Sparkles size={12} /> Stage 01 / Requirement Analysis
            </div>
            <h1 style={{ fontSize: '2rem', margin: 0 }}>
              Structured <span className="gradient-text-cyan">Project Requirements</span>
            </h1>
          </div>
        </div>

        <button
          onClick={() => navigate(`/projects/${id}/technology-selection`)}
          className="btn btn-gradient btn-lg"
        >
          Next: Technology Selection <ArrowRight size={18} />
        </button>
      </div>

      {/* Parameter Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '28px' }}>
        <div className="glass-card p-4" style={{ padding: '16px 20px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Team Size</span>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#38BDF8', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Users size={20} /> {reqs?.team_size || 3} Devs
          </div>
        </div>

        <div className="glass-card p-4" style={{ padding: '16px 20px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Deadline</span>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#34D399', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Clock size={20} /> {reqs?.deadline_days || 30} Days
          </div>
        </div>

        <div className="glass-card p-4" style={{ padding: '16px 20px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Complexity</span>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#FBBF24', marginTop: '4px', textTransform: 'capitalize' }}>
            {reqs?.complexity || 'high'}
          </div>
        </div>

        <div className="glass-card p-4" style={{ padding: '16px 20px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Skill Level</span>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#C084FC', marginTop: '4px', textTransform: 'capitalize' }}>
            {reqs?.skill_level || 'intermediate'}
          </div>
        </div>
      </div>

      {/* Main Breakdown Section */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '24px' }}>
        {/* Project Goals */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="glass-card" style={{ padding: '28px' }}>
          <h3 style={{ fontSize: '1.2rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle2 size={20} color="var(--accent-cyan)" /> Core Project Goals
          </h3>
          <ul style={{ listStyle: 'none', display: 'grid', gap: '10px' }}>
            {goals.map((goal, idx) => (
              <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '0.9rem', color: 'var(--text-main)' }}>
                <span style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>•</span>
                <span>{goal}</span>
              </li>
            ))}
          </ul>
        </motion.div>

        {/* Feature Backlog */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card" style={{ padding: '28px' }}>
          <h3 style={{ fontSize: '1.2rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={20} color="var(--accent-violet)" /> Required Features
          </h3>
          <ul style={{ listStyle: 'none', display: 'grid', gap: '10px' }}>
            {features.map((feat, idx) => (
              <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '0.9rem', color: 'var(--text-main)' }}>
                <span className="badge badge-purple" style={{ fontSize: '0.65rem', padding: '2px 6px' }}>F{idx + 1}</span>
                <span>{feat}</span>
              </li>
            ))}
          </ul>
        </motion.div>
      </div>
    </div>
  );
}
