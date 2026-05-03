"""Experiments router — start experiments and poll status."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.experiment_runner import start_experiment, get_experiment, list_experiments

router = APIRouter()


class ExperimentRequest(BaseModel):
    project_type: str
    architectures: List[str]
    source: str = "builtin"  # "builtin", "sample", "uploaded"
    upload_id: Optional[str] = None


@router.post("/run-experiment")
def run_experiment(req: ExperimentRequest):
    if len(req.architectures) < 2:
        raise HTTPException(400, "Select at least 2 architectures for comparison")

    exp_id = start_experiment(
        project_type=req.project_type,
        architectures=req.architectures,
        source=req.source,
        upload_id=req.upload_id,
    )
    return {"id": exp_id, "status": "running"}


@router.get("/experiments")
def get_experiments():
    return {"experiments": list_experiments()}


@router.get("/experiments/{exp_id}")
def get_experiment_status(exp_id: str):
    exp = get_experiment(exp_id)
    if not exp:
        raise HTTPException(404, "Experiment not found")
    return exp
