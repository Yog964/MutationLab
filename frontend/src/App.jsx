import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ExperimentPage from './pages/ExperimentPage';
import ResultsPage from './pages/ResultsPage';
import AnalysisPage from './pages/AnalysisPage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/experiment" element={<ExperimentPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/analysis" element={<AnalysisPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
