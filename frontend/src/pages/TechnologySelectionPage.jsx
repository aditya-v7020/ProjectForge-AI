import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Lock,
  Sparkles,
  Check,
  CheckCircle2,
  AlertCircle,
  Cpu,
  Layout,
  Server,
  Database,
  Shield,
  Cloud,
  Layers,
  ArrowLeft,
  Loader2,
  Search,
  Ban,
  Terminal,
  Code2,
  Zap,
  TestTube2,
  XCircle,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import api from '../services/api';
import { getErrorMessage } from '../utils/errors';
import AgentProgressModal from '../components/AgentProgressModal';
import TechComparisonModal from '../components/TechComparisonModal';
import TavilySourcesCard from '../components/TavilySourcesCard';
import { useSSE } from '../hooks/useSSE';

// Standard 10 logical categories metadata
const CATEGORY_META = [
  { key: 'frontend', label: 'Frontend', icon: Layout, required: true, desc: 'User interface frameworks' },
  { key: 'backend', label: 'Backend', icon: Server, required: true, desc: 'Server & API frameworks' },
  { key: 'database', label: 'Database', icon: Database, required: true, desc: 'Data persistence & storage' },
  { key: 'ai_ml', label: 'AI / ML', icon: Cpu, required: false, desc: 'Intelligence & machine learning' },
  { key: 'authentication', label: 'Authentication', icon: Shield, required: false, desc: 'User identity & security' },
  { key: 'deployment', label: 'Deployment / Cloud', icon: Cloud, required: false, desc: 'Hosting & cloud infrastructure' },
  { key: 'api_communication', label: 'API / Comm', icon: Code2, required: false, desc: 'Protocols & APIs' },
  { key: 'devops', label: 'DevOps / CI/CD', icon: Terminal, required: false, desc: 'Automation & containerization' },
  { key: 'caching_messaging', label: 'Cache / Queue', icon: Zap, required: false, desc: 'In-memory cache & messaging' },
  { key: 'testing', label: 'Testing', icon: TestTube2, required: false, desc: 'Testing & QA frameworks' },
];

const REQUIRED_CATEGORY_KEYS = ['frontend', 'backend', 'database'];

const getCategoryMeta = (catKey) => {
  const normalized = (catKey || '').toLowerCase();
  return (
    CATEGORY_META.find((c) => c.key === normalized) || {
      key: catKey,
      label: catKey.replace(/_/g, ' ').toUpperCase(),
      icon: Layers,
      required: false,
      desc: 'Technology options',
    }
  );
};

const getMatchScoreColor = (score) => {
  if (score >= 85) return '#38BDF8';
  if (score >= 70) return '#818CF8';
  return '#C084FC';
};

export default function TechnologySelectionPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [categories, setCategories] = useState([]);
  const [selectedTechs, setSelectedTechs] = useState({});
  const [isLocked, setIsLocked] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [showSSE, setShowSSE] = useState(false);

  // Tab, Search & Expansion state
  const [activeCategoryKey, setActiveCategoryKey] = useState('frontend');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedCardKey, setExpandedCardKey] = useState(null);
  const [expandedCategories, setExpandedCategories] = useState({});

  // Feature 4 & Feature 6 state
  const [compareModalCat, setCompareModalCat] = useState(null);
  const [regenerating, setRegenerating] = useState(false);

  const handleRegenerateTech = async () => {
    setRegenerating(true);
    setError('');
    try {
      await api.post(`/api/projects/${id}/regenerate/technology`);
      await loadOptions();
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to regenerate technology options.'));
    } finally {
      setRegenerating(false);
    }
  };

  const toggleExpandCategory = (catKey) => {
    setExpandedCategories((prev) => ({
      ...prev,
      [catKey]: !prev[catKey],
    }));
  };

  const { agentProgress, isConnected, isFinished } = useSSE(showSSE ? id : null);

  useEffect(() => {
    loadOptions();
  }, [id]);

  useEffect(() => {
    if (isFinished) {
      setTimeout(() => {
        navigate(`/projects/${id}/architecture`);
      }, 1200);
    }
  }, [isFinished, id, navigate]);

  const loadOptions = async () => {
    setLoading(true);
    setError('');
    setSelectedTechs({});
    setIsLocked(false);
    setCategories([]);
    try {
      const optionsRes = await api.get(`/api/projects/${id}/technology-options`);
      const cats = optionsRes.data.categories || [];
      setCategories(cats);

      if (cats.length > 0 && cats[0].category) {
        setActiveCategoryKey(cats[0].category);
      }

      const projRes = await api.get(`/api/projects/${id}`);
      const existingSelections = projRes.data.selected_technologies || [];

      const initialSelected = {};
      let alreadyLocked = false;

      if (existingSelections.length > 0) {
        existingSelections.forEach((s) => {
          initialSelected[s.category] = s.name;
        });
        alreadyLocked = existingSelections.every((s) => s.is_locked);
      }

      setSelectedTechs(initialSelected);
      setIsLocked(alreadyLocked);
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load technology options.'));
    } finally {
      setLoading(false);
    }
  };

  const handleSelectTech = (catKey, techName) => {
    if (isLocked) return;

    setSelectedTechs((prev) => {
      if (prev[catKey] === techName) {
        const next = { ...prev };
        delete next[catKey];
        return next;
      }
      return {
        ...prev,
        [catKey]: techName,
      };
    });
  };

  const handleSetNotRequired = (catKey) => {
    if (isLocked) return;

    setSelectedTechs((prev) => {
      if (prev[catKey] === 'Not Required') {
        const next = { ...prev };
        delete next[catKey];
        return next;
      }
      return {
        ...prev,
        [catKey]: 'Not Required',
      };
    });
  };

  const handleConfirmAndLock = async () => {
    if (isLocked) return;

    const missingRequired = REQUIRED_CATEGORY_KEYS.filter((key) => !selectedTechs[key]);

    if (missingRequired.length > 0) {
      const missingLabels = missingRequired
        .map((k) => getCategoryMeta(k).label)
        .join(', ');
      setError(`Please select a technology for all required categories: ${missingLabels}.`);
      return;
    }

    // Default any untouched optional category to "Not Required"
    const finalPayload = { ...selectedTechs };
    categories.forEach((catObj) => {
      const catKey = catObj.category;
      if (!REQUIRED_CATEGORY_KEYS.includes(catKey) && !finalPayload[catKey]) {
        finalPayload[catKey] = 'Not Required';
      }
    });

    setSubmitting(true);
    setError('');
    setShowSSE(true);

    try {
      await api.post(`/api/projects/${id}/technology-selection`, {
        selections: finalPayload,
      });

      setIsLocked(true);
      setSelectedTechs(finalPayload);

      await api.post(`/api/projects/${id}/generate-plan`);
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to lock technologies and generate architecture.'));
      setSubmitting(false);
      setShowSSE(false);
    }
  };

  // Filtered categories and search matching
  const activeCategoryObj = useMemo(() => {
    return categories.find((c) => c.category === activeCategoryKey) || {
      category: activeCategoryKey,
      alternatives: [],
    };
  }, [categories, activeCategoryKey]);

  const searchResults = useMemo(() => {
    if (!searchQuery.trim()) return null;
    const q = searchQuery.toLowerCase().trim();

    const results = [];
    categories.forEach((catObj) => {
      const catMeta = getCategoryMeta(catObj.category);
      (catObj.alternatives || []).forEach((alt) => {
        const nameMatch = alt.name.toLowerCase().includes(q);
        const descMatch = (alt.fit_reason || '').toLowerCase().includes(q);
        const catMatch = catMeta.label.toLowerCase().includes(q);
        const advMatch = (alt.advantages || []).some((a) => a.toLowerCase().includes(q));

        if (nameMatch || descMatch || catMatch || advMatch) {
          results.push({ ...alt, category: catObj.category, catMeta });
        }
      });
    });
    return results;
  }, [categories, searchQuery]);

  // Compute selection stats
  const requiredCount = REQUIRED_CATEGORY_KEYS.filter((k) => Boolean(selectedTechs[k])).length;
  const isRequiredComplete = requiredCount === 3;

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: '16px' }}>
        <Loader2 size={36} className="spinner text-cyan" />
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>Analyzing technology options & recommendations...</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', paddingBottom: '100px' }}>
      {showSSE && <AgentProgressModal progress={agentProgress} isConnected={isConnected} isFinished={isFinished} />}

      {/* Header Banner */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <button onClick={() => navigate(`/projects/${id}/requirements`)} className="btn btn-secondary btn-sm" style={{ padding: '6px 12px' }}>
            <ArrowLeft size={14} /> Requirements
          </button>
          <div className="badge badge-info" style={{ margin: 0 }}>
            <Cpu size={14} className="pulse-glow" /> Stage 02 / Interactive Technology Selector
          </div>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'flex-end', justifyContent: 'space-between', gap: '16px' }}>
          <div>
            <h1 style={{ fontSize: '2.1rem', fontWeight: 900, letterSpacing: '-0.02em', margin: 0 }}>
              Technology <span className="gradient-text-cyan">Selection & Architecture Lock</span>
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginTop: '4px', maxWidth: '800px' }}>
              Review AI recommendations or set optional categories to "Not Required". Your locked selections dictate downstream architecture, task plan, timeline, and risk analysis.
            </p>
          </div>

          {/* Action controls & Search */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <button
              onClick={() => setCompareModalCat(activeCategoryKey)}
              className="btn btn-secondary btn-sm"
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Layers size={14} /> Compare Alternatives
            </button>
            <button
              onClick={handleRegenerateTech}
              disabled={regenerating}
              className="btn btn-secondary btn-sm"
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Loader2 size={14} className={regenerating ? 'spinner' : ''} />
              {regenerating ? 'Regenerating...' : 'Regenerate Options'}
            </button>
            <div style={{ position: 'relative', width: '100%', maxWidth: '240px' }}>
              <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="text"
                placeholder="Search tech..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 14px 8px 38px',
                  borderRadius: '10px',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  color: '#FFF',
                  fontSize: '0.85rem',
                  outline: 'none',
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger" style={{ marginBottom: '20px' }}>
          <AlertCircle size={18} /> {error}
        </div>
      )}

      {/* Main Layout Grid: Left Tabs & Cards (Minmax), Right Sticky Sidebar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 320px', gap: '24px', alignItems: 'start' }}>
        
        {/* Left Column: Category Tabs + Technology Grid */}
        <div style={{ minWidth: 0 }}>
          
          {/* Horizontal Category Navigation Tabs */}
          {!searchQuery && (
            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '8px',
                paddingBottom: '10px',
                marginBottom: '20px',
                borderBottom: '1px solid var(--border-dark)',
              }}
            >
              {CATEGORY_META.map((catMeta) => {
                const catKey = catMeta.key;
                const Icon = catMeta.icon;
                const isActive = activeCategoryKey === catKey;
                const selectedVal = selectedTechs[catKey];
                const isSelected = Boolean(selectedVal);
                const isNotRequired = selectedVal === 'Not Required';

                return (
                  <button
                    key={catKey}
                    type="button"
                    onClick={() => setActiveCategoryKey(catKey)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '8px 14px',
                      borderRadius: '12px',
                      border: isActive
                        ? '1px solid var(--accent-cyan)'
                        : isSelected
                        ? '1px solid rgba(52, 211, 153, 0.4)'
                        : '1px solid var(--border-dark)',
                      background: isActive
                        ? 'rgba(6, 182, 212, 0.16)'
                        : isSelected
                        ? 'rgba(16, 185, 129, 0.08)'
                        : 'rgba(15, 23, 42, 0.6)',
                      color: isActive ? '#38BDF8' : isSelected ? '#34D399' : 'var(--text-muted)',
                      cursor: 'pointer',
                      whiteSpace: 'nowrap',
                      fontSize: '0.82rem',
                      fontWeight: isActive || isSelected ? 700 : 500,
                      transition: 'all 0.2s ease',
                      flexShrink: 0,
                    }}
                  >
                    <Icon size={15} color={isActive ? '#38BDF8' : isSelected ? '#34D399' : 'var(--text-muted)'} />
                    <span>{catMeta.label}</span>

                    {catMeta.required ? (
                      <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: isSelected ? '#34D399' : '#FBBF24' }} />
                    ) : (
                      <span style={{ fontSize: '0.65rem', padding: '2px 5px', borderRadius: '4px', background: 'rgba(255,255,255,0.06)', color: 'var(--text-dim)' }}>
                        Opt
                      </span>
                    )}

                    {isSelected && (
                      <span style={{ fontSize: '0.7rem', fontWeight: 800 }}>
                        {isNotRequired ? '✕' : '✓'}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          )}

          {/* Search Active Banner */}
          {searchQuery && (
            <div style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(6, 182, 212, 0.08)', padding: '10px 16px', borderRadius: '10px', border: '1px solid rgba(6, 182, 212, 0.2)' }}>
              <span style={{ fontSize: '0.85rem', color: '#38BDF8' }}>
                Search results for: <strong>"{searchQuery}"</strong> ({searchResults ? searchResults.length : 0} found)
              </span>
              <button onClick={() => setSearchQuery('')} className="btn btn-secondary btn-sm" style={{ padding: '4px 10px', fontSize: '0.75rem' }}>
                Clear Search
              </button>
            </div>
          )}

          {/* SEARCH RESULTS VIEW */}
          {searchQuery ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px' }}>
              {searchResults && searchResults.length > 0 ? (
                searchResults.map((alt) => {
                  const catKey = alt.category;
                  const isSelected = selectedTechs[catKey] === alt.name;
                  const isRecommended = alt.is_recommended;
                  const scoreColor = getMatchScoreColor(alt.suitability_score);

                  return (
                    <motion.div
                      key={`${catKey}-${alt.name}`}
                      whileHover={{ y: isLocked ? 0 : -2 }}
                      style={{
                        padding: '16px',
                        borderRadius: '14px',
                        background: isSelected
                          ? 'linear-gradient(135deg, rgba(6, 182, 212, 0.14) 0%, rgba(15, 23, 42, 0.95) 100%)'
                          : 'rgba(15, 23, 42, 0.7)',
                        border: isSelected ? '2px solid var(--accent-cyan)' : '1px solid var(--border-dark)',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                          <span className="badge" style={{ background: 'rgba(255,255,255,0.06)', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                            {alt.catMeta.label}
                          </span>
                          {isRecommended && (
                            <span className="badge badge-purple" style={{ fontSize: '0.65rem', padding: '2px 6px' }}>
                              <Sparkles size={10} /> AI PICK
                            </span>
                          )}
                        </div>

                        <h3 style={{ fontSize: '1.1rem', fontWeight: 800, margin: '0 0 6px 0', color: '#FFF' }}>
                          {alt.name}
                        </h3>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                          <div style={{ flex: 1, height: '5px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px', overflow: 'hidden' }}>
                            <div style={{ width: `${alt.suitability_score}%`, height: '100%', background: scoreColor }} />
                          </div>
                          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: scoreColor }}>
                            {alt.suitability_score}%
                          </span>
                        </div>

                        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: '0 0 12px 0', lineHeight: 1.4 }}>
                          {alt.fit_reason?.slice(0, 90)}...
                        </p>
                      </div>

                      <button
                        type="button"
                        disabled={isLocked}
                        onClick={() => handleSelectTech(catKey, alt.name)}
                        className={`btn btn-sm ${isSelected ? 'btn-primary' : 'btn-secondary'}`}
                        style={{ width: '100%', fontSize: '0.8rem', padding: '8px' }}
                      >
                        {isSelected ? '✓ Selected' : 'Select'}
                      </button>
                    </motion.div>
                  );
                })
              ) : (
                <div style={{ gridColumn: '1 / -1', padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  No technology matches found for "{searchQuery}".
                </div>
              )}
            </div>
          ) : (
            /* ACTIVE TAB CONTENT VIEW */
            <div>
              {(() => {
                const catMeta = getCategoryMeta(activeCategoryKey);
                const alternatives = activeCategoryObj.alternatives || [];
                const currentSelected = selectedTechs[activeCategoryKey];
                const isNotRequiredSelected = currentSelected === 'Not Required';

                const isCategoryExpanded = Boolean(expandedCategories[activeCategoryKey]);
                const visibleAlternatives = isCategoryExpanded ? alternatives : alternatives.slice(0, 6);
                const remainingCount = Math.max(0, alternatives.length - 6);

                return (
                  <div>
                    {/* Category Header */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                      <div>
                        <h2 style={{ fontSize: '1.2rem', fontWeight: 800, margin: 0, display: 'flex', alignItems: 'center', gap: '8px', color: '#FFF' }}>
                          {catMeta.label}
                          {catMeta.required ? (
                            <span className="badge badge-warning" style={{ fontSize: '0.7rem', padding: '2px 8px' }}>
                              Required
                            </span>
                          ) : (
                            <span className="badge badge-info" style={{ fontSize: '0.7rem', padding: '2px 8px' }}>
                              Optional
                            </span>
                          )}
                        </h2>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          {catMeta.desc} • {alternatives.length} Alternatives Evaluated
                        </span>
                      </div>

                      {currentSelected ? (
                        <span
                          className={`badge ${isNotRequiredSelected ? 'badge-secondary' : 'badge-success'}`}
                          style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px', fontSize: '0.82rem' }}
                        >
                          {isLocked ? <Lock size={13} /> : <CheckCircle2 size={13} />}
                          {isNotRequiredSelected ? 'Not Required' : `Selected: ${currentSelected}`}
                        </span>
                      ) : (
                        <span className="badge badge-warning" style={{ fontSize: '0.8rem', padding: '5px 10px' }}>
                          {catMeta.required ? 'Selection Needed' : 'Optional Choice'}
                        </span>
                      )}
                    </div>

                    {/* Compact Card Grid (2-3 Cols Desktop) */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(270px, 1fr))', gap: '16px' }}>
                      
                      {/* Optional "Not Required" Card */}
                      {!catMeta.required && (
                        <motion.div
                          whileHover={{ y: isLocked ? 0 : -2 }}
                          onClick={() => handleSetNotRequired(activeCategoryKey)}
                          style={{
                            padding: '18px',
                            borderRadius: '14px',
                            cursor: isLocked ? 'default' : 'pointer',
                            background: isNotRequiredSelected
                              ? 'rgba(148, 163, 184, 0.15)'
                              : 'rgba(15, 23, 42, 0.5)',
                            border: isNotRequiredSelected
                              ? '2px solid #94A3B8'
                              : '1px dashed var(--border-medium)',
                            display: 'flex',
                            flexDirection: 'column',
                            justify: 'space-between',
                            transition: 'all 0.2s ease',
                          }}
                        >
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                              <span className="badge badge-secondary" style={{ fontSize: '0.7rem' }}>
                                INTENTIONAL EXCLUSION
                              </span>
                              {isNotRequiredSelected && (
                                <span className="badge badge-info" style={{ fontSize: '0.7rem', background: '#94A3B8', color: '#0F172A' }}>
                                  NOT REQUIRED ✓
                                </span>
                              )}
                            </div>

                            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: '0 0 6px 0', color: isNotRequiredSelected ? '#F1F5F9' : 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <Ban size={18} color={isNotRequiredSelected ? '#94A3B8' : 'var(--text-muted)'} />
                              Not Required
                            </h3>

                            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.4, margin: '0 0 14px 0' }}>
                              Skip this category. Downstream architecture, task plan, timeline, and risk analysis will intentionally exclude {catMeta.label}.
                            </p>
                          </div>

                          <button
                            type="button"
                            disabled={isLocked}
                            onClick={(e) => {
                              e.stopPropagation();
                              handleSetNotRequired(activeCategoryKey);
                            }}
                            className="btn btn-secondary btn-sm"
                            style={{
                              width: '100%',
                              borderRadius: '8px',
                              background: isNotRequiredSelected ? 'rgba(148, 163, 184, 0.3)' : undefined,
                              borderColor: isNotRequiredSelected ? '#94A3B8' : undefined,
                              color: isNotRequiredSelected ? '#FFF' : undefined,
                            }}
                          >
                            {isLocked ? (isNotRequiredSelected ? 'Locked: Not Required' : 'Locked') : isNotRequiredSelected ? '✓ Marked Not Required' : 'Set as Not Required'}
                          </button>
                        </motion.div>
                      )}

                      {/* Tech Options Cards */}
                      {visibleAlternatives.map((alt) => {
                        const isSelected = currentSelected === alt.name;
                        const isRecommended = alt.is_recommended;
                        const scoreColor = getMatchScoreColor(alt.suitability_score);
                        const isExpanded = expandedCardKey === `${activeCategoryKey}-${alt.name}`;

                        return (
                          <motion.div
                            key={alt.name}
                            whileHover={{ y: isLocked ? 0 : -2 }}
                            onClick={() => handleSelectTech(activeCategoryKey, alt.name)}
                            style={{
                              padding: '18px',
                              borderRadius: '14px',
                              cursor: isLocked ? 'default' : 'pointer',
                              background: isSelected
                                ? 'linear-gradient(135deg, rgba(6, 182, 212, 0.16) 0%, rgba(15, 23, 42, 0.95) 100%)'
                                : 'rgba(15, 23, 42, 0.7)',
                              border: isSelected
                                ? '2px solid var(--accent-cyan)'
                                : isRecommended
                                ? '1px solid rgba(139, 92, 246, 0.4)'
                                : '1px solid var(--border-dark)',
                              boxShadow: isSelected
                                ? '0 0 20px rgba(6, 182, 212, 0.2)'
                                : 'none',
                              display: 'flex',
                              flexDirection: 'column',
                              justify: 'space-between',
                              transition: 'all 0.2s ease',
                            }}
                          >
                            <div>
                              {/* Top Row: AI Pick & Difficulty */}
                              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                                {isRecommended ? (
                                  <span className="badge badge-purple" style={{ gap: '4px', padding: '3px 8px', fontSize: '0.68rem', fontWeight: 700 }}>
                                    <Sparkles size={11} color="#C084FC" /> AI RECOMMENDED
                                  </span>
                                ) : (
                                  <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-dim)', fontSize: '0.68rem', textTransform: 'capitalize' }}>
                                    {alt.difficulty || 'medium'}
                                  </span>
                                )}

                                {isSelected && (
                                  <span className="badge badge-info pulse-glow" style={{ padding: '3px 8px', fontSize: '0.72rem', fontWeight: 700 }}>
                                    {isLocked ? <Lock size={11} /> : <Check size={11} />} {isLocked ? 'LOCKED' : 'SELECTED ✓'}
                                  </span>
                                )}
                              </div>

                              {/* Name & Suitability Bar */}
                              <div style={{ marginBottom: '10px' }}>
                                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, margin: '0 0 6px 0', color: '#FFF' }}>
                                  {alt.name}
                                </h3>

                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                  <div style={{ flex: 1, height: '5px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px', overflow: 'hidden' }}>
                                    <div style={{ width: `${alt.suitability_score}%`, height: '100%', background: scoreColor }} />
                                  </div>
                                  <span style={{ fontSize: '0.78rem', fontWeight: 700, color: scoreColor, fontFamily: 'var(--font-mono)' }}>
                                    {alt.suitability_score}%
                                  </span>
                                </div>
                              </div>

                              {/* Advantages Summary */}
                              <div style={{ marginBottom: '10px' }}>
                                <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'grid', gap: '4px' }}>
                                  {(alt.advantages || []).slice(0, 2).map((adv, i) => (
                                    <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '5px', fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.3 }}>
                                      <Check size={12} color="#34D399" style={{ flexShrink: 0, marginTop: '2px' }} />
                                      <span>{adv}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>

                              {/* Fit Reason preview */}
                              {alt.fit_reason && (
                                <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', margin: '0 0 12px 0', lineHeight: 1.35, display: '-webkit-box', WebkitLineClamp: isExpanded ? 'none' : 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                  <strong style={{ color: 'var(--accent-cyan)' }}>Why fit:</strong> {alt.fit_reason}
                                </p>
                              )}
                            </div>

                            {/* Select Action Button */}
                            <button
                              type="button"
                              disabled={isLocked}
                              onClick={(e) => {
                                e.stopPropagation();
                                handleSelectTech(activeCategoryKey, alt.name);
                              }}
                              className={`btn btn-sm ${isSelected ? 'btn-primary' : 'btn-secondary'}`}
                              style={{
                                width: '100%',
                                borderRadius: '8px',
                                fontSize: '0.8rem',
                                fontWeight: 600,
                              }}
                            >
                              {isLocked
                                ? isSelected
                                  ? 'Locked Choice'
                                  : 'Locked'
                                : isSelected
                                ? '✓ Selected'
                                : 'Select Option'}
                            </button>
                          </motion.div>
                        );
                      })}
                    </div>

                    {/* View More / Show Less Button */}
                    {alternatives.length > 6 && (
                      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '24px' }}>
                        <button
                          type="button"
                          onClick={() => toggleExpandCategory(activeCategoryKey)}
                          className="btn btn-secondary btn-sm"
                          style={{
                            padding: '8px 24px',
                            fontSize: '0.82rem',
                            fontWeight: 700,
                            borderRadius: '10px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            background: 'rgba(30, 41, 59, 0.8)',
                            border: '1px solid var(--border-medium)',
                          }}
                        >
                          {isCategoryExpanded ? (
                            <>
                              Show Less Options <ChevronUp size={15} />
                            </>
                          ) : (
                            <>
                              View More ({remainingCount} more options) <ChevronDown size={15} />
                            </>
                          )}
                        </button>
                      </div>
                    )}
                  </div>
                );
              })()}
            </div>
          )}
        </div>

        {/* Right Sticky Sidebar Panel: Selected Stack */}
        <aside style={{ position: 'sticky', top: '90px' }}>
          <div
            className="glass-card"
            style={{
              padding: '20px',
              borderRadius: '16px',
              border: isLocked ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid var(--border-medium)',
              background: 'linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(9, 13, 22, 0.98) 100%)',
            }}
          >
            {/* Header & Status */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px', paddingBottom: '10px', borderBottom: '1px solid var(--border-dark)' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 800, margin: 0, display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Lock size={16} color={isLocked ? '#34D399' : '#38BDF8'} /> Selected Stack
              </h3>
              <span className={`badge ${isLocked ? 'badge-success' : isRequiredComplete ? 'badge-info' : 'badge-warning'}`} style={{ fontSize: '0.72rem' }}>
                {isLocked ? '🔒 LOCKED' : `Required: ${requiredCount}/3 ${isRequiredComplete ? '✓' : ''}`}
              </span>
            </div>

            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '14px', lineHeight: 1.35 }}>
              {isLocked
                ? 'Stack is LOCKED in database. Downstream agents operate on these choices.'
                : 'Select options for required categories (Frontend, Backend, Database). Optional categories default to "Not Required" if unselected.'}
            </p>

            {/* List of all 10 Categories & Choices */}
            <div style={{ display: 'grid', gap: '6px', marginBottom: '18px', maxHeight: '380px', overflowY: 'auto', paddingRight: '4px' }}>
              {CATEGORY_META.map((catMeta) => {
                const catKey = catMeta.key;
                const chosenName = selectedTechs[catKey];
                const isChosen = Boolean(chosenName);
                const isNotReq = chosenName === 'Not Required';

                return (
                  <div
                    key={catKey}
                    onClick={() => setActiveCategoryKey(catKey)}
                    style={{
                      padding: '8px 10px',
                      borderRadius: '8px',
                      background: isChosen
                        ? isNotReq
                          ? 'rgba(148, 163, 184, 0.08)'
                          : 'rgba(16, 185, 129, 0.08)'
                        : catMeta.required
                        ? 'rgba(245, 158, 11, 0.06)'
                        : 'rgba(255, 255, 255, 0.02)',
                      border: isChosen
                        ? isNotReq
                          ? '1px solid rgba(148, 163, 184, 0.25)'
                          : '1px solid rgba(16, 185, 129, 0.3)'
                        : catMeta.required
                        ? '1px dashed rgba(245, 158, 11, 0.3)'
                        : '1px solid var(--border-dark)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      cursor: 'pointer',
                    }}
                  >
                    <div>
                      <span style={{ fontSize: '0.62rem', fontWeight: 700, color: 'var(--text-dim)', display: 'block', textTransform: 'uppercase' }}>
                        {catMeta.label} {catMeta.required && <strong style={{ color: '#FBBF24' }}>*</strong>}
                      </span>
                      <span
                        style={{
                          fontSize: '0.82rem',
                          fontWeight: 700,
                          color: isChosen ? (isNotReq ? '#94A3B8' : '#34D399') : catMeta.required ? '#FBBF24' : 'var(--text-dim)',
                        }}
                      >
                        {isChosen ? chosenName : catMeta.required ? 'Required' : 'Not Required'}
                      </span>
                    </div>

                    {isChosen ? (
                      isNotReq ? (
                        <span style={{ fontSize: '0.7rem', color: '#94A3B8', fontWeight: 700 }}>Skip</span>
                      ) : (
                        <CheckCircle2 size={14} color="#34D399" />
                      )
                    ) : catMeta.required ? (
                      <span style={{ fontSize: '0.7rem', color: '#FBBF24', fontWeight: 800 }}>!</span>
                    ) : (
                      <span style={{ fontSize: '0.65rem', color: 'var(--text-dim)' }}>Default</span>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Lock Button */}
            {!isLocked && (
              <button
                type="button"
                onClick={handleConfirmAndLock}
                disabled={submitting || !isRequiredComplete}
                className="btn btn-gradient"
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '10px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  fontSize: '0.85rem',
                  fontWeight: 700,
                  opacity: !isRequiredComplete ? 0.5 : 1,
                  cursor: !isRequiredComplete ? 'not-allowed' : 'pointer',
                }}
              >
                {submitting ? (
                  <>
                    <Loader2 size={16} className="spinner" /> Locking & Generating...
                  </>
                ) : (
                  <>
                    <Lock size={16} /> LOCK & GENERATE ARCHITECTURE
                  </>
                )}
              </button>
            )}
          </div>
        </aside>
      </div>

      {/* Feature 9: Tavily Research Sources */}
      <TavilySourcesCard projectId={id} />

      {/* Feature 6: Technology Comparison Modal */}
      {compareModalCat && (() => {
        const catObj = categories.find((c) => c.category === compareModalCat) || { category: compareModalCat, alternatives: [] };
        return (
          <TechComparisonModal
            categoryName={getCategoryMeta(compareModalCat).label}
            options={catObj.alternatives || []}
            selectedName={selectedTechs[compareModalCat]}
            onSelect={(name) => handleSelectTech(compareModalCat, name)}
            onClose={() => setCompareModalCat(null)}
          />
        );
      })()}
    </div>
  );
}
