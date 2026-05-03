import { Download, FileJson, FileSpreadsheet } from 'lucide-react';
import { exportJSON, exportCSV } from '../api/client';

export default function ReportExport({ experimentId }) {
    if (!experimentId) return null;

    const handleDownload = async (type) => {
        try {
            const res = type === 'json' ? await exportJSON(experimentId) : await exportCSV(experimentId);
            const blob = new Blob([res.data], { type: type === 'json' ? 'application/json' : 'text/csv' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `${experimentId}_report.${type}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        } catch (err) { console.error('Export failed:', err); }
    };

    return (
        <div className="card card-body">
            <div className="flex items-center" style={{ gap: 'var(--space-xs)' }}>
                <Download size={18} color="var(--accent)" />
                <h3 className="font-bold text-sm accent-text">Export Report</h3>
            </div>
            <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                Download the experiment results for offline analysis or submission.
            </p>
            <div className="flex flex-wrap" style={{ gap: 'var(--space-sm)' }}>
                <button className="btn-secondary" onClick={() => handleDownload('json')}>
                    <FileJson size={16} /> JSON Report
                </button>
                <button className="btn-secondary" onClick={() => handleDownload('csv')}>
                    <FileSpreadsheet size={16} /> CSV Report
                </button>
            </div>
        </div>
    );
}
