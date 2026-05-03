import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

export default function ExperimentStatus({ status, progress, experimentId, currentArch }) {
    if (!status || status === 'idle') return null;

    const configs = {
        running: { icon: Loader2, color: 'var(--accent)', bg: 'var(--accent-bg)', label: 'Running real mutation testing…' },
        completed: { icon: CheckCircle2, color: 'var(--success)', bg: 'var(--success-bg)', label: 'Experiment completed!' },
        error: { icon: AlertCircle, color: 'var(--danger)', bg: 'var(--danger-bg)', label: 'Experiment failed' },
    };
    const c = configs[status] || configs.running;
    const Icon = c.icon;

    return (
        <div className="card" style={{ background: c.bg, borderColor: `${c.color}30`, padding: 'var(--space-lg)' }}>
            <div className="flex items-center" style={{ gap: 'var(--space-md)' }}>
                <div className={status === 'running' ? 'animate-spin' : ''}><Icon size={22} color={c.color} /></div>
                <div className="flex-1">
                    <div className="flex items-center justify-between" style={{ marginBottom: status === 'running' ? 10 : 0 }}>
                        <div>
                            <span className="font-semibold text-sm" style={{ color: c.color }}>{c.label}</span>
                            {status === 'running' && currentArch && (
                                <span className="text-xs" style={{ color: 'var(--text-secondary)', marginLeft: 8 }}>
                                    Testing: <strong className="capitalize">{currentArch.replace('_', ' ')}</strong>
                                </span>
                            )}
                        </div>
                        {experimentId && <span className="text-xs" style={{ color: 'var(--text-muted)' }}>ID: {experimentId}</span>}
                    </div>
                    {status === 'running' && (
                        <div className="w-full rounded-full overflow-hidden" style={{ height: 6, background: '#e2e8f0' }}>
                            <div className="rounded-full transition-all duration-500"
                                style={{ height: '100%', width: `${progress}%`, background: c.color }} />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
