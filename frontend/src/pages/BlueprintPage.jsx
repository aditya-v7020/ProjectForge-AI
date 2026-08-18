import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BookOpen, Printer, ArrowLeft, Lock, Cpu, Layers, Kanban, Calendar, ShieldAlert, LayoutDashboard, Database, Server, Code, Users, Flag, AlertTriangle, Zap, CheckCircle2, Download, FileText } from 'lucide-react';
import api from '../services/api';
import { getErrorMessage } from '../utils/errors';
import CostEstimationCard from '../components/CostEstimationCard';
import InteractiveSystemTopology from '../components/InteractiveSystemTopology';

export default function BlueprintPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [blueprint, setBlueprint] = useState(null);
  const [projectData, setProjectData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      localStorage.setItem('active_project_id', id);
      fetchBlueprintData();
    }
  }, [id]);

  const fetchBlueprintData = async () => {
    setLoading(true);
    setError('');
    try {
      const [bpRes, projRes] = await Promise.all([
        api.get(`/api/projects/${id}/blueprint`),
        api.get(`/api/projects/${id}`),
      ]);
      setBlueprint(bpRes.data || {});
      setProjectData(projRes.data || {});
    } catch (err) {
      setError(getErrorMessage(err, 'Complete project blueprint is being compiled.'));
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExport = async (format) => {
    try {
      const res = await api.get(`/api/projects/${id}/export/${format}`);
      const data = res.data;
      let blob;
      if (format === 'json') {
        blob = new Blob([JSON.stringify(data.data, null, 2)], { type: 'application/json' });
      } else {
        blob = new Blob([data.content], { type: data.content_type || 'text/plain' });
      }
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = data.filename || `blueprint.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert(`Export failed for format ${format}`);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'grid', gap: '16px', maxWidth: '1280px', margin: '0 auto' }}>
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="skeleton" style={{ height: '180px', borderRadius: '12px' }} />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card" style={{ padding: '48px', textAlign: 'center', maxWidth: '600px', margin: '40px auto' }}>
        <ShieldAlert size={48} color="var(--accent-rose)" style={{ marginBottom: '16px' }} />
        <h2 style={{ fontSize: '1.4rem', marginBottom: '8px' }}>Blueprint Compilation Pending</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
          {error}
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
          <button onClick={() => navigate(`/projects/${id}/risks`)} className="btn btn-secondary">
            Go to Risk Analysis
          </button>
          <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
            <LayoutDashboard size={16} /> Dashboard
          </button>
        </div>
      </div>
    );
  }

  const content = blueprint?.content || blueprint || {};
  const reqs = content.requirements || projectData?.requirements || {};

  const selectedTechObj = content.selected_technology_stack || projectData?.selected_technologies || {};
  const selectedTechs = Array.isArray(selectedTechObj)
    ? selectedTechObj
    : Object.entries(selectedTechObj).map(([cat, name]) => ({
        category: cat,
        name: typeof name === 'string' ? name : name?.name || String(name),
      }));

  const arch = content.system_architecture || content.architecture || {};
  const tasks = content.development_tasks || content.tasks || [];
  const timeline = content.timeline || content.schedule || [];
  const risks = content.risk_analysis || content.risks || [];
  const critique = content.critique || content.critique_summary || {};
  const milestones = content.milestones || [];
  const teamAlloc = content.team_allocation || [];

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', paddingBottom: '80px' }}>
      {/* Top Banner Navigation */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '32px', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button onClick={() => navigate(`/projects/${id}/risks`)} className="btn btn-secondary btn-sm" style={{ padding: '8px 14px' }}>
            <ArrowLeft size={16} /> Back: Risk Analysis
          </button>
          <div>
            <div className="badge badge-info" style={{ marginBottom: '6px' }}>
              <BookOpen size={12} /> Stage 07 / Final Blueprint Delivery
            </div>
            <h1 style={{ fontSize: '2rem', margin: 0 }}>
              Master <span className="gradient-text-cyan">Project Blueprint</span>
            </h1>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <button onClick={() => handleExport('json')} className="btn btn-secondary btn-md">
            <Download size={16} /> Export JSON
          </button>
          <button onClick={() => handleExport('markdown')} className="btn btn-secondary btn-md">
            <FileText size={16} /> Export Markdown
          </button>
          <button onClick={handlePrint} className="btn btn-gradient btn-md">
            <Printer size={16} /> Export / Print PDF
          </button>
        </div>
      </div>

      {/* Printable Document Container */}
      <div className="printable-document glass-card" style={{ padding: '40px', background: 'rgba(15, 23, 42, 0.95)', border: '1px solid var(--border-medium)', borderRadius: '20px' }}>
        {/* Document Header */}
        <div style={{ borderBottom: '2px solid var(--border-dark)', paddingBottom: '24px', marginBottom: '32px' }}>
          <h2 style={{ fontSize: '2.2rem', fontWeight: 900, color: '#FFF', margin: '0 0 8px 0' }}>
            {projectData?.name || blueprint?.project_overview?.name || 'Project Blueprint'}
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '1rem', margin: '0 0 16px 0', lineHeight: 1.5 }}>
            {projectData?.description || blueprint?.project_overview?.description || 'Automated multi-agent architecture and project specification.'}
          </p>

          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            {reqs.complexity && (
              <span className="badge badge-purple" style={{ fontSize: '0.8rem' }}>
                Complexity: {reqs.complexity}
              </span>
            )}
            {reqs.team_size && (
              <span className="badge badge-info" style={{ fontSize: '0.8rem' }}>
                Team Size: {reqs.team_size} members
              </span>
            )}
            {reqs.deadline_days && (
              <span className="badge badge-warning" style={{ fontSize: '0.8rem' }}>
                Target: {reqs.deadline_days} Days
              </span>
            )}
          </div>
        </div>

        {/* Feature 7: Cost Estimation */}
        <CostEstimationCard projectId={id} />

        {/* Section 1: Locked Technology Stack */}
        <section style={{ marginBottom: '40px' }}>
          <h3 style={{ fontSize: '1.25rem', color: 'var(--accent-cyan)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Lock size={20} /> 1. Locked Technology Stack
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
            {selectedTechs.map((st) => (
              <div key={st.category} style={{ background: 'rgba(9, 13, 22, 0.7)', padding: '12px 16px', borderRadius: '10px', border: '1px solid var(--border-dark)' }}>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase', display: 'block' }}>{st.category}</span>
                <strong style={{ fontSize: '1rem', color: '#34D399' }}>{st.name}</strong>
              </div>
            ))}
          </div>
        </section>

        {/* Section 2: Requirements Summary */}
        {(reqs.features || reqs.goals) && (
          <section style={{ marginBottom: '40px' }}>
            <h3 style={{ fontSize: '1.25rem', color: 'var(--accent-cyan)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={20} /> 2. Project Requirements & Goals
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
              {reqs.goals && (
                <div style={{ background: 'rgba(9, 13, 22, 0.5)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-dark)' }}>
                  <h4 style={{ fontSize: '0.95rem', color: 'var(--accent-amber)', margin: '0 0 8px 0' }}>Core Goals</h4>
                  <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    {(Array.isArray(reqs.goals) ? reqs.goals : [reqs.goals]).map((g, i) => (
                      <li key={i}>{g}</li>
                    ))}
                  </ul>
                </div>
              )}
              {reqs.features && (
                <div style={{ background: 'rgba(9, 13, 22, 0.5)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-dark)' }}>
                  <h4 style={{ fontSize: '0.95rem', color: 'var(--accent-cyan)', margin: '0 0 8px 0' }}>Key Features</h4>
                  <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    {(Array.isArray(reqs.features) ? reqs.features : [reqs.features]).map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </section>
        )}

        {/* Section 3: Architecture Overview & Diagram */}
        <section style={{ marginBottom: '40px' }}>
          <h3 style={{ fontSize: '1.25rem', color: 'var(--accent-cyan)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={20} /> 3. System Architecture Specification & Topology
          </h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '20px', lineHeight: 1.6 }}>
            {arch?.overview || arch?.system_overview || 'System architecture specified for your locked technology selections.'}
          </p>

          {arch && (arch.overview || arch.system_overview || arch.subsystems || arch.diagrams || Object.keys(arch).length > 0) ? (
            <div style={{ padding: '20px', background: 'rgba(9, 13, 22, 0.8)', borderRadius: '12px', border: '1px solid var(--border-dark)' }}>
              <InteractiveSystemTopology selectedTechs={selectedTechs} architectureData={arch} projectId={id} />
            </div>
          ) : (
            <div style={{ padding: '30px', textAlign: 'center', background: 'rgba(9, 13, 22, 0.7)', borderRadius: '12px', border: '1px solid var(--border-dark)' }}>
              <Layers size={36} color="var(--accent-amber)" style={{ marginBottom: '12px' }} />
              <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', margin: 0 }}>
                Architecture has not been generated yet. Complete the Architecture stage to view it here.
              </p>
            </div>
          )}
        </section>

        {/* Section 4: Tasks Backlog */}
        <section style={{ marginBottom: '40px' }}>
          <h3 style={{ fontSize: '1.25rem', color: 'var(--accent-cyan)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Kanban size={20} /> 4. Development Tasks ({tasks.length} Tasks)
          </h3>
          <div style={{ display: 'grid', gap: '10px' }}>
            {tasks.map((t, idx) => (
              <div key={idx} style={{ padding: '12px 16px', background: 'rgba(9, 13, 22, 0.5)', borderRadius: '8px', border: '1px solid var(--border-dark)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                <div>
                  <strong style={{ fontSize: '0.9rem', color: 'var(--text-main)' }}>{t.title}</strong>
                  {t.assigned_role && (
                    <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', marginLeft: '10px' }}>
                      ({t.assigned_role})
                    </span>
                  )}
                </div>
                <span className="badge badge-info">{t.estimated_hours || 4} Hours</span>
              </div>
            ))}
          </div>
        </section>

        {/* Section 5: Timeline & Execution Schedule */}
        {timeline.length > 0 && (
          <section style={{ marginBottom: '40px' }}>
            <h3 style={{ fontSize: '1.25rem', color: 'var(--accent-cyan)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Calendar size={20} /> 5. Execution Schedule & Timeline
            </h3>
            <div style={{ display: 'grid', gap: '10px' }}>
              {timeline.map((entry, idx) => (
                <div key={idx} style={{ padding: '12px 16px', background: 'rgba(9, 13, 22, 0.5)', borderRadius: '8px', border: '1px solid var(--border-dark)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{entry.title || entry.task_id || `Task ${idx + 1}`}</span>
                  <span className="badge badge-success">Day {entry.start_day || 1} → Day {entry.end_day || 5}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Section 6: Risk Audit */}
        {risks.length > 0 && (
          <section>
            <h3 style={{ fontSize: '1.25rem', color: 'var(--accent-cyan)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldAlert size={20} /> 6. Quality Audit & Risk Mitigations
            </h3>
            <div style={{ display: 'grid', gap: '12px' }}>
              {risks.map((r, idx) => (
                <div key={idx} style={{ padding: '14px', background: 'rgba(9, 13, 22, 0.5)', borderRadius: '8px', border: '1px solid var(--border-dark)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <strong>{r.category ? `Category: ${r.category}` : r.title || `Risk #${idx + 1}`}</strong>
                    <span className="badge badge-warning">{r.severity?.toUpperCase() || 'MEDIUM'}</span>
                  </div>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0 0 8px 0', lineHeight: 1.4 }}>
                    {r.explanation || r.description || r.risk}
                  </p>
                  {r.mitigation && (
                    <div style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>
                      <strong>Mitigation: </strong> {r.mitigation}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
