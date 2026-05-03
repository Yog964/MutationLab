import { Link, useLocation } from 'react-router-dom';
import { FlaskConical } from 'lucide-react';

const navLinks = [
    { path: '/', label: 'Home' },
    { path: '/experiment', label: 'Experiment' },
    { path: '/results', label: 'Results' },
    { path: '/analysis', label: 'ML Analysis' },
];

export default function Navbar() {
    const location = useLocation();

    return (
        <nav className="sticky top-0 z-50 bg-white border-b" style={{ borderColor: 'var(--border)' }}>
            <div className="page-container" style={{ padding: '0 var(--space-xl)' }}>
                <div className="flex items-center justify-between" style={{ height: 60 }}>
                    <Link to="/" className="flex items-center no-underline" style={{ gap: 'var(--space-sm)' }}>
                        <div className="flex items-center justify-center rounded-lg" style={{ width: 36, height: 36, background: 'var(--accent)' }}>
                            <FlaskConical size={18} color="white" />
                        </div>
                        <span className="text-base font-bold hidden sm:inline" style={{ color: 'var(--accent)' }}>
                            MutationLab
                        </span>
                    </Link>

                    <div className="flex items-center" style={{ gap: 4 }}>
                        {navLinks.map(({ path, label }) => {
                            const active = location.pathname === path;
                            return (
                                <Link key={path} to={path}
                                    className="rounded-lg text-sm font-medium no-underline transition-colors"
                                    style={{
                                        padding: '8px 16px',
                                        color: active ? 'var(--accent)' : 'var(--text-secondary)',
                                        background: active ? 'var(--accent-bg)' : 'transparent',
                                    }}>
                                    {label}
                                </Link>
                            );
                        })}
                    </div>
                </div>
            </div>
        </nav>
    );
}
