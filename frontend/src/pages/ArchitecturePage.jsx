import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Layers,
  ArrowRight,
  ArrowLeft,
  Database,
  Cpu,
  Shield,
  Network,
  CheckCircle2,
  Lock,
  LayoutDashboard,
  ShieldAlert,
  Server,
  Code,
  Globe,
  Zap,
  Terminal,
  FileText,
  Ban,
} from 'lucide-react';
import api from '../services/api';
import { getErrorMessage } from '../utils/errors';
import MermaidDiagram from '../components/MermaidDiagram';
import InteractiveSystemTopology from '../components/InteractiveSystemTopology';

function buildDynamicMermaidDiagram(selectedTechs, rawDiagramDef) {
  const techMap = {};

  if (Array.isArray(selectedTechs)) {
    selectedTechs.forEach((t) => {
      if (t?.category && t?.name) {
        techMap[t.category.toLowerCase()] = t.name;
      }
    });
  } else if (typeof selectedTechs === 'object' && selectedTechs !== null) {
    Object.entries(selectedTechs).forEach(([cat, val]) => {
      techMap[cat.toLowerCase()] = typeof val === 'string' ? val : val?.name || String(val);
    });
  }

  const fe = techMap.frontend && techMap.frontend !== 'Not Required' ? techMap.frontend : 'Frontend App';
  const be = techMap.backend && techMap.backend !== 'Not Required' ? techMap.backend : 'Backend Service';
  const db = techMap.database && techMap.database !== 'Not Required' ? techMap.database : 'Database System';

  const auth = techMap.authentication && techMap.authentication !== 'Not Required' ? techMap.authentication : null;
  const aiml = techMap.ai_ml && techMap.ai_ml !== 'Not Required' ? techMap.ai_ml : null;
  const apiComm = techMap.api_communication && techMap.api_communication !== 'Not Required' ? techMap.api_communication : null;
  const cacheMsg = techMap.caching_messaging && techMap.caching_messaging !== 'Not Required' ? techMap.caching_messaging : null;
  const deploy = techMap.deployment && techMap.deployment !== 'Not Required' ? techMap.deployment : null;
  const devops = techMap.devops && techMap.devops !== 'Not Required' ? techMap.devops : null;

  // Sanitize strings for Mermaid node labels
  const sanitize = (str) => (str || '').replace(/[\[\]\(\)\{\}\"]+/g, '');

  let diagram = `graph TD\n`;
  diagram += `    FE["Frontend (${sanitize(fe)})"]\n`;
  diagram += `    BE["Backend (${sanitize(be)})"]\n`;
  diagram += `    DB[("Database (${sanitize(db)})")]\n`;

  if (apiComm) {
    diagram += `    FE -->|"${sanitize(apiComm)}"| BE\n`;
  } else {
    diagram += `    FE -->|"HTTP/REST"| BE\n`;
  }

  diagram += `    BE -->|"Data Query"| DB\n`;

  if (auth) {
    diagram += `    Auth["Auth (${sanitize(auth)})"]\n`;
    diagram += `    FE -.->|"Verify Token"| Auth\n`;
    diagram += `    BE -.->|"Validate Session"| Auth\n`;
  }

  if (cacheMsg) {
    diagram += `    Cache["Cache/Queue (${sanitize(cacheMsg)})"]\n`;
    diagram += `    BE -->|"In-Memory / Queue"| Cache\n`;
  }

  if (aiml) {
    diagram += `    AIML["AI/ML Service (${sanitize(aiml)})"]\n`;
    diagram += `    BE -->|"Inference Request"| AIML\n`;
  }

  if (deploy) {
    diagram += `\n    subgraph TargetPlatform ["Target Cloud Environment: ${sanitize(deploy)}"]\n`;
    diagram += `        FE\n        BE\n        DB\n`;
    if (auth) diagram += `        Auth\n`;
    if (cacheMsg) diagram += `        Cache\n`;
    if (aiml) diagram += `        AIML\n`;
    diagram += `    end\n`;
  }

  return diagram;
}

export default function ArchitecturePage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [arch, setArch] = useState(null);
  const [selectedTechs, setSelectedTechs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      localStorage.setItem('active_project_id', id);
      fetchArchitecture();
    }
  }, [id]);

  const fetchArchitecture = async () => {
    setLoading(true);
    setError('');
    try {
      const projRes = await api.get(`/api/projects/${id}`);
      setSelectedTechs(projRes.data.selected_technologies || []);

      const archRes = await api.get(`/api/projects/${id}/architecture`);
      setArch(archRes.data || {});
    } catch (err) {
      setError(
        getErrorMessage(
          err,
          'Architecture not generated yet. Complete Technology Selection first.'
        )
      );
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'grid', gap: '16px', maxWidth: '1280px', margin: '0 auto' }}>
        {[1, 2, 3].map((i) => (
          <div key={i} className="skeleton" style={{ height: '140px', borderRadius: '12px' }} />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card" style={{ padding: '48px', textAlign: 'center', maxWidth: '600px', margin: '40px auto' }}>
        <ShieldAlert size={48} color="var(--accent-rose)" style={{ marginBottom: '16px' }} />
        <h2 style={{ fontSize: '1.4rem', marginBottom: '8px' }}>Architecture Not Ready</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>{error}</p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
          <button onClick={() => navigate(`/projects/${id}/technology-selection`)} className="btn btn-secondary">
            Go to Technology Selection
          </button>
          <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
            <LayoutDashboard size={16} /> Dashboard
          </button>
        </div>
      </div>
    );
  }

  const diagrams = arch?.diagrams || {};
  const diagramDef = diagrams?.definition || (Array.isArray(diagrams) ? diagrams[0]?.definition : null);
  const diagramText = buildDynamicMermaidDiagram(selectedTechs, diagramDef);

  const sysArch = arch?.system_architecture || {};
  const componentsList = sysArch.components || arch?.components || [];

  return (
    <div style={{ maxWidth: '1360px', margin: '0 auto', paddingBottom: '80px' }}>
      
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <button onClick={() => navigate(`/projects/${id}/technology-selection`)} className="btn btn-secondary btn-sm" style={{ padding: '6px 12px' }}>
            <ArrowLeft size={15} /> Tech Selection
          </button>
          <div>
            <div className="badge badge-info" style={{ marginBottom: '4px' }}>
              <Layers size={12} /> Stage 03 / System Architecture Dashboard
            </div>
            <h1 style={{ fontSize: '2rem', margin: 0, fontWeight: 900 }}>
              System <span className="gradient-text-cyan">Architecture Topology</span>
            </h1>
          </div>
        </div>

        <button onClick={() => navigate(`/projects/${id}/tasks`)} className="btn btn-gradient btn-lg">
          Next: Agile Task Board <ArrowRight size={18} />
        </button>
      </div>

      {/* 1. LOCKED TECHNOLOGY STACK SUMMARY */}
      <div className="glass-card mb-6" style={{ padding: '20px', marginBottom: '24px', borderRadius: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Lock size={16} color="#34D399" />
            <span style={{ fontWeight: 800, fontSize: '0.85rem', color: '#34D399', letterSpacing: '0.05em' }}>
              LOCKED TECHNOLOGY STACK IN USE:
            </span>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Downstream agents build strictly using these choices
          </span>
        </div>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {selectedTechs.map((st) => {
            const isNotReq = st.name === 'Not Required';
            return (
              <span
                key={st.category}
                className={`badge ${isNotReq ? 'badge-secondary' : 'badge-success'}`}
                style={{
                  padding: '6px 12px',
                  fontSize: '0.8rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  background: isNotReq ? 'rgba(148, 163, 184, 0.15)' : undefined,
                  border: isNotReq ? '1px solid rgba(148, 163, 184, 0.3)' : undefined,
                }}
              >
                <span style={{ opacity: 0.7, textTransform: 'capitalize' }}>{st.category.replace(/_/g, ' ')}:</span>
                <strong>{st.name}</strong>
              </span>
            );
          })}
        </div>
      </div>

      {/* 2. SYSTEM ARCHITECTURE DIAGRAM */}
      <div className="glass-card" style={{ padding: '28px', marginBottom: '24px', borderRadius: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 800, margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Network size={20} color="var(--accent-cyan)" /> System Flowchart & Subsystem Topology
          </h3>
          <span className="badge badge-info" style={{ fontSize: '0.75rem' }}>
            Multi-Layer Interactive Topology
          </span>
        </div>

        <InteractiveSystemTopology selectedTechs={selectedTechs} architectureData={arch} projectId={id} />
      </div>

      {/* 3. ARCHITECTURE OVERVIEW */}
      <div className="glass-card" style={{ padding: '28px', marginBottom: '24px', borderRadius: '16px' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Server size={20} color="var(--accent-cyan)" /> High-Level Architecture Overview
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', lineHeight: 1.6, margin: 0 }}>
          {sysArch.overview || arch?.system_overview || 'System architecture specification compiled by Agent 3 for your locked technology selections.'}
        </p>
      </div>

      {/* 4. SUBSYSTEM COMPONENTS */}
      {componentsList.length > 0 && (
        <div className="glass-card" style={{ padding: '28px', marginBottom: '24px', borderRadius: '16px' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={20} color="var(--accent-violet)" /> Subsystem Components Breakdown
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))', gap: '16px' }}>
            {componentsList.map((comp, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(15, 23, 42, 0.75)',
                  padding: '18px',
                  borderRadius: '12px',
                  border: '1px solid var(--border-dark)',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--accent-cyan)', margin: 0 }}>
                      {comp.name || comp.component_name || `Component ${idx + 1}`}
                    </h4>
                    <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                      Subsystem
                    </span>
                  </div>

                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.45 }}>
                    {comp.description || comp.responsibilities || 'Specifies responsibilities, interface boundaries, and data dependencies.'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 5. DATABASE / API / DEPLOYMENT DETAILS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px' }}>
        {/* Frontend Architecture */}
        {(sysArch.frontend_architecture || arch?.frontend_architecture) && (
          <div className="glass-card" style={{ padding: '24px', borderRadius: '16px' }}>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--accent-cyan)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Code size={18} /> Frontend Client Architecture
            </h4>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              {typeof (sysArch.frontend_architecture || arch?.frontend_architecture) === 'string' ? (
                <p style={{ margin: 0 }}>{sysArch.frontend_architecture || arch?.frontend_architecture}</p>
              ) : (
                <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0, fontSize: '0.8rem' }}>
                  {JSON.stringify(sysArch.frontend_architecture || arch?.frontend_architecture, null, 2)}
                </pre>
              )}
            </div>
          </div>
        )}

        {/* Backend Architecture */}
        {(sysArch.backend_architecture || arch?.backend_architecture) && (
          <div className="glass-card" style={{ padding: '24px', borderRadius: '16px' }}>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--accent-violet)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Server size={18} /> Backend & Service Architecture
            </h4>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              {typeof (sysArch.backend_architecture || arch?.backend_architecture) === 'string' ? (
                <p style={{ margin: 0 }}>{sysArch.backend_architecture || arch?.backend_architecture}</p>
              ) : (
                <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0, fontSize: '0.8rem' }}>
                  {JSON.stringify(sysArch.backend_architecture || arch?.backend_architecture, null, 2)}
                </pre>
              )}
            </div>
          </div>
        )}

        {/* Database Design */}
        {(sysArch.database_design || arch?.database_design) && (
          <div className="glass-card" style={{ padding: '24px', borderRadius: '16px' }}>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#34D399', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Database size={18} /> Database Schema & Data Models
            </h4>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              {typeof (sysArch.database_design || arch?.database_design) === 'string' ? (
                <p style={{ margin: 0 }}>{sysArch.database_design || arch?.database_design}</p>
              ) : (
                <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0, fontSize: '0.8rem' }}>
                  {JSON.stringify(sysArch.database_design || arch?.database_design, null, 2)}
                </pre>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
