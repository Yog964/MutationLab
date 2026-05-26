# 🧬 MutationLab: AI-Powered Architectural Testability Analyzer
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/e394b201-2d46-441a-ba8e-49fe1890d988" />

An advanced, academic-grade experimental platform that compares how different software architectural patterns (MVC, Layered, Hexagonal, etc.) affect **Mutation Testing Effectiveness**. The system dynamically executes real AST-based mutation testing across multiple projects and uses Machine Learning to score, rank, and recommend the best architecture for testability, speed, and maintainability.

![MutationLab Banner](https://img.shields.io/badge/Status-Active-brightgreen) ![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB) ![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688) ![Python](https://img.shields.io/badge/ML-Scikit--Learn-F7931E)

---

## ✨ Key Features & Capabilities

### 🧪 1. Real AST-Based Mutation Testing Engine
The backend doesn't just simulate results—it dynamically parses Python source code, mutates operators (`+` to `-`, `>` to `<`, `True` to `False`), and executes `pytest` in isolated subprocesses to determine if your test suites can catch the artificial bugs (Killed vs. Survived Mutants).

### 🧠 2. Dynamic Machine Learning Recommendations
Instead of flat metrics, the platform uses an **Ensemble ML Model** (`RandomForestClassifier` + `GradientBoostingRegressor`) to rank architectures. 
- **Interactive Weighting:** Users can dynamically prioritize *Speed*, *Test Quality*, or *Maintainability* via the frontend to instantly recalculate recommendations.
- **Academic Insights:** The ML engine generates detailed text explaining *Why Recommended*, *Why Not Recommended*, and highlighting the inherent *Strengths & Weaknesses* of the chosen patterns.

### 📊 3. Multi-Dimensional Visualizations
The React dashboard features cutting-edge charts via `Recharts`:
- **Performance Heatmap:** A visual matrix highlighting absolute best (Green) and worst (Red) metrics across architectures.
- **Mutant Breakdown:** Stacked bar charts separating Killed, Survived, and **Equivalent** mutants.
- **Execution Trend Lines & Radar Charts** for multi-dimensional profile comparison.

### 📂 4. Bring Your Own Code (Custom Uploads)
Beyond the built-in and sample projects, users can upload their own `.zip` files containing multi-architecture Python code and a `test_*.py` file. The engine will parse the upload and run the full ML analysis pipeline against the custom code.

---

## 🏗️ Architectures Compared

| # | Architecture | Pattern Description | Testability Profile |
|---|---|---|---|
| 1 | **Layered** | Presentation → Business Logic → Data Access | Easy to unit test, but highly coupled. |
| 2 | **MVC** | Model-View-Controller separation | Good UI separation; Controllers often become bloated. |
| 3 | **Hexagonal** | Ports & Adapters (domain isolation) | Extremely highly testable; Mocking adapters is trivial. |
| 4 | **Microservices** | Independent services + API Gateway | Excellent unit testability; Difficult integration testing. |
| 5 | **Event-Driven** | In-memory event bus, publish/subscribe | Great for async testing; Weak against sequential state bugs. |

---

## � Research-Grade Metrics Collected

The pipeline executes and extracts the following data points for ML scoring:
- **Mutation Score (%)**: The absolute percentage of bugs caught.
- **Code Coverage (%)**: Standard line coverage (highlighting the **Cov-Mut Gap**).
- **Execution Time (ms)**: Total pipeline execution speed.
- **Code Complexity**: Cyclomatic complexity estimate.
- **Maintainability Index**: Based on Lines of Code (LOC) and complexity.
- **Mutation Efficiency**: Mutants killed per second.
- **Equivalent Mutant Rate**: Statistical isolation of syntactically mutated but logically identical code.

---

## 🛠️ Technology Stack

### Frontend
- **React 18** (via Vite)
- **Tailwind CSS v4** (Custom Light Theme & CSS Variables)
- **Recharts** (Complex Radar, Heatmap, Bar, and Line charts)
- **Lucide React** (Modern iconography)
- **Axios** & **React Router**

### Backend
- **Python 3.10+** (FastAPI REST API + Uvicorn)
- **PyTest** & **Coverage.py** (Subprocess test execution)
- **Scikit-learn** & **Numpy** (Ensemble ML Models)

---

## 🚀 Setup Instructions

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.10+

### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python main.py
```
> **Backend:** `http://localhost:8000` | **API Docs:** `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
> **Frontend Dashboard:** `http://localhost:5173`

---

## 🔌 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/run-experiment` | Triggers the mutation engine `{ project_type, architectures }` |
| POST | `/api/upload-project` | Upload custom `.zip` for analysis |
| GET | `/api/results/{exp_id}` | Get completed metrics matrix |
| POST | `/api/ml-analysis` | Get ML predictions with dynamic `{ weights }` |
| GET | `/api/export-report/{id}/csv` | Download CSV Research Report |

---

## 🤖 ML Model Architecture & Scoring Logistics

The `ml_service.py` heavily relies on an ensemble of **Scikit-Learn** ML tools and heuristic formulas to score, rank, and classify software architectures.

### 1. Base ML Predictions (`scikit-learn`)
- **Scaling:** `StandardScaler` standardizes the 6-dimensional input vectors.
- **Classification:** `RandomForestClassifier` (100 estimators) determines the **Categorical Tier** (`High`, `Medium`, `Low`). ML Confidence correlates directly to voting tree percentage (e.g. 92/100 trees vote High = 92% Confidence).
- **Regression:** `GradientBoostingRegressor` predicts baseline expected mutation scores on a 1-100 scale based on historical data.

### 2. Dimension Scoring Formulas
The raw pipeline metrics are grouped into three primary "Dimensions" scored dynamically out of 100:

| Dimension | Calculation Logic Formula | Target Insight |
|-----------|---------------------------|----------------|
| **Test Quality** | `(Mutation Score × 0.70) + (Code Coverage × 0.30)` | Weights Mutation success heavily over blind Line Coverage. |
| **Speed** | `100 - (Execution Time ms / 30)` | Faster execution scores higher. Loses 1 point every 30ms. |
| **Maintainability** | `(Maintainability Index × 0.80) + (100 - (Complexity × 5)) × 0.20` | Penalizes high Cyclomatic Complexity and bloated code sizes. |

### 3. Dynamic Composite Score
This dictates the final "Winning" architecture. The UI priority buttons modify the scoring Weights iteratively, recalculating the ranks without needing a heavy re-test.

| Priority Toggle | Final Dynamic Equation |
|-----------------|------------------------|
| ⚖️ **Balanced** | `(Quality × 0.5) + (Maintainability × 0.3) + (Speed × 0.2)` |
| ⚡ **Speed** | `(Speed × 0.7) + (Quality × 0.2) + (Maintainability × 0.1)` |
| 🛡️ **Test Quality** | `(Quality × 0.8) + (Maintainability × 0.1) + (Speed × 0.1)` |
| 🏗️ **Maintainability**| `(Maintainability × 0.7) + (Quality × 0.2) + (Speed × 0.1)` |

---

## 👥 Authors
Software Engineering Course Project — VIT, 2026. Designed for academic research regarding Architectural Technical Debt and Testability.

## 📄 License
Academic use only. Not for commercial distribution.
