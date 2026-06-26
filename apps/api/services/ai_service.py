"""
AI Service — Symptom → Specialist mapping.
1. Tries deterministic CSV-based lookup first (symptom_specialist_mappings.csv).
2. Falls back to Gemini / OpenAI if no CSV match is found.
3. Final fallback: rule-based SPECIALIST_RULES.
"""
import json
import csv
import os
import re
from config import settings

# ─── Load CSV Mappings ────────────────────────────────────
# Path relative to the api/ directory
_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "dataset", "symptom_specialist_mappings.csv"
)

# Build a lookup: { symptom_lower: (specialist, urgency_level) }
_SYMPTOM_MAP: dict[str, tuple[str, str]] = {}

def _load_symptom_csv():
    """Load symptom-specialist-urgency mappings from CSV."""
    global _SYMPTOM_MAP
    try:
        with open(_CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                symptom = row.get('symptom', '').strip().lower()
                specialist = row.get('specialist', '').strip()
                urgency = row.get('urgency_level', 'medium').strip()
                if symptom and specialist:
                    _SYMPTOM_MAP[symptom] = (specialist, urgency)
        print(f"[AI Service] Loaded {len(_SYMPTOM_MAP)} symptom mappings from CSV.")
    except FileNotFoundError:
        print(f"[AI Service] WARNING: CSV not found at {_CSV_PATH}. CSV lookup disabled.")
    except Exception as e:
        print(f"[AI Service] WARNING: Failed to load CSV: {e}. CSV lookup disabled.")

_load_symptom_csv()

# Normalize specialist names from CSV to canonical names used in the app
_SPECIALIST_NORMALIZE = {
    "ENT": "ENT Specialist",
    "Orthopedic": "Orthopedic Surgeon",
    "Pulmonologist": "Pulmonologist",
    "General Physician": "General Physician",
    "Dermatologist": "Dermatologist",
    "Cardiologist": "Cardiologist",
    "Neurologist": "Neurologist",
    "Dentist": "Dentist",
    "Psychiatrist": "Psychiatrist",
    "Ophthalmologist": "Ophthalmologist",
    "Gastroenterologist": "Gastroenterologist",
    "Gynecologist": "Gynecologist",
    "Pediatrician": "Pediatrician",
    "Nephrologist": "Nephrologist",
    "Endocrinologist": "Endocrinologist",
    "Urologist": "Urologist",
    "Physiotherapist": "Physiotherapist",
}

_URGENCY_NORMALIZE = {
    "low": "low",
    "medium": "moderate",
    "moderate": "moderate",
    "high": "high",
    "emergency": "emergency",
}


def _csv_classify(symptom_text: str) -> dict | None:
    """
    Try to match the symptom text against the loaded CSV mappings.
    Returns a result dict if a match is found, else None.
    Tries exact phrase match first, then partial keyword matching.
    """
    if not _SYMPTOM_MAP:
        return None

    text_lower = symptom_text.lower()

    # Phase 1: Exact phrase match
    for symptom_key, (specialist, urgency) in _SYMPTOM_MAP.items():
        if symptom_key in text_lower:
            canonical_specialist = _SPECIALIST_NORMALIZE.get(specialist, specialist)
            canonical_urgency = _URGENCY_NORMALIZE.get(urgency.lower(), "moderate")
            emergency = canonical_urgency == "emergency" or urgency.lower() == "high"
            return {
                "specialist_type": canonical_specialist,
                "specialist_explanation": f"Your symptoms match '{symptom_key}', which is best treated by a {canonical_specialist}.",
                "urgency_level": canonical_urgency,
                "urgency_reason": f"Urgency classified as {canonical_urgency} based on clinical symptom mapping.",
                "emergency_mode": canonical_urgency == "emergency",
                "fallback": False,
                "source": "csv",
            }

    # Phase 2: Token matching — check if any multi-word symptom key words appear in the text
    words_in_text = set(re.findall(r'\b\w+\b', text_lower))
    best_match = None
    best_overlap = 0

    for symptom_key, (specialist, urgency) in _SYMPTOM_MAP.items():
        symptom_words = set(re.findall(r'\b\w+\b', symptom_key))
        if len(symptom_words) < 2:
            continue  # Skip single-word keys for phase 2 (already covered above)
        overlap = len(symptom_words & words_in_text)
        if overlap >= len(symptom_words) - 1 and overlap > best_overlap:
            best_overlap = overlap
            best_match = (symptom_key, specialist, urgency)

    if best_match:
        symptom_key, specialist, urgency = best_match
        canonical_specialist = _SPECIALIST_NORMALIZE.get(specialist, specialist)
        canonical_urgency = _URGENCY_NORMALIZE.get(urgency.lower(), "moderate")
        return {
            "specialist_type": canonical_specialist,
            "specialist_explanation": f"Your symptoms suggest you need a {canonical_specialist}.",
            "urgency_level": canonical_urgency,
            "urgency_reason": f"Urgency classified as {canonical_urgency} based on clinical symptom mapping.",
            "emergency_mode": canonical_urgency == "emergency",
            "fallback": False,
            "source": "csv",
        }

    return None


# ─── Prompt Template ──────────────────────────────────────
SYMPTOM_PROMPT = """You are a medical triage assistant. A user has described their symptoms.

Analyze them and return ONLY a valid JSON object (no markdown, no explanation):

{{
  "specialist_type": "<use one of the canonical names below>",
  "specialist_explanation": "<one sentence why this specialist>",
  "urgency_level": "<low|moderate|high|emergency>",
  "urgency_reason": "<one sentence>",
  "emergency_mode": <true|false>
}}

Canonical specialist names (use EXACTLY one):
General Physician, Cardiologist, Dermatologist, Orthopedic Surgeon, Gynecologist,
Pediatrician, Neurologist, Gastroenterologist, ENT Specialist, Ophthalmologist,
Dentist, Nephrologist, Psychiatrist, Physiotherapist, Endocrinologist, Urologist,
Pulmonologist, Emergency Physician

Urgency levels:
- emergency: chest pain, stroke signs, severe breathing difficulty, unconsciousness, severe trauma
- high: high fever >103F, severe pain, injury needing stitches, suspected fracture
- moderate: persistent symptoms 2+ days, moderate pain, vomiting, infection signs
- low: mild symptoms, wellness query, pharmacy-only need

Set emergency_mode: true ONLY when urgency_level is "emergency".

User symptoms: {symptom_text}
City: {city}
"""

# ─── Fallback Rules ───────────────────────────────────────
EMERGENCY_KEYWORDS = [
    "chest pain", "can't breathe", "cannot breathe", "difficulty breathing",
    "unconscious", "stroke", "heart attack", "severe bleeding", "seizure",
    "loss of consciousness", "not responding", "choking"
]

SPECIALIST_RULES = [
    (["skin", "rash", "acne", "itch", "dermat", "infection"], "Dermatologist"),
    (["eye", "vision", "blur", "sight"], "Ophthalmologist"),
    (["ear", "nose", "throat", "ent", "sinus"], "ENT Specialist"),
    (["heart", "cardiac", "chest", "cardio", "palpitation"], "Cardiologist"),
    (["bone", "fracture", "joint", "ortho", "knee", "ankle", "back pain", "spine"], "Orthopedic Surgeon"),
    (["stomach", "gastro", "nausea", "vomit", "diarrhea", "abdomen", "bowel"], "Gastroenterologist"),
    (["teeth", "dental", "gum", "tooth"], "Dentist"),
    (["child", "baby", "infant", "pediatric"], "Pediatrician"),
    (["mental", "anxiety", "depression", "stress", "psychiatr", "panic"], "Psychiatrist"),
    (["kidney", "renal", "urine", "urinary"], "Nephrologist"),
    (["women", "gynec", "period", "pregnancy", "menstrual"], "Gynecologist"),
    (["diabetes", "thyroid", "hormone", "endo"], "Endocrinologist"),
    (["neuro", "headache", "migraine", "brain"], "Neurologist"),
    (["physio", "rehabilitation", "physiother"], "Physiotherapist"),
    (["lung", "breath", "cough", "wheez", "pulmo"], "Pulmonologist"),
]


def _fallback_classify(symptom_text: str) -> dict:
    """Rule-based fallback when AI and CSV are both unavailable."""
    text = symptom_text.lower()

    if any(kw in text for kw in EMERGENCY_KEYWORDS):
        return {
            "specialist_type": "Emergency Physician",
            "specialist_explanation": "Your symptoms may indicate an emergency. Please seek immediate care.",
            "urgency_level": "emergency",
            "urgency_reason": "Symptoms suggest potentially life-threatening condition.",
            "emergency_mode": True,
            "fallback": True,
        }

    for keywords, specialist in SPECIALIST_RULES:
        if any(kw in text for kw in keywords):
            return {
                "specialist_type": specialist,
                "specialist_explanation": f"Your symptoms suggest a {specialist} consultation.",
                "urgency_level": "moderate",
                "urgency_reason": "Please consult a doctor for an accurate diagnosis.",
                "emergency_mode": False,
                "fallback": True,
            }

    return {
        "specialist_type": "General Physician",
        "specialist_explanation": "A General Physician can evaluate your symptoms and refer you if needed.",
        "urgency_level": "moderate",
        "urgency_reason": "Unable to determine specific specialist. A GP is the safest first visit.",
        "emergency_mode": False,
        "fallback": True,
    }


# ─── Gemini ───────────────────────────────────────────────
async def _analyze_gemini(symptom_text: str, city: str) -> dict:
    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)
    prompt = SYMPTOM_PROMPT.format(symptom_text=symptom_text, city=city or "Unknown")
    response = await model.generate_content_async(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            max_output_tokens=400,
            temperature=0.1,
        )
    )
    return json.loads(response.text)


# ─── OpenAI ───────────────────────────────────────────────
async def _analyze_openai(symptom_text: str, city: str) -> dict:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    prompt = SYMPTOM_PROMPT.format(symptom_text=symptom_text, city=city or "Unknown")
    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=400,
        temperature=0.1,
    )
    return json.loads(response.choices[0].message.content)


# ─── Main Entry ───────────────────────────────────────────
async def analyze_symptoms(symptom_text: str, city: str | None = None) -> dict:
    """
    Analyze symptoms using the following priority:
    1. CSV-based deterministic lookup (fastest, most reliable for known symptoms)
    2. Gemini / OpenAI AI call (for complex or novel symptoms)
    3. Rule-based fallback (always available)
    """
    # Step 1: Try CSV mapping first
    csv_result = _csv_classify(symptom_text)
    if csv_result:
        print(f"[AI Service] CSV match found: {csv_result['specialist_type']}")
        return csv_result

    # Step 2: Try AI
    try:
        if settings.ai_provider == "gemini" and settings.gemini_api_key:
            result = await _analyze_gemini(symptom_text, city or "")
        elif settings.openai_api_key:
            result = await _analyze_openai(symptom_text, city or "")
        else:
            return _fallback_classify(symptom_text)

        required = ["specialist_type", "urgency_level", "emergency_mode"]
        if not all(k in result for k in required):
            raise ValueError("AI response missing required fields")

        result["fallback"] = False
        result["source"] = "ai"
        return result

    except Exception as e:
        print(f"[AI Service] AI call failed: {e}. Using rule-based fallback.")
        return _fallback_classify(symptom_text)
