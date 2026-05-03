"""Configuration settings for the ML-Based Mutation Testing Analysis platform."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_projects")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Canonical architecture list
ARCHITECTURE_NAMES = ["layered", "mvc", "hexagonal", "microservices", "event_driven"]

ARCHITECTURES = [
    {"id": "layered", "display_name": "Layered Architecture", "description": "Horizontal layers (Presentation → Business Logic → Data Access). Simple, well-understood separation of concerns."},
    {"id": "mvc", "display_name": "MVC Architecture", "description": "Model-View-Controller pattern separating data, presentation, and control flow."},
    {"id": "hexagonal", "display_name": "Hexagonal Architecture", "description": "Ports & Adapters pattern isolating core domain from infrastructure through abstract interfaces."},
    {"id": "microservices", "display_name": "Microservices Architecture", "description": "Independent, loosely-coupled services coordinated by a gateway."},
    {"id": "event_driven", "display_name": "Event-Driven Architecture", "description": "Components communicate via an in-memory event bus using publish/subscribe messaging."},
]

# Built-in project types
PROJECT_TYPES = {
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

# Business constants
TAX_RATE = 0.08
DISCOUNT_THRESHOLD = 500.0
DISCOUNT_RATE = 0.10
