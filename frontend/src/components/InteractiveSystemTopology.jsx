import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Globe,
  Server,
  Shield,
  Search,
  Bot,
  Zap,
  Info,
  Database,
  Activity,
  FileText,
  Lock,
  Layers,
  ArrowRight,
  ArrowDown,
  Sparkles,
  CheckCircle2,
  Cpu,
  Calendar,
  Kanban,
  ShieldCheck,
  FileCheck,
} from 'lucide-react';

export default function InteractiveSystemTopology({ selectedTechs = [], architectureData = {}, projectId }) {
  // Extract locked tech map from selectedTechs
  const techMap = useMemo(() => {
    const map = {};
    if (Array.isArray(selectedTechs)) {
      selectedTechs.forEach((t) => {
        if (t?.category && t?.name) {
          map[t.category.toLowerCase()] = t.name;
        }
      });
    } else if (typeof selectedTechs === 'object' && selectedTechs !== null) {
      Object.entries(selectedTechs).forEach(([cat, val]) => {
        map[cat.toLowerCase()] = typeof val === 'string' ? val : val?.name || String(val);
      });
    }
    return map;
  }, [selectedTechs]);

  const feTech = techMap.frontend && techMap.frontend !== 'Not Required' ? techMap.frontend : 'React (Vite)';
  const beTech = techMap.backend && techMap.backend !== 'Not Required' ? techMap.backend : 'FastAPI (Python)';
  const dbTech = techMap.database && techMap.database !== 'Not Required' ? techMap.database : 'PostgreSQL';
  const authTech = techMap.authentication && techMap.authentication !== 'Not Required' ? techMap.authentication : 'JWT OAuth2 Bearer';

  // State for zoom and selection
  const [zoomLevel, setZoomLevel] = useState(1);
  const [selectedNodeId, setSelectedNodeId] = useState('agent_2');

  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 0.15, 1.4));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 0.15, 0.7));
  const handleResetView = () => setZoomLevel(1);

  // Component details dictionary
  const COMPONENT_DETAILS = {
    user: {
      title: 'User / Developer',
      section: 'SECTION 1 — USER & FRONTEND',
      tech: 'Browser / Client',
      color: '#38BDF8',
      desc: 'The human user who inputs raw project concepts, locks technologies, and interacts with the multi-agent dashboard.',
      inputs: ['Raw project description', 'Team size & target deadline', 'Refinement prompts'],
      outputs: ['HTTP user interactions', 'API requests'],
    },
    frontend: {
      title: 'React Frontend SPA',
      section: 'SECTION 1 — USER & FRONTEND',
      tech: feTech,
      color: '#38BDF8',
      desc: `Dynamic client SPA built with ${feTech}. Renders 7-stage interactive pipeline, SSE progress modals, task board, and blueprint downloads.`,
      inputs: ['User interactions', 'Backend REST responses', 'Live SSE stream events'],
      outputs: ['Axios HTTP Requests', 'JWT Authorization headers'],
    },
    auth: {
      title: 'JWT Authentication',
      section: 'SECTION 1 — USER & FRONTEND',
      tech: authTech,
      color: '#38BDF8',
      desc: `Secures routes and verifies session state using ${authTech}.`,
      inputs: ['User login credentials'],
      outputs: ['Bearer Access Tokens'],
    },
    sse: {
      title: 'SSE / Live Activity',
      section: 'SECTION 1 — USER & FRONTEND',
      tech: 'EventSource Stream',
      color: '#38BDF8',
      desc: 'Dispatches real-time agent execution notifications ("running", "completed", "failed") back to the user interface.',
      inputs: ['Agent step notifications'],
      outputs: ['Server-Sent Events (SSE)'],
    },

    backend: {
      title: 'FastAPI Backend',
      section: 'SECTION 2 — BACKEND & AI AGENTS',
      tech: beTech,
      color: '#818CF8',
      desc: `High-performance REST API gateway built with ${beTech}. Handles project creation, stage execution, chat, health score, and export endpoints.`,
      inputs: ['HTTP requests from Frontend'],
      outputs: ['Routed service calls', 'JSON responses'],
    },
    orchestrator: {
      title: 'Project Orchestrator',
      section: 'SECTION 2 — BACKEND & AI AGENTS',
      tech: 'AgentService (LangGraph Driver)',
      color: '#818CF8',
      desc: 'Coordinates the multi-agent execution pipeline, manages stage state transitions, and commits records to database.',
      inputs: ['Stage execution commands & project parameters'],
      outputs: ['LangGraph state dictionary', 'Database ORM commits'],
    },

    agent_1: {
      title: '1. Requirement Analyst Agent',
      section: 'SECTION 2 — BACKEND & AI AGENTS',
      tech: 'Specification Agent Node',
      color: '#06B6D4',
      desc: 'Parses raw project description into structured technical goals, key user features, team size, and deadline constraints.',
      inputs: ['Raw project description'],
      outputs: ['Structured requirements object'],
    },
    agent_2: {
      title: '2. Technology Advisor Agent',
      section: 'SECTION 2 — BACKEND & AI AGENTS',
      tech: 'Tech Selection Node',
      color: '#06B6D4',
      desc: 'Evaluates requirements, executes Tavily live web research for tech ecosystems, recommends alternatives, and enforces locked stack choices.',
      inputs: ['Requirements spec', 'Tavily web search results'],
      outputs: ['Technology options catalog & Locked tech stack'],
    },
    agent_3: {
      title: '3. Architecture Agent',
      section: 'SECTION 2 — BACKEND & AI AGENTS',
      tech: 'System Design Node',
      color: '#06B6D4',
      desc: 'Generates system architecture overview, subsystem breakdown, database schemas, and dynamic flowchart definitions from locked tech choices.',
      inputs: ['Requirements spec', 'Locked technology stack'],
      outputs: ['Architecture specification & Mermaid diagrams'],
    },
    agent_4: {
      title: '4. Task Planner Agent',
      section: 'SECTION 2 — BACKEND & AI AGENTS',
      tech: 'Agile Task Node',
      color: '#06B6D4',
      desc: 'Decomposes architecture into actionable agile development tasks, assigned developer roles, priority ratings, and estimated hours.',
      inputs: ['Architecture spec', 'Locked technology stack'],
      outputs: ['Agile task plan & role assignments'],
    },
    agent_5: {
      title: '5. Timeline & Resource Agent',
      section: 'SECTION 2 — BACKEND & AI AGENTS',
      tech: 'Gantt Schedule Node',
      color: '#06B6D4',
      desc: 'Calculates development phase dates, Gantt timeline entries, milestone target dates, and team developer resource allocations.',
      inputs: ['Agile task plan', 'Target deadline days'],
      outputs: ['Timeline schedule & milestone dates'],
    },
    agent_6: {
      title: '6. Critic & Risk Agent',
      section: 'SECTION 2 — BACKEND & AI AGENTS',
      tech: 'Risk Audit Node',
      color: '#06B6D4',
      desc: 'Audits overall project feasibility score (0-100), identifies critical technical & security risks, and generates mitigation strategies.',
      inputs: ['All upstream agent outputs'],
      outputs: ['Feasibility score & Risk matrix'],
    },
    agent_7: {
      title: '7. Final Blueprint Generator',
      section: 'SECTION 2 — BACKEND & AI AGENTS',
      tech: 'Master Document Finalizer',
      color: '#8B5CF6',
      desc: 'Synthesizes all 6 agent outputs into a comprehensive master blueprint document ready for PDF, JSON, and Markdown export.',
      inputs: ['Requirements, Tech Stack, Architecture, Tasks, Timeline, Risks'],
      outputs: ['Master Blueprint Document'],
    },

    tavily: {
      title: 'Tavily Web Search API',
      section: 'SECTION 3 — EXTERNAL SERVICES',
      tech: 'Live Web Research API',
      color: '#F59E0B',
      desc: 'Provides real-time web research, documentation sources, and library compatibility data directly to Agent 2 (Technology Advisor).',
      inputs: ['Tech search query from Agent 2'],
      outputs: ['Live documentation links & tech snippets'],
    },
    llm_fallback: {
      title: 'LLM Provider Fallback Chain',
      section: 'SECTION 3 — EXTERNAL SERVICES',
      tech: 'Groq → OpenRouter → Gemini',
      color: '#F59E0B',
      desc: 'Automated 3-tier fallback provider matrix. If Groq rate-limits (429), fails over to OpenRouter, then Google Gemini, maintaining 100% uptime.',
      inputs: ['Structured agent prompts'],
      outputs: ['Structured JSON Pydantic responses'],
    },

    database: {
      title: 'PostgreSQL Database Engine',
      section: 'SECTION 4 — DATA & STORAGE',
      tech: dbTech,
      color: '#34D399',
      desc: `Persistent relational data store running ${dbTech}. Persists users, raw ideas, locked tech choices, architecture schemas, tasks, timeline, risks, and final blueprint.`,
      inputs: ['SQL Queries & ORM commits from Orchestrator & Agents'],
      outputs: ['Persisted project records'],
    },
  };

  const activeDetail = COMPONENT_DETAILS[selectedNodeId] || COMPONENT_DETAILS.agent_2;

  return (
    <div style={{ width: '100%', position: 'relative' }}>
      {/* Top Viewport Control Bar */}
      <div
        className="diagram-controls"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          padding: '12px 18px',
          background: 'rgba(15, 23, 42, 0.95)',
          borderRadius: '12px',
          marginBottom: '16px',
          border: '1px solid var(--border-dark)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Layers size={16} /> System Flowchart Architecture (4 Sections)
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button onClick={handleZoomIn} className="btn btn-secondary btn-sm" title="Zoom In" style={{ padding: '6px 10px' }}>
            <ZoomIn size={14} />
          </button>
          <button onClick={handleZoomOut} className="btn btn-secondary btn-sm" title="Zoom Out" style={{ padding: '6px 10px' }}>
            <ZoomOut size={14} />
          </button>
          <button onClick={handleResetView} className="btn btn-secondary btn-sm" title="Reset View" style={{ padding: '6px 10px' }}>
            <RotateCcw size={14} /> Reset
          </button>
          <span className="badge badge-info" style={{ fontSize: '0.72rem' }}>
            {Math.round(zoomLevel * 100)}%
          </span>
        </div>
      </div>

      {/* Main Flowchart Canvas Container */}
      <div
        style={{
          width: '100%',
          padding: '24px',
          background: 'radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.98) 0%, rgba(6, 9, 17, 0.99) 100%)',
          borderRadius: '16px',
          border: '1px solid var(--border-medium)',
          boxSizing: 'border-box',
          overflowX: 'auto',
        }}
      >
        {/* Transform Box for Zoom */}
        <div
          style={{
            transform: `scale(${zoomLevel})`,
            transformOrigin: 'top center',
            transition: 'transform 0.2s cubic-bezier(0.2, 0, 0, 1)',
            display: 'flex',
            flexDirection: 'column',
            gap: '24px',
            maxWidth: '1100px',
            margin: '0 auto',
          }}
        >
          {/* SECTION 1 — USER & FRONTEND */}
          <div
            style={{
              background: 'rgba(56, 189, 248, 0.03)',
              border: '1.5px dashed rgba(56, 189, 248, 0.35)',
              borderRadius: '14px',
              padding: '20px',
            }}
          >
            <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#38BDF8', textTransform: 'uppercase', marginBottom: '14px', letterSpacing: '0.05em' }}>
              SECTION 1 — USER & FRONTEND
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px' }}>
              <ComponentCard
                id="user"
                title="User / Developer"
                tech="Browser Client"
                subText="Enters idea & parameters"
                color="#38BDF8"
                icon={Globe}
                isSelected={selectedNodeId === 'user'}
                onClick={() => setSelectedNodeId('user')}
              />
              <ComponentCard
                id="frontend"
                title="React Frontend"
                tech={feTech}
                subText="Single Page App & Dashboards"
                color="#38BDF8"
                icon={Globe}
                isSelected={selectedNodeId === 'frontend'}
                onClick={() => setSelectedNodeId('frontend')}
              />
              <ComponentCard
                id="auth"
                title="JWT Authentication"
                tech={authTech}
                subText="Security & Token Management"
                color="#38BDF8"
                icon={Shield}
                isSelected={selectedNodeId === 'auth'}
                onClick={() => setSelectedNodeId('auth')}
              />
              <ComponentCard
                id="sse"
                title="SSE / Live Activity"
                tech="EventSource Stream"
                subText="Real-time execution updates"
                color="#38BDF8"
                icon={Activity}
                isSelected={selectedNodeId === 'sse'}
                onClick={() => setSelectedNodeId('sse')}
              />
            </div>
          </div>

          {/* DOWN ARROW CONNECTOR */}
          <div style={{ display: 'flex', justifyContent: 'center', margin: '-8px 0' }}>
            <div style={{ background: 'rgba(99, 102, 241, 0.2)', padding: '6px 16px', borderRadius: '20px', border: '1px solid rgba(99, 102, 241, 0.4)', display: 'flex', alignItems: 'center', gap: '8px', color: '#818CF8', fontSize: '0.78rem', fontWeight: 700 }}>
              <span>HTTP / REST API Requests</span>
              <ArrowDown size={14} />
            </div>
          </div>

          {/* MAIN 2-COLUMN GRID (SECTION 2 LEFT/CENTER & SECTION 3 RIGHT) */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
            {/* SECTION 2 — BACKEND & AI AGENTS */}
            <div
              style={{
                background: 'rgba(99, 102, 241, 0.03)',
                border: '1.5px dashed rgba(99, 102, 241, 0.35)',
                borderRadius: '14px',
                padding: '20px',
              }}
            >
              <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#818CF8', textTransform: 'uppercase', marginBottom: '14px', letterSpacing: '0.05em' }}>
                SECTION 2 — BACKEND & AI AGENTS (7 STAGES)
              </div>

              {/* FastAPI Gateway & Orchestrator Header Row */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '16px' }}>
                <ComponentCard
                  id="backend"
                  title="FastAPI Backend"
                  tech={beTech}
                  subText="REST API Gateway Router"
                  color="#818CF8"
                  icon={Server}
                  isSelected={selectedNodeId === 'backend'}
                  onClick={() => setSelectedNodeId('backend')}
                />
                <ComponentCard
                  id="orchestrator"
                  title="Project Orchestrator"
                  tech="AgentService & LangGraph"
                  subText="Drives Agent Execution Pipeline"
                  color="#818CF8"
                  icon={Server}
                  isSelected={selectedNodeId === 'orchestrator'}
                  onClick={() => setSelectedNodeId('orchestrator')}
                />
              </div>

              <div style={{ textAlign: 'center', color: '#06B6D4', fontSize: '0.75rem', fontWeight: 700, margin: '8px 0', textTransform: 'uppercase' }}>
                ↓ Sequential Agent Execution Workflow (Stages 1 → 7)
              </div>

              {/* 7 Vertical Agent Pipeline Cards */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {[
                  { id: 'agent_1', title: '1. Requirement Analyst Agent', stage: '[1]', tech: 'Specification Agent', subText: 'Parses raw idea into technical goals & scope', icon: Bot },
                  { id: 'agent_2', title: '2. Technology Advisor Agent', stage: '[2]', tech: 'Tech Selection Agent', subText: 'Researches web tech & locks stack choices', icon: Cpu, badge: 'Connects to Tavily →' },
                  { id: 'agent_3', title: '3. Architecture Agent', stage: '[3]', tech: 'System Design Agent', subText: 'Designs subsystem topology & database schemas', icon: Layers },
                  { id: 'agent_4', title: '4. Task Planner Agent', stage: '[4]', tech: 'Agile Task Agent', subText: 'Decomposes architecture into developer tasks', icon: Kanban },
                  { id: 'agent_5', title: '5. Timeline & Resource Agent', stage: '[5]', tech: 'Gantt Schedule Agent', subText: 'Schedules milestone dates & team allocations', icon: Calendar },
                  { id: 'agent_6', title: '6. Critic & Risk Agent', stage: '[6]', tech: 'Risk Audit Agent', subText: 'Audits feasibility score (0-100) & mitigations', icon: ShieldCheck },
                  { id: 'agent_7', title: '7. Final Blueprint Generator', stage: '[7]', tech: 'Master Document Finalizer', subText: 'Compiles master specification document', icon: FileCheck, color: '#8B5CF6' },
                ].map((ag) => (
                  <ComponentCard
                    key={ag.id}
                    id={ag.id}
                    title={ag.title}
                    tech={ag.tech}
                    subText={ag.subText}
                    color={ag.color || '#06B6D4'}
                    icon={ag.icon}
                    badge={ag.badge}
                    isSelected={selectedNodeId === ag.id}
                    onClick={() => setSelectedNodeId(ag.id)}
                  />
                ))}
              </div>
            </div>

            {/* SECTION 3 — EXTERNAL SERVICES (RIGHT COLUMN) */}
            <div
              style={{
                background: 'rgba(245, 158, 11, 0.03)',
                border: '1.5px dashed rgba(245, 158, 11, 0.35)',
                borderRadius: '14px',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '16px',
              }}
            >
              <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#FBBF24', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                SECTION 3 — EXTERNAL SERVICES
              </div>

              {/* Tavily Web Search Card */}
              <div
                style={{
                  background: 'rgba(245, 158, 11, 0.06)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  borderRadius: '12px',
                  padding: '16px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <Search size={18} color="#FBBF24" />
                  <span style={{ fontSize: '0.9rem', fontWeight: 800, color: '#FFF' }}>Tavily Web Search API</span>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#FBBF24', fontWeight: 700, marginBottom: '6px' }}>
                  ➜ Connected to 2. Technology Advisor
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
                  Provides real-time web research, documentation links, and library benchmarks directly during Stage 2.
                </p>
              </div>

              {/* LLM Provider Fallback Chain Card */}
              <div
                style={{
                  background: 'rgba(245, 158, 11, 0.06)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  borderRadius: '12px',
                  padding: '16px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                  <Zap size={18} color="#FBBF24" />
                  <span style={{ fontSize: '0.9rem', fontWeight: 800, color: '#FFF' }}>LLM Fallback Chain</span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#38BDF8', fontWeight: 700, background: 'rgba(9, 13, 22, 0.6)', padding: '6px 10px', borderRadius: '6px' }}>
                    <span>1. Groq AI (Primary Llama-3)</span>
                  </div>
                  <div style={{ textAlign: 'center', fontSize: '0.7rem', color: '#FBBF24', fontWeight: 800 }}>↓ 429 Failover</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#A855F7', fontWeight: 700, background: 'rgba(9, 13, 22, 0.6)', padding: '6px 10px', borderRadius: '6px' }}>
                    <span>2. OpenRouter Gateway</span>
                  </div>
                  <div style={{ textAlign: 'center', fontSize: '0.7rem', color: '#FBBF24', fontWeight: 800 }}>↓ Backup Failover</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#10B981', fontWeight: 700, background: 'rgba(9, 13, 22, 0.6)', padding: '6px 10px', borderRadius: '6px' }}>
                    <span>3. Google Gemini 1.5/2.0</span>
                  </div>
                </div>

                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
                  Automated multi-provider AI resilience matrix ensuring 100% agent execution uptime.
                </p>
              </div>
            </div>
          </div>

          {/* DOWN ARROW CONNECTOR */}
          <div style={{ display: 'flex', justifyContent: 'center', margin: '-6px 0' }}>
            <div style={{ background: 'rgba(16, 185, 129, 0.2)', padding: '6px 16px', borderRadius: '20px', border: '1px solid rgba(16, 185, 129, 0.4)', display: 'flex', alignItems: 'center', gap: '8px', color: '#34D399', fontSize: '0.78rem', fontWeight: 700 }}>
              <span>ORM Persistence & Storage Commitment</span>
              <ArrowDown size={14} />
            </div>
          </div>

          {/* SECTION 4 — DATA & STORAGE (BOTTOM SECTION) */}
          <div
            style={{
              background: 'rgba(16, 185, 129, 0.03)',
              border: '1.5px dashed rgba(16, 185, 129, 0.35)',
              borderRadius: '14px',
              padding: '20px',
            }}
          >
            <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#34D399', textTransform: 'uppercase', marginBottom: '12px', letterSpacing: '0.05em' }}>
              SECTION 4 — DATA & STORAGE ({dbTech})
            </div>

            <div
              onClick={() => setSelectedNodeId('database')}
              style={{
                background: selectedNodeId === 'database' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(9, 13, 22, 0.7)',
                border: selectedNodeId === 'database' ? '2px solid #34D399' : '1px solid rgba(16, 185, 129, 0.3)',
                borderRadius: '12px',
                padding: '16px',
                cursor: 'pointer',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                <Database size={22} color="#34D399" />
                <div>
                  <h4 style={{ fontSize: '1rem', fontWeight: 800, color: '#FFF', margin: 0 }}>PostgreSQL Database Engine</h4>
                  <span style={{ fontSize: '0.75rem', color: '#34D399', fontWeight: 600 }}>Relational Data Persistence Layer</span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {['User Profiles', 'Project Specs', 'Requirements', 'Locked Tech Choices', 'Architecture Schemas', 'Agile Tasks', 'Gantt Timelines', 'Risk Audits', 'Final Blueprint'].map((m) => (
                  <span key={m} className="badge badge-emerald" style={{ fontSize: '0.72rem', padding: '3px 8px' }}>
                    ✓ {m}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* SYSTEM WORKFLOW SUMMARY BAR */}
      <div
        className="glass-card"
        style={{
          padding: '14px 20px',
          marginTop: '16px',
          background: 'rgba(15, 23, 42, 0.8)',
          borderRadius: '14px',
          border: '1px solid var(--border-dark)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', flexWrap: 'wrap', fontSize: '0.8rem', fontWeight: 700 }}>
          <span style={{ color: 'var(--text-muted)' }}>How the system works:</span>
          <span style={{ color: '#38BDF8' }}>User</span> ➔
          <span style={{ color: '#38BDF8' }}>Frontend</span> ➔
          <span style={{ color: '#818CF8' }}>Backend</span> ➔
          <span style={{ color: '#06B6D4' }}>AI Agents</span> ➔
          <span style={{ color: '#FBBF24' }}>External Services / LLMs</span> ➔
          <span style={{ color: '#34D399' }}>Database</span> ➔
          <span style={{ color: '#C084FC' }}>Final Blueprint</span>
        </div>
      </div>

      {/* SIMPLE COMPONENT DETAILS INSPECTOR PANEL */}
      <div className="glass-card" style={{ padding: '20px 24px', marginTop: '16px', background: 'rgba(15, 23, 42, 0.95)', borderRadius: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', borderBottom: '1px solid var(--border-dark)', paddingBottom: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: activeDetail.color }} />
            <div>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                {activeDetail.section}
              </span>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 900, color: '#FFF', margin: 0 }}>
                {activeDetail.title}
              </h3>
            </div>
          </div>

          <span className="badge badge-purple" style={{ fontSize: '0.78rem', padding: '5px 12px' }}>
            Technology: {activeDetail.tech}
          </span>
        </div>

        <p style={{ color: 'var(--text-main)', fontSize: '0.9rem', lineHeight: 1.5, marginBottom: '14px' }}>
          {activeDetail.desc}
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
          <div style={{ background: 'rgba(9, 13, 22, 0.6)', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--border-dark)' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--accent-cyan)', textTransform: 'uppercase', display: 'block', marginBottom: '4px' }}>
              📥 Data Inputs:
            </span>
            <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              {activeDetail.inputs.map((inp, idx) => (
                <li key={idx}>{inp}</li>
              ))}
            </ul>
          </div>

          <div style={{ background: 'rgba(9, 13, 22, 0.6)', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--border-dark)' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#34D399', textTransform: 'uppercase', display: 'block', marginBottom: '4px' }}>
              📤 Data Outputs:
            </span>
            <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              {activeDetail.outputs.map((out, idx) => (
                <li key={idx}>{out}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

function ComponentCard({ id, title, tech, subText, color, icon: Icon, badge, isSelected, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        padding: '12px 14px',
        borderRadius: '10px',
        background: isSelected ? 'rgba(30, 41, 59, 0.95)' : 'rgba(9, 13, 22, 0.75)',
        border: isSelected ? `2.5px solid ${color}` : '1px solid rgba(255, 255, 255, 0.1)',
        boxShadow: isSelected ? `0 0 20px ${color}40` : 'none',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '10px',
        transition: 'all 0.15s ease',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', overflow: 'hidden' }}>
        <div
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: `${color}20`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <Icon size={18} color={color} />
        </div>

        <div style={{ overflow: 'hidden' }}>
          <div style={{ fontSize: '0.82rem', fontWeight: 800, color: '#FFF', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {title}
          </div>
          <div style={{ fontSize: '0.72rem', color: color, fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {tech}
          </div>
          {subText && (
            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {subText}
            </div>
          )}
        </div>
      </div>

      {badge && (
        <span className="badge badge-warning" style={{ fontSize: '0.65rem', flexShrink: 0, padding: '2px 6px' }}>
          {badge}
        </span>
      )}
    </div>
  );
}
