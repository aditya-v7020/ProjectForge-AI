import React, { useState } from 'react';
import { X, Check, ArrowRightLeft, ShieldCheck, AlertTriangle, Zap, ThumbsUp, ThumbsDown } from 'lucide-react';

export default function TechComparisonModal({ categoryName, options = [], selectedName, onSelect, onClose }) {
  const [techA, setTechA] = useState(options.find((o) => o.name === selectedName) || options[0] || null);
  const [techB, setTechB] = useState(options.find((o) => o.name !== (techA?.name)) || options[1] || null);

  if (!techA || !techB) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(8px)',
        zIndex: 1100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
      }}
    >
      <div
        className="glass-card"
        style={{
          width: '900px',
          maxWidth: '95vw',
          maxHeight: '90vh',
          overflowY: 'auto',
          backgroundColor: '#0F172A',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          borderRadius: '20px',
          padding: '28px',
          boxShadow: '0 25px 50px rgba(0, 0, 0, 0.5)',
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <ArrowRightLeft size={22} color="var(--accent-cyan)" />
              <h2 style={{ margin: 0, fontSize: '1.4rem', color: '#FFF' }}>
                Technology Comparison Matrix — <span style={{ color: 'var(--accent-cyan)' }}>{categoryName}</span>
              </h2>
            </div>
            <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Compare features, tradeoffs, difficulty, and suitability scores side-by-side.
            </p>
          </div>
          <button onClick={onClose} className="btn btn-ghost btn-sm" style={{ color: 'var(--text-muted)' }}>
            <X size={20} />
          </button>
        </div>

        {/* Dropdown Selectors */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
              Option A (Primary)
            </label>
            <select
              value={techA.name}
              onChange={(e) => setTechA(options.find((o) => o.name === e.target.value))}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '8px',
                backgroundColor: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                color: '#FFF',
                fontSize: '0.9rem',
              }}
            >
              {options.map((o) => (
                <option key={o.name} value={o.name}>{o.name} (Score: {o.suitability_score || o.score || 80})</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
              Option B (Alternative)
            </label>
            <select
              value={techB.name}
              onChange={(e) => setTechB(options.find((o) => o.name === e.target.value))}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '8px',
                backgroundColor: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                color: '#FFF',
                fontSize: '0.9rem',
              }}
            >
              {options.map((o) => (
                <option key={o.name} value={o.name}>{o.name} (Score: {o.suitability_score || o.score || 80})</option>
              ))}
            </select>
          </div>
        </div>

        {/* Side by side comparison cards */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          {[techA, techB].map((item, idx) => {
            const isSelected = item.name === selectedName;
            const score = item.suitability_score || item.score || 80;
            const advs = item.advantages || (typeof item.advantages === 'string' ? JSON.parse(item.advantages) : []);
            const disadvs = item.disadvantages || (typeof item.disadvantages === 'string' ? JSON.parse(item.disadvantages) : []);

            return (
              <div
                key={idx}
                style={{
                  padding: '20px',
                  borderRadius: '14px',
                  backgroundColor: isSelected ? 'rgba(6, 182, 212, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                  border: isSelected ? '1px solid var(--accent-cyan)' : '1px solid rgba(255, 255, 255, 0.08)',
                  display: 'flex',
                  flexDirection: 'column',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <h3 style={{ margin: 0, fontSize: '1.2rem', color: '#FFF' }}>{item.name}</h3>
                  {isSelected && <span className="badge badge-info">Currently Selected</span>}
                </div>

                {/* Score & Difficulty */}
                <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                  <div style={{ flex: 1, padding: '8px 12px', borderRadius: '8px', backgroundColor: 'rgba(255, 255, 255, 0.04)' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Suitability Score</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#38BDF8' }}>{score}/100</div>
                  </div>
                  <div style={{ flex: 1, padding: '8px 12px', borderRadius: '8px', backgroundColor: 'rgba(255, 255, 255, 0.04)' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Difficulty</div>
                    <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#C084FC', textTransform: 'capitalize' }}>{item.difficulty || 'Medium'}</div>
                  </div>
                </div>

                {/* Fit Reason */}
                <div style={{ marginBottom: '16px', fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  <strong style={{ color: '#FFF' }}>Fit Assessment:</strong> {item.fit_reason || item.description || 'Suitable for project requirements.'}
                </div>

                {/* Advantages */}
                <div style={{ marginBottom: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', fontWeight: 700, color: '#34D399', marginBottom: '6px' }}>
                    <ThumbsUp size={14} /> Advantages
                  </div>
                  <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.8rem', color: 'var(--text-main)', display: 'grid', gap: '4px' }}>
                    {Array.isArray(advs) && advs.map((ad, i) => (
                      <li key={i}>{ad}</li>
                    ))}
                  </ul>
                </div>

                {/* Disadvantages */}
                <div style={{ marginBottom: '20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', fontWeight: 700, color: '#F87171', marginBottom: '6px' }}>
                    <ThumbsDown size={14} /> Disadvantages
                  </div>
                  <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.8rem', color: 'var(--text-muted)', display: 'grid', gap: '4px' }}>
                    {Array.isArray(disadvs) && disadvs.map((dis, i) => (
                      <li key={i}>{dis}</li>
                    ))}
                  </ul>
                </div>

                {/* Select Action */}
                <button
                  onClick={() => {
                    onSelect(item.name);
                    onClose();
                  }}
                  className={`btn ${isSelected ? 'btn-secondary' : 'btn-gradient'}`}
                  style={{ marginTop: 'auto', width: '100%' }}
                >
                  {isSelected ? 'Keep Selection' : `Select ${item.name}`}
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
