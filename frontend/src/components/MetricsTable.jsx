export default function MetricsTable({ metrics }) {
    if (!metrics || Object.keys(metrics).length === 0) {
        return (
            <div className="card text-center" style={{ padding: 'var(--space-2xl) var(--space-lg)', color: 'var(--text-muted)' }}>
                No metrics available.
            </div>
        );
    }

    const architectures = Object.keys(metrics);

    const rows = [
        { key: 'tests_passed', label: 'Tests Passed', fmt: (v, m) => `${v}/${m.tests_total}`, invert: false },
        { key: 'code_coverage', label: 'Coverage (%)', fmt: v => `${v}%`, invert: false },
        { key: 'mutation_score', label: 'Mutation Score (%)', fmt: v => `${v}%`, invert: false },
        { key: 'total_mutants', label: 'Total Mutants', fmt: v => v, invert: false },
        { key: 'killed_mutants', label: 'Killed', fmt: v => v, invert: false },
        { key: 'survived_mutants', label: 'Survived', fmt: v => v, invert: true },
        { key: 'equivalent_mutants', label: 'Equivalent', fmt: v => v, invert: true },
        { key: 'execution_time_ms', label: 'Exec Time (ms)', fmt: v => `${Math.round(v)}ms`, invert: true },
        { key: 'code_complexity', label: 'Complexity', fmt: v => v, invert: true },
    ];

    const getHighlightColor = (key, val, min, max, invert) => {
        if (min === max || val == null) return 'transparent';
        if (!invert) {
            if (val === max) return '#dcfce7'; // green-100
            if (val === min) return '#fee2e2'; // red-100
        } else {
            if (val === min) return '#dcfce7'; // green-100 for lowest time/complexity
            if (val === max) return '#fee2e2'; // red-100
        }
        return 'transparent';
    };

    const getTextColor = (key, val, min, max, invert) => {
        if (min === max || val == null) return 'var(--text-primary)';
        if (!invert) {
            if (val === max) return '#166534'; // green-800
            if (val === min) return '#991b1b'; // red-800
        } else {
            if (val === min) return '#166534';
            if (val === max) return '#991b1b';
        }
        return 'var(--text-primary)';
    };

    // Calculate min/max for highlighting
    const bounds = {};
    rows.forEach(r => {
        const vals = architectures.map(a => metrics[a][r.key]).filter(v => v != null);
        if (vals.length > 0) {
            bounds[r.key] = { min: Math.min(...vals), max: Math.max(...vals) };
        }
    });

    return (
        <div className="overflow-x-auto rounded-xl border" style={{ borderColor: 'var(--border)' }}>
            <table className="w-full text-sm" style={{ borderSpacing: 0 }}>
                <thead>
                    <tr style={{ background: 'var(--bg-muted)' }}>
                        <th className="text-left font-semibold" style={{ padding: '14px 20px', color: 'var(--text-secondary)' }}>Metric</th>
                        {architectures.map(a => (
                            <th key={a} className="text-center font-semibold capitalize" style={{ padding: '14px 20px', color: 'var(--accent)' }}>
                                {a.replace('_', ' ')}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {rows.map(({ key, label, fmt, invert }, i) => (
                        <tr key={key} style={{ borderTop: '1px solid var(--border)', background: i % 2 === 0 ? 'white' : 'var(--bg-muted)' }}>
                            <td className="font-medium" style={{ padding: '12px 20px', color: 'var(--text-secondary)' }}>{label}</td>
                            {architectures.map(a => {
                                const m = metrics[a];
                                const val = m[key];
                                const min = bounds[key]?.min;
                                const max = bounds[key]?.max;
                                const bg = getHighlightColor(key, val, min, max, invert);
                                const color = getTextColor(key, val, min, max, invert);
                                return (
                                    <td key={a} className="text-center font-semibold"
                                        style={{ padding: '12px 20px' }}>
                                        <span style={{
                                            background: bg,
                                            color: color,
                                            padding: '4px 10px',
                                            borderRadius: '6px'
                                        }}>
                                            {fmt(val, m)}
                                        </span>
                                    </td>
                                );
                            })}
                        </tr>
                    ))}
                </tbody>
            </table>
            <div className="text-xs" style={{ padding: '8px 20px', background: 'var(--bg-muted)', color: 'var(--text-muted)' }}>
                <span style={{ color: '#166534', background: '#dcfce7', padding: '2px 6px', borderRadius: 4, marginRight: 8 }}>Green</span> = Best in category &middot;
                <span style={{ color: '#991b1b', background: '#fee2e2', padding: '2px 6px', borderRadius: 4, margin: '0 8px' }}>Red</span> = Worst in category
            </div>
        </div>
    );
}
