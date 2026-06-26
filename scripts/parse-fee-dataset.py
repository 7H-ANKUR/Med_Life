"""
ETL: Parse dataset/docter.csv → insert into fee_estimates table.
Run: python scripts/parse-fee-dataset.py

Dataset columns:
  Name, Degree, DP Score, NPV Value, Location, City, Consult Fee, Years of Experience, Speciality
"""
import sys, os, re, csv, json, asyncio
from collections import defaultdict

# Add api to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../apps/api"))

DATASET_PATH = os.path.join(os.path.dirname(__file__), "../apps/api/dataset/docter.csv")

# ─── Specialist Normalization Map ─────────────────────────
SPECIALTY_MAP = {
    "general physician":         "General Physician",
    "internal medicine":         "General Physician",
    "consultant physician":      "General Physician",
    "cardiologist":              "Cardiologist",
    "dermatologist":             "Dermatologist",
    "venereologist":             "Dermatologist",
    "aesthetic dermatologist":   "Dermatologist",
    "orthopedic":                "Orthopedic Surgeon",
    "orthopaedic":               "Orthopedic Surgeon",
    "gynecologist":              "Gynecologist",
    "obstetrician":              "Gynecologist",
    "pediatrician":              "Pediatrician",
    "neurologist":               "Neurologist",
    "gastroenterologist":        "Gastroenterologist",
    "ent":                       "ENT Specialist",
    "ophthalmologist":           "Ophthalmologist",
    "eye surgeon":               "Ophthalmologist",
    "dentist":                   "Dentist",
    "orthodontist":              "Dentist",
    "endodontist":               "Dentist",
    "periodontist":              "Dentist",
    "nephrologist":              "Nephrologist",
    "renal specialist":          "Nephrologist",
    "psychiatrist":              "Psychiatrist",
    "physiotherapist":           "Physiotherapist",
    "endocrinologist":           "Endocrinologist",
    "urologist":                 "Urologist",
    "sexologist":                "Urologist",
    "implantologist":            "Dentist",
    "cosmetologist":             "Dermatologist",
}


def normalize_specialist(raw: str) -> str | None:
    if not raw:
        return None
    raw_lower = raw.lower()
    for key, canonical in SPECIALTY_MAP.items():
        if key in raw_lower:
            return canonical
    return None


def parse_fee(fee_str: str) -> int | None:
    """
    Parse fee string from CSV.
    Examples: "₹,11200" → 1120  |  "₹500" → 500  |  "" → None
    Known issue: "₹,11200" is actually "₹1,200" with encoding bug → divide by 10 if > 5000
    """
    if not fee_str:
        return None
    digits = re.sub(r"[^\d]", "", str(fee_str))
    if not digits:
        return None
    fee = int(digits)
    # Fix malformed fees: "11200" is likely "1,120" → ₹1120
    if fee > 10000:
        fee = fee // 10
    # Sanity bounds: ₹100 – ₹10,000
    if 100 <= fee <= 10000:
        return fee
    return None


def compute_p25_p75(values: list[int]) -> tuple[int, int]:
    sorted_v = sorted(values)
    n = len(sorted_v)
    p25_idx = max(0, int(n * 0.25) - 1)
    p75_idx = min(n - 1, int(n * 0.75))
    return sorted_v[p25_idx], sorted_v[p75_idx]


def main():
    data = defaultdict(list)  # (city, specialist) → list of fees

    with open(DATASET_PATH, encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            city = (row.get("City") or "").strip()
            specialist_raw = (row.get("Speciality") or "").strip()
            fee_raw = (row.get("Consult Fee") or "").strip()

            if not city or not specialist_raw:
                continue

            specialist = normalize_specialist(specialist_raw)
            fee = parse_fee(fee_raw)

            if specialist and fee:
                data[(city, specialist)].append(fee)

    results = []
    for (city, specialist), fees in data.items():
        if len(fees) < 2:
            continue
        fee_min, fee_max = compute_p25_p75(fees)
        results.append({
            "city": city,
            "specialist_type": specialist,
            "fee_min": fee_min,
            "fee_max": fee_max,
            "sample_count": len(fees),
            "data_source": "practo_dataset",
        })

    # Print as JSON (pipe to seed script or inspect)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\n# Processed {len(results)} city×specialist fee ranges", file=sys.stderr)


if __name__ == "__main__":
    main()
