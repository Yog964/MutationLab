import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    PieChart, Pie, Cell, LineChart, Line
} from 'recharts';

const COLORS = ['#4f46e5', '#7c3aed', '#059669', '#d97706', '#ec4899'];

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload) return null;
    return (
        <div className="bg-white border shadow-lg"
            style={{ padding: '12px 16px', borderRadius: 10, borderColor: 'var(--border)' }}>
            <p className="font-semibold" style={{ color: 'var(--text-primary)', fontSize: 13, marginBottom: 6 }}>{label}</p>
            {payload.map((e, i) => (
                <p key={i} style={{ color: e.color || e.fill, fontSize: 12, lineHeight: 1.7 }}>
                    {e.name}: <span className="font-bold">{e.value}</span>
                </p>
            ))}
        </div>
    );
};

export default function ComparisonChart({ metrics }) {
    if (!metrics || Object.keys(metrics).length === 0) return null;

    const archs = Object.keys(metrics);

    // 1. Performance Overview (Metrics)
    const barData = archs.map(a => ({
        name: a.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()),
        'Mutation Score (%)': metrics[a].mutation_score,
        'Coverage (%)': metrics[a].code_coverage,
        'Pass Rate (%)': metrics[a].test_pass_rate,
    }));

    // 2. Multi-Dimensional (Radar)
    const radarData = [
        { metric: 'Mutation Score', ...Object.fromEntries(archs.map(a => [a, metrics[a].mutation_score])) },
        { metric: 'Coverage', ...Object.fromEntries(archs.map(a => [a, metrics[a].code_coverage])) },
        { metric: 'Pass Rate', ...Object.fromEntries(archs.map(a => [a, metrics[a].test_pass_rate || 100])) },
        { metric: 'Kill Rate', ...Object.fromEntries(archs.map(a => [a, Math.round((metrics[a].killed_mutants / Math.max(metrics[a].total_mutants, 1)) * 100)])) },
        { metric: '100-Complexity', ...Object.fromEntries(archs.map(a => [a, Math.max(0, 100 - metrics[a].code_complexity)])) },
    ];

    // 3. Mutants Breakdown per architecture (Stacked Bar)
    const mutantBarData = archs.map(a => ({
        name: a.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()),
        'Killed': metrics[a].killed_mutants,
        'Survived': metrics[a].survived_mutants,
        'Equivalent': metrics[a].equivalent_mutants,
    }));

    // 4. Execution Time (Area/Line Chart)
    const execTimeData = archs.map(a => ({
        name: a.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()),
        'Time (ms)': metrics[a].execution_time_ms,
    }));


    return (
        <div className="section-stack">
            {/* Performance Bar Chart & Mutant Stacked Bar */}
            <div className="card-grid-2">
                <div className="card" style={{ padding: 'var(--space-lg)' }}>
                    <h3 className="text-base font-bold" style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-md)' }}>Quality Metrics</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={barData} barGap={4} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                            <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} dy={10} />
                            <YAxis tick={{ fill: '#64748b', fontSize: 11 }} domain={[0, 100]} axisLine={false} tickLine={false} />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend wrapperStyle={{ fontSize: 12, paddingTop: 16 }} />
                            <Bar dataKey="Mutation Score (%)" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="Coverage (%)" fill="#059669" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="Pass Rate (%)" fill="#7c3aed" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                <div className="card" style={{ padding: 'var(--space-lg)' }}>
                    <h3 className="text-base font-bold" style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-md)' }}>Mutant Breakdown</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={mutantBarData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                            <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} dy={10} />
                            <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend wrapperStyle={{ fontSize: 12, paddingTop: 16 }} />
                            <Bar dataKey="Killed" stackId="a" fill="#16a34a" />
                            <Bar dataKey="Equivalent" stackId="a" fill="#f59e0b" />
                            <Bar dataKey="Survived" stackId="a" fill="#dc2626" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Radar + Execution Time Line */}
            <div className="card-grid-2">
                <div className="card" style={{ padding: 'var(--space-lg)' }}>
                    <h3 className="text-base font-bold" style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-md)' }}>Multi-Dimensional Profile</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <RadarChart data={radarData} margin={{ top: 10, right: 30, left: 30, bottom: 10 }}>
                            <PolarGrid stroke="#e2e8f0" />
                            <PolarAngleAxis dataKey="metric" tick={{ fill: '#64748b', fontSize: 10 }} />
                            <PolarRadiusAxis tick={{ fill: '#94a3b8', fontSize: 9 }} domain={[0, 100]} />
                            {archs.map((a, i) => (
                                <Radar key={a} name={a.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())} dataKey={a}
                                    stroke={COLORS[i % COLORS.length]} fill={COLORS[i % COLORS.length]}
                                    fillOpacity={0.15} strokeWidth={2} />
                            ))}
                            <Legend wrapperStyle={{ fontSize: 11, paddingTop: 12 }} />
                            <Tooltip content={<CustomTooltip />} />
                        </RadarChart>
                    </ResponsiveContainer>
                </div>

                <div className="card" style={{ padding: 'var(--space-lg)' }}>
                    <h3 className="text-base font-bold" style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-md)' }}>Execution Time Comparison</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={execTimeData} margin={{ top: 20, right: 20, left: -10, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                            <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} dy={10} />
                            <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                            <Tooltip content={<CustomTooltip />} />
                            <Line type="monotone" dataKey="Time (ms)" stroke="#ea580c" strokeWidth={3} dot={{ r: 6, fill: '#ea580c', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 8 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}
