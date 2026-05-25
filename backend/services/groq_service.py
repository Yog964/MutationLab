"""
Groq LLM Service — Generates intelligent architectural recommendations
using the Llama 3 model via the Groq API.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the backend directory
load_dotenv(Path(__file__).parent.parent / ".env")

_GROQ_CLIENT = None


def _get_client():
    """Lazy-initialize the Groq client."""
    global _GROQ_CLIENT
    if _GROQ_CLIENT is None:
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set in .env")
        _GROQ_CLIENT = Groq(api_key=api_key)
    return _GROQ_CLIENT


def generate_recommendation(best: dict, worst: dict, weights: dict) -> dict:
    """
    Send the best/worst architecture metrics to Groq's Llama 3 model
    and get back intelligent, contextual recommendation text.
    
    Returns:
        {
            "best_arch": str,
            "why_recommended": [str, str, str],
            "worst_arch": str,
            "why_not_recommended": [str, str, str],
            "ai_generated": True
        }
    """
    best_arch = best.get("architecture", "unknown")
    worst_arch = worst.get("architecture", "unknown")
    best_metrics = best.get("raw_metrics", {})
    worst_metrics = worst.get("raw_metrics", {})

    prompt = f"""You are a senior software architect analyzing mutation testing results.

CONTEXT: A mutation testing experiment was run on the same business logic implemented 
in different software architecture patterns. The user's priority weights are:
- Quality: {weights.get('quality', 0.5):.0%}
- Speed: {weights.get('speed', 0.2):.0%}
- Maintainability: {weights.get('maintainability', 0.3):.0%}

BEST ARCHITECTURE: {best_arch.replace('_', ' ').title()}
- Mutation Score: {best.get('raw_metrics', {}).get('mutation_score', 'N/A')}%
- Execution Time: {best.get('raw_metrics', {}).get('execution_time_ms', 'N/A')}ms
- Code Coverage: {best.get('raw_metrics', {}).get('code_coverage', 'N/A')}%
- Composite Score: {best.get('composite_score', 'N/A')}/100
- ML Confidence: {best.get('confidence', 'N/A')}%
- Quality Score: {best.get('quality_score', 'N/A')}/100
- Speed Score: {best.get('speed_score', 'N/A')}/100

WORST ARCHITECTURE: {worst_arch.replace('_', ' ').title()}
- Mutation Score: {worst.get('raw_metrics', {}).get('mutation_score', 'N/A')}%
- Execution Time: {worst.get('raw_metrics', {}).get('execution_time_ms', 'N/A')}ms
- Code Coverage: {worst.get('raw_metrics', {}).get('code_coverage', 'N/A')}%
- Composite Score: {worst.get('composite_score', 'N/A')}/100
- ML Confidence: {worst.get('confidence', 'N/A')}%
- Quality Score: {worst.get('quality_score', 'N/A')}/100
- Speed Score: {worst.get('speed_score', 'N/A')}/100

TASK: Provide exactly 3 bullet-point reasons for why the BEST architecture is recommended,
and exactly 3 bullet-point reasons for why the WORST architecture is NOT recommended.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS (no extra text):
WHY_RECOMMENDED:
- reason 1
- reason 2
- reason 3
WHY_NOT_RECOMMENDED:
- reason 1
- reason 2
- reason 3"""

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=500,
        )
        text = response.choices[0].message.content.strip()
        return _parse_response(text, best_arch, worst_arch)
    except Exception as e:
        print(f"[Groq] API call failed: {e}")
        return _fallback(best, worst, best_arch, worst_arch)


def _parse_response(text: str, best_arch: str, worst_arch: str) -> dict:
    """Parse the structured LLM response into lists."""
    why_recommended = []
    why_not_recommended = []
    current_section = None

    for line in text.split("\n"):
        line = line.strip()
        if "WHY_RECOMMENDED" in line.upper():
            current_section = "rec"
            continue
        elif "WHY_NOT_RECOMMENDED" in line.upper():
            current_section = "not_rec"
            continue

        if line.startswith("- ") and current_section == "rec":
            why_recommended.append(line[2:])
        elif line.startswith("- ") and current_section == "not_rec":
            why_not_recommended.append(line[2:])

    # Ensure we always have at least something
    if not why_recommended:
        why_recommended = ["Strong overall composite score for the selected priorities."]
    if not why_not_recommended:
        why_not_recommended = ["Lower composite score compared to other architectures."]

    return {
        "best_arch": best_arch,
        "why_recommended": why_recommended[:3],
        "worst_arch": worst_arch,
        "why_not_recommended": why_not_recommended[:3],
        "ai_generated": True
    }


def _fallback(best: dict, worst: dict, best_arch: str, worst_arch: str) -> dict:
    """Hardcoded fallback if the Groq API is unreachable."""
    why_recommended = []
    if best.get("quality_score", 0) > 85:
        why_recommended.append(f"Exceptional Test Quality score ({best['quality_score']}/100).")
    if best.get("speed_score", 0) > 80:
        why_recommended.append(f"Fast execution time creates a tight feedback loop.")
    why_recommended.append("Best overall composite score for the chosen priorities.")

    why_not_recommended = []
    if worst.get("quality_score", 0) < 75:
        why_not_recommended.append(f"Poor Test Quality ({worst['quality_score']}/100).")
    if worst.get("speed_score", 0) < 50:
        why_not_recommended.append(f"Slow execution time hurts CI/CD pipelines.")
    why_not_recommended.append("Lowest composite score among all tested architectures.")

    return {
        "best_arch": best_arch,
        "why_recommended": why_recommended,
        "worst_arch": worst_arch,
        "why_not_recommended": why_not_recommended,
        "ai_generated": False
    }
