"""Upload router — handles ZIP uploads and lists sample projects."""
import os, json, shutil, zipfile, tempfile, uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path

router = APIRouter()

SAMPLE_DIR = Path(__file__).parent.parent / "sample_projects"
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@router.get("/sample-projects")
def list_sample_projects():
    """List available sample projects."""
    projects = []
    if SAMPLE_DIR.exists():
        for d in sorted(SAMPLE_DIR.iterdir()):
            cfg = d / "project.json"
            if cfg.exists():
                with open(cfg) as f:
                    info = json.load(f)
                info["id"] = d.name
                info["source"] = "sample"
                info["architectures"] = ["layered", "mvc", "hexagonal", "microservices", "event_driven"]
                projects.append(info)
    return {"projects": projects}


@router.post("/upload-project")
async def upload_project(file: UploadFile = File(...)):
    """Upload a ZIP of a project folder. Returns upload_id."""
    if not file.filename.endswith('.zip'):
        raise HTTPException(400, "Only .zip files accepted")

    upload_id = str(uuid.uuid4())[:8]
    dest = UPLOAD_DIR / upload_id
    dest.mkdir(parents=True, exist_ok=True)

    # Save and extract
    zip_path = dest / file.filename
    contents = await file.read()
    with open(zip_path, 'wb') as f:
        f.write(contents)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(dest)
    except zipfile.BadZipFile:
        shutil.rmtree(dest, ignore_errors=True)
        raise HTTPException(400, "Invalid ZIP file")

    # Find project root (look for project.json or test files)
    project_root = _find_project_root(dest)
    if not project_root:
        shutil.rmtree(dest, ignore_errors=True)
        raise HTTPException(400, "No valid project found in ZIP. Need architecture .py files + a test file.")

    # Detect architectures
    archs = []
    for name in ["layered", "mvc", "hexagonal", "microservices", "event_driven"]:
        if (project_root / f"{name}.py").exists():
            archs.append(name)

    # Detect test file
    test_file = None
    for f in project_root.iterdir():
        if f.name.startswith("test_") and f.name.endswith(".py"):
            test_file = f.name
            break

    # Read project.json if exists
    info = {"name": "Uploaded Project", "description": "Custom uploaded project"}
    cfg = project_root / "project.json"
    if cfg.exists():
        with open(cfg) as f:
            info = json.load(f)

    return {
        "upload_id": upload_id,
        "project_root": str(project_root),
        "name": info.get("name", "Uploaded Project"),
        "description": info.get("description", ""),
        "architectures": archs,
        "test_file": test_file,
    }


@router.get("/upload/{upload_id}")
def get_upload_info(upload_id: str):
    """Get info about an uploaded project."""
    dest = UPLOAD_DIR / upload_id
    if not dest.exists():
        raise HTTPException(404, "Upload not found")

    project_root = _find_project_root(dest)
    archs = [n for n in ["layered", "mvc", "hexagonal", "microservices", "event_driven"]
             if (project_root / f"{n}.py").exists()]
    test_file = None
    for f in project_root.iterdir():
        if f.name.startswith("test_") and f.name.endswith(".py"):
            test_file = f.name; break

    info = {"name": "Uploaded Project"}
    cfg = project_root / "project.json"
    if cfg.exists():
        with open(cfg) as f: info = json.load(f)

    return {"upload_id": upload_id, "project_root": str(project_root),
            "name": info.get("name"), "architectures": archs, "test_file": test_file}


def _find_project_root(base: Path) -> Path:
    """Find the directory containing architecture .py files."""
    # Check base itself
    if any((base / f"{n}.py").exists() for n in ["layered", "mvc"]):
        return base
    # Check one level down (ZIP might have a wrapper folder)
    for child in base.iterdir():
        if child.is_dir() and any((child / f"{n}.py").exists() for n in ["layered", "mvc"]):
            return child
        # Two levels
        if child.is_dir():
            for grandchild in child.iterdir():
                if grandchild.is_dir() and any((grandchild / f"{n}.py").exists() for n in ["layered", "mvc"]):
                    return grandchild
    return base
