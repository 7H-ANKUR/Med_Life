"""
Scoring / Ranking Engine.
Pure function — no external API calls.
Implements: 08-scoring-engine-spec.md
"""


# ─── Score Component Functions ────────────────────────────

def rating_norm(rating: float | None) -> float:
    """Normalize Google rating (1–5) to 0.0–1.0. Default 0.5 if missing."""
    if rating is None:
        return 0.5
    return (max(1.0, min(5.0, rating)) - 1) / 4


def review_quality(count: int | None) -> float:
    """Convert review count to quality score 0.0–1.0."""
    if not count:
        return 0.0
    if count >= 500: return 1.0
    if count >= 200: return 0.8
    if count >= 50:  return 0.6
    if count >= 10:  return 0.4
    return 0.2


def open_now_score(open_now: bool, is_24x7: bool = False) -> float:
    if is_24x7:   return 1.0
    if open_now:  return 0.8
    return 0.0


def distance_score(meters: int | None) -> float:
    """Inverse distance: 1.0 at 0m, 0.0 at 10km+"""
    if meters is None:
        return 0.3
    MAX = 10_000
    return max(0.0, 1.0 - (min(meters, MAX) / MAX))


def hospital_capability(place_type: str) -> float:
    if place_type == "hospital":  return 1.0
    if place_type == "clinic":    return 0.3
    return 0.0


# ─── Hard Filters ─────────────────────────────────────────

def apply_hard_filters(places: list[dict], context: dict) -> list[dict]:
    filtered = []
    for p in places:
        # We don't have live opening hours, assume hospitals are 24x7 / open
        place_type = p.get("_place_type", "clinic")
        open_now = True if place_type == "hospital" else False
        
        meters = p.get("_distance_meters")
        rating = p.get("rating")
        fee_min = p.get("_fee_min", 0)

        # Emergency: exclude pharmacies unless no other option
        if context.get("mode") == "emergency" and place_type == "pharmacy":
            continue

        # Emergency: exclude closed places (hard exclusion)
        # Assuming hospitals are always open
        if context.get("mode") == "emergency" and not open_now:
            continue

        # Open now required
        if context.get("open_now_required") and not open_now:
            continue

        # Budget filter
        if context.get("budget_max") and fee_min > context["budget_max"]:
            continue

        # Rating minimum
        if context.get("rating_min") and rating and rating < context["rating_min"]:
            continue

        # 24×7 required
        if context.get("is_24x7_required"):
            if place_type != "hospital":
                continue

        filtered.append(p)

    return filtered


# ─── Main Ranking Function ────────────────────────────────

def rank_places(places: list[dict], context: dict) -> list[dict]:
    """
    Rank places by scoring formula (normal or emergency mode).
    context keys:
      mode: 'normal' | 'emergency'
      specialist_type: str | None
      language_pref: str | None
      open_now_required: bool
      budget_max: int | None
      rating_min: float | None
      is_24x7_required: bool
    Returns sorted list with '_score' field added.
    """
    mode = context.get("mode", "normal")

    # Step 1: Hard filters
    filtered = apply_hard_filters(places, context)

    # Fallback: if emergency filters left 0 results, loosen to include clinics
    if mode == "emergency" and len(filtered) == 0:
        context_relaxed = {**context, "mode": "normal"}
        filtered = apply_hard_filters(places, context_relaxed)

    # Step 2: Score each place
    scored = []
    for p in filtered:
        place_type = p.get("_place_type", "clinic")
        open_now = True if place_type == "hospital" else False
        is_24x7 = True if place_type == "hospital" else False
        meters = p.get("_distance_meters")

        if mode == "emergency":
            base = (
                distance_score(meters)                       * 0.50 +
                open_now_score(open_now, is_24x7)           * 0.30 +
                hospital_capability(place_type)             * 0.20
            )
        else:
            base = (
                rating_norm(p.get("rating"))                * 0.40 +
                review_quality(p.get("user_ratings_total")) * 0.20 +
                open_now_score(open_now, is_24x7)           * 0.20 +
                distance_score(meters)                      * 0.20
            )

        # Soft boosts
        boost = 0.0
        specialist = context.get("specialist_type", "")
        if specialist:
            name_lower = p.get("name", "").lower()
            keyword = specialist.lower().split()[0]  # e.g., "cardiologist"
            if keyword in name_lower:
                boost += 0.10

        lang = context.get("language_pref", "")
        if lang and lang != "en":
            name = p.get("name", "").lower()
            # Simple heuristic: regional language names
            if lang == "hi" and any(w in name for w in ["हिंदी", "hindi", "bharat"]):
                boost += 0.05

        if is_24x7:
            boost += 0.05
            
        # Boost based on experience if available
        exp_str = p.get("_doctor_exp", "")
        if exp_str:
            try:
                exp = int("".join(filter(str.isdigit, exp_str)))
                if exp > 20:
                    boost += 0.10
                elif exp > 10:
                    boost += 0.05
            except ValueError:
                pass

        p["_score"] = round(min(1.20, base + boost), 4)
        scored.append(p)

    # Step 3: Sort descending
    ranked = sorted(scored, key=lambda x: x.get("_score", 0), reverse=True)

    # Step 4: Emergency — force nearest open hospital to position 0
    if mode == "emergency":
        hospitals = [p for p in ranked if p.get("_place_type") == "hospital"]
        if hospitals:
            nearest = min(hospitals, key=lambda x: x.get("_distance_meters", 99999))
            ranked = [nearest] + [p for p in ranked if p.get("place_id") != nearest.get("place_id")]

    return ranked
