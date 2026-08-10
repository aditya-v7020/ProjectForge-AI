import React, { useState, useEffect } from 'react';
import { Globe, ExternalLink, BookOpen, ShieldCheck, Sparkles } from 'lucide-react';
import api from '../services/api';

export default function TavilySourcesCard({ projectId }) {
  const [sourcesData, setSourcesData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (projectId) {
      fetchSources();
    }
  }, [projectId]);

  const fetchSources = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/api/projects/${projectId}/tavily-sources`);
      setSourcesData(res.data);
    } catch (err) {
      console.error('Failed to fetch Tavily sources:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="skeleton" style={{ height: '140px', borderRadius: '16px', marginBottom: '24px' }} />;
  }

  if (!sourcesData || !sourcesData.sources || sourcesData.sources.length === 0) return null;

  return (
    <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Globe size={20} color="var(--accent-cyan)" />
          <h3 style={{ margin: 0, fontSize: '1.15rem', color: '#FFF' }}>
            Live Market Research Sources <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 400 }}>(via Tavily Search Engine)</span>
          </h3>
        </div>
        <span className="badge badge-info" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Sparkles size={12} /> {sourcesData.sources.length} Verified Sources
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
        {sourcesData.sources.map((src, idx) => (
          <a
            key={idx}
            href={src.url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              padding: '14px',
              borderRadius: '12px',
              backgroundColor: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              textDecoration: 'none',
              transition: 'all 0.2s ease',
              display: 'flex',
              flexDirection: 'column',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'var(--accent-cyan)')}
            onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)')}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--accent-cyan)', textTransform: 'uppercase' }}>
                {src.category || src.domain}
              </span>
              <ExternalLink size={14} color="var(--text-muted)" />
            </div>
            <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#FFF', marginBottom: '6px', lineHeight: 1.3 }}>
              {src.title}
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
              {src.snippet}
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
