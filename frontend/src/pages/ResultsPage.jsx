import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { BarChart3, Table2, LayoutGrid } from 'lucide-react';
import MetricsTable from '../components/MetricsTable';
import ComparisonChart from '../components/ComparisonChart';
import ReportExport from '../components/ReportExport';
import HeatmapChart from '../components/HeatmapChart';
import { getResults } from '../api/client';

const PROJECT_LABELS = {
    order_processing: 'Order Processing System',
    student_result: 'Student Result System',
    library_management: 'Library Management System',
};

export default function ResultsPage() {
    const [searchParams] = useSearchParams();
    const project = searchParams.get('project');
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(true);
    const [tab, setTab] = useState('heatmap'); // 'heatmap', 'charts', 'table'

    useEffect(() => { loadResults(); }, [project]);

    const loadResults = async () => {
        try { const res = await getResults(project); setResults(res.data); }
        catch { /* no results */ }
        finally { setLoading(false); }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center" style={{ paddingTop: 120, paddingBottom: 120 }}>
                <div className="border-2 border-t-transparent rounded-full animate-spin"
                    style={{ width: 32, height: 32, borderColor: 'var(--accent)', borderTopColor: 'transparent' }} />
            </div>
        );
    }

    if (!results || !results.metrics || Object.keys(results.metrics).length === 0) {
        return (
            <div className="text-center" style={{ paddingTop: 120, paddingBottom: 120 }}>
                <BarChart3 size={48} color="var(--border-dark)" style={{ margin: '0 auto 16px' }} />
                <h2 className="font-bold" style={{ fontSize: 20, marginBottom: 8 }}>No Results Yet</h2>
                <p className="text-sm" style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-lg)' }}>Run an experiment first to see results.</p>
                <Link to="/experiment" className="btn-primary no-underline">Go to Experiment</Link>
            </div>
        );
    }

    const projectType = results.project_type || 'uploaded_project';
    const metrics = results.metrics;
    const archCount = Object.keys(metrics).length;
    const avgMutation = (Object.values(metrics).reduce((s, m) => s + m.mutation_score, 0) / archCount).toFixed(1);
    const avgCoverage = (Object.values(metrics).reduce((s, m) => s + m.code_coverage, 0) / archCount).toFixed(1);
    const totalMutants = Object.values(metrics).reduce((s, m) => s + m.total_mutants, 0);

    return (
        <div className="page-container section-stack">
            {/* Header */}
            <div className="flex items-center justify-between flex-wrap" style={{ gap: 'var(--space-lg)' }}>
                <div>
                    <h1 className="font-extrabold" style={{ fontSize: 26, marginBottom: 'var(--space-xs)' }}>Experiment Results</h1>
                    <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        <span className="font-semibold" style={{ color: 'var(--accent)' }}>{PROJECT_LABELS[projectType] || projectType.replace(/_/g, ' ').toUpperCase()}</span>
                        {' '}&middot; {results.experiment_id} &middot; {new Date(results.timestamp).toLocaleString()}
                    </p>
                </div>
                <div className="flex overflow-hidden rounded-lg border bg-white" style={{ borderColor: 'var(--border)' }}>
                    {[{ id: 'heatmap', Icon: LayoutGrid }, { id: 'charts', Icon: BarChart3 }, { id: 'table', Icon: Table2 }].map(({ id, Icon }) => (
                        <button key={id} className="flex items-center font-medium capitalize"
                            style={{
                                padding: '8px 16px', gap: 6, fontSize: 13,
                                background: tab === id ? 'var(--accent)' : 'transparent',
                                color: tab === id ? 'white' : 'var(--text-secondary)',
                            }}
                            onClick={() => setTab(id)}>
                            <Icon size={14} /> {id}
                        </button>
                    ))}
                </div>
            </div>

            {/* Quick stats generated from real metrics */}
            <div className="card-grid-4">
                {[
                    { label: 'Architectures', value: archCount, color: '#4f46e5' },
                    { label: 'Avg Mutation Score', value: `${avgMutation}%`, color: '#059669' },
                    { label: 'Avg Coverage', value: `${avgCoverage}%`, color: '#7c3aed' },
                    { label: 'Total Mutants Evaluated', value: totalMutants, color: '#d97706' },
                ].map(s => (
                    <div key={s.label} className="card text-center" style={{ padding: 'var(--space-lg)' }}>
                        <p className="font-extrabold" style={{ fontSize: 24, color: s.color, marginBottom: 4 }}>{s.value}</p>
                        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{s.label}</p>
                    </div>
                ))}
            </div>

            {/* Tab Selection Content */}
            {tab === 'heatmap' && <HeatmapChart metrics={metrics} />}
            {tab === 'charts' && <ComparisonChart metrics={metrics} />}
            {tab === 'table' && <MetricsTable metrics={metrics} />}

            {/* Export */}
            <ReportExport experimentId={results.experiment_id} />
        </div>
    );
}
