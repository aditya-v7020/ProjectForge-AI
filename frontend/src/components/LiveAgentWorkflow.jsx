import React from 'react';
import { motion } from 'framer-motion';
import { Bot, CheckCircle2, Play, AlertCircle, Clock, ArrowRight, ShieldCheck, Layers, Cpu, FileSearch, Kanban, Calendar } from 'lucide-react';

const AGENTS = [
  { id: 'requirement_analyst', name: 'Requirement Analyst', role: 'Decomposes raw prompt into structured goals & features', icon: FileSearch },
  { id: 'technology_advisor', name: 'Technology Advisor', role: 'Evaluates unbiased options with Tavily research', icon: Cpu },
  { id: 'architecture', name: 'Architecture Agent', role: 'Designs system components using LOCKED stack', icon: Layers },
  { id: 'task_planner', name: 'Task Planner', role: 'Decomposes features into agile backlog tasks', icon: Kanban },
  { id: 'timeline', name: 'Timeline Agent', role: 'Schedules phases, milestones & resource allocation', icon: Calendar },
  { id: 'critic', name: 'Critic & Risk Agent', role: 'Audits plan quality & risk mitigations', icon: ShieldCheck },
];

export default function LiveAgentWorkflow({ agentProgress, isConnected }) {
  return (
    <div className="glass-card p-6" style={{ padding: '24px', position: 'relative', overflow: 'hidden' }}>
      {/* Visual Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h3 style={{ fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
            <Bot size={20} className="text-accent" color="var(--accent-cyan)" /> Live Multi-Agent Workflow Engine
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
            LangGraph Orchestrator running 6 specialized AI agents in sequence.
          </p>
        </div>

        {isConnected && (
          <span className="badge badge-info pulse-glow" style={{ padding: '6px 14px' }}>
            ● LIVE SSE STREAMING
          </span>
        )}
      </div>

      {/* Agents Grid Flow */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        {AGENTS.map((agent, index) => {
          const Icon = agent.icon;
          const status = agentProgress?.[agent.id] || 'pending';
          const isWorking = status === 'working' || status === 'running';
          const isDone = status === 'completed' || status === 'done';
          const isFailed = status === 'failed' || status === 'error';

          return (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.08 }}
              style={{
                padding: '16px',
                borderRadius: '12px',
                background: isWorking
                  ? 'linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(15, 23, 42, 0.9) 100%)'
                  : isDone
                  ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(15, 23, 42, 0.9) 100%)'
                  : 'rgba(15, 23, 42, 0.6)',
                border: isWorking
                  ? '1px solid rgba(6, 182, 212, 0.6)'
                  : isDone
                  ? '1px solid rgba(16, 185, 129, 0.3)'
                  : isFailed
                  ? '1px solid rgba(244, 63, 94, 0.4)'
                  : '1px solid var(--border-dark)',
                boxShadow: isWorking ? '0 0 25px rgba(6, 182, 212, 0.25)' : 'none',
                transition: 'all 0.3s ease',
                position: 'relative',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div
                    style={{
                      padding: '8px',
                      borderRadius: '8px',
                      background: isWorking
                        ? 'rgba(6, 182, 212, 0.2)'
                        : isDone
                        ? 'rgba(16, 185, 129, 0.2)'
                        : 'rgba(255, 255, 255, 0.05)',
                      color: isWorking ? '#38BDF8' : isDone ? '#34D399' : 'var(--text-muted)',
                    }}
                  >
                    <Icon size={18} />
                  </div>
                  <div>
                    <span style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)', display: 'block' }}>
                      {agent.name}
                    </span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                      Agent 0{index + 1}
                    </span>
                  </div>
                </div>

                {/* Status Indicator Badge */}
                {isWorking && (
                  <span className="badge badge-info" style={{ gap: '4px' }}>
                    <Play size={10} className="spinner" /> WORKING
                  </span>
                )}
                {isDone && (
                  <span className="badge badge-success" style={{ gap: '4px' }}>
                    <CheckCircle2 size={10} /> DONE
                  </span>
                )}
                {isFailed && (
                  <span className="badge badge-danger" style={{ gap: '4px' }}>
                    <AlertCircle size={10} /> FAILED
                  </span>
                )}
                {!isWorking && !isDone && !isFailed && (
                  <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-dim)' }}>
                    <Clock size={10} /> WAITING
                  </span>
                )}
              </div>

              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
                {agent.role}
              </p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
