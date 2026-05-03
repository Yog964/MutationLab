import React from 'react';

// Generates a color between red (worst) and green (best) based on min/max
const getColor = (val, min, max, invert = false) => {
    if (max === min) return '#e2e8f0';
    let ratio = (val - min) / (max - min);
    if (invert) ratio = 1 - ratio; // e.g., lower execution time is better

    // Interpolate between red (0) and green (1)
    // Red: hsl(0, 70%, 50%), Green: hsl(120, 70%, 45%)
    const hue = ratio * 120;
    return `hsl(${hue}, 70%, 45%)`;
};

export default function HeatmapChart({ metrics }) {
    const architectures = Object.keys(metrics);
    if (architectures.length === 0) return null;

    // Define metrics to display in the heatmap
    const rows = [
        { key: 'mutation_score', label: 'Mutation Score (%)', invert: false },
        { key: 'code_coverage', label: 'Coverage (%)', invert: false },
        { key: 'execution_time_ms', label: 'Execution Time (ms)', invert: true },
        { key: 'code_complexity', label: 'Complexity', invert: true },
    ];

    // Calculate min/max for each row
    const rowStats = rows.map(r => {
        const vals = architectures.map(a => metrics[a][r.key] || 0);
        return { ...r, min: Math.min(...vals), max: Math.max(...vals) };
    });

    return (
        <div className="card" style={{ padding: 'var(--space-xl)', overflowX: 'auto' }}>
            <div style={{ marginBottom: 'var(--space-md)' }}>
                <h3 className="font-bold text-lg" style={{ color: 'var(--text-primary)' }}>Architecture Performance Heatmap</h3>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Green indicates the best performance in the category, red indicates the worst.</p>
            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center' }}>
                <thead>
                    <tr>
                        <th style={{ padding: '12px', textAlign: 'left', color: 'var(--text-muted)', fontSize: 13, borderBottom: '2px solid var(--border)' }}>Metric</th>
                        {architectures.map(a => (
                            <th key={a} className="capitalize" style={{ padding: '12px', color: 'var(--text-primary)', fontSize: 13, borderBottom: '2px solid var(--border)' }}>
                                {a.replace('_', ' ')}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {rowStats.map(row => (
                        <tr key={row.key} style={{ borderBottom: '1px solid var(--border-light)' }}>
                            <td style={{ padding: '12px', textAlign: 'left', fontWeight: '500', fontSize: 13, color: 'var(--text-secondary)' }}>
                                {row.label}
                            </td>
                            {architectures.map(a => {
                                const val = metrics[a][row.key] || 0;
                                const bgColor = getColor(val, row.min, row.max, row.invert);
                                return (
                                    <td key={a} style={{ padding: '8px' }}>
                                        <div style={{
                                            background: bgColor,
                                            color: 'white',
                                            padding: '8px',
                                            borderRadius: '6px',
                                            fontSize: 13,
                                            fontWeight: 'bold',
                                            textShadow: '0 1px 2px rgba(0,0,0,0.2)'
                                        }}>
                                            {val.toLocaleString()}
                                        </div>
                                    </td>
                                );
                            })}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
