"""FastAPI entry point — ML-Based Mutation Testing Analysis Platform v3.0 (Dynamic)."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import architectures, experiments, results, ml_analysis, reports, upload

app = FastAPI(
    title="ML-Based Mutation Testing Analysis",
    description="Real-time mutation testing comparison across architectures with ML analysis.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(architectures.router, prefix="/api", tags=["Projects & Architectures"])
app.include_router(experiments.router, prefix="/api", tags=["Experiments"])
app.include_router(results.router, prefix="/api", tags=["Results"])
app.include_router(ml_analysis.router, prefix="/api", tags=["ML Analysis"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])
app.include_router(upload.router, prefix="/api", tags=["Upload & Samples"])


@app.get("/")
def root():
    return {"message": "ML-Based Mutation Testing Analysis API v3.0 — Dynamic"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
