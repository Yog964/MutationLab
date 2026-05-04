"""Generate a 500-row realistic training dataset for the ML model."""
import csv
import random
random.seed(42)

# Realistic profile ranges for each architecture
# (mut_score_range, exec_time_range, coverage_range, complexity_range, equiv_rate_range, effectiveness_weights)
PROFILES = {
    "layered": {
        "mutation_score": (68, 88),
        "execution_time": (800, 1800),
        "code_coverage": (85, 96),
        "complexity": (6, 16),
        "equivalent_rate": (2.0, 7.0),
        "effectiveness": {"high": 0.55, "medium": 0.35, "low": 0.10},
    },
    "mvc": {
        "mutation_score": (65, 85),
        "execution_time": (1000, 2200),
        "code_coverage": (82, 94),
        "complexity": (8, 18),
        "equivalent_rate": (3.0, 8.0),
        "effectiveness": {"high": 0.40, "medium": 0.45, "low": 0.15},
    },
    "hexagonal": {
        "mutation_score": (75, 95),
        "execution_time": (1400, 2800),
        "code_coverage": (88, 99),
        "complexity": (12, 22),
        "equivalent_rate": (1.0, 5.0),
        "effectiveness": {"high": 0.65, "medium": 0.28, "low": 0.07},
    },
    "microservices": {
        "mutation_score": (55, 80),
        "execution_time": (2500, 5000),
        "code_coverage": (75, 92),
        "complexity": (16, 28),
        "equivalent_rate": (5.0, 12.0),
        "effectiveness": {"high": 0.15, "medium": 0.40, "low": 0.45},
    },
    "event_driven": {
        "mutation_score": (60, 85),
        "execution_time": (1800, 3800),
        "code_coverage": (78, 94),
        "complexity": (14, 24),
        "equivalent_rate": (4.0, 10.0),
        "effectiveness": {"high": 0.25, "medium": 0.45, "low": 0.30},
    },
}

rows = []
for arch, profile in PROFILES.items():
    for _ in range(100):  # 100 rows per architecture = 500 total
        mut = round(random.uniform(*profile["mutation_score"]), 1)
        exe = round(random.uniform(*profile["execution_time"]))
        cov = round(random.uniform(*profile["code_coverage"]), 1)
        comp = round(random.uniform(*profile["complexity"]))
        eq = round(random.uniform(*profile["equivalent_rate"]), 1)

        # Assign effectiveness label based on weighted probabilities
        r = random.random()
        weights = profile["effectiveness"]
        if r < weights["high"]:
            eff = "high"
        elif r < weights["high"] + weights["medium"]:
            eff = "medium"
        else:
            eff = "low"

        # Add correlation: high mutation scores push towards "high" label
        if mut > 85 and eff == "low":
            eff = "medium"
        if mut < 62 and eff == "high":
            eff = "medium"

        rows.append([arch, mut, exe, cov, comp, eq, eff])

# Shuffle for randomness
random.shuffle(rows)

# Write CSV
with open("data/training_dataset.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["architecture", "mutation_score", "execution_time",
                     "code_coverage", "complexity", "equivalent_rate", "effectiveness"])
    writer.writerows(rows)

print(f"Generated {len(rows)} rows -> data/training_dataset.csv")
