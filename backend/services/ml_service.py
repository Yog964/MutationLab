"""
ML Analysis Service — calculates dynamic weighted scores and generates detailed reasoning.
"""
import math
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import cross_val_score

# Predefined strengths and weaknesses for architectures
ARCH_KNOWLEDGE = {
    "layered": {
        "strengths": ["Simple to understand and implement", "Clear separation of concerns for basic apps"],
        "weaknesses": ["Prone to 'sinkhole' antipattern", "Rigid testing requirements across layers"]
    },
    "mvc": {
        "strengths": ["Excellent separation of UI and business logic", "Highly standardized and predictable tests"],
        "weaknesses": ["View and Controller can become tightly coupled", "Fat controllers are harder to unit test"]
    },
    "hexagonal": {
        "strengths": ["Highly testable business logic (isolated from IO)", "Easy to mock adapters for fast tests"],
        "weaknesses": ["Steep learning curve", "High boilerplate code (Ports/Adapters overhead)"]
    },
    "microservices": {
        "strengths": ["Highly scalable and independent deployments", "Fault isolation across boundaries"],
        "weaknesses": ["Extremely slow integration testing", "Equivalent mutants hard to detect over network boundaries"]
    },
    "event_driven": {
        "strengths": ["Perfectly decoupled components", "Highly resilient to failure states"],
        "weaknesses": ["Event tracing makes debugging surviving mutants very difficult", "Requires complex test harnesses"]
    }
}


class MLAnalysisService:
    _TRAINING_DATA = [
        ("layered", 78, 1200, 92.5, 12, 4.5, "high"),
        ("layered", 80, 1100, 91.0, 13, 5.0, "high"),
        ("mvc", 75, 1500, 89.3, 14, 5.2, "medium"),
        ("mvc", 77, 1350, 90.5, 13, 4.8, "high"),
        ("hexagonal", 82, 2000, 95.1, 18, 3.0, "high"),
        ("hexagonal", 88, 1800, 97.0, 18, 2.0, "high"),
        ("microservices", 70, 3500, 84.7, 22, 7.5, "low"),
        ("microservices", 73, 3200, 86.0, 21, 6.5, "medium"),
        ("event_driven", 73, 2800, 87.2, 20, 6.0, "medium"),
        ("event_driven", 78, 2400, 90.0, 18, 4.5, "high"),
    ]

    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
        self.regressor = GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=4)
        self._is_trained = False
        self._train()

    def _train(self):
        df = pd.DataFrame(self._TRAINING_DATA, columns=[
            "architecture", "mutation_score", "execution_time",
            "code_coverage", "complexity", "equivalent_rate", "effectiveness",
        ])
        df["arch_encoded"] = self.label_encoder.fit_transform(df["architecture"])
        feature_cols = ["mutation_score", "execution_time", "code_coverage",
                        "complexity", "equivalent_rate", "arch_encoded"]
        X = df[feature_cols].values
        self.classifier.fit(self.scaler.fit_transform(X), df["effectiveness"].values)
        self.regressor.fit(self.scaler.transform(X), df["mutation_score"].values)
        self._is_trained = True

    def analyze(self, metrics_list: list[dict], weights: dict = None) -> dict:
        if not metrics_list:
            return {"error": "No metrics provided"}

        # Dynamic weights (speed, quality, maintainability)
        if not weights:
            weights = {"speed": 0.2, "quality": 0.5, "maintainability": 0.3}

        project_type = metrics_list[0].get("project_type", "unknown")

        results = []
        for m in metrics_list:
            results.append(self._predict_single(m, weights))

        # Rank based on the new composite score
        results.sort(key=lambda x: x["composite_score"], reverse=True)
        for idx, r in enumerate(results):
            r["rank"] = idx + 1

        best_arch = results[0]["architecture"] if results else None
        worst_arch = results[-1]["architecture"] if results else None

        recommendations = self._generate_recommendation_details(results, best_arch, worst_arch)

        feature_names = ["mutation_score", "execution_time", "code_coverage", "complexity", "equivalent_rate", "architecture_type"]
        importances = self.classifier.feature_importances_.tolist()
        feature_importance = {n: round(v, 4) for n, v in zip(feature_names, importances)}

        return {
            "project_type": project_type,
            "rankings": results,
            "best_architecture": best_arch,
            "weights_used": weights,
            "recommendation_details": recommendations,
            "feature_importance": feature_importance,
            "model_type": "RandomForest + GradientBoosting ensemble",
            "training_samples": len(self._TRAINING_DATA),
        }

    def _predict_single(self, metrics: dict, weights: dict) -> dict:
        arch = metrics.get("architecture", "layered")
        try:
            arch_encoded = self.label_encoder.transform([arch])[0]
        except ValueError:
            arch_encoded = 0

        # Extract metrics
        mut_score = metrics.get("mutation_score", 75)
        exec_time = metrics.get("execution_time_ms", 2000)
        cov = metrics.get("code_coverage", 85)
        comp = metrics.get("code_complexity", 15)
        equiv_rate = (metrics.get("equivalent_mutants", 5) / max(metrics.get("total_mutants", 100), 1) * 100)
        maintainability = metrics.get("maintainability_index", 75.0)

        # ML Features
        features = np.array([[mut_score, exec_time, cov, comp, equiv_rate, arch_encoded]])
        features_scaled = self.scaler.transform(features)
        effectiveness = self.classifier.predict(features_scaled)[0]
        confidence = round(float(max(self.classifier.predict_proba(features_scaled)[0])) * 100, 2)
        predicted_score = round(float(self.regressor.predict(features_scaled)[0]), 2)

        # Dimension Scores (0-100)
        # Quality: heavily weights mutation score
        quality_score = mut_score * 0.7 + cov * 0.3
        
        # Speed: faster is better (baseline ~3000ms is score 0)
        speed_score = max(0, 100 - (exec_time / 30))
        
        # Maintainability: uses maintainability index and complexity
        maint_score = (maintainability * 0.8) + max(0, 100 - (comp * 5)) * 0.2

        # Final Composite Score based on user weights
        composite = (
            quality_score * weights.get("quality", 0.5) +
            speed_score * weights.get("speed", 0.2) +
            maint_score * weights.get("maintainability", 0.3)
        )

        return {
            "architecture": arch,
            "effectiveness": effectiveness,
            "confidence": confidence,
            "predicted_mutation_score": predicted_score,
            "quality_score": round(quality_score, 1),
            "speed_score": round(speed_score, 1),
            "maintainability_score": round(maint_score, 1),
            "composite_score": round(composite, 1),
            "equivalent_mutant_rate": round(equiv_rate, 1),
            "strengths": ARCH_KNOWLEDGE.get(arch, {}).get("strengths", []),
            "weaknesses": ARCH_KNOWLEDGE.get(arch, {}).get("weaknesses", []),
            "raw_metrics": metrics # keep for UI rendering
        }

    def _generate_recommendation_details(self, rankings: list[dict], best_arch: str, worst_arch: str) -> dict:
        if not rankings:
            return {}

        best = rankings[0]
        worst = rankings[-1]

        # Generate "Why Recommended" reasons dynamically for the best
        why_recommended = []
        if best["quality_score"] > 85:
            why_recommended.append(f"Achieved exceptional Test Quality score ({best['quality_score']}/100) indicating strong test coverage and high mutant detection.")
        if best["speed_score"] > 80:
            why_recommended.append(f"Very fast execution time ({best['raw_metrics'].get('execution_time_ms', 0)}ms) creates a tight feedback loop for developers.")
        if best["maintainability_score"] > 80:
            why_recommended.append(f"High maintainability score ({best['maintainability_score']}/100) meaning the test suite will be easy to update as code changes.")
        why_recommended.append(f"Overall composite score perfectly balanced for the chosen priorities.")

        # Generate "Why Not" for the worst
        why_not_recommended = []
        if worst["quality_score"] < 75:
            why_not_recommended.append(f"Poor Test Quality ({worst['quality_score']}/100) — too many mutants survived the test suite.")
        if worst["speed_score"] < 50:
            why_not_recommended.append(f"Unacceptably slow execution time ({worst['raw_metrics'].get('execution_time_ms', 0)}ms) which slows down CI/CD pipelines.")
        if worst["maintainability_score"] < 60:
            why_not_recommended.append(f"Low maintainability ({worst['maintainability_score']}/100) meaning testing requires high overhead and coupling.")
        if worst["raw_metrics"].get("equivalent_mutants", 0) > 10:
             why_not_recommended.append(f"High number of equivalent mutants suggests testing complexity is yielding false positives.")

        return {
            "best_arch": best_arch,
            "why_recommended": why_recommended,
            "worst_arch": worst_arch,
            "why_not_recommended": why_not_recommended
        }

    def get_cross_val_scores(self) -> dict:
        df = pd.DataFrame(self._TRAINING_DATA, columns=[
            "architecture", "mutation_score", "execution_time",
            "code_coverage", "complexity", "equivalent_rate", "effectiveness",
        ])
        df["arch_encoded"] = self.label_encoder.transform(df["architecture"])
        feature_cols = ["mutation_score", "execution_time", "code_coverage",
                        "complexity", "equivalent_rate", "arch_encoded"]
        X = self.scaler.transform(df[feature_cols].values)
        y = df["effectiveness"].values
        scores = cross_val_score(self.classifier, X, y, cv=3, scoring="accuracy")
        return {
            "mean_accuracy": round(float(scores.mean()), 4),
            "std_accuracy": round(float(scores.std()), 4),
            "fold_scores": [round(float(s), 4) for s in scores],
        }
