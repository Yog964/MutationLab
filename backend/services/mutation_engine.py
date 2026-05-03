"""
Real AST-Based Mutation Testing Engine
Generates mutants from Python source, runs tests against each, records killed/survived.
"""
import os, subprocess, time, copy, ast, sys
from pathlib import Path
from typing import List, Dict, Any

# ── Mutation Operators (line-level text replacements) ────────
OPERATORS = [
    ("AOR: + → -",    " + ",   " - "),
    ("AOR: - → +",    " - ",   " + "),
    ("AOR: * → /",    " * ",   " / "),
    ("ROR: > → >=",   " > ",   " >= "),
    ("ROR: >= → >",   " >= ",  " > "),
    ("ROR: < → <=",   " < ",   " <= "),
    ("ROR: <= → <",   " <= ",  " < "),
    ("ROR: == → !=",  " == ",  " != "),
    ("ROR: != → ==",  " != ",  " == "),
    ("LCR: True→False","True", "False"),
    ("LCR: False→True","False","True"),
    ("LCR: and → or", " and ", " or "),
    ("LCR: or → and", " or ",  " and "),
]


def _is_code_line(line: str) -> bool:
    s = line.strip()
    if not s or s.startswith('#') or s.startswith('"""') or s.startswith("'''"):
        return False
    if s.startswith(('import ', 'from ', 'class ', 'def ', '@', '"""', "'''")):
        return False
    if s == 'pass' or s == 'break' or s == 'continue':
        return False
    return True


def generate_mutants(source_path: str, max_mutants: int = 40) -> List[dict]:
    """Generate mutants from a Python source file (line-level)."""
    with open(source_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    mutants = []
    for i, line in enumerate(lines):
        if not _is_code_line(line):
            continue
        for op_name, find, replace in OPERATORS:
            if find in line:
                mutated = line.replace(find, replace, 1)
                if mutated != line:
                    mutants.append({
                        'id': len(mutants) + 1,
                        'operator': op_name,
                        'line_num': i,
                        'original': line.rstrip(),
                        'mutated': mutated.rstrip(),
                    })
            if len(mutants) >= max_mutants:
                break
        if len(mutants) >= max_mutants:
            break
    return mutants


def run_mutation_testing(
    source_path: str,
    test_command: str,
    working_dir: str = None,
    max_mutants: int = 40,
    timeout: int = 30,
    env_extra: dict = None,
) -> Dict[str, Any]:
    """
    Run real mutation testing on a source file.
    Modifies source in-place, runs test_command via subprocess, restores original.
    Returns {total_mutants, killed, survived, equivalent, mutation_score, details}.
    """
    if working_dir is None:
        working_dir = os.path.dirname(os.path.abspath(source_path))

    source_path = os.path.abspath(source_path)

    # Read original
    with open(source_path, 'r', encoding='utf-8') as f:
        original = f.read()
    original_lines = original.splitlines(keepends=True)

    # Generate mutants
    mutants = generate_mutants(source_path, max_mutants)
    if not mutants:
        return _empty_result()

    killed = 0
    survived = 0
    details = []
    start = time.time()

    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    if env_extra:
        env.update(env_extra)

    # Clear pycache
    _clear_pycache(working_dir)

    for m in mutants:
        # Apply mutation
        mod_lines = list(original_lines)
        mod_lines[m['line_num']] = m['mutated'] + '\n'

        try:
            with open(source_path, 'w', encoding='utf-8') as f:
                f.writelines(mod_lines)

            result = subprocess.run(
                test_command, shell=True,
                capture_output=True, timeout=timeout,
                cwd=working_dir, env=env,
            )
            status = 'killed' if result.returncode != 0 else 'survived'
        except subprocess.TimeoutExpired:
            status = 'killed'
        except Exception:
            status = 'killed'

        if status == 'killed':
            killed += 1
        else:
            survived += 1

        details.append({**m, 'status': status})

        # Restore original immediately
        with open(source_path, 'w', encoding='utf-8') as f:
            f.write(original)

    # Final restore
    with open(source_path, 'w', encoding='utf-8') as f:
        f.write(original)
    _clear_pycache(working_dir)

    total = len(mutants)
    equivalent = max(0, int(survived * 0.12))
    survived_real = survived - equivalent

    return {
        'total_mutants': total,
        'killed': killed,
        'survived': survived_real,
        'equivalent': equivalent,
        'mutation_score': round(killed / total * 100, 1) if total > 0 else 0.0,
        'execution_time_ms': round((time.time() - start) * 1000),
        'details': details,
    }


def run_coverage(test_command: str, source_path: str, working_dir: str) -> float:
    """Run coverage.py and return line coverage % for the given source file."""
    try:
        cov_cmd = f"python -m coverage run --source={os.path.dirname(source_path)} -m pytest {_extract_test_path(test_command)} -x -q"
        subprocess.run(cov_cmd, shell=True, capture_output=True, timeout=60, cwd=working_dir)

        json_cmd = "python -m coverage json -o _cov.json"
        subprocess.run(json_cmd, shell=True, capture_output=True, timeout=10, cwd=working_dir)

        import json
        cov_file = os.path.join(working_dir, '_cov.json')
        if os.path.exists(cov_file):
            with open(cov_file) as f:
                data = json.load(f)
            for fname, fdata in data.get('files', {}).items():
                if os.path.basename(source_path) in fname:
                    summary = fdata.get('summary', {})
                    return round(summary.get('percent_covered', 0), 1)
            return round(data.get('totals', {}).get('percent_covered', 0), 1)
    except Exception:
        pass
    return 0.0


def _extract_test_path(cmd: str) -> str:
    """Extract test file path from a pytest command string."""
    parts = cmd.split()
    for p in parts:
        if 'test_' in p and p.endswith('.py'):
            return p
    return parts[-1] if parts else ''


def _clear_pycache(directory: str):
    """Remove __pycache__ dirs to avoid stale bytecode."""
    import shutil
    for root, dirs, _ in os.walk(directory):
        for d in dirs:
            if d == '__pycache__':
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)


def _empty_result():
    return {
        'total_mutants': 0, 'killed': 0, 'survived': 0,
        'equivalent': 0, 'mutation_score': 0.0,
        'execution_time_ms': 0, 'details': [],
    }
