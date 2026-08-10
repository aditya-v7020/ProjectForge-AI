import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import LiveAgentWorkflow from './LiveAgentWorkflow';
import { Bot, Sparkles, CheckCircle2, ArrowRight } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';

export default function AgentProgressModal({ progress, isConnected, isFinished }) {
  const navigate = useNavigate();
  const { id } = useParams();

  const handleProceed = () => {
    if (id) {
      navigate(`/projects/${id}/architecture`);
    }
  };

  return (
    <AnimatePresence>
      <div
        style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(6, 9, 17, 0.88)',
          backdropFilter: 'blur(14px)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '24px',
        }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.3 }}
          style={{
            maxWidth: '1100px',
            width: '100%',
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-medium)',
            borderRadius: '24px',
            boxShadow: 'var(--shadow-xl), 0 0 50px rgba(59, 130, 246, 0.2)',
            padding: '32px',
          }}
        >
          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '56px',
                height: '56px',
                borderRadius: '16px',
                background: 'var(--gradient-primary)',
                boxShadow: 'var(--glow-primary)',
                marginBottom: '16px',
              }}
            >
              <Sparkles size={28} color="#FFF" />
            </div>
            <h2 style={{ fontSize: '1.8rem', fontWeight: 800, margin: '0 0 8px 0' }}>
              ProjectForge <span className="gradient-text-cyan">AI Orchestrator</span>
            </h2>
            <p style={{ fontSize: '0.95rem', color: 'var(--text-muted)', maxWidth: '600px', margin: '0 auto' }}>
              Executing autonomous 6-Agent workflow. Transforming your requirements and locked tech stack into a complete architectural blueprint.
            </p>
          </div>

          <LiveAgentWorkflow agentProgress={progress} isConnected={isConnected} />

          {/* Proceed Button when all agents finish */}
          {isFinished && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              style={{ marginTop: '24px', textAlign: 'center' }}
            >
              <button onClick={handleProceed} className="btn btn-gradient btn-lg" style={{ padding: '14px 32px' }}>
                <CheckCircle2 size={18} /> All 6 Agents Completed — View System Architecture <ArrowRight size={18} />
              </button>
            </motion.div>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
