import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Kanban,
  ArrowRight,
  ArrowLeft,
  Clock,
  ShieldAlert,
  LayoutDashboard,
  User,
  Star,
  Link2,
  HelpCircle,
  CheckCircle2,
  Search,
  Filter,
  AlertTriangle,
  PlayCircle,
  CheckSquare,
  ListTodo,
  ChevronDown,
  ChevronRight,
  Sparkles,
  Layers,
  SlidersHorizontal,
  ArrowUpDown,
  PlusCircle,
  Activity,
  CheckCircle,
  FileText,
  Tag,
  Cpu,
  RotateCcw,
  Eye,
} from 'lucide-react';
import api from '../services/api';
import { getErrorMessage } from '../utils/errors';

const STATUS_CONFIG = {
  todo: { id: 'todo', label: 'To Do', color: '#38BDF8', bg: 'rgba(56, 189, 248, 0.12)', border: 'rgba(56, 189, 248, 0.3)', icon: PlayCircle },
  in_progress: { id: 'in_progress', label: 'In Progress', color: '#FBBF24', bg: 'rgba(251, 191, 36, 0.12)', border: 'rgba(251, 191, 36, 0.3)', icon: Clock },
  in_review: { id: 'in_review', label: 'In Review', color: '#C084FC', bg: 'rgba(192, 132, 252, 0.12)', border: 'rgba(192, 132, 252, 0.3)', icon: CheckSquare },
  done: { id: 'done', label: 'Done', color: '#34D399', bg: 'rgba(52, 211, 153, 0.12)', border: 'rgba(52, 211, 153, 0.3)', icon: CheckCircle2 },
};

const PRIORITY_CONFIG = {
  critical: { label: 'CRITICAL', color: '#F43F5E', bg: 'rgba(244, 63, 94, 0.18)' },
  high: { label: 'HIGH', color: '#FB7185', bg: 'rgba(251, 113, 133, 0.15)' },
  medium: { label: 'MEDIUM', color: '#FBBF24', bg: 'rgba(251, 191, 36, 0.15)' },
  low: { label: 'LOW', color: '#34D399', bg: 'rgba(52, 211, 153, 0.15)' },
};

// 7-Stage Project Pipeline Steps
const STAGES = [
  { key: 'requirements', label: 'Requirements', path: 'requirements' },
  { key: 'technology', label: 'Tech Selection', path: 'technology' },
  { key: 'architecture', label: 'Architecture', path: 'architecture' },
  { key: 'tasks', label: 'Task Board', path: 'tasks', active: true },
  { key: 'timeline', label: 'Timeline', path: 'timeline' },
  { key: 'risks', label: 'Risk Analysis', path: 'risks' },
  { key: 'blueprint', label: 'Final Blueprint', path: 'blueprint' },
];

export default function TaskBoardPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [taskPlan, setTaskPlan] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Selected task state for Details Panel
  const [selectedTaskId, setSelectedTaskId] = useState(null);

  // Filters & Sorting state
  const [activeStatusFilter, setActiveStatusFilter] = useState('all');
  const [selectedPriority, setSelectedPriority] = useState('all');
  const [selectedRole, setSelectedRole] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [groupBy, setGroupBy] = useState('status'); // 'status', 'priority', 'role', 'none'
  const [sortBy, setSortBy] = useState('id'); // 'id', 'priority', 'hours', 'title'

  // Expandable sections collapse state
  const [collapsedGroups, setCollapsedGroups] = useState({});

  // AI Assistant advice state for selected task
  const [aiAdvice, setAiAdvice] = useState({});
  const [loadingAdvice, setLoadingAdvice] = useState(false);

  useEffect(() => {
    if (id) {
      localStorage.setItem('active_project_id', id);
      fetchTasks();
    }
  }, [id]);

  const fetchTasks = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get(`/api/projects/${id}/tasks`);
      const data = res.data || {};
      setTaskPlan(data);

      const rawTasks = data.tasks || (Array.isArray(data) ? data : []);
      const initialized = rawTasks.map((t, idx) => {
        const normStatus = (t.status || '').toLowerCase();
        let colId = 'todo';
        if (normStatus === 'completed' || normStatus === 'done') colId = 'done';
        else if (normStatus === 'in_progress' || normStatus === 'inprogress') colId = 'in_progress';
        else if (normStatus === 'review' || normStatus === 'in_review') colId = 'in_review';
        else if (t.columnId) colId = t.columnId;
        else if (idx % 4 === 0) colId = 'in_progress';
        else if (idx % 5 === 0) colId = 'in_review';
        else if (idx % 6 === 0) colId = 'done';

        return {
          ...t,
          id: t.task_id || t.id || `TASK-${idx + 1}`,
          task_id: t.task_id || t.id || `TASK-${idx + 1}`,
          columnId: colId,
          subtasksDone: t.subtasksDone || [],
        };
      });

      setTasks(initialized);
      if (initialized.length > 0) {
        setSelectedTaskId(initialized[0].id);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Tasks not generated yet.'));
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = (taskId, newCol) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId || t.task_id === taskId ? { ...t, columnId: newCol, status: newCol } : t))
    );
  };

  const handleToggleSubtask = (taskId, subtaskIdx) => {
    setTasks((prev) =>
      prev.map((t) => {
        if (t.id === taskId || t.task_id === taskId) {
          const current = t.subtasksDone || [];
          const updated = current.includes(subtaskIdx)
            ? current.filter((i) => i !== subtaskIdx)
            : [...current, subtaskIdx];
          return { ...t, subtasksDone: updated };
        }
        return t;
      })
    );
  };

  const toggleGroupCollapse = (groupKey) => {
    setCollapsedGroups((prev) => ({ ...prev, [groupKey]: !prev[groupKey] }));
  };

  // Available roles for filter dropdown
  const availableRoles = useMemo(() => {
    const rolesSet = new Set();
    tasks.forEach((t) => {
      if (t.assigned_role) rolesSet.add(t.assigned_role);
    });
    return Array.from(rolesSet);
  }, [tasks]);

  // Filtered tasks array
  const filteredTasks = useMemo(() => {
    return tasks.filter((t) => {
      // Status filter
      if (activeStatusFilter !== 'all' && t.columnId !== activeStatusFilter) {
        return false;
      }
      // Priority filter
      if (selectedPriority !== 'all' && (t.priority || '').toLowerCase() !== selectedPriority.toLowerCase()) {
        return false;
      }
      // Role filter
      if (selectedRole !== 'all' && t.assigned_role !== selectedRole) {
        return false;
      }
      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesTitle = t.title?.toLowerCase().includes(q);
        const matchesId = (t.task_id || t.id)?.toLowerCase().includes(q);
        const matchesRole = t.assigned_role?.toLowerCase().includes(q);
        const matchesDesc = t.description?.toLowerCase().includes(q);
        if (!matchesTitle && !matchesId && !matchesRole && !matchesDesc) {
          return false;
        }
      }
      return true;
    }).sort((a, b) => {
      if (sortBy === 'priority') {
        const prioOrder = { critical: 4, high: 3, medium: 2, low: 1 };
        return (prioOrder[(b.priority || 'medium').toLowerCase()] || 0) - (prioOrder[(a.priority || 'medium').toLowerCase()] || 0);
      }
      if (sortBy === 'hours') {
        return (b.estimated_hours || 0) - (a.estimated_hours || 0);
      }
      if (sortBy === 'title') {
        return (a.title || '').localeCompare(b.title || '');
      }
      return (a.id || '').localeCompare(b.id || '');
    });
  }, [tasks, activeStatusFilter, selectedPriority, selectedRole, searchQuery, sortBy]);

  // Grouped tasks matrix
  const groupedTasks = useMemo(() => {
    if (groupBy === 'none') {
      return [{ key: 'all', title: 'All Tasks', tasks: filteredTasks }];
    }

    if (groupBy === 'priority') {
      const groups = {
        critical: { key: 'critical', title: 'Critical Priority Tasks', tasks: [] },
        high: { key: 'high', title: 'High Priority Tasks', tasks: [] },
        medium: { key: 'medium', title: 'Medium Priority Tasks', tasks: [] },
        low: { key: 'low', title: 'Low Priority Tasks', tasks: [] },
      };
      filteredTasks.forEach((t) => {
        const prio = (t.priority || 'medium').toLowerCase();
        if (groups[prio]) groups[prio].tasks.push(t);
        else groups.medium.tasks.push(t);
      });
      return Object.values(groups).filter((g) => g.tasks.length > 0);
    }

    if (groupBy === 'role') {
      const map = {};
      filteredTasks.forEach((t) => {
        const role = t.assigned_role || 'Unassigned';
        if (!map[role]) map[role] = { key: role, title: `${role} Tasks`, tasks: [] };
        map[role].tasks.push(t);
      });
      return Object.values(map);
    }

    // Default: group by status
    const statusGroups = [
      { key: 'todo', title: 'To Do', icon: STATUS_CONFIG.todo.icon, color: STATUS_CONFIG.todo.color },
      { key: 'in_progress', title: 'In Progress', icon: STATUS_CONFIG.in_progress.icon, color: STATUS_CONFIG.in_progress.color },
      { key: 'in_review', title: 'In Review', icon: STATUS_CONFIG.in_review.icon, color: STATUS_CONFIG.in_review.color },
      { key: 'done', title: 'Done', icon: STATUS_CONFIG.done.icon, color: STATUS_CONFIG.done.color },
    ];

    return statusGroups.map((sg) => ({
      ...sg,
      tasks: filteredTasks.filter((t) => t.columnId === sg.key),
    }));
  }, [filteredTasks, groupBy]);

  // Currently selected task object
  const selectedTask = useMemo(() => {
    return tasks.find((t) => t.id === selectedTaskId) || tasks[0] || null;
  }, [tasks, selectedTaskId]);

  // Overall metric counts
  const totalCount = tasks.length;
  const todoCount = tasks.filter((t) => t.columnId === 'todo').length;
  const inProgressCount = tasks.filter((t) => t.columnId === 'in_progress').length;
  const inReviewCount = tasks.filter((t) => t.columnId === 'in_review').length;
  const doneCount = tasks.filter((t) => t.columnId === 'done').length;
  const overallProgressPct = totalCount > 0 ? Math.round((doneCount / totalCount) * 100) : 0;

  // AI execution advice for selected task
  const handleFetchAiAdvice = async (task) => {
    if (!task) return;
    setLoadingAdvice(true);
    try {
      const res = await api.post(`/api/projects/${id}/chat`, {
        message: `Provide concise implementation advice and key code requirements for task "${task.title}" (Role: ${task.assigned_role || 'Developer'}, Priority: ${task.priority || 'Medium'}).`,
      });
      setAiAdvice((prev) => ({ ...prev, [task.id]: res.data?.response || 'No specific advice generated.' }));
    } catch (err) {
      setAiAdvice((prev) => ({ ...prev, [task.id]: 'AI Assistant is currently unavailable. Review task specs manually.' }));
    } finally {
      setLoadingAdvice(false);
    }
  };

  if (loading) {
    return (
      <div style={{ maxWidth: '1600px', margin: '0 auto', paddingBottom: '60px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
          <div className="skeleton" style={{ height: '80px', borderRadius: '16px' }} />
          <div className="skeleton" style={{ height: '100px', borderRadius: '16px' }} />
          <div className="skeleton" style={{ height: '600px', borderRadius: '16px' }} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card" style={{ padding: '48px', textAlign: 'center', maxWidth: '600px', margin: '40px auto' }}>
        <ShieldAlert size={48} color="var(--accent-rose)" style={{ marginBottom: '16px' }} />
        <h2 style={{ fontSize: '1.4rem', marginBottom: '8px' }}>Task Board Not Ready</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>{error}</p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
          <button onClick={() => navigate(`/projects/${id}/architecture`)} className="btn btn-secondary">
            Go to Architecture
          </button>
          <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
            <LayoutDashboard size={16} /> Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1600px', margin: '0 auto', paddingBottom: '80px', width: '100%' }}>
      {/* 1. PAGE HEADER */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 900, letterSpacing: '-0.02em', margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
            Task Board <span className="gradient-text-cyan">Overview</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            Structured, beginner-friendly view of development tasks generated by the multi-agent system.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <button onClick={() => navigate(`/projects/${id}/architecture`)} className="btn btn-secondary btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <ArrowLeft size={14} /> Back: Architecture
          </button>
          <button onClick={() => navigate('/projects/new')} className="btn btn-secondary btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <PlusCircle size={14} /> New Project
          </button>
          <button onClick={() => navigate(`/projects/${id}/timeline`)} className="btn btn-gradient btn-md" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            Next: Timeline <ArrowRight size={16} />
          </button>
        </div>
      </div>

      {/* 2. 7-STAGE PIPELINE STEP BAR */}
      <div className="glass-card mb-6" style={{ padding: '12px 20px', marginBottom: '20px', background: 'rgba(15, 23, 42, 0.8)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', overflowX: 'auto', gap: '8px', paddingBottom: '4px' }}>
          {STAGES.map((s, idx) => (
            <React.Fragment key={s.key}>
              <button
                onClick={() => navigate(`/projects/${id}/${s.path}`)}
                style={{
                  background: s.active ? 'linear-gradient(135deg, rgba(6, 182, 212, 0.25) 0%, rgba(59, 130, 246, 0.25) 100%)' : 'transparent',
                  border: s.active ? '1px solid var(--accent-cyan)' : '1px solid transparent',
                  color: s.active ? '#FFF' : 'var(--text-muted)',
                  borderRadius: '8px',
                  padding: '6px 12px',
                  fontSize: '0.82rem',
                  fontWeight: s.active ? 700 : 500,
                  whiteSpace: 'nowrap',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  transition: 'all 0.2s ease',
                }}
              >
                <span
                  style={{
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    background: s.active ? 'var(--accent-cyan)' : 'rgba(255, 255, 255, 0.1)',
                    color: s.active ? '#090D16' : 'var(--text-muted)',
                    fontSize: '0.7rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 800,
                  }}
                >
                  {idx + 1}
                </span>
                {s.label}
              </button>
              {idx < STAGES.length - 1 && (
                <span style={{ color: 'var(--border-medium)', fontSize: '0.8rem' }}>→</span>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* 3. SUMMARY CARDS ROW */}
      <div className="summary-cards-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px', marginBottom: '20px' }}>
        <div className="glass-card" style={{ padding: '14px 16px', background: 'rgba(15, 23, 42, 0.85)' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Total Tasks</span>
          <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#FFF', marginTop: '2px' }}>{totalCount}</div>
        </div>

        <div className="glass-card" style={{ padding: '14px 16px', background: 'rgba(15, 23, 42, 0.85)', borderLeft: '3px solid #38BDF8' }}>
          <span style={{ fontSize: '0.7rem', color: '#38BDF8', textTransform: 'uppercase', fontWeight: 700 }}>To Do</span>
          <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#38BDF8', marginTop: '2px' }}>{todoCount}</div>
        </div>

        <div className="glass-card" style={{ padding: '14px 16px', background: 'rgba(15, 23, 42, 0.85)', borderLeft: '3px solid #FBBF24' }}>
          <span style={{ fontSize: '0.7rem', color: '#FBBF24', textTransform: 'uppercase', fontWeight: 700 }}>In Progress</span>
          <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#FBBF24', marginTop: '2px' }}>{inProgressCount}</div>
        </div>

        <div className="glass-card" style={{ padding: '14px 16px', background: 'rgba(15, 23, 42, 0.85)', borderLeft: '3px solid #C084FC' }}>
          <span style={{ fontSize: '0.7rem', color: '#C084FC', textTransform: 'uppercase', fontWeight: 700 }}>In Review</span>
          <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#C084FC', marginTop: '2px' }}>{inReviewCount}</div>
        </div>

        <div className="glass-card" style={{ padding: '14px 16px', background: 'rgba(15, 23, 42, 0.85)', borderLeft: '3px solid #34D399' }}>
          <span style={{ fontSize: '0.7rem', color: '#34D399', textTransform: 'uppercase', fontWeight: 700 }}>Done</span>
          <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#34D399', marginTop: '2px' }}>{doneCount}</div>
        </div>

        <div className="glass-card" style={{ padding: '14px 16px', background: 'rgba(15, 23, 42, 0.85)', borderLeft: '3px solid var(--accent-cyan)' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--accent-cyan)', textTransform: 'uppercase', fontWeight: 700 }}>Overall Progress</span>
          <div style={{ fontSize: '1.4rem', fontWeight: 900, color: 'var(--accent-cyan)', marginTop: '2px' }}>{overallProgressPct}%</div>
          <div style={{ width: '100%', background: 'rgba(255, 255, 255, 0.1)', height: '4px', borderRadius: '2px', marginTop: '6px', overflow: 'hidden' }}>
            <div style={{ width: `${overallProgressPct}%`, background: 'var(--accent-cyan)', height: '100%' }} />
          </div>
        </div>
      </div>

      {/* 4. FULL-WIDTH FILTER & CONTROL TOOLBAR */}
      <div className="glass-card" style={{ padding: '14px 18px', marginBottom: '20px', background: 'rgba(15, 23, 42, 0.88)' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* Search Box */}
          <div style={{ position: 'relative', flex: '1 1 260px', minWidth: '220px' }}>
            <Search size={15} color="var(--text-dim)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search tasks by title, ID, role, description..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="form-control"
              style={{ paddingLeft: '36px', height: '36px', fontSize: '0.82rem', width: '100%' }}
            />
          </div>

          {/* Filter Dropdowns Controls */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center' }}>
            {/* Status Filter */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Filter size={13} color="var(--accent-cyan)" />
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>Status:</span>
              <select
                value={activeStatusFilter}
                onChange={(e) => setActiveStatusFilter(e.target.value)}
                className="form-control"
                style={{ height: '36px', fontSize: '0.8rem', width: 'auto', padding: '4px 10px' }}
              >
                <option value="all">All Statuses ({totalCount})</option>
                <option value="todo">To Do ({todoCount})</option>
                <option value="in_progress">In Progress ({inProgressCount})</option>
                <option value="in_review">In Review ({inReviewCount})</option>
                <option value="done">Done ({doneCount})</option>
              </select>
            </div>

            {/* Priority Filter */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>Priority:</span>
              <select
                value={selectedPriority}
                onChange={(e) => setSelectedPriority(e.target.value)}
                className="form-control"
                style={{ height: '36px', fontSize: '0.8rem', width: 'auto', padding: '4px 10px' }}
              >
                <option value="all">All Priorities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            {/* Role Filter */}
            {availableRoles.length > 0 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>Role:</span>
                <select
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  className="form-control"
                  style={{ height: '36px', fontSize: '0.8rem', width: 'auto', padding: '4px 10px' }}
                >
                  <option value="all">All Roles</option>
                  {availableRoles.map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Group By Selector */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Layers size={13} color="var(--accent-cyan)" />
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>Group:</span>
              <select
                value={groupBy}
                onChange={(e) => setGroupBy(e.target.value)}
                className="form-control"
                style={{ height: '36px', fontSize: '0.8rem', width: 'auto', padding: '4px 10px' }}
              >
                <option value="status">By Status</option>
                <option value="priority">By Priority</option>
                <option value="role">By Role</option>
                <option value="none">Flat List</option>
              </select>
            </div>

            {/* Sort Selector */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ArrowUpDown size={13} color="var(--accent-violet)" />
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>Sort:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="form-control"
                style={{ height: '36px', fontSize: '0.8rem', width: 'auto', padding: '4px 10px' }}
              >
                <option value="id">Task ID</option>
                <option value="priority">Priority</option>
                <option value="hours">Est. Hours</option>
                <option value="title">Title</option>
              </select>
            </div>

            {/* Reset Button */}
            <button
              onClick={() => {
                setActiveStatusFilter('all');
                setSelectedPriority('all');
                setSelectedRole('all');
                setSearchQuery('');
                setGroupBy('status');
                setSortBy('id');
              }}
              className="btn btn-secondary btn-sm"
              style={{ height: '36px', padding: '0 12px', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <RotateCcw size={13} /> Reset
            </button>
          </div>
        </div>
      </div>

      {/* 5. MAIN TASK LIST + TASK DETAILS ADAPTIVE CONTAINER */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
          gap: '20px',
          alignItems: 'start',
        }}
      >
        {/* LEFT/CENTER PRIMARY TASK LIST (Expands to 100% when details below, or ~68% on wide screens) */}
        <div style={{ minWidth: 0, width: '100%' }}>
          {groupedTasks.length === 0 || filteredTasks.length === 0 ? (
            <div className="glass-card" style={{ padding: '48px', textAlign: 'center', background: 'rgba(15, 23, 42, 0.7)' }}>
              <ListTodo size={40} color="var(--text-dim)" style={{ marginBottom: '12px' }} />
              <h3 style={{ fontSize: '1.1rem', marginBottom: '6px' }}>No Tasks Match Selected Filters</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
                Try resetting search or filter options in the toolbar above.
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {groupedTasks.map((group) => {
                const isCollapsed = collapsedGroups[group.key];
                const GroupIcon = group.icon || Layers;
                const groupColor = group.color || 'var(--accent-cyan)';

                return (
                  <div key={group.key} className="glass-card" style={{ overflow: 'hidden', background: 'rgba(15, 23, 42, 0.88)', borderRadius: '14px' }}>
                    {/* Collapsible Section Header */}
                    <div
                      onClick={() => toggleGroupCollapse(group.key)}
                      style={{
                        padding: '12px 18px',
                        background: 'rgba(30, 41, 59, 0.5)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        cursor: 'pointer',
                        userSelect: 'none',
                        borderBottom: isCollapsed ? 'none' : '1px solid var(--border-dark)',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        {isCollapsed ? <ChevronRight size={16} /> : <ChevronDown size={16} />}
                        <GroupIcon size={16} color={groupColor} />
                        <h4 style={{ fontSize: '0.95rem', fontWeight: 800, color: groupColor, margin: 0 }}>
                          {group.title}
                        </h4>
                        <span className="badge" style={{ background: 'rgba(255, 255, 255, 0.08)', fontSize: '0.75rem' }}>
                          {group.tasks.length} {group.tasks.length === 1 ? 'task' : 'tasks'}
                        </span>
                      </div>
                    </div>

                    {/* Section Task Items List */}
                    {!isCollapsed && (
                      <div style={{ padding: '10px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {group.tasks.length === 0 ? (
                          <div style={{ padding: '16px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.82rem' }}>
                            No tasks in this group
                          </div>
                        ) : (
                          group.tasks.map((t) => {
                            const isSelected = selectedTask?.id === t.id;
                            const prioKey = (t.priority || 'medium').toLowerCase();
                            const prioMeta = PRIORITY_CONFIG[prioKey] || PRIORITY_CONFIG.medium;
                            const statusMeta = STATUS_CONFIG[t.columnId] || STATUS_CONFIG.todo;

                            return (
                              <div
                                key={t.id}
                                onClick={() => setSelectedTaskId(t.id)}
                                style={{
                                  padding: '14px 16px',
                                  borderRadius: '12px',
                                  background: isSelected ? 'rgba(59, 130, 246, 0.14)' : 'rgba(9, 13, 22, 0.55)',
                                  border: isSelected ? '1.5px solid var(--accent-blue)' : '1px solid rgba(255, 255, 255, 0.06)',
                                  boxShadow: isSelected ? '0 0 16px rgba(59, 130, 246, 0.25)' : 'none',
                                  cursor: 'pointer',
                                  transition: 'all 0.15s ease',
                                  display: 'flex',
                                  flexDirection: 'column',
                                  gap: '8px',
                                }}
                              >
                                {/* Header Row: ID, Priority, Role & Status */}
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                                      {t.task_id || t.id}
                                    </span>
                                    <span
                                      style={{
                                        fontSize: '0.65rem',
                                        fontWeight: 800,
                                        padding: '2px 7px',
                                        borderRadius: '4px',
                                        background: prioMeta.bg,
                                        color: prioMeta.color,
                                      }}
                                    >
                                      {prioMeta.label}
                                    </span>
                                  </div>

                                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                      <User size={12} color="var(--accent-cyan)" /> {t.assigned_role || 'Developer'}
                                    </span>
                                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '3px' }}>
                                      <Clock size={12} color="var(--text-dim)" /> {t.estimated_hours || 4}h
                                    </span>

                                    {/* Inline Status Dropdown */}
                                    <div onClick={(e) => e.stopPropagation()}>
                                      <select
                                        value={t.columnId}
                                        onChange={(e) => handleStatusChange(t.id, e.target.value)}
                                        style={{
                                          background: statusMeta.bg,
                                          color: statusMeta.color,
                                          border: `1px solid ${statusMeta.border}`,
                                          borderRadius: '6px',
                                          fontSize: '0.72rem',
                                          fontWeight: 700,
                                          padding: '3px 8px',
                                          cursor: 'pointer',
                                          outline: 'none',
                                        }}
                                      >
                                        <option value="todo">To Do</option>
                                        <option value="in_progress">In Progress</option>
                                        <option value="in_review">In Review</option>
                                        <option value="done">Done</option>
                                      </select>
                                    </div>
                                  </div>
                                </div>

                                {/* Body Row: Title & Description */}
                                <div>
                                  <h4 style={{ fontSize: '0.95rem', fontWeight: 800, color: isSelected ? '#FFF' : 'var(--text-main)', margin: '0 0 4px 0', lineHeight: 1.35 }}>
                                    {t.title}
                                  </h4>
                                  {t.description && (
                                    <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
                                      {t.description}
                                    </p>
                                  )}
                                </div>
                              </div>
                            );
                          })
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* RIGHT / BOTTOM SELECTED TASK DETAILS PANEL */}
        <div
          className="glass-card"
          style={{
            padding: '20px',
            background: 'rgba(15, 23, 42, 0.92)',
            borderRadius: '16px',
            position: 'sticky',
            top: '85px',
            minWidth: '320px',
          }}
        >
          {selectedTask ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Details Header */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-dark)', paddingBottom: '12px' }}>
                <span className="badge badge-cyan" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', fontWeight: 800 }}>
                  {selectedTask.task_id || selectedTask.id}
                </span>

                {/* Status Dropdown in Details */}
                <select
                  value={selectedTask.columnId}
                  onChange={(e) => handleStatusChange(selectedTask.id, e.target.value)}
                  style={{
                    background: STATUS_CONFIG[selectedTask.columnId]?.bg,
                    color: STATUS_CONFIG[selectedTask.columnId]?.color,
                    border: `1px solid ${STATUS_CONFIG[selectedTask.columnId]?.border}`,
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    padding: '4px 8px',
                    cursor: 'pointer',
                  }}
                >
                  <option value="todo">To Do</option>
                  <option value="in_progress">In Progress</option>
                  <option value="in_review">In Review</option>
                  <option value="done">Done</option>
                </select>
              </div>

              {/* Task Title */}
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#FFF', margin: 0, lineHeight: 1.3 }}>
                {selectedTask.title}
              </h3>

              {/* Specification / Description */}
              <div style={{ background: 'rgba(9, 13, 22, 0.6)', padding: '12px', borderRadius: '10px', border: '1px solid var(--border-dark)' }}>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '4px' }}>
                  Description / Specification:
                </span>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', margin: 0, lineHeight: 1.45 }}>
                  {selectedTask.description || 'Implement core task deliverable based on architecture blueprint.'}
                </p>
              </div>

              {/* Task Metadata Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '8px 10px', borderRadius: '8px' }}>
                  <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', display: 'block' }}>Assigned Role</span>
                  <strong style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>{selectedTask.assigned_role || 'Developer'}</strong>
                </div>

                <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '8px 10px', borderRadius: '8px' }}>
                  <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', display: 'block' }}>Priority</span>
                  <strong style={{ fontSize: '0.8rem', color: PRIORITY_CONFIG[(selectedTask.priority || 'medium').toLowerCase()]?.color || '#FFF' }}>
                    {(selectedTask.priority || 'Medium').toUpperCase()}
                  </strong>
                </div>

                <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '8px 10px', borderRadius: '8px' }}>
                  <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', display: 'block' }}>Estimated Hours</span>
                  <strong style={{ fontSize: '0.8rem', color: '#FFF' }}>{selectedTask.estimated_hours || 4} Hours</strong>
                </div>

                <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '8px 10px', borderRadius: '8px' }}>
                  <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', display: 'block' }}>Complexity</span>
                  <strong style={{ fontSize: '0.8rem', color: 'var(--accent-amber)' }}>{selectedTask.complexity || 2} / 5</strong>
                </div>
              </div>

              {/* Dependencies */}
              {selectedTask.dependencies && selectedTask.dependencies.length > 0 && (
                <div>
                  <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
                    Prerequisite Tasks:
                  </span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {selectedTask.dependencies.map((dep, idx) => (
                      <span key={idx} className="badge badge-purple" style={{ fontSize: '0.7rem' }}>
                        <Link2 size={10} style={{ marginRight: '4px' }} /> {dep}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Subtasks / Deliverables Checklist */}
              <div>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
                  Subtasks & Deliverables Checklist:
                </span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {(selectedTask.subtasks || [
                    `Design & setup data structures for ${selectedTask.title}`,
                    `Implement logic and write unit tests`,
                    `Perform peer code review and integration check`,
                  ]).map((st, idx) => {
                    const isChecked = (selectedTask.subtasksDone || []).includes(idx);
                    return (
                      <div
                        key={idx}
                        onClick={() => handleToggleSubtask(selectedTask.id, idx)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '6px 10px',
                          borderRadius: '6px',
                          background: isChecked ? 'rgba(52, 211, 153, 0.1)' : 'rgba(255, 255, 255, 0.03)',
                          cursor: 'pointer',
                          fontSize: '0.8rem',
                          color: isChecked ? '#34D399' : 'var(--text-main)',
                          textDecoration: isChecked ? 'line-through' : 'none',
                        }}
                      >
                        <CheckSquare size={14} color={isChecked ? '#34D399' : 'var(--text-dim)'} />
                        <span>{st}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* AI Assistant Guidance Action */}
              <div style={{ borderTop: '1px solid var(--border-dark)', paddingTop: '12px' }}>
                {!aiAdvice[selectedTask.id] ? (
                  <button
                    onClick={() => handleFetchAiAdvice(selectedTask)}
                    disabled={loadingAdvice}
                    className="btn btn-secondary btn-sm"
                    style={{ width: '100%', justifyContent: 'center', gap: '6px', fontSize: '0.8rem' }}
                  >
                    <Sparkles size={14} color="var(--accent-cyan)" />
                    {loadingAdvice ? 'Generating Advice...' : 'Get AI Execution Advice'}
                  </button>
                ) : (
                  <div style={{ background: 'rgba(56, 189, 248, 0.1)', padding: '10px', borderRadius: '8px', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
                    <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                      <Sparkles size={12} /> AI Execution Tip:
                    </span>
                    <p style={{ fontSize: '0.78rem', color: '#E2E8F0', margin: 0, lineHeight: 1.4 }}>
                      {aiAdvice[selectedTask.id]}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-dim)' }}>
              <Eye size={36} style={{ marginBottom: '12px' }} />
              <p style={{ fontSize: '0.85rem' }}>Select any task from the list to view its full specification and subtasks.</p>
            </div>
          )}
        </div>
      </div>

      {/* 6. BOTTOM "UNDERSTANDING THE TASK BOARD" HELP CARD */}
      <div className="glass-card" style={{ padding: '20px 24px', marginTop: '32px', background: 'rgba(15, 23, 42, 0.7)', borderRadius: '16px' }}>
        <h4 style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--accent-cyan)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <HelpCircle size={16} /> Understanding the Task Board
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          <div>
            <strong style={{ color: '#FFF', display: 'block', marginBottom: '2px' }}>📌 Status Lifecycle:</strong>
            Tasks progress through 4 statuses: <em>To Do</em> → <em>In Progress</em> → <em>In Review</em> → <em>Done</em>.
          </div>
          <div>
            <strong style={{ color: '#FFF', display: 'block', marginBottom: '2px' }}>🔍 Detailed Inspection:</strong>
            Click any task card to open the selected Task Details panel.
          </div>
          <div>
            <strong style={{ color: '#FFF', display: 'block', marginBottom: '2px' }}>⚡ Priority Levels:</strong>
            Critical and High priorities require immediate developer focus before low priority tasks.
          </div>
          <div>
            <strong style={{ color: '#FFF', display: 'block', marginBottom: '2px' }}>🔄 Updating Status:</strong>
            Use status dropdowns in the task card or details panel to update completion state instantly.
          </div>
        </div>
      </div>
    </div>
  );
}
