import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sparkles, ArrowRight, Bot, Clock, Users, Zap, CheckCircle2, AlertCircle } from 'lucide-react';
import api from '../services/api';
import { getErrorMessage } from '../utils/errors';
import AgentProgressModal from '../components/AgentProgressModal';
import { useSSE } from '../hooks/useSSE';

const SAMPLE_PROMPTS = [
  "I want to build an AI-powered e-commerce platform for 3 developers in 30 days with payment integration and product recommendation engine.",
  "Build a real-time collaborative task board with drag-and-drop Kanban, web sockets, role-based access control, and PDF reporting.",
  "Create a multi-tenant SaaS analytics dashboard for monitoring microservice logs, error rates, and custom metrics with Slack alerts.",
];

export default function CreateProjectPage() {
  const navigate = useNavigate();

  const [projectName, setProjectName] = useState('');
  const [projectIdea, setProjectIdea] = useState('');
  const [teamSize, setTeamSize] = useState(3);
  const [deadlineDays, setDeadlineDays] = useState(30);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [createdProjectId, setCreatedProjectId] = useState(null);
  const [showSSE, setShowSSE] = useState(false);

  const { agentProgress, isConnected, isFinished } = useSSE(showSSE ? createdProjectId : null);

  React.useEffect(() => {
    if (isFinished && createdProjectId) {
      setTimeout(() => {
        navigate(`/projects/${createdProjectId}/technology-selection`);
      }, 1200);
    }
  }, [isFinished, createdProjectId, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!projectIdea.trim()) return;

    setLoading(true);
    setError('');

    try {
      // Step 1: Create Project record
      const name = projectName.trim() || 'AI-Architected Project';
      const createRes = await api.post('/api/projects', {
        name: name,
        raw_idea: projectIdea,
        team_size: teamSize,
        deadline_days: deadlineDays,
      });

      const projId = createRes.data.id;
      setCreatedProjectId(projId);
      localStorage.setItem('active_project_id', projId);
      setShowSSE(true);

      // Step 2: Trigger Phase 1 requirement analysis & technology advisor agents
      await api.post(`/api/projects/${projId}/requirements`, {
        project_idea: projectIdea,
      });
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to start AI analysis wizard.'));
      setLoading(false);
      setShowSSE(false);
    }
  };

  const handleSelectTemplate = (promptText) => {
    setProjectIdea(promptText);
    if (!projectName) {
      setProjectName('E-Commerce Platform');
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', paddingBottom: '120px' }}>
      {showSSE && (
        <AgentProgressModal progress={agentProgress} isConnected={isConnected} />
      )}

      {/* Page Header */}
      <div style={{ marginBottom: '32px' }}>
        <div className="badge badge-info" style={{ marginBottom: '12px' }}>
          <Sparkles size={14} className="pulse-glow" /> AI Architecture Wizard
        </div>
        <h1 style={{ fontSize: '2.2rem', marginBottom: '8px' }}>
          Forge Your <span className="gradient-text">Project Architecture</span>
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem' }}>
          Describe your vision, set project parameters, and let 7 specialized AI agents create your architecture.
        </p>
      </div>

      {error && (
        <div className="alert alert-danger" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={18} /> {error}
          </span>
          <button
            type="button"
            onClick={() => { setError(''); setLoading(false); setShowSSE(false); setCreatedProjectId(null); }}
            className="btn btn-sm btn-secondary"
            style={{ flexShrink: 0 }}
          >
            Try Again
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="glass-card" style={{ padding: '36px', marginBottom: '32px' }}>
          {/* Project Name */}
          <div className="form-group">
            <label className="form-label">Project Name</label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g. AI-Powered E-Commerce Platform"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
            />
          </div>

          {/* Project Idea / Prompt */}
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label className="form-label" style={{ margin: 0 }}>Project Idea & Core Requirements *</label>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                {projectIdea.length} characters
              </span>
            </div>
            <textarea
              className="form-control"
              placeholder="Describe your project idea in plain English... Mention key features, target audience, preferred technologies, or constraints."
              value={projectIdea}
              onChange={(e) => setProjectIdea(e.target.value)}
              required
              rows={5}
            />
          </div>

          {/* Quick Prompt Templates */}
          <div style={{ marginBottom: '28px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', display: 'block', marginBottom: '8px' }}>
              Or choose an example prompt template:
            </span>
            <div style={{ display: 'grid', gap: '8px' }}>
              {SAMPLE_PROMPTS.map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelectTemplate(prompt)}
                  className="btn btn-secondary btn-sm"
                  style={{ textAlign: 'left', justifyContent: 'flex-start', fontSize: '0.8rem', whiteSpace: 'normal', padding: '10px 14px' }}
                >
                  <Zap size={14} color="var(--accent-cyan)" style={{ flexShrink: 0 }} />
                  <span>{prompt}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Team Size & Deadline Parameters */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', paddingTop: '20px', borderTop: '1px solid var(--border-dark)' }}>
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Users size={16} color="var(--accent-blue)" /> Team Size (Developers)
              </label>
              <input
                type="number"
                min={1}
                max={50}
                className="form-control"
                value={teamSize}
                onChange={(e) => setTeamSize(parseInt(e.target.value) || 1)}
              />
            </div>

            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Clock size={16} color="var(--accent-cyan)" /> Target Deadline (Days)
              </label>
              <input
                type="number"
                min={1}
                max={365}
                className="form-control"
                value={deadlineDays}
                onChange={(e) => setDeadlineDays(parseInt(e.target.value) || 1)}
              />
            </div>
          </div>
        </motion.div>

        {/* Action Button */}
        <div style={{ display: 'flex', justifyContent: 'flex-start', marginTop: '20px' }}>
          <button
            type="submit"
            disabled={loading || !projectIdea.trim()}
            className="btn btn-gradient btn-lg"
            style={{
              padding: '16px 36px',
              fontSize: '1.05rem',
              fontWeight: 800,
              boxShadow: '0 10px 30px -5px rgba(59, 130, 246, 0.4)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
            }}
          >
            {loading ? 'Initializing AI Agents...' : 'Start AI Architecture Analysis'} <ArrowRight size={20} />
          </button>
        </div>
      </form>
    </div>
  );
}
