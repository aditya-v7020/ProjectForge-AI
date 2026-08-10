import React, { useState, useEffect } from 'react';
import { Outlet, useParams, useLocation, useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import AiActivityDrawer from './AiActivityDrawer';
import AiProjectChatDrawer from './AiProjectChatDrawer';
import { useSSE } from '../hooks/useSSE';
import { Cpu, Plus, Sparkles, ChevronRight, Menu, X } from 'lucide-react';

export default function Layout() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  // Sync active project ID to localStorage whenever id is in URL
  useEffect(() => {
    if (id) {
      localStorage.setItem('active_project_id', id);
    }
  }, [id]);

  // Close mobile sidebar on route change
  useEffect(() => {
    setIsMobileSidebarOpen(false);
  }, [location.pathname]);

  const activeProjectId = id || localStorage.getItem('active_project_id');
  const { agentProgress, isConnected } = useSSE(activeProjectId);

  // Compute active stage title
  const getStageTitle = () => {
    const path = location.pathname;
    if (path.includes('/requirements')) return 'Requirements Analysis';
    if (path.includes('/technology-selection')) return 'Technology Selection & Locking';
    if (path.includes('/architecture')) return 'System Architecture';
    if (path.includes('/tasks')) return 'Agile Task Board';
    if (path.includes('/timeline')) return 'Project Timeline & Gantt';
    if (path.includes('/risks')) return 'Risk Analysis Matrix';
    if (path.includes('/blueprint')) return 'Executive Blueprint';
    if (path.includes('/projects/new')) return 'AI Project Wizard';
    return 'Command Center';
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg-darker)' }}>
      {/* Mobile Backdrop Overlay */}
      <div
        className={`mobile-sidebar-backdrop ${isMobileSidebarOpen ? 'active' : ''}`}
        onClick={() => setIsMobileSidebarOpen(false)}
      />

      {/* Sidebar */}
      <Sidebar isMobileOpen={isMobileSidebarOpen} onCloseMobile={() => setIsMobileSidebarOpen(false)} />

      {/* Main Container */}
      <div
        className="app-main-content"
        style={{
          marginLeft: 'var(--sidebar-width)',
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          minWidth: 0,
        }}
      >
        {/* Top Header Bar */}
        <header
          style={{
            height: 'var(--header-height)',
            backgroundColor: 'rgba(9, 13, 22, 0.85)',
            backdropFilter: 'blur(12px)',
            borderBottom: '1px solid var(--border-dark)',
            padding: '0 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            position: 'sticky',
            top: 0,
            zIndex: 90,
          }}
        >
          {/* Mobile Hamburger & Breadcrumbs / Stage Title */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              onClick={() => setIsMobileSidebarOpen(!isMobileSidebarOpen)}
              className="btn btn-secondary btn-sm hamburger-btn"
              style={{ padding: '8px', borderRadius: '8px' }}
              title="Toggle Navigation Menu"
            >
              {isMobileSidebarOpen ? <X size={20} color="#FFF" /> : <Menu size={20} color="#FFF" />}
            </button>

            <span
              onClick={() => navigate('/dashboard')}
              style={{ fontSize: '0.85rem', color: 'var(--text-muted)', cursor: 'pointer' }}
            >
              Command Center
            </span>
            <ChevronRight size={14} color="var(--text-dim)" />
            <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {getStageTitle()}
            </span>
          </div>

          {/* Controls & Quick Actions */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {/* Live AI Drawer Toggle */}
            <button
              onClick={() => setIsDrawerOpen(true)}
              className="btn btn-secondary btn-sm"
              style={{ display: 'flex', alignItems: 'center', gap: '6px', borderRadius: '8px', padding: '6px 10px', fontSize: '0.8rem' }}
            >
              <Cpu size={15} className={isConnected ? 'text-cyan pulse-glow' : ''} color={isConnected ? '#38BDF8' : 'var(--text-muted)'} />
              <span className="hidden-mobile">Live AI Activity</span>
              {isConnected && (
                <span
                  style={{
                    width: '7px',
                    height: '7px',
                    borderRadius: '50%',
                    background: '#10B981',
                    display: 'inline-block',
                  }}
                />
              )}
            </button>

            {/* Quick New Project Button */}
            <button
              onClick={() => navigate('/projects/new')}
              className="btn btn-primary btn-sm"
              style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 10px', fontSize: '0.8rem' }}
            >
              <Plus size={15} />
              <span className="hidden-mobile">New Project</span>
            </button>
          </div>
        </header>

        {/* Page Content Viewport */}
        <main className="main-viewport" style={{ flex: 1, padding: '28px 32px', maxWidth: '1600px', width: '100%', margin: '0 auto', boxSizing: 'border-box' }}>
          <Outlet />
        </main>
      </div>

      {/* AI Activity Drawer Overlay */}
      <AiActivityDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        agentProgress={agentProgress}
        isConnected={isConnected}
      />

      {/* Feature 2: Interactive AI Project Chat */}
      <AiProjectChatDrawer />
    </div>
  );
}

