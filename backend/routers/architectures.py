"""Architectures router — lists projects and architectures."""
from fastapi import APIRouter
from config import ARCHITECTURES, PROJECT_TYPES

router = APIRouter()


@router.get("/projects")
def get_projects():
    """List built-in business case projects."""
    projects = []
    for key, info in PROJECT_TYPES.items():
        projects.append({
            "id": key,
            "display_name": info["display_name"],
            "description": info.get("description", ""),
            "icon": info.get("icon", "ShoppingCart"),
            "source": "builtin",
        })
    return {"projects": projects}


@router.get("/architectures")
def get_architectures():
    """List all 5 architecture patterns."""
    return {"architectures": ARCHITECTURES}
