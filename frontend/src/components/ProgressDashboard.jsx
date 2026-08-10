import React from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, Circle, Clock, ArrowRight, FileText, Cpu, Layers, Kanban, Calendar, ShieldAlert, BookOpen } from 'lucide-react';

const STAGES = [
  { key: 'requirements', label: 'Requirements', icon: FileText, path: 'requirements' },
  { key: 'technology', label: 'Technology', icon: Cpu, path: 'technology-selection' },
  { key: 'architecture', label: 'Architecture', icon: Layers, path: 'architecture' },
  { key: 'tasks', label: 'Tasks', icon: Kanban, path: 'tasks' },
  { key: 'timeline', label: 'Timeline', icon: Calendar, path: 'timeline' },
  { key: 'risks', label: 'Risks', icon: ShieldAlert, path: 'risks' },
  { key: 'blueprint', label: 'Blueprint', icon: BookOpen, path: 'blueprint' },
];

export function getStageStatus(project, stageKey) {
  if (!project) return 'pending';
  const status = project.status || 'created';

  // Map backend status to stage indices
  const statusMap = {
    'created': 0,
    'requirements_done': 1,
    'tech_analysis_done': 1,
    'tech_selected': 2,
    'architecture_done': 3,
    'tasks_done': 4,
    'timeline_done': 5,
    'review_done': 6,
    'blueprint_done': 7,
    'completed': 7,
  };

  const currentLevel = statusMap[status] ?? 0;
  const stageIndex = STAGES.findIndex((s) => s.key === stageKey);

  if (currentLevel > stageIndex) return 'completed';
  if (currentLevel === stageIndex) return 'active';
  return 'pending';
}

export function calculateProgressPercent(project) {
  if (!project) return 0;
  let completedCount = 0;
  STAGES.forEach((stage) => {
    if (getStageStatus(project, stage.key) === 'completed') {
      completedCount++;
    }
  });
  // If active stage exists, count half credit or full stage
  const activeStage = STAGES.find((s) => getStageStatus(project, s.key) === 'active');
  const percent = Math.min(100, Math.round(((completedCount + (activeStage ? 0.5 : 0)) / STAGES.length) * 100));
  return percent;
}

export default function ProgressDashboard({ project, currentStage, compact = false }) {
  const navigate = useNavigate();
  if (!project) return null;

  const percent = calculateProgressPercent(project);

  const handleStageClick = (stage) => {
    localStorage.setItem('active_project_id', project.id);
    navigate(`/projects/${project.id}/${stage.path}`);
  };

  return (
    <div className="glass-card" style={{ padding: compact ? '16px 20px' : '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ fontWeight: 700, fontSize: compact ? '0.95rem' : '1.1rem', color: '#FFF' }}>
            Workflow Stage Tracker
          </div>
          <span className="badge badge-info" style={{ fontSize: '0.75rem', fontWeight: 600 }}>
            {percent}% Completed
          </span>
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Project: <strong style={{ color: 'var(--accent-cyan)' }}>{project.name}</strong>
        </div>
      </div>

      {/* Progress Bar Container */}
      <div
        style={{
          width: '100%',
          height: '6px',
          backgroundColor: 'rgba(255, 255, 255, 0.08)',
          borderRadius: '10px',
          marginBottom: '20px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${percent}%`,
            background: 'var(--gradient-primary)',
            borderRadius: '10px',
            transition: 'width 0.4s ease',
          }}
        />
      </div>

      {/* Stage Nodes Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))',
          gap: '8px',
        }}
      >
        {STAGES.map((stage, idx) => {
          const status = getStageStatus(project, stage.key);
          const isCurrent = currentStage === stage.key;
          const Icon = stage.icon;

          let badgeColor = 'var(--text-muted)';
          let bgStyle = 'rgba(255, 255, 255, 0.02)';
          let borderColor = 'rgba(255, 255, 255, 0.08)';

          if (isCurrent) {
            badgeColor = '#38BDF8';
            bgStyle = 'rgba(6, 182, 212, 0.15)';
            borderColor = 'var(--accent-cyan)';
          } else if (status === 'completed') {
            badgeColor = '#34D399';
            bgStyle = 'rgba(16, 185, 129, 0.1)';
            borderColor = 'rgba(16, 185, 129, 0.3)';
          } else if (status === 'active') {
            badgeColor = '#FBBF24';
            bgStyle = 'rgba(245, 158, 11, 0.1)';
            borderColor = 'rgba(245, 158, 11, 0.3)';
          }

          return (
            <button
              key={stage.key}
              onClick={() => handleStageClick(stage)}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                padding: '10px 6px',
                borderRadius: '10px',
                backgroundColor: bgStyle,
                border: `1px solid ${borderColor}`,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                color: isCurrent ? '#FFF' : 'var(--text-main)',
              }}
              title={`Go to ${stage.label}`}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '6px' }}>
                {status === 'completed' ? (
                  <CheckCircle2 size={14} color="#34D399" />
                ) : status === 'active' ? (
                  <Clock size={14} color="#FBBF24" />
                ) : (
                  <Circle size={14} color="var(--text-muted)" />
                )}
                <span style={{ fontSize: '0.68rem', color: badgeColor, fontWeight: 700 }}>
                  0{idx + 1}
                </span>
              </div>
              <Icon size={18} color={badgeColor} style={{ marginBottom: '4px' }} />
              <span style={{ fontSize: '0.78rem', fontWeight: isCurrent ? 700 : 500, lineHeight: 1.2 }}>
                {stage.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
