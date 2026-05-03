"""Results router — returns experiment results."""
from fastapi import APIRouter
from typing import Optional
from services.experiment_runner import get_latest_results, get_experiment, get_experiment_history, _results_store

router = APIRouter()


@router.get("/results")
def get_results(project_type: Optional[str] = None):
    """Get the latest experiment results, optionally filtered by project."""
    result = get_latest_results(project_type)
    if not result:
        return {"message": "No results available", "metrics": {}}
    # Remove mutant_details from response (too large)
    metrics = {}
    for arch, m in result.get("metrics", {}).items():
        clean = {k: v for k, v in m.items() if k != "mutant_details"}
        metrics[arch] = clean
    return {**result, "metrics": metrics}


@router.get("/results/history")
def get_history(project_type: Optional[str] = None):
    """Get the history of experiments for trend visualization."""
    history = get_experiment_history(project_type)
    cleaned_history = []
    for exp in history:
        clean_exp = {**exp, "metrics": {}}
        for arch, m in exp.get("metrics", {}).items():
            clean_exp["metrics"][arch] = {k: v for k, v in m.items() if k != "mutant_details"}
        cleaned_history.append(clean_exp)
    return {"history": cleaned_history}


@router.get("/results/{exp_id}")
def get_experiment_results(exp_id: str):
    """Get results for a specific experiment."""
    if exp_id in _results_store:
        result = _results_store[exp_id]
        metrics = {}
        for arch, m in result.get("metrics", {}).items():
            clean = {k: v for k, v in m.items() if k != "mutant_details"}
            metrics[arch] = clean
        return {**result, "metrics": metrics}
    return {"message": "Results not found"}


@router.get("/results/{exp_id}/mutants/{arch}")
def get_mutant_details(exp_id: str, arch: str):
    """Get detailed mutant info for a specific architecture in an experiment."""
    if exp_id in _results_store:
        result = _results_store[exp_id]
        m = result.get("metrics", {}).get(arch, {})
        return {
            "architecture": arch,
            "total": m.get("total_mutants", 0),
            "killed": m.get("killed_mutants", 0),
            "survived": m.get("survived_mutants", 0),
            "details": m.get("mutant_details", []),
        }
    return {"message": "Not found", "details": []}
