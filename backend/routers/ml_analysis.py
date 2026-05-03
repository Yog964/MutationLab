"""ML Analysis router — ML-based effectiveness analysis."""
from fastapi import APIRouter, HTTPException, Query, Body
from services.ml_service import MLAnalysisService
from services.experiment_runner import get_latest_results, get_experiment

router = APIRouter()
ml_service = MLAnalysisService()


@router.post("/ml-analysis")
def get_ml_analysis(project_type: str = Query(None), weights: dict = Body(None)):
    result = get_latest_results(project_type)
    if result is None:
        raise HTTPException(status_code=404, detail="No experiment results. Run an experiment first.")
    metrics = result.get("metrics", {})
    metrics_list = []
    for arch, m in metrics.items():
        row = dict(m)
        row["architecture"] = arch
        metrics_list.append(row)
    
    # We use a POST request to submit user-defined weights
    # weights = {"speed": 0.2, "quality": 0.5, "maintainability": 0.3}
    return ml_service.analyze(metrics_list, weights=weights)


@router.get("/ml-analysis/model/info")
def model_info():
    cv_scores = ml_service.get_cross_val_scores()
    training_count = len(ml_service._TRAINING_DATA)
    # Include accumulated data count
    from services.experiment_runner import TRAINING_FILE
    accumulated = 0
    try:
        import json
        if TRAINING_FILE.exists():
            with open(TRAINING_FILE) as f:
                accumulated = len(json.load(f))
    except Exception:
        pass
    return {
        "model_type": "RandomForest Classifier + GradientBoosting Regressor",
        "features": ["mutation_score", "execution_time", "code_coverage",
                      "complexity", "equivalent_rate", "architecture_type"],
        "training_samples": training_count + accumulated,
        "cross_validation": cv_scores,
    }
