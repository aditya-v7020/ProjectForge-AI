import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { PlusCircle, Database, Cpu, Layers, BookOpen, Trash2, ArrowRight, Sparkles, RefreshCw } from 'lucide-react';
import api from '../services/api';
import { getErrorMessage } from '../utils/errors';
import ProgressDashboard from '../components/ProgressDashboard';
import ProjectHealthScoreCard from '../components/ProjectHealthScoreCard';

export default function DashboardPage() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [seeding, setSeeding] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get('/api/projects');
      setProjects(res.data || []);
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load projects.'));
    } finally {
      setLoading(false);
    }
  };

  const handleSeedDemo = async () => {
    setSeeding(true);
    setError('');
    try {
      const res = await api.post('/api/projects/demo/seed');
      const projId = res.data.project_id;
      localStorage.setItem('active_project_id', projId);
      navigate(`/projects/${projId}/technology-selection`);
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to seed demo project.'));
    } finally {
      setSeeding(false);
    }
  };

  const handleDeleteProject = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this project?')) return;
    try {
      await api.delete(`/api/projects/${id}`);
      setProjects((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      alert('Failed to delete project.');
    }
  };

  // Compute stats
  const totalProjects = projects.length;
  const techLocked = projects.filter((p) => p.status === 'tech_selected' || p.status === 'completed' || p.status === 'blueprint_done').length;
  const completedBlueprints = projects.filter((p) => p.status === 'completed' || p.status === 'blueprint_done').length;

  return (
    <div>
      {/* Header Banner */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '32px' }}>
        <div>
          <h1 style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '2rem' }}>
            Command <span className="gradient-text-cyan">Center</span>
          </h1>
          <p style={{ margin: '4px 0 0 0', color: 'var(--text-muted)' }}>
            Manage your AI-architected project blueprints and multi-agent workflows.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button onClick={handleSeedDemo} disabled={seeding} className="btn btn-secondary">
            <RefreshCw size={16} className={seeding ? 'spinner' : ''} />
            {seeding ? 'Seeding...' : 'Seed Demo Project'}
          </button>

          <button onClick={() => navigate('/projects/new')} className="btn btn-gradient">
            <PlusCircle size={18} /> Create New Project
          </button>
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {/* Stats Metric Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '36px' }}>
        <div className="glass-card p-5" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Projects</span>
            <Layers size={18} color="var(--accent-blue)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-main)' }}>{totalProjects}</div>
        </div>

        <div className="glass-card p-5" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Stack Locked</span>
            <Cpu size={18} color="var(--accent-cyan)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#38BDF8' }}>{techLocked}</div>
        </div>

        <div className="glass-card p-5" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Blueprints Ready</span>
            <BookOpen size={18} color="var(--accent-emerald)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#34D399' }}>{completedBlueprints}</div>
        </div>

        <div className="glass-card p-5" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Active Database</span>
            <Database size={18} color="var(--accent-violet)" />
          </div>
          <div style={{ fontSize: '1rem', fontWeight: 700, color: '#C084FC', marginTop: '6px' }}>PostgreSQL 16</div>
        </div>
      </div>

      {/* Active Project Progress Dashboard & Health Score */}
      {projects.length > 0 && (() => {
        const activeId = localStorage.getItem('active_project_id');
        const activeProj = projects.find((p) => String(p.id) === String(activeId)) || projects[0];
        return (
          <>
            <ProgressDashboard project={activeProj} />
            <ProjectHealthScoreCard projectId={activeProj.id} />
          </>
        );
      })()}

      {/* Projects List Section */}
      <div style={{ marginBottom: '16px' }}>
        <h2 style={{ fontSize: '1.35rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={18} color="var(--accent-cyan)" /> Project Architecture Portfolio
        </h2>

        {loading ? (
          <div style={{ display: 'grid', gap: '16px' }}>
            {[1, 2, 3].map((i) => (
              <div key={i} className="skeleton" style={{ height: '80px', borderRadius: '12px' }} />
            ))}
          </div>
        ) : projects.length === 0 ? (
          <div className="glass-card" style={{ padding: '48px', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>🚀</div>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '8px' }}>No Projects Created Yet</h3>
            <p style={{ maxWidth: '400px', margin: '0 auto 24px', fontSize: '0.9rem' }}>
              Create your first project or click "Seed Demo Project" to explore a pre-built e-commerce blueprint.
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
              <button onClick={handleSeedDemo} disabled={seeding} className="btn btn-secondary">
                Seed Demo Project
              </button>
              <button onClick={() => navigate('/projects/new')} className="btn btn-gradient">
                Create Project
              </button>
            </div>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '16px' }}>
            {projects.map((proj) => {
              const isDone = proj.status === 'completed' || proj.status === 'blueprint_done';
              const isTechSelected = proj.status === 'tech_selected';

              return (
                <motion.div
                  key={proj.id}
                  whileHover={{ translateY: -2 }}
                  onClick={() => {
                    localStorage.setItem('active_project_id', proj.id);
                    if (isDone) navigate(`/projects/${proj.id}/blueprint`);
                    else if (isTechSelected) navigate(`/projects/${proj.id}/architecture`);
                    else navigate(`/projects/${proj.id}/technology-selection`);
                  }}
                  className="glass-card glass-card-hover"
                  style={{
                    padding: '24px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '6px' }}>
                      <h3 style={{ fontSize: '1.15rem', margin: 0 }}>{proj.name}</h3>
                      {isDone ? (
                        <span className="badge badge-success">🔒 Blueprint Ready</span>
                      ) : isTechSelected ? (
                        <span className="badge badge-info">Stack Locked</span>
                      ) : (
                        <span className="badge badge-warning">Tech Selection Pending</span>
                      )}
                    </div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
                      {proj.description || proj.raw_idea?.slice(0, 120) || 'Project description...'}
                    </p>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <button
                      onClick={(e) => handleDeleteProject(proj.id, e)}
                      title="Delete Project"
                      className="btn btn-ghost btn-sm"
                      style={{ color: 'var(--text-muted)' }}
                    >
                      <Trash2 size={16} />
                    </button>
                    <ArrowRight size={20} color="var(--accent-cyan)" />
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
