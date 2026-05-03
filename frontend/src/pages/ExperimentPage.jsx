import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, RotateCcw, Upload, FolderOpen, Package } from 'lucide-react';
import ProjectSelector from '../components/ProjectSelector';
import ArchitectureSelector from '../components/ArchitectureSelector';
import ExperimentStatus from '../components/ExperimentStatus';
import {
    getProjects, getArchitectures, getSampleProjects,
    runExperiment, getExperimentStatus, uploadProject,
} from '../api/client';

const FALLBACK_ARCHS = [
    { id: 'layered', display_name: 'Layered Architecture', description: 'Horizontal layers separation' },
    { id: 'mvc', display_name: 'MVC Architecture', description: 'Model-View-Controller pattern' },
    { id: 'hexagonal', display_name: 'Hexagonal Architecture', description: 'Ports & Adapters pattern' },
    { id: 'microservices', display_name: 'Microservices Architecture', description: 'Independent services' },
    { id: 'event_driven', display_name: 'Event-Driven Architecture', description: 'Publish/subscribe messaging' },
];

export default function ExperimentPage() {
    const navigate = useNavigate();
    const [mode, setMode] = useState('sample'); // 'sample', 'upload'
    const [builtinProjects, setBuiltinProjects] = useState([]);
    const [sampleProjects, setSampleProjects] = useState([]);
    const [archs, setArchs] = useState(FALLBACK_ARCHS);
    const [selectedProject, setSelectedProject] = useState('');
    const [selectedArchs, setSelectedArchs] = useState([]);
    const [status, setStatus] = useState('idle');
    const [progress, setProgress] = useState(0);
    const [currentArch, setCurrentArch] = useState('');
    const [expId, setExpId] = useState(null);
    const [error, setError] = useState(null);

    // Upload state
    const [uploadId, setUploadId] = useState(null);
    const [uploadInfo, setUploadInfo] = useState(null);
    const [uploading, setUploading] = useState(false);
    const fileRef = useRef(null);

    useEffect(() => {
        (async () => {
            try {
                const [pRes, aRes, sRes] = await Promise.all([
                    getProjects(), getArchitectures(), getSampleProjects().catch(() => ({ data: { projects: [] } })),
                ]);
                if (pRes.data?.projects) { setBuiltinProjects(pRes.data.projects); setSelectedProject(pRes.data.projects[0]?.id || ''); }
                if (aRes.data?.architectures) setArchs(aRes.data.architectures);
                if (sRes.data?.projects) setSampleProjects(sRes.data.projects);
            } catch { /* fallback */ }
        })();
    }, []);

    const toggleArch = (id) => setSelectedArchs(p => p.includes(id) ? p.filter(a => a !== id) : [...p, id]);

    const handleUpload = async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        setUploading(true); setError(null);
        try {
            const res = await uploadProject(file);
            setUploadId(res.data.upload_id);
            setUploadInfo(res.data);
            setSelectedProject(res.data.upload_id);
            setSelectedArchs(res.data.architectures || []);
        } catch (err) {
            setError(err.response?.data?.detail || 'Upload failed');
        }
        setUploading(false);
    };

    const handleRun = async () => {
        if (selectedArchs.length < 2) { setError('Select at least 2 architectures for comparison'); return; }
        setStatus('running'); setProgress(0); setError(null); setCurrentArch('');

        try {
            const source = mode === 'upload' ? 'uploaded' : mode;
            const projId = mode === 'upload' ? (uploadInfo?.name || 'uploaded') : selectedProject;
            const res = await runExperiment(projId, selectedArchs, source, uploadId);
            const id = res.data.id;
            setExpId(id);

            // Poll for completion
            const poll = async () => {
                try {
                    const s = await getExperimentStatus(id);
                    setProgress(s.data.progress || 0);
                    setCurrentArch(s.data.current_arch || '');
                    if (s.data.status === 'completed') {
                        setStatus('completed'); setProgress(100);
                        setTimeout(() => navigate(`/results?project=${projId}`), 800);
                    } else if (s.data.status === 'error') {
                        setStatus('error'); setError(s.data.error || 'Experiment failed');
                    } else {
                        setTimeout(poll, 1500);
                    }
                } catch (e) {
                    if (e.response?.status === 404) {
                        setStatus('error'); setError('Experiment lost (server may have restarted)');
                    } else {
                        setTimeout(poll, 2000);
                    }
                }
            };
            setTimeout(poll, 1000);
        } catch (e) {
            setStatus('error'); setError(e.response?.data?.detail || 'Experiment failed');
        }
    };

    const handleReset = () => {
        setStatus('idle'); setProgress(0); setExpId(null); setError(null); setCurrentArch('');
    };

    const activeProjects = mode === 'builtin' ? builtinProjects : sampleProjects;

    return (
        <div className="page-container section-stack">
            {/* Header */}
            <div>
                <h1 className="font-extrabold" style={{ fontSize: 26, marginBottom: 'var(--space-xs)' }}>Run Experiment</h1>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                    Select a project source, pick at least 2 architectures, then run <strong>real mutation testing</strong>.
                </p>
            </div>

            {/* Mode tabs */}
            <div className="card" style={{ padding: 'var(--space-md)' }}>
                <div className="flex flex-wrap" style={{ gap: 'var(--space-xs)' }}>
                    {[
                        { id: 'sample', label: 'Sample Projects', icon: FolderOpen },
                        { id: 'upload', label: 'Upload Custom', icon: Upload },
                    ].map(({ id, label, icon: Icon }) => (
                        <button key={id} className="flex items-center rounded-lg font-medium"
                            style={{
                                padding: '10px 20px', gap: 8, fontSize: 13,
                                background: mode === id ? 'var(--accent)' : 'white',
                                color: mode === id ? 'white' : 'var(--text-secondary)',
                                border: `1px solid ${mode === id ? 'var(--accent)' : 'var(--border)'}`,
                            }}
                            onClick={() => { setMode(id); setSelectedArchs([]); setError(null); }}>
                            <Icon size={15} /> {label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Step 1: Project selection */}
            <div className="card card-body">
                <div className="flex items-center" style={{ gap: 'var(--space-sm)' }}>
                    <span className="flex items-center justify-center rounded-full font-bold"
                        style={{ width: 28, height: 28, fontSize: 12, background: 'var(--accent)', color: 'white' }}>1</span>
                    <h2 className="font-bold" style={{ fontSize: 15 }}>
                        {mode === 'upload' ? 'Upload Project (ZIP)' : 'Select Project'}
                    </h2>
                </div>

                {mode === 'upload' ? (
                    <div>
                        <div className="rounded-xl border-2 border-dashed text-center cursor-pointer"
                            style={{ padding: 'var(--space-xl)', borderColor: uploadInfo ? 'var(--success)' : 'var(--border)' }}
                            onClick={() => fileRef.current?.click()}>
                            <Upload size={28} color={uploadInfo ? 'var(--success)' : 'var(--text-muted)'} style={{ margin: '0 auto 12px' }} />
                            {uploading ? (
                                <p className="text-sm font-medium" style={{ color: 'var(--accent)' }}>Uploading…</p>
                            ) : uploadInfo ? (
                                <>
                                    <p className="text-sm font-semibold" style={{ color: 'var(--success)' }}>{uploadInfo.name}</p>
                                    <p className="text-xs" style={{ color: 'var(--text-muted)', marginTop: 4 }}>
                                        {uploadInfo.architectures?.length || 0} architectures detected · {uploadInfo.test_file}
                                    </p>
                                </>
                            ) : (
                                <>
                                    <p className="text-sm font-medium">Click to upload a ZIP file</p>
                                    <p className="text-xs" style={{ color: 'var(--text-muted)', marginTop: 4 }}>
                                        ZIP should contain architecture .py files + test file
                                    </p>
                                </>
                            )}
                            <input ref={fileRef} type="file" accept=".zip" className="hidden" onChange={handleUpload} style={{ display: 'none' }} />
                        </div>
                    </div>
                ) : (
                    <ProjectSelector projects={activeProjects} selected={selectedProject} onSelect={setSelectedProject} />
                )}
            </div>

            {/* Step 2: Architectures */}
            <div className="card card-body">
                <div className="flex items-center justify-between">
                    <div className="flex items-center" style={{ gap: 'var(--space-sm)' }}>
                        <span className="flex items-center justify-center rounded-full font-bold"
                            style={{ width: 28, height: 28, fontSize: 12, background: 'var(--accent)', color: 'white' }}>2</span>
                        <h2 className="font-bold" style={{ fontSize: 15 }}>Select Architectures <span className="font-normal text-xs" style={{ color: 'var(--text-muted)' }}>(min 2)</span></h2>
                    </div>
                    <div className="flex" style={{ gap: 'var(--space-xs)' }}>
                        <button className="font-medium border rounded-lg"
                            style={{ fontSize: 12, padding: '5px 12px', borderColor: 'var(--border)', color: 'var(--accent)', background: 'white' }}
                            onClick={() => setSelectedArchs(archs.map(a => a.id))}>All</button>
                        <button className="font-medium border rounded-lg"
                            style={{ fontSize: 12, padding: '5px 12px', borderColor: 'var(--border)', color: 'var(--text-muted)', background: 'white' }}
                            onClick={() => setSelectedArchs([])}>Clear</button>
                    </div>
                </div>
                <ArchitectureSelector architectures={archs} selected={selectedArchs} onToggle={toggleArch} />
                <p className="text-xs" style={{ color: selectedArchs.length < 2 ? 'var(--danger)' : 'var(--text-muted)' }}>
                    {selectedArchs.length} of {archs.length} selected {selectedArchs.length < 2 && '— need at least 2'}
                </p>
            </div>

            {/* Status */}
            {status !== 'idle' && (
                <ExperimentStatus status={status} progress={progress} experimentId={expId} currentArch={currentArch} />
            )}
            {error && (
                <div className="card" style={{ background: 'var(--danger-bg)', borderColor: '#fecaca', padding: 'var(--space-md) var(--space-lg)' }}>
                    <p className="text-sm" style={{ color: 'var(--danger)' }}>{error}</p>
                </div>
            )}

            {/* Actions */}
            <div className="flex items-center" style={{ gap: 'var(--space-sm)' }}>
                <button className="btn-primary" onClick={handleRun}
                    disabled={selectedArchs.length < 2 || status === 'running' || (mode === 'upload' && !uploadInfo)}>
                    <Play size={16} /> {status === 'running' ? 'Running…' : 'Run Mutation Testing'}
                </button>
                {status !== 'idle' && (
                    <button className="btn-secondary" onClick={handleReset}><RotateCcw size={14} /> Reset</button>
                )}
            </div>

            {/* Info box */}
            <div className="card" style={{ background: 'var(--accent-bg)', borderColor: 'var(--accent-border)', padding: 'var(--space-md) var(--space-lg)' }}>
                <p className="text-xs" style={{ color: 'var(--accent)' }}>
                    <strong>⚡ Real Mutation Testing:</strong> The engine modifies your source code (arithmetic, comparison, boolean operators),
                    runs tests against each mutant, and records which mutations are caught (killed) vs missed (survived).
                    This may take 30s–2min depending on code size.
                </p>
            </div>
        </div>
    );
}
