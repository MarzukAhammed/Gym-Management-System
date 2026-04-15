import datetime
import random
from dataclasses import dataclass

from django.utils import timezone

from .models import DailyChallenge


@dataclass(frozen=True)
class ChallengeIdea:
    title: str
    # instruction template should fit in 255 chars after formatting
    instruction_template: str
    # rough difficulty score 1-5
    difficulty: int
    # how "cardio" this is (helps mixing variety)
    cardio_weight: int = 0


# Harder, consistent-with-daily-training set (mostly equipment-free).
# We avoid extremely advanced/unsafe movements (e.g., handstand pushups) but keep it challenging.
IDEAS: list[ChallengeIdea] = [
    ChallengeIdea("Push-ups", "Target: {reps} reps (strict form)", 3),
    ChallengeIdea("Diamond Push-ups", "Target: {reps} reps (elbows tight)", 4),
    ChallengeIdea("Decline Push-ups", "Target: {reps} reps (feet elevated)", 4),
    ChallengeIdea("Bodyweight Squats", "Target: {reps} reps (below parallel)", 3),
    ChallengeIdea("Jump Squats", "Target: {reps} reps (soft landings)", 4, cardio_weight=1),
    ChallengeIdea("Walking Lunges", "Target: {reps} reps total", 4),
    ChallengeIdea("Reverse Lunges", "Target: {reps} reps total (controlled)", 3),
    ChallengeIdea("Wall Sit", "Target: {minutes} minutes total (no breaks if possible)", 4),
    ChallengeIdea("Plank", "Target: {minutes} minutes total (tight core)", 4),
    ChallengeIdea("Side Plank", "Target: {minutes} min per side", 4),
    ChallengeIdea("Mountain Climbers", "Target: {reps} reps total (fast, clean)", 4, cardio_weight=2),
    ChallengeIdea("Burpees", "Target: {reps} reps (chest to floor)", 5, cardio_weight=2),
    ChallengeIdea("High Knees", "Target: {reps} reps total (drive up)", 4, cardio_weight=2),
    ChallengeIdea("Jumping Jacks", "Target: {reps} reps (steady pace)", 3, cardio_weight=2),
    ChallengeIdea("Russian Twists", "Target: {reps} reps total (feet up if possible)", 4),
    ChallengeIdea("Sit-ups", "Target: {reps} reps (full range)", 3),
    ChallengeIdea("Hollow Hold", "Target: {minutes} minutes total (no arch)", 5),
    ChallengeIdea("Glute Bridges", "Target: {reps} reps (pause at top)", 3),
    ChallengeIdea("Calf Raises", "Target: {reps} reps (2s squeeze)", 3),
    ChallengeIdea("Bear Crawl", "Target: {meters} meters total (slow + controlled)", 5, cardio_weight=1),
]


def _targets_for(difficulty: int, rng: random.Random) -> dict:
    """
    Returns targets tuned for "only daily exercisers can do it".
    Still achievable with effort, but not beginner-easy.
    """
    # Base ranges by difficulty.
    rep_ranges = {
        3: (70, 140),
        4: (80, 180),
        5: (40, 120),  # for hard moves like burpees/hollow: reps are lower
    }
    minute_ranges = {
        3: (3.0, 6.0),
        4: (4.0, 8.0),
        5: (4.0, 10.0),
    }
    meter_ranges = {
        3: (120, 250),
        4: (160, 320),
        5: (200, 450),
    }

    reps_lo, reps_hi = rep_ranges.get(difficulty, (60, 120))
    minutes_lo, minutes_hi = minute_ranges.get(difficulty, (3.0, 7.0))
    meters_lo, meters_hi = meter_ranges.get(difficulty, (120, 300))

    reps = int(rng.randint(reps_lo, reps_hi) // 5 * 5)  # round to 5s
    minutes = round(rng.uniform(minutes_lo, minutes_hi) * 2) / 2  # to 0.5
    meters = int(rng.randint(meters_lo, meters_hi) // 10 * 10)
    return {"reps": reps, "minutes": minutes, "meters": meters}


def _coins_for(difficulty: int) -> int:
    # Reward daily effort; harder tasks give more.
    return {3: 14, 4: 18, 5: 24}.get(int(difficulty or 3), 14)


def generate_week(seed_date: datetime.date | None = None, per_day: int = 7) -> list[dict]:
    """
    Generates a full week's worth of DailyChallenge rows (Mon..Sun).
    Deterministic per day based on date seed, so it feels "AI generated"
    but is stable if regenerated on a fresh database.
    """
    if seed_date is None:
        seed_date = timezone.localdate()

    # Use ISO year/week to keep week-consistency.
    iso_year, iso_week, _ = seed_date.isocalendar()

    results: list[dict] = []
    for day_idx in range(7):
        day_seed = int(f"{iso_year}{iso_week:02d}{day_idx}")
        rng = random.Random(day_seed)

        # Pick a varied set: bias toward difficulty 4/5, ensure at least one cardio-ish.
        pool = IDEAS[:]
        rng.shuffle(pool)

        chosen: list[ChallengeIdea] = []
        cardio_picked = 0
        for idea in pool:
            if len(chosen) >= per_day:
                break
            if idea in chosen:
                continue
            # small preference for harder ideas
            if idea.difficulty <= 3 and rng.random() < 0.35:
                continue
            if idea.cardio_weight > 0 and cardio_picked < 1:
                chosen.append(idea)
                cardio_picked += 1
                continue
            if rng.random() < 0.85:
                chosen.append(idea)

        # If we still don't have enough, fill from start.
        if len(chosen) < per_day:
            for idea in pool:
                if len(chosen) >= per_day:
                    break
                if idea not in chosen:
                    chosen.append(idea)

        # Build row dicts.
        for idea in chosen[:per_day]:
            targets = _targets_for(idea.difficulty, rng)
            instruction = idea.instruction_template.format(**targets)
            results.append({
                "day_of_week": day_idx,
                "title": idea.title,
                "instruction": instruction[:255],
                "coins_reward": _coins_for(idea.difficulty),
                "is_active": True,
            })

    return results


def ensure_active_challenges(min_per_day: int = 7) -> int:
    """
    Ensures the database has a reasonable set of active challenges.
    Returns number of challenges created.
    """
    created = 0

    # If completely empty (common when switching PCs / new DB), generate everything.
    if not DailyChallenge.objects.filter(is_active=True).exists():
        rows = generate_week(per_day=min_per_day)
        DailyChallenge.objects.bulk_create([DailyChallenge(**r) for r in rows])
        return len(rows)

    # Otherwise, top up days that are missing or underfilled.
    existing_counts = (
        DailyChallenge.objects
        .filter(is_active=True)
        .values("day_of_week")
        .order_by("day_of_week")
    )
    counts = {d: 0 for d in range(7)}
    for row in existing_counts:
        counts[int(row["day_of_week"])] = counts.get(int(row["day_of_week"]), 0) + 1

    # If the counts query above didn't aggregate (values only), do a real count per day.
    for d in range(7):
        counts[d] = DailyChallenge.objects.filter(is_active=True, day_of_week=d).count()

    if all(v >= min_per_day for v in counts.values()):
        return 0

    generated = generate_week(per_day=min_per_day)
    to_create: list[DailyChallenge] = []
    for d in range(7):
        need = max(0, min_per_day - counts.get(d, 0))
        if need <= 0:
            continue
        candidates = [r for r in generated if r["day_of_week"] == d]
        # Avoid exact duplicates by title within day.
        existing_titles = set(
            DailyChallenge.objects.filter(is_active=True, day_of_week=d).values_list("title", flat=True)
        )
        for r in candidates:
            if need <= 0:
                break
            if r["title"] in existing_titles:
                continue
            to_create.append(DailyChallenge(**r))
            existing_titles.add(r["title"])
            need -= 1

    if to_create:
        DailyChallenge.objects.bulk_create(to_create)
        created = len(to_create)
    return created

