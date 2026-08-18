import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Calendar, ArrowRight, ArrowLeft, Clock, Flag, Users, CheckCircle2, Sparkles, ShieldAlert, LayoutDashboard, CheckCircle, Zap } from 'lucide-react';
import api from '../services/api';
import { getErrorMessage } from '../utils/errors';

export default function TimelinePage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [timeline, setTimeline] = useState(null);
  const [projectReqs, setProjectReqs] = useState(null);
  const [tasksList, setTasksList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      localStorage.setItem('active_project_id', id);
      fetchData();
    }
  }, [id]);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const [tlRes, reqRes, tasksRes] = await Promise.all([
        api.get(`/api/projects/${id}/timeline`),
        api.get(`/api/projects/${id}/requirements`).catch(() => ({ data: {} })),
        api.get(`/api/projects/${id}/tasks`).catch(() => ({ data: {} })),
      ]);

      setTimeline(tlRes.data || {});
      setProjectReqs(reqRes.data || {});
      setTasksList(tasksRes.data?.tasks || (Array.isArray(tasksRes.data) ? tasksRes.data : []));
    } catch (err) {
      setError(getErrorMessage(err, 'Timeline not generated yet.'));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'grid', gap: '16px', maxWidth: '1280px', margin: '0 auto' }}>
        {[1, 2, 3].map((i) => (
          <div key={i} className="skeleton" style={{ height: '120px', borderRadius: '12px' }} />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card" style={{ padding: '48px', textAlign: 'center', maxWidth: '600px', margin: '40px auto' }}>
        <ShieldAlert size={48} color="var(--accent-rose)" style={{ marginBottom: '16px' }} />
        <h2 style={{ fontSize: '1.4rem', marginBottom: '8px' }}>Timeline Not Ready</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
          {error}
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
          <button onClick={() => navigate(`/projects/${id}/tasks`)} className="btn btn-secondary">
            Go to Task Board
          </button>
          <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
            <LayoutDashboard size={16} /> Dashboard
          </button>
        </div>
      </div>
    );
  }

  // Create a map of task_id -> task title from Task Planner output
  const taskTitleMap = {};
  tasksList.forEach((t) => {
    const tid = t.task_id || t.id;
    if (tid && t.title) {
      taskTitleMap[tid] = t.title;
    }
  });

  const entries = timeline?.schedule || timeline?.entries || timeline?.phases || [];
  const rawMilestones = timeline?.milestones || [];
  const teamAlloc = timeline?.team_allocation || [];

  // Configured project deadline from Requirements
  const configuredDeadline = projectReqs?.deadline_days || 30;

  // Compute maximum end day across tasks and milestones
  const maxTaskEnd = entries.reduce((max, e) => Math.max(max, e.end_day || 0), 0);
  const maxMilestoneTarget = rawMilestones.reduce((max, m) => Math.max(max, m.target_day || m.day || 0), 0);

  // Total project duration (uses actual configured deadline, or max calculated)
  const totalDays = timeline?.total_days || Math.max(configuredDeadline, maxTaskEnd, maxMilestoneTarget);

  // Filter & validate milestones so none exceed totalDays
  const milestones = rawMilestones.map((m, idx) => ({
    ...m,
    target_day: Math.min(m.target_day || m.day || (idx + 1) * 7, totalDays),
  }));

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
      {/* Top Banner Navigation */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '32px', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button onClick={() => navigate(`/projects/${id}/tasks`)} className="btn btn-secondary btn-sm" style={{ padding: '8px 14px' }}>
            <ArrowLeft size={16} /> Back: Task Board
          </button>
          <div>
            <div className="badge badge-info" style={{ marginBottom: '6px' }}>
              <Calendar size={12} /> Stage 05 / Timeline & Schedule
            </div>
            <h1 style={{ fontSize: '2rem', margin: 0 }}>
              Project <span className="gradient-text">Gantt Timeline</span>
            </h1>
          </div>
        </div>

        <button onClick={() => navigate(`/projects/${id}/risks`)} className="btn btn-gradient btn-lg">
          Next: Risk Analysis <ArrowRight size={18} />
        </button>
      </div>

      {/* Feasibility Overview Header */}
      {(timeline?.feasibility_score !== undefined || timeline?.feasibility_notes || timeline?.feasibility) && (
        <div className="glass-card mb-6" style={{ padding: '24px', marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Zap size={22} color="var(--accent-amber)" />
              <h3 style={{ fontSize: '1.15rem', margin: 0 }}>Timeline Feasibility Assessment</h3>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              {timeline?.feasibility && (
                <span className="badge badge-info" style={{ textTransform: 'uppercase', fontSize: '0.8rem' }}>
                  {timeline.feasibility}
                </span>
              )}
              {timeline?.feasibility_score !== undefined && (
                <span className="badge badge-success" style={{ fontSize: '0.8rem' }}>
                  Feasibility: {timeline.feasibility_score}%
                </span>
              )}
            </div>
          </div>
          {timeline?.feasibility_notes && (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: 0, lineHeight: 1.5 }}>
              {timeline.feasibility_notes}
            </p>
          )}
        </div>
      )}

      {/* Gantt Phase & Scheduled Tasks Visualizer */}
      <div className="glass-card mb-6" style={{ padding: '28px', marginBottom: '32px' }}>
        <h3 style={{ fontSize: '1.2rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Clock size={20} color="var(--accent-cyan)" /> Data-Driven Execution Schedule ({totalDays} Total Days)
        </h3>

        {entries.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', textAlign: 'center', padding: '20px' }}>
            No scheduled timeline entries generated.
          </p>
        ) : (
          <div style={{ display: 'grid', gap: '16px' }}>
            {entries.map((entry, idx) => {
              const startDay = entry.start_day || idx * 3 + 1;
              const endDay = entry.end_day || startDay + 2;
              const duration = Math.max(1, endDay - startDay + 1);
              const startPct = Math.min(100, Math.max(0, ((startDay - 1) / totalDays) * 100));
              const widthPct = Math.min(100, Math.max(8, (duration / totalDays) * 100));

              // Clean task label: Avoid "T1: T1" redundancy!
              const rawTitle = entry.title || entry.task_name || entry.name;
              const cleanTaskTitle = (rawTitle && rawTitle !== entry.task_id)
                ? rawTitle
                : (taskTitleMap[entry.task_id] || `Task Execution #${idx + 1}`);

              const fullLabel = entry.task_id && !cleanTaskTitle.startsWith(entry.task_id)
                ? `${entry.task_id}: ${cleanTaskTitle}`
                : cleanTaskTitle;

              const assigned = entry.assigned_member || entry.role || entry.assigned_role;
              const isCritical = entry.is_critical;

              return (
                <div key={idx} style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '18px', borderRadius: '12px', border: '1px solid var(--border-dark)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-main)' }}>
                        {fullLabel}
                      </span>
                      {assigned && (
                        <span className="badge badge-info" style={{ fontSize: '0.75rem', padding: '4px 8px' }}>
                          <Users size={12} style={{ marginRight: '4px' }} /> {assigned}
                        </span>
                      )}
                      {isCritical && (
                        <span className="badge badge-danger" style={{ fontSize: '0.75rem', padding: '4px 8px' }}>
                          Critical Path
                        </span>
                      )}
                    </div>
                    <span style={{ fontSize: '0.85rem', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                      Day {startDay} → Day {endDay} ({duration} {duration === 1 ? 'day' : 'days'})
                    </span>
                  </div>

                  {/* Progress bar line */}
                  <div style={{ width: '100%', height: '12px', background: 'rgba(255,255,255,0.05)', borderRadius: '6px', overflow: 'hidden', position: 'relative' }}>
                    <div
                      style={{
                        position: 'absolute',
                        left: `${startPct}%`,
                        width: `${widthPct}%`,
                        height: '100%',
                        background: isCritical ? 'linear-gradient(90deg, #F43F5E, #FB7185)' : 'var(--gradient-primary)',
                        borderRadius: '6px',
                        boxShadow: isCritical ? '0 0 10px rgba(244, 63, 94, 0.5)' : '0 0 10px rgba(59, 130, 246, 0.5)',
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Grid for Milestones and Team Allocation */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
        {/* Major Milestones */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.15rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Flag size={20} color="var(--accent-amber)" /> Major Milestones
          </h3>
          {milestones.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: 0 }}>No specific milestones provided.</p>
          ) : (
            <div style={{ display: 'grid', gap: '12px' }}>
              {milestones.map((m, idx) => (
                <div key={idx} style={{ padding: '14px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-dark)', borderRadius: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <span className="badge badge-warning" style={{ fontSize: '0.75rem' }}>
                      Target Day {m.target_day}
                    </span>
                    {m.associated_tasks && m.associated_tasks.length > 0 && (
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Tasks: {m.associated_tasks.join(', ')}
                      </span>
                    )}
                  </div>
                  <h4 style={{ fontSize: '0.95rem', margin: '4px 0', color: 'var(--text-main)' }}>
                    {m.name || m.title || `Milestone ${idx + 1}`}
                  </h4>
                  {m.description && (
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
                      {m.description}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Team Allocation */}
        {teamAlloc.length > 0 && (
          <div className="glass-card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Users size={20} color="var(--accent-violet)" /> Team Resource Allocation
            </h3>
            <div style={{ display: 'grid', gap: '12px' }}>
              {teamAlloc.map((member, idx) => (
                <div key={idx} style={{ padding: '14px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-dark)', borderRadius: '10px' }}>
                  <h4 style={{ fontSize: '0.95rem', margin: '0 0 6px 0', color: 'var(--accent-cyan)' }}>
                    {member.role || member.name || `Role ${idx + 1}`}
                    {member.name && member.role ? ` (${member.name})` : ''}
                  </h4>
                  {member.assigned_tasks && member.assigned_tasks.length > 0 && (
                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                      {member.assigned_tasks.map((taskRef, tIdx) => (
                        <span key={tIdx} className="badge badge-info" style={{ fontSize: '0.75rem' }}>
                          {taskRef}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
