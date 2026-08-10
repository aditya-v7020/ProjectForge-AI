import React from 'react';
import { NavLink, useParams, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, PlusCircle, FileText, Cpu, Layers,
  Kanban, Calendar, ShieldAlert, BookOpen, LogOut, Sparkles, ChevronRight
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ isMobileOpen, onCloseMobile }) {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const activeProjectId = id || localStorage.getItem('active_project_id');

  const mainNav = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'New Project', path: '/projects/new', icon: PlusCircle, highlight: true },
  ];

  const projectStages = [
    { name: 'Requirements', path: activeProjectId ? `/projects/${activeProjectId}/requirements` : '/projects/new', icon: FileText, step: '01' },
    { name: 'Tech Selection', path: activeProjectId ? `/projects/${activeProjectId}/technology-selection` : '/projects/new', icon: Cpu, step: '02' },
    { name: 'Architecture', path: activeProjectId ? `/projects/${activeProjectId}/architecture` : '/projects/new', icon: Layers, step: '03' },
    { name: 'Task Board', path: activeProjectId ? `/projects/${activeProjectId}/tasks` : '/projects/new', icon: Kanban, step: '04' },
    { name: 'Timeline', path: activeProjectId ? `/projects/${activeProjectId}/timeline` : '/projects/new', icon: Calendar, step: '05' },
    { name: 'Risk Analysis', path: activeProjectId ? `/projects/${activeProjectId}/risks` : '/projects/new', icon: ShieldAlert, step: '06' },
    { name: 'Final Blueprint', path: activeProjectId ? `/projects/${activeProjectId}/blueprint` : '/projects/new', icon: BookOpen, step: '07' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside
      className={`app-sidebar ${isMobileOpen ? 'mobile-open' : ''}`}
      style={{
        width: 'var(--sidebar-width)',
        backgroundColor: 'var(--bg-dark)',
        borderRight: '1px solid var(--border-dark)',
        height: '100vh',
        position: 'fixed',
        top: 0,
        left: 0,
        display: 'flex',
        flexDirection: 'column',
        zIndex: 100,
        userSelect: 'none',
      }}
    >
      {/* Brand Header */}
      <div
        onClick={() => navigate('/dashboard')}
        style={{
          padding: '24px 20px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          cursor: 'pointer',
          borderBottom: '1px solid var(--border-dark)',
        }}
      >
        <div
          style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'var(--gradient-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px rgba(139, 92, 246, 0.4)',
          }}
        >
          <Sparkles size={20} color="#FFF" />
        </div>
        <div>
          <span style={{ fontWeight: 800, fontSize: '1.15rem', color: '#FFF', letterSpacing: '-0.02em', display: 'block', lineHeight: 1.1 }}>
            ProjectForge <span style={{ color: 'var(--accent-cyan)' }}>AI</span>
          </span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Multi-Agent Engine
          </span>
        </div>
      </div>

      {/* Navigation Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 12px' }}>
        {/* Primary Controls */}
        <div style={{ marginBottom: '24px' }}>
          <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-dim)', padding: '0 10px 8px', letterSpacing: '0.06em' }}>
            Navigation
          </div>
          {mainNav.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.name}
                to={item.path}
                className={`nav-link ${isActive ? 'active' : ''}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '10px 14px',
                  borderRadius: '10px',
                  color: isActive ? '#FFF' : 'var(--text-muted)',
                  backgroundColor: isActive
                    ? 'rgba(59, 130, 246, 0.15)'
                    : item.highlight
                    ? 'rgba(6, 182, 212, 0.08)'
                    : 'transparent',
                  border: isActive ? '1px solid rgba(59, 130, 246, 0.3)' : '1px solid transparent',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: '0.9rem',
                  marginBottom: '4px',
                  transition: 'all 0.15s ease',
                }}
              >
                <Icon size={18} color={isActive ? '#38BDF8' : 'var(--text-muted)'} />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </div>

        {/* Project Workflow Steps */}
        <div>
          <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-dim)', padding: '0 10px 8px', letterSpacing: '0.06em', display: 'flex', justifyContent: 'space-between' }}>
            <span>Project Blueprint</span>
            {activeProjectId && <span style={{ color: 'var(--accent-cyan)' }}>Active</span>}
          </div>
          {projectStages.map((stage) => {
            const Icon = stage.icon;
            const isActive = location.pathname === stage.path;
            return (
              <NavLink
                key={stage.name}
                to={stage.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '9px 12px',
                  borderRadius: '8px',
                  color: isActive ? '#FFF' : 'var(--text-muted)',
                  backgroundColor: isActive ? 'rgba(6, 182, 212, 0.12)' : 'transparent',
                  border: isActive ? '1px solid rgba(6, 182, 212, 0.3)' : '1px solid transparent',
                  fontWeight: isActive ? 600 : 400,
                  fontSize: '0.85rem',
                  marginBottom: '3px',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '0.7rem', fontFamily: 'var(--font-mono)', color: isActive ? 'var(--accent-cyan)' : 'var(--text-dim)' }}>
                    {stage.step}
                  </span>
                  <Icon size={16} color={isActive ? '#38BDF8' : 'var(--text-muted)'} />
                  <span>{stage.name}</span>
                </div>
                {isActive && <ChevronRight size={14} color="var(--accent-cyan)" />}
              </NavLink>
            );
          })}
        </div>
      </div>

      {/* User Footer */}
      <div
        style={{
          padding: '16px 20px',
          borderTop: '1px solid var(--border-dark)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'rgba(9, 13, 22, 0.95)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', overflow: 'hidden' }}>
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: 'rgba(59, 130, 246, 0.2)',
              color: '#38BDF8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: '0.85rem',
              border: '1px solid rgba(59, 130, 246, 0.3)',
            }}
          >
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div style={{ overflow: 'hidden' }}>
            <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#FFF', display: 'block', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
              {user?.username || 'User'}
            </span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', display: 'block' }}>
              Project Lead
            </span>
          </div>
        </div>

        <button
          onClick={handleLogout}
          title="Sign Out"
          className="btn btn-ghost btn-sm"
          style={{ padding: '6px', color: 'var(--text-muted)' }}
        >
          <LogOut size={16} />
        </button>
      </div>
    </aside>
  );
}
