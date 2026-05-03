import { Link } from 'react-router-dom';
import { FlaskConical, Layers, BarChart3, Brain, Zap, GitBranch, ArrowRight } from 'lucide-react';

const features = [
    { icon: Layers, title: '5 Architectural Patterns', desc: 'Layered, MVC, Hexagonal, Microservices, and Event-Driven implementations of identical business logic.', color: '#4f46e5' },
    { icon: FlaskConical, title: 'Mutation Testing', desc: 'Automated mutation analysis with killed, survived, and equivalent mutant tracking per architecture.', color: '#059669' },
    { icon: BarChart3, title: 'Comprehensive Metrics', desc: 'Code coverage, test pass rates, mutation scores, execution time, and cyclomatic complexity.', color: '#d97706' },
    { icon: Brain, title: 'ML-Based Analysis', desc: 'RandomForest + GradientBoosting ensemble predicts architecture effectiveness and generates rankings.', color: '#7c3aed' },
    { icon: GitBranch, title: 'Multi-Project Support', desc: 'Compare architectures across Order Processing, Student Result, and Library Management systems.', color: '#ec4899' },
    { icon: Zap, title: 'Exportable Reports', desc: 'Download results as JSON or CSV for further analysis, academic submission, or presentations.', color: '#0891b2' },
];

export default function HomePage() {
    return (
        <div className="page-container section-stack">
            {/* Hero */}
            <section className="text-center" style={{ paddingTop: 'var(--space-xl)', paddingBottom: 'var(--space-md)' }}>
                <div className="inline-flex items-center rounded-full font-semibold"
                    style={{
                        gap: 'var(--space-xs)',
                        padding: '8px 18px',
                        marginBottom: 'var(--space-lg)',
                        fontSize: 13,
                        background: 'var(--accent-bg)',
                        color: 'var(--accent)',
                        border: '1px solid var(--accent-border)',
                    }}>
                    <FlaskConical size={14} />
                    Software Engineering Research Project
                </div>
                <h1 className="font-extrabold leading-tight"
                    style={{ fontSize: 'clamp(28px, 4vw, 42px)', color: 'var(--text-primary)', marginBottom: 'var(--space-md)' }}>
                    ML-Based Mutation Testing<br />Effectiveness Analysis
                </h1>
                <p style={{ fontSize: 16, maxWidth: 560, margin: '0 auto', color: 'var(--text-secondary)', marginBottom: 'var(--space-lg)' }}>
                    Compare how different software architectural patterns affect mutation testing effectiveness across multiple business case projects.
                </p>
                <div className="flex items-center justify-center" style={{ gap: 'var(--space-sm)' }}>
                    <Link to="/experiment" className="btn-primary no-underline"><FlaskConical size={16} /> Run Experiment</Link>
                    <Link to="/results" className="btn-secondary no-underline">View Results</Link>
                </div>
            </section>

            {/* Pipeline */}
            <section className="card" style={{ padding: 'var(--space-lg) var(--space-xl)' }}>
                <h2 className="text-sm font-bold accent-text text-center" style={{ marginBottom: 'var(--space-md)' }}>Experiment Pipeline</h2>
                <div className="flex flex-wrap items-center justify-center" style={{ gap: 'var(--space-sm)' }}>
                    {['Select Project', 'Select Architectures', 'Build & Test', 'Code Coverage', 'Mutation Testing', 'ML Analysis', 'Report'].map((step, i) => (
                        <div key={step} className="flex items-center" style={{ gap: 'var(--space-sm)' }}>
                            <span className="font-medium"
                                style={{
                                    padding: '6px 14px',
                                    borderRadius: 8,
                                    fontSize: 13,
                                    background: 'var(--bg-muted)',
                                    border: '1px solid var(--border)',
                                    color: 'var(--text-primary)',
                                }}>
                                {step}
                            </span>
                            {i < 6 && <ArrowRight size={14} color="var(--text-muted)" />}
                        </div>
                    ))}
                </div>
            </section>

            {/* Features */}
            <section>
                <h2 className="font-bold text-center" style={{ fontSize: 20, color: 'var(--text-primary)', marginBottom: 'var(--space-lg)' }}>Key Features</h2>
                <div className="card-grid-3">
                    {features.map(({ icon: Icon, title, desc, color }) => (
                        <div key={title} className="card card-body">
                            <div className="flex items-center justify-center rounded-lg"
                                style={{ width: 44, height: 44, background: `${color}10` }}>
                                <Icon size={22} color={color} />
                            </div>
                            <h3 className="font-bold" style={{ fontSize: 14 }}>{title}</h3>
                            <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Tech stack */}
            <section className="card text-center">
                <h2 className="text-sm font-bold accent-text" style={{ marginBottom: 'var(--space-md)' }}>Technology Stack</h2>
                <div className="flex flex-wrap items-center justify-center" style={{ gap: 'var(--space-xs)' }}>
                    {['React', 'Tailwind CSS', 'Recharts', 'Axios', 'Python', 'FastAPI', 'PyTest', 'Scikit-learn', 'Pandas', 'Coverage.py'].map(t => (
                        <span key={t} className="font-medium"
                            style={{
                                padding: '6px 14px',
                                borderRadius: 8,
                                fontSize: 12,
                                background: 'var(--bg-muted)',
                                border: '1px solid var(--border)',
                                color: 'var(--accent)',
                            }}>{t}</span>
                    ))}
                </div>
            </section>
        </div>
    );
}
