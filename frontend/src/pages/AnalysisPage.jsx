import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Brain, Info, Sliders } from 'lucide-react';
import MLRecommendation from '../components/MLRecommendation';
import { getMLAnalysis, getModelInfo } from '../api/client';

const PROJECT_LABELS = {
    order_processing: 'Order Processing System',
    student_result: 'Student Result System',
    library_management: 'Library Management System',
};

export default function AnalysisPage() {
    const [searchParams] = useSearchParams();
    const project = searchParams.get('project');
    const [analysis, setAnalysis] = useState(null);
    const [modelInfo, setModelInfo] = useState(null);
    const [loading, setLoading] = useState(true);

    // Initial Weights
    const [weights, setWeights] = useState({
        speed: 0.2,
        quality: 0.5,
        maintainability: 0.3
    });

    useEffect(() => { load(); }, [project]);

    const load = async (customWeights = weights) => {
        setLoading(true);
        try {
            const [a, m] = await Promise.all([
                getMLAnalysis(project, customWeights).catch(() => null),
                getModelInfo().catch(() => null),
            ]);
            if (a) setAnalysis(a.data);
            if (m) setModelInfo(m.data);
        } catch { }
        finally { setLoading(false); }
    };

    const handlePriorityChange = (priority) => {
        let newWeights;
        if (priority === 'speed') newWeights = { speed: 0.7, quality: 0.2, maintainability: 0.1 };
        else if (priority === 'quality') newWeights = { speed: 0.1, quality: 0.8, maintainability: 0.1 };
        else if (priority === 'maintainability') newWeights = { speed: 0.1, quality: 0.2, maintainability: 0.7 };
        else newWeights = { speed: 0.2, quality: 0.5, maintainability: 0.3 }; // balanced

        setWeights(newWeights);
        load(newWeights);
    };

    if (loading && !analysis) {
        return (
            <div className="flex items-center justify-center" style={{ paddingTop: 120, paddingBottom: 120 }}>
                <div className="border-2 border-t-transparent rounded-full animate-spin"
                    style={{ width: 32, height: 32, borderColor: 'var(--accent)', borderTopColor: 'transparent' }} />
            </div>
        );
    }

    if (!analysis) {
        return (
            <div className="text-center" style={{ paddingTop: 120, paddingBottom: 120 }}>
                <Brain size={48} color="var(--border-dark)" style={{ margin: '0 auto 16px' }} />
                <h2 className="font-bold" style={{ fontSize: 20, marginBottom: 8 }}>No Analysis Available</h2>
                <p className="text-sm" style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-lg)' }}>Run an experiment first.</p>
                <Link to="/experiment" className="btn-primary no-underline">Go to Experiment</Link>
            </div>
        );
    }

    const projectType = analysis.project_type || project || 'order_processing';

    return (
        <div className="page-container section-stack">
            {/* Header */}
            <div>
                <h1 className="font-extrabold" style={{ fontSize: 26, marginBottom: 'var(--space-xs)' }}>Academic ML Analysis</h1>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                    <span className="font-semibold" style={{ color: 'var(--accent)' }}>{PROJECT_LABELS[projectType] || projectType.replace('_', ' ').toUpperCase()}</span>
                    {' '}&middot; Dynamic architecture recommendations based on weighted scoring.
                </p>
            </div>

            {/* Selection Toggles */}
            <div className="card card-body flex flex-col md:flex-row items-start md:items-center justify-between" style={{ gap: 16 }}>
                <div className="flex items-center" style={{ gap: 'var(--space-xs)' }}>
                    <Sliders size={20} color="var(--accent)" />
                    <div>
                        <h3 className="font-bold text-sm">Prioritize Attributes</h3>
                        <p className="text-xs text-gray-500">Select what matters most for your final score ranking.</p>
                    </div>
                </div>

                <div className="flex flex-wrap gap-2">
                    <button onClick={() => handlePriorityChange('balanced')}
                        style={{
                            padding: '8px 16px', borderRadius: 6, fontSize: 13, fontWeight: 600, border: '1px solid',
                            transition: 'all 0.2s', cursor: 'pointer',
                            background: (weights.speed === 0.2 && weights.quality === 0.5) ? 'var(--accent)' : 'white',
                            color: (weights.speed === 0.2 && weights.quality === 0.5) ? 'white' : 'var(--text-secondary)',
                            borderColor: (weights.speed === 0.2 && weights.quality === 0.5) ? 'var(--accent)' : 'var(--border)'
                        }}>
                        Balanced
                    </button>
                    <button onClick={() => handlePriorityChange('speed')}
                        style={{
                            padding: '8px 16px', borderRadius: 6, fontSize: 13, fontWeight: 600, border: '1px solid',
                            transition: 'all 0.2s', cursor: 'pointer',
                            background: weights.speed === 0.7 ? '#ea580c' : 'white',
                            color: weights.speed === 0.7 ? 'white' : 'var(--text-secondary)',
                            borderColor: weights.speed === 0.7 ? '#ea580c' : 'var(--border)'
                        }}>
                        Speed (Execution Time)
                    </button>
                    <button onClick={() => handlePriorityChange('quality')}
                        style={{
                            padding: '8px 16px', borderRadius: 6, fontSize: 13, fontWeight: 600, border: '1px solid',
                            transition: 'all 0.2s', cursor: 'pointer',
                            background: weights.quality === 0.8 ? 'var(--success)' : 'white',
                            color: weights.quality === 0.8 ? 'white' : 'var(--text-secondary)',
                            borderColor: weights.quality === 0.8 ? 'var(--success)' : 'var(--border)'
                        }}>
                        Test Quality (Mutation Score)
                    </button>
                    <button onClick={() => handlePriorityChange('maintainability')}
                        style={{
                            padding: '8px 16px', borderRadius: 6, fontSize: 13, fontWeight: 600, border: '1px solid',
                            transition: 'all 0.2s', cursor: 'pointer',
                            background: weights.maintainability === 0.7 ? '#9333ea' : 'white',
                            color: weights.maintainability === 0.7 ? 'white' : 'var(--text-secondary)',
                            borderColor: weights.maintainability === 0.7 ? '#9333ea' : 'var(--border)'
                        }}>
                        Maintainability (Complexity)
                    </button>
                </div>
            </div>

            {loading && analysis && (
                <div className="text-center text-sm font-semibold text-indigo-600" style={{ padding: '20px 0' }}>
                    Recalculating weights...
                </div>
            )}

            {/* ML Recommendations */}
            {!loading && <MLRecommendation analysis={analysis} />}

        </div>
    );
}
