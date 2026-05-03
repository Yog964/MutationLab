import axios from 'axios';

const API = axios.create({ baseURL: '/api' });

// Projects & Architectures
export const getProjects = () => API.get('/projects');
export const getArchitectures = () => API.get('/architectures');
export const getSampleProjects = () => API.get('/sample-projects');

// Upload
export const uploadProject = (file) => {
    const form = new FormData();
    form.append('file', file);
    return API.post('/upload-project', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
};

// Experiments
export const runExperiment = (projectType, architectures, source = 'builtin', uploadId = null) =>
    API.post('/run-experiment', {
        project_type: projectType,
        architectures: architectures,
        source: source,
        upload_id: uploadId,
    });

export const getExperimentStatus = (expId) => API.get(`/experiments/${expId}`);
export const getExperiments = () => API.get('/experiments');

// Results
export const getResults = (projectType) =>
    API.get('/results', { params: projectType ? { project_type: projectType } : {} });
export const getExperimentResults = (expId) => API.get(`/results/${expId}`);
export const getMutantDetails = (expId, arch) => API.get(`/results/${expId}/mutants/${arch}`);
export const getResultsHistory = (projectType) =>
    API.get('/results/history', { params: projectType ? { project_type: projectType } : {} });

// ML Analysis (Updated to POST for dynamic weights)
export const getMLAnalysis = (projectType, weights = null) =>
    API.post('/ml-analysis', weights || {}, { params: projectType ? { project_type: projectType } : {} });
export const getModelInfo = () => API.get('/ml-analysis/model/info');

// Export
export const exportJSON = (id) => API.get(`/export-report/${id}/json`, { responseType: 'blob' });
export const exportCSV = (id) => API.get(`/export-report/${id}/csv`, { responseType: 'blob' });
