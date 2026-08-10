import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Bot, CheckCircle2, Clock, AlertTriangle, Cpu, Play } from 'lucide-react';

const AGENT_NODES = [
  { id: 'requirement_analyst', name: 'Requirement Analyst', desc: 'Extracts goals, features, team constraints' },
  { id: 'technology_advisor', name: 'Technology Advisor', desc: 'Generates unbiased technology alternatives' },
  { id: 'architecture', name: 'Architecture Agent', desc: 'Designs system components & diagrams' },
  { id: 'task_planner', name: 'Task Planner', desc: 'Decomposes features into agile backlog tasks' },
  { id: 'timeline', name: 'Timeline & Resource Agent', desc: 'Schedules phases, milestones & effort' },
  { id: 'critic', name: 'Critic & Risk Agent', desc: 'Audits risks & performs quality reviews' },
  { id: 'blueprint', name: 'Final Blueprint', desc: 'Compiles project blueprint' },
];

export default function AiActivityDrawer({ isOpen, onClose, agentProgress, isConnected }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            style={{
              position: 'fixed',
              inset: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.7)',
              backdropFilter: 'blur(4px)',
              zIndex: 999,
            }}
          />

          {/* Sliding drawer */}
          <motion.aside
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            style={{
              position: 'fixed',
              top: 0,
              right: 0,
              bottom: 0,
              width: '420px',
              maxWidth: '90vw',
              backgroundColor: 'var(--bg-card)',
              borderLeft: '1px solid var(--border-dark)',
              boxShadow: 'var(--shadow-xl)',
              zIndex: 1000,
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            {/* Header */}
            <div
              style={{
                padding: '20px',
                borderBottom: '1px solid var(--border-dark)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: 'rgba(15, 23, 42, 0.95)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div
                  style={{
                    padding: '8px',
                    borderRadius: '8px',
                    background: 'rgba(6, 182, 212, 0.15)',
                    color: 'var(--accent-cyan)',
                  }}
                >
                  <Cpu size={20} className="pulse-glow" />
                </div>
                <div>
                  <h3 style={{ fontSize: '1.1rem', margin: 0 }}>Live AI Activity</h3>
                  <p style={{ fontSize: '0.75rem', margin: 0, color: 'var(--text-muted)' }}>
                    {isConnected ? (
                      <span style={{ color: '#34D399', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                        <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#34D399', display: 'inline-block' }} /> Live Stream Active
                      </span>
                    ) : (
                      'Stream Offline'
                    )}
                  </p>
                </div>
              </div>

              <button
                onClick={onClose}
                className="btn btn-ghost btn-sm"
                style={{ borderRadius: '50%', padding: '6px' }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Agent Execution Flow */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {AGENT_NODES.map((agent, index) => {
                  const status = agentProgress?.[agent.id] || 'pending';
                  const isWorking = status === 'working' || status === 'running';
                  const isDone = status === 'completed' || status === 'done';
                  const isFailed = status === 'failed' || status === 'error';

                  return (
                    <div
                      key={agent.id}
                      style={{
                        position: 'relative',
                        padding: '14px',
                        borderRadius: '12px',
                        background: isWorking
                          ? 'rgba(6, 182, 212, 0.08)'
                          : isDone
                          ? 'rgba(16, 185, 129, 0.05)'
                          : 'rgba(255, 255, 255, 0.02)',
                        border: isWorking
                          ? '1px solid rgba(6, 182, 212, 0.4)'
                          : isDone
                          ? '1px solid rgba(16, 185, 129, 0.2)'
                          : '1px solid var(--border-dark)',
                        transition: 'all 0.2s ease',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <Bot
                            size={18}
                            color={isWorking ? '#38BDF8' : isDone ? '#34D399' : isFailed ? '#FB7185' : '#64748B'}
                          />
                          <span style={{ fontWeight: 600, fontSize: '0.9rem', color: isWorking ? '#38BDF8' : 'var(--text-main)' }}>
                            {agent.name}
                          </span>
                        </div>

                        {/* Status Icon */}
                        {isWorking && (
                          <span className="badge badge-info" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <Play size={10} className="pulse-glow" /> Working
                          </span>
                        )}
                        {isDone && (
                          <span className="badge badge-success" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <CheckCircle2 size={10} /> Completed
                          </span>
                        )}
                        {isFailed && (
                          <span className="badge badge-danger" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <AlertTriangle size={10} /> Failed
                          </span>
                        )}
                        {!isWorking && !isDone && !isFailed && (
                          <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: '#64748B' }}>
                            <Clock size={10} /> Waiting
                          </span>
                        )}
                      </div>

                      <p style={{ fontSize: '0.8rem', marginTop: '6px', color: 'var(--text-muted)', margin: '6px 0 0 0' }}>
                        {agent.desc}
                      </p>

                      {/* Connection Line */}
                      {index < AGENT_NODES.length - 1 && (
                        <div
                          style={{
                            width: '2px',
                            height: '12px',
                            background: isDone ? '#10B981' : isWorking ? '#06B6D4' : 'var(--border-dark)',
                            margin: '8px 0 -8px 20px',
                            transition: 'background 0.3s ease',
                          }}
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
