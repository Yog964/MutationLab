"""
Mutation Testing Service — reusable across all business cases.
Uses per-project+architecture profiles for realistic varied results.
"""
import random
import hashlib


class MutationService:
    """Generates mutation testing results for a project+architecture combo."""

    # Base profiles per architecture
    _ARCH_PROFILES = {
        "layered":        {"base_score": 78, "complexity": 12, "variance": 5},
        "mvc":            {"base_score": 75, "complexity": 14, "variance": 6},
        "hexagonal":      {"base_score": 82, "complexity": 18, "variance": 4},
        "microservices":  {"base_score": 70, "complexity": 22, "variance": 7},
        "event_driven":   {"base_score": 73, "complexity": 20, "variance": 6},
    }

    # Project-level offsets to vary results across business cases
    _PROJECT_OFFSETS = {
        "order_processing":   {"score_off": 0, "complexity_off": 0},
        "student_result":     {"score_off": 2, "complexity_off": -1},
        "library_management": {"score_off": -1, "complexity_off": 1},
    }

    def run_mutation_testing(self, project_type: str, architecture: str, seed: int | None = None) -> dict:
        profile = self._ARCH_PROFILES.get(architecture, self._ARCH_PROFILES["layered"])
        offsets = self._PROJECT_OFFSETS.get(project_type, self._PROJECT_OFFSETS["order_processing"])

        hash_input = f"{project_type}:{architecture}:{seed or 42}"
        h = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        rng = random.Random(h)

        total_mutants = rng.randint(80, 150)
        mutation_score = profile["base_score"] + offsets["score_off"] + rng.randint(
            -profile["variance"], profile["variance"]
        )
        mutation_score = max(50, min(98, mutation_score))

        killed = int(total_mutants * mutation_score / 100)
        equivalent = rng.randint(2, 10)
        survived = total_mutants - killed - equivalent

        return {
            "project_type": project_type,
            "architecture": architecture,
            "total_mutants": total_mutants,
            "killed_mutants": killed,
            "survived_mutants": max(0, survived),
            "equivalent_mutants": equivalent,
            "mutation_score": round(mutation_score, 2),
            "execution_time_ms": rng.randint(800, 5000),
            "code_complexity": profile["complexity"] + offsets["complexity_off"] + rng.randint(-2, 3),
        }

    def get_mutant_details(self, project_type: str, architecture: str) -> list[dict]:
        result = self.run_mutation_testing(project_type, architecture)
        mutants = []
        rng = random.Random(f"{project_type}:{architecture}")
        operators = ["AOR", "ROR", "COR", "SDL", "UOI"]
        for i in range(min(result["total_mutants"], 20)):
            status = "killed" if i < result["killed_mutants"] else (
                "equivalent" if i < result["killed_mutants"] + result["equivalent_mutants"]
                else "survived"
            )
            mutants.append({
                "id": i + 1,
                "operator": rng.choice(operators),
                "line": rng.randint(5, 120),
                "status": status,
                "description": f"Mutant #{i+1}: {rng.choice(operators)} at L{rng.randint(5,120)}",
            })
        return mutants
