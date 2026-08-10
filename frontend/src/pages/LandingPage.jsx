import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Sparkles,
  ArrowRight,
  Bot,
  Cpu,
  Layers,
  Kanban,
  Calendar,
  ShieldCheck,
  CheckCircle2,
  Lock,
  Search,
  MessageSquare,
  FileText,
  Download,
  Activity,
  Zap,
  LayoutDashboard,
  BarChart2,
  FileCheck,
  ChevronRight,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LandingPage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleStart = () => {
    if (user) {
      navigate('/projects/new');
    } else {
      navigate('/register');
    }
  };

  const handleDemo = () => {
    if (user) {
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };

  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  // 7 Specialized AI Agents
  const agents = [
    {
      name: 'Requirement Analyst',
      stage: 'Stage 01',
      desc: 'Synthesizes raw ideas into explicit goals, user stories, team size, and constraints.',
      color: '#38BDF8',
      icon: Bot,
    },
    {
      name: 'Technology Advisor',
      stage: 'Stage 02',
      desc: 'Researches web tech options via Tavily, evaluates alternatives, and locks stack choices.',
      color: '#A855F7',
      icon: Cpu,
    },
    {
      name: 'Architecture Agent',
      stage: 'Stage 03',
      desc: 'Designs subsystem component topology, API endpoints, database schemas, and flowcharts.',
      color: '#06B6D4',
      icon: Layers,
    },
    {
      name: 'Task Planner',
      stage: 'Stage 04',
      desc: 'Decomposes architecture into actionable agile development tasks and assigned roles.',
      color: '#EC4899',
      icon: Kanban,
    },
    {
      name: 'Timeline & Resource Agent',
      stage: 'Stage 05',
      desc: 'Calculates development phase dates, Gantt milestones, and effort allocations.',
      color: '#F59E0B',
      icon: Calendar,
    },
    {
      name: 'Critic & Risk Agent',
      stage: 'Stage 06',
      desc: 'Audits project feasibility score (0-100), identifies risks, and suggests mitigations.',
      color: '#10B981',
      icon: ShieldCheck,
    },
    {
      name: 'Final Blueprint Generator',
      stage: 'Stage 07',
      desc: 'Compiles master specification document for PDF, Markdown, and JSON export.',
      color: '#8B5CF6',
      icon: FileCheck,
    },
  ];

  // 10 Key Features
  const featuresList = [
    {
      title: 'Live Technology Research',
      desc: 'Integrates Tavily AI search to gather real-time documentation, benchmarks, and compatibility data.',
      icon: Search,
    },
    {
      title: 'Interactive Architecture Flowchart',
      desc: '5-layer directional system topology with component inspection and connection highlighting.',
      icon: Layers,
    },
    {
      title: 'AI Task Planning',
      desc: 'Decomposes system design into agile task cards with estimated hours, priority, and assigned roles.',
      icon: Kanban,
    },
    {
      title: 'Timeline & Resource Planning',
      desc: 'Calculates milestone target dates, Gantt execution schedules, and developer labor allocation.',
      icon: Calendar,
    },
    {
      title: 'Risk Analysis & Audit',
      desc: 'Identifies technical, security, and scalability risks with one-click AI mitigation suggestions.',
      icon: ShieldCheck,
    },
    {
      title: 'Project Health Score',
      desc: 'Evaluates overall project feasibility across 6 technical, complexity, and resource factors.',
      icon: Activity,
    },
    {
      title: 'AI Project Chat',
      desc: 'Context-aware floating assistant to answer instant questions about requirements, stack, or schedule.',
      icon: MessageSquare,
    },
    {
      title: 'Export PDF / Markdown / JSON',
      desc: 'One-click export of complete project specifications for team sharing or client presentations.',
      icon: Download,
    },
    {
      title: 'Save & Resume Workflows',
      desc: 'Persists user session state and locked technology choices seamlessly across user sessions.',
      icon: Zap,
    },
    {
      title: 'Technology Comparison',
      desc: 'Side-by-side comparison modal evaluating recommended stack options against alternative choices.',
      icon: BarChart2,
    },
  ];

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#090D16', color: 'var(--text-main)', fontFamily: 'var(--font-sans)' }}>
      {/* 1. HEADER (Navbar) */}
      <nav
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '16px 40px',
          borderBottom: '1px solid var(--border-dark)',
          position: 'sticky',
          top: 0,
          zIndex: 100,
          background: 'rgba(9, 13, 22, 0.92)',
          backdropFilter: 'blur(12px)',
        }}
      >
        {/* Brand */}
        <div onClick={() => navigate('/')} style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
          <div
            style={{
              width: '34px',
              height: '34px',
              borderRadius: '8px',
              background: 'var(--gradient-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Sparkles size={18} color="#FFF" />
          </div>
          <span style={{ fontWeight: 800, fontSize: '1.2rem', color: '#FFF' }}>
            ProjectForge <span className="gradient-text-cyan">AI</span>
          </span>
        </div>

        {/* Navigation Links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '28px', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          <span onClick={() => scrollToSection('how-it-works')} style={{ cursor: 'pointer', transition: 'color 0.2s' }} className="nav-link-hover">
            How It Works
          </span>
          <span onClick={() => scrollToSection('ai-agents')} style={{ cursor: 'pointer', transition: 'color 0.2s' }} className="nav-link-hover">
            AI Agents
          </span>
          <span onClick={() => scrollToSection('features')} style={{ cursor: 'pointer', transition: 'color 0.2s' }} className="nav-link-hover">
            Features
          </span>
          <span onClick={handleDemo} style={{ cursor: 'pointer', transition: 'color 0.2s' }} className="nav-link-hover">
            Demo
          </span>
        </div>

        {/* Right CTA */}
        <div>
          {user ? (
            <button onClick={() => navigate('/dashboard')} className="btn btn-primary btn-sm">
              <LayoutDashboard size={14} /> Go to Dashboard
            </button>
          ) : (
            <div style={{ display: 'flex', gap: '10px' }}>
              <button onClick={() => navigate('/login')} className="btn btn-ghost btn-sm">
                Sign In
              </button>
              <button onClick={() => navigate('/register')} className="btn btn-gradient btn-sm">
                Get Started →
              </button>
            </div>
          )}
        </div>
      </nav>

      {/* 2. HERO SECTION */}
      <section style={{ maxWidth: '1100px', margin: '0 auto', padding: '80px 24px 60px', textAlign: 'center' }}>
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <span className="badge badge-info" style={{ marginBottom: '20px', padding: '6px 14px', fontSize: '0.8rem' }}>
            <Sparkles size={13} /> Autonomous AI Engineering & Architecture Platform
          </span>

          <h1 style={{ fontSize: '3.1rem', fontWeight: 900, lineHeight: 1.15, marginBottom: '20px', color: '#FFF', letterSpacing: '-0.02em' }}>
            Turn Your Project Idea Into a <br />
            <span className="gradient-text">Complete Development Blueprint</span>
          </h1>

          <p style={{ fontSize: '1.1rem', color: 'var(--text-muted)', maxWidth: '780px', margin: '0 auto 32px', lineHeight: 1.6 }}>
            ProjectForge AI uses specialized AI agents to analyze requirements, select technologies, design architecture, plan development tasks, estimate timelines, identify risks, and generate a final project blueprint.
          </p>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '14px', marginBottom: '40px' }}>
            <button onClick={handleStart} className="btn btn-gradient btn-lg" style={{ padding: '14px 28px', fontSize: '1rem', fontWeight: 800 }}>
              Create Your Project →
            </button>
            <button onClick={handleDemo} className="btn btn-secondary btn-lg" style={{ padding: '14px 24px', fontSize: '0.95rem' }}>
              Explore Demo
            </button>
          </div>

          {/* Status Trust Row */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '24px',
              flexWrap: 'wrap',
              fontSize: '0.85rem',
              color: 'var(--text-muted)',
              padding: '12px 20px',
              background: 'rgba(15, 23, 42, 0.6)',
              borderRadius: '50px',
              border: '1px solid var(--border-dark)',
              width: 'fit-content',
              margin: '0 auto',
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34D399' }}>
              <CheckCircle2 size={15} /> Multi-Agent AI
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34D399' }}>
              <CheckCircle2 size={15} /> Technology Research with Tavily
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34D399' }}>
              <CheckCircle2 size={15} /> Interactive Architecture
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34D399' }}>
              <CheckCircle2 size={15} /> Complete Development Blueprint
            </span>
          </div>
        </motion.div>
      </section>

      {/* 3. PRODUCT PREVIEW (Pipeline Visual Mockup) */}
      <section style={{ maxWidth: '1100px', margin: '0 auto', padding: '0 24px 80px' }}>
        <div
          className="glass-card"
          style={{
            padding: '28px',
            background: 'rgba(15, 23, 42, 0.95)',
            borderRadius: '20px',
            border: '1px solid var(--border-medium)',
            boxShadow: '0 20px 50px rgba(0, 0, 0, 0.5)',
          }}
        >
          <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--accent-cyan)', textTransform: 'uppercase', marginBottom: '16px', textAlign: 'center' }}>
            Interactive 7-Stage AI Architecture Pipeline Preview
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px' }}>
            {[
              { step: '01', title: 'Requirements', color: '#38BDF8' },
              { step: '02', title: 'Tech Selection', color: '#A855F7' },
              { step: '03', title: 'Architecture', color: '#06B6D4' },
              { step: '04', title: 'Task Board', color: '#EC4899' },
              { step: '05', title: 'Timeline', color: '#F59E0B' },
              { step: '06', title: 'Risk Analysis', color: '#10B981' },
              { step: '07', title: 'Final Blueprint', color: '#8B5CF6' },
            ].map((stage, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(9, 13, 22, 0.7)',
                  border: `1px solid ${stage.color}40`,
                  borderRadius: '10px',
                  padding: '12px 10px',
                  textAlign: 'center',
                }}
              >
                <span style={{ fontSize: '0.68rem', color: stage.color, fontWeight: 800, display: 'block', marginBottom: '4px' }}>
                  {stage.step}
                </span>
                <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#FFF' }}>{stage.title}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 4. HOW IT WORKS */}
      <section id="how-it-works" style={{ maxWidth: '1100px', margin: '0 auto', padding: '60px 24px 80px' }}>
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 900, color: '#FFF', marginBottom: '8px' }}>How It Works</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            From raw concept to complete technical specification in four simple steps.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: '20px' }}>
          {[
            {
              step: '01',
              title: 'Describe Your Idea',
              desc: 'Enter your project requirements, team size, and deadline parameters in simple English.',
            },
            {
              step: '02',
              title: 'AI Agents Analyze',
              desc: 'Specialized agents analyze requirements, research technologies, and design architecture.',
            },
            {
              step: '03',
              title: 'Review & Lock',
              desc: 'Review AI recommendations, compare tech alternatives, and lock your preferred stack.',
            },
            {
              step: '04',
              title: 'Get Your Blueprint',
              desc: 'Receive complete architecture diagrams, task backlog, Gantt schedule, risks, and PDF exports.',
            },
          ].map((item) => (
            <div
              key={item.step}
              className="glass-card"
              style={{ padding: '24px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '14px', border: '1px solid var(--border-dark)' }}
            >
              <div style={{ fontSize: '1.4rem', fontWeight: 900, color: 'var(--accent-cyan)', marginBottom: '12px' }}>{item.step}</div>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#FFF', marginBottom: '8px' }}>{item.title}</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5, margin: 0 }}>{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 5. AI AGENTS */}
      <section id="ai-agents" style={{ maxWidth: '1100px', margin: '0 auto', padding: '60px 24px 80px' }}>
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 900, color: '#FFF', marginBottom: '8px' }}>
            7 Specialized <span className="gradient-text-cyan">AI Agents</span>
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Collaborative multi-agent architecture pipeline executing deterministically.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {agents.map((ag) => {
            const Icon = ag.icon;
            return (
              <div
                key={ag.name}
                className="glass-card"
                style={{
                  padding: '18px 20px',
                  background: 'rgba(15, 23, 42, 0.7)',
                  borderRadius: '12px',
                  border: '1px solid var(--border-dark)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '14px',
                }}
              >
                <div
                  style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '8px',
                    background: `${ag.color}20`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  <Icon size={18} color={ag.color} />
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span style={{ fontSize: '0.92rem', fontWeight: 800, color: '#FFF' }}>{ag.name}</span>
                    <span className="badge" style={{ fontSize: '0.65rem', background: 'rgba(255,255,255,0.06)', color: ag.color }}>
                      {ag.stage}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.4, margin: 0 }}>{ag.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 6. KEY FEATURES */}
      <section id="features" style={{ maxWidth: '1100px', margin: '0 auto', padding: '60px 24px 80px' }}>
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 900, color: '#FFF', marginBottom: '8px' }}>Key Platform Capabilities</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Built specifically for developers, technical leads, and AI project managers.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '16px' }}>
          {featuresList.map((f, i) => {
            const Icon = f.icon;
            return (
              <div
                key={i}
                className="glass-card"
                style={{
                  padding: '16px 20px',
                  background: 'rgba(15, 23, 42, 0.5)',
                  borderRadius: '12px',
                  border: '1px solid var(--border-dark)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '14px',
                }}
              >
                <div
                  style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '8px',
                    background: 'rgba(56, 189, 248, 0.12)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  <Icon size={18} color="var(--accent-cyan)" />
                </div>
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFF', margin: '0 0 2px 0' }}>{f.title}</h4>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>{f.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 7. FINAL CTA */}
      <section style={{ maxWidth: '900px', margin: '0 auto 80px', padding: '0 24px' }}>
        <div
          className="glass-card"
          style={{
            padding: '48px 36px',
            textAlign: 'center',
            background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%)',
            borderRadius: '20px',
            border: '1px solid var(--border-medium)',
          }}
        >
          <h2 style={{ fontSize: '2.2rem', fontWeight: 900, color: '#FFF', marginBottom: '12px' }}>
            Ready to Build Your Project Blueprint?
          </h2>
          <p style={{ fontSize: '1rem', color: 'var(--text-muted)', maxWidth: '560px', margin: '0 auto 28px', lineHeight: 1.5 }}>
            Describe your idea and let ProjectForge AI build the technical plan.
          </p>
          <button onClick={handleStart} className="btn btn-gradient btn-lg" style={{ padding: '16px 36px', fontSize: '1.05rem', fontWeight: 800 }}>
            Start Building →
          </button>
        </div>
      </section>
    </div>
  );
}
