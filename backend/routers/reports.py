"""Report export router — JSON/CSV download."""
import json, csv, io
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from services.experiment_runner import get_latest_results, _results_store

router = APIRouter()


@router.get("/export-report/{experiment_id}/json")
def export_json(experiment_id: str):
    if experiment_id not in _results_store:
        raise HTTPException(status_code=404, detail="Experiment not found")
    exp = _results_store[experiment_id]
    # Remove mutant_details for cleaner export
    clean = {**exp, "metrics": {
        a: {k: v for k, v in m.items() if k != "mutant_details"}
        for a, m in exp.get("metrics", {}).items()
    }}
    content = json.dumps(clean, indent=2, default=str)
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={experiment_id}_report.json"},
    )


@router.get("/export-report/{experiment_id}/csv")
def export_csv(experiment_id: str):
    if experiment_id not in _results_store:
        raise HTTPException(status_code=404, detail="Experiment not found")
    exp = _results_store[experiment_id]
    metrics = exp.get("metrics", {})
    rows = []
    for arch, m in metrics.items():
        row = {"architecture": arch}
        row.update({k: v for k, v in m.items() if k != "mutant_details"})
        rows.append(row)
    if not rows:
        raise HTTPException(status_code=400, detail="No metrics to export")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={experiment_id}_report.csv"},
    )
