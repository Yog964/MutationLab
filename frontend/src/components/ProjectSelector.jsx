import { ShoppingCart, GraduationCap, BookOpen, Calculator, Package, CheckSquare } from 'lucide-react';

const ICON_MAP = {
    ShoppingCart, GraduationCap, BookOpen, Calculator, Package, CheckSquare,
    order_processing: ShoppingCart, student_result: GraduationCap, library_management: BookOpen,
    calculator: Calculator, inventory: Package, todo_app: CheckSquare,
};

const COLOR_MAP = {
    order_processing: '#4f46e5', student_result: '#059669', library_management: '#d97706',
    calculator: '#7c3aed', inventory: '#0891b2', todo_app: '#ec4899',
};

export default function ProjectSelector({ projects, selected, onSelect }) {
    if (!projects || projects.length === 0) {
        return <p className="text-xs" style={{ color: 'var(--text-muted)' }}>No projects available.</p>;
    }

    return (
        <div className="card-grid-3">
            {projects.map((p) => {
                const isActive = selected === p.id;
                const Icon = ICON_MAP[p.icon] || ICON_MAP[p.id] || Package;
                const color = COLOR_MAP[p.id] || '#4f46e5';

                return (
                    <button key={p.id} onClick={() => onSelect(p.id)}
                        className="text-left rounded-xl border-2 transition-all duration-200"
                        style={{
                            padding: 'var(--space-lg)',
                            background: isActive ? `${color}08` : 'white',
                            borderColor: isActive ? color : 'var(--border)',
                            boxShadow: isActive ? `0 0 0 1px ${color}40` : 'var(--shadow-sm)',
                        }}>
                        <div className="flex items-start" style={{ gap: 'var(--space-md)' }}>
                            <div className="flex items-center justify-center rounded-lg shrink-0"
                                style={{ width: 44, height: 44, background: `${color}12` }}>
                                <Icon size={22} color={color} />
                            </div>
                            <div>
                                <h3 className="font-semibold text-sm" style={{ color: isActive ? color : 'var(--text-primary)', marginBottom: 6 }}>
                                    {p.display_name || p.name}
                                </h3>
                                <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                                    {p.description}
                                </p>
                                {p.source === 'sample' && (
                                    <span className="inline-block text-xs font-medium rounded mt-1"
                                        style={{ padding: '2px 8px', background: `${color}15`, color }}>Sample</span>
                                )}
                            </div>
                        </div>
                    </button>
                );
            })}
        </div>
    );
}
