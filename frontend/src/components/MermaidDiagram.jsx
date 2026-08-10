import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    darkMode: true,
    background: 'transparent',
    primaryColor: '#0F172A',
    primaryTextColor: '#F8FAFC',
    primaryBorderColor: '#06B6D4',
    lineColor: '#38BDF8',
    secondaryColor: '#1E1B4B',
    tertiaryColor: '#090D16',
    edgeLabelBackground: '#0F172A',
    clusterBkg: 'rgba(15, 23, 42, 0.7)',
    clusterBorder: 'rgba(56, 189, 248, 0.3)',
    nodeBorder: '#06B6D4',
    fontFamily: 'Inter, system-ui, sans-serif',
    fontSize: '14px',
  },
  flowchart: {
    htmlLabels: true,
    curve: 'basis',
    padding: 15,
    nodeSpacing: 50,
    rankSpacing: 50,
  },
  securityLevel: 'loose',
});

export default function MermaidDiagram({ chart }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (chart && containerRef.current) {
      const id = `mermaid-${Math.random().toString(36).substring(2, 9)}`;
      try {
        mermaid
          .render(id, chart)
          .then(({ svg }) => {
            if (containerRef.current) {
              containerRef.current.innerHTML = svg;
              // Make SVG responsive
              const svgEl = containerRef.current.querySelector('svg');
              if (svgEl) {
                svgEl.style.width = '100%';
                svgEl.style.height = 'auto';
                svgEl.style.maxHeight = '600px';
              }
            }
          })
          .catch((err) => {
            console.error('Mermaid render error:', err);
            if (containerRef.current) {
              containerRef.current.innerHTML = `<pre style="font-size:0.8rem; color:var(--text-muted); padding:16px;">${chart}</pre>`;
            }
          });
      } catch (e) {
        if (containerRef.current) {
          containerRef.current.innerHTML = `<pre style="font-size:0.8rem; color:var(--text-muted); padding:16px;">${chart}</pre>`;
        }
      }
    }
  }, [chart]);

  return (
    <div
      ref={containerRef}
      className="mermaid-diagram-container"
      style={{
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        overflowX: 'auto',
        padding: '20px 10px',
        background: 'rgba(9, 13, 22, 0.85)',
        borderRadius: '14px',
        border: '1px solid var(--border-medium)',
      }}
    />
  );
}
