"""
Domain registry — maps project/business cases to their architecture modules.
Used by the experiment runner to load the correct controller for each combo.
"""

# Project / Business Case metadata
PROJECTS = {
    "order_processing": {
        "display_name": "Order Processing System",
        "description": "Order lifecycle management with items, tax/discount calculation, payment processing, and status tracking.",
        "icon": "ShoppingCart",
    },
    "student_result": {
        "display_name": "Student Result System",
        "description": "Student mark entry, percentage/grade calculation, pass/fail determination, and result generation.",
        "icon": "GraduationCap",
    },
    "library_management": {
        "display_name": "Library Management System",
        "description": "Book cataloging, issue/return workflow, availability tracking, and overdue fine calculation.",
        "icon": "BookOpen",
    },
}

# Architecture metadata
ARCHITECTURES = {
    "layered": "Layered Architecture",
    "mvc": "MVC Architecture",
    "hexagonal": "Hexagonal Architecture",
    "microservices": "Microservices Architecture",
    "event_driven": "Event-Driven Architecture",
}

ARCHITECTURE_DESCRIPTIONS = {
    "layered": "Horizontal layers (Presentation → Business Logic → Data Access). Simple, well-understood separation of concerns.",
    "mvc": "Model-View-Controller pattern separating data, presentation, and control flow.",
    "hexagonal": "Ports & Adapters pattern isolating core domain from infrastructure through abstract interfaces.",
    "microservices": "Independent, loosely-coupled services coordinated by a gateway.",
    "event_driven": "Components communicate via an in-memory event bus using publish/subscribe messaging.",
}


def get_controller(project_type: str, architecture: str):
    """
    Dynamically import and return a fresh controller instance for the given
    project_type + architecture combination.

    For order_processing we use the legacy architectures/ modules.
    For newer domains we use domains/<project>/<arch>.py modules.
    """
    if project_type == "order_processing":
        # Use existing implementations in architectures/ folder
        module_map = {
            "layered": "architectures.layered.order_processing",
            "mvc": "architectures.mvc.order_processing",
            "hexagonal": "architectures.hexagonal.order_processing",
            "microservices": "architectures.microservices.order_processing",
            "event_driven": "architectures.event_driven.order_processing",
        }
        mod_path = module_map.get(architecture)
        if mod_path is None:
            raise ValueError(f"Unknown architecture: {architecture}")
        import importlib
        mod = importlib.import_module(mod_path)
        return mod.OrderController()

    elif project_type == "student_result":
        module_map = {
            "layered": "domains.student_result.layered",
            "mvc": "domains.student_result.mvc",
            "hexagonal": "domains.student_result.hexagonal",
            "microservices": "domains.student_result.microservices",
            "event_driven": "domains.student_result.event_driven",
        }
        mod_path = module_map.get(architecture)
        if mod_path is None:
            raise ValueError(f"Unknown architecture: {architecture}")
        import importlib
        mod = importlib.import_module(mod_path)
        return mod.StudentController()

    elif project_type == "library_management":
        module_map = {
            "layered": "domains.library_management.layered",
            "mvc": "domains.library_management.mvc",
            "hexagonal": "domains.library_management.hexagonal",
            "microservices": "domains.library_management.microservices",
            "event_driven": "domains.library_management.event_driven",
        }
        mod_path = module_map.get(architecture)
        if mod_path is None:
            raise ValueError(f"Unknown architecture: {architecture}")
        import importlib
        mod = importlib.import_module(mod_path)
        return mod.LibraryController()

    else:
        raise ValueError(f"Unknown project type: {project_type}")
