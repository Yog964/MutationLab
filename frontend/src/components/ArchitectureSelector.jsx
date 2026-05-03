import { Layers, Grid3X3, Hexagon, Network, Zap } from 'lucide-react';

const ARCH_ICONS = { layered: Layers, mvc: Grid3X3, hexagonal: Hexagon, microservices: Network, event_driven: Zap };
const ARCH_COLORS = { layered: '#4f46e5', mvc: '#7c3aed', hexagonal: '#059669', microservices: '#d97706', event_driven: '#ec4899' };

export default function ArchitectureSelector({ architectures, selected, onToggle }) {
    return (
        <div className="card-grid-3">
            {architectures.map((arch) => {
                const isSelected = selected.includes(arch.id);
                const Icon = ARCH_ICONS[arch.id] || Layers;
                const color = ARCH_COLORS[arch.id] || '#4f46e5';

                return (
                    <button key={arch.id} onClick={() => onToggle(arch.id)}
                        className="text-left rounded-xl border transition-all duration-200"
                        style={{
                            padding: 'var(--space-md) var(--space-lg)',
                            background: isSelected ? `${color}06` : 'white',
                            borderColor: isSelected ? color : 'var(--border)',
                        }}>
                        <div className="flex items-start" style={{ gap: 'var(--space-md)' }}>
                            <div className="flex items-center justify-center rounded-lg shrink-0"
                                style={{ width: 40, height: 40, background: `${color}10` }}>
                                <Icon size={18} color={color} />
                            </div>
                            <div className="flex-1 min-w-0">
                                <h3 className="font-semibold text-sm" style={{ color: isSelected ? color : 'var(--text-primary)' }}>
                                    {arch.display_name}
                                </h3>
                                <p className="text-xs" style={{ color: 'var(--text-muted)', marginTop: 4 }}>{arch.description}</p>
                            </div>
                            <div className="flex items-center justify-center shrink-0 rounded border-2"
                                style={{
                                    width: 22, height: 22, marginTop: 2,
                                    borderColor: isSelected ? color : 'var(--border-dark)',
                                    background: isSelected ? color : 'transparent',
                                }}>
                                {isSelected && <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 6L5 9L10 3" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>}
                            </div>
                        </div>
                    </button>
                );
            })}
        </div>
    );
}
