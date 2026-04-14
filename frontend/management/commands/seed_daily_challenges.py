from django.core.management.base import BaseCommand
from frontend.models import DailyChallenge


class Command(BaseCommand):
    help = "Seed predefined DailyChallenge entries (safe to run multiple times)."

    def handle(self, *args, **options):
        predefined = [
            # Monday
            (0, "Push-ups", "Target: 50 reps", 15),
            (0, "Plank", "Target: 2 minutes", 12),
            (0, "Bodyweight Squats", "Target: 70 reps", 15),
            (0, "Jumping Jacks", "Target: 120 reps", 10),
            (0, "Mountain Climbers", "Target: 60 reps (30 each)", 12),
            (0, "Lunges", "Target: 40 reps (20 each)", 15),
            (0, "Wall Sit", "Target: 2 minutes", 12),
            # Tuesday
            (1, "Bodyweight Squats", "Target: 80 reps", 15),
            (1, "Push-ups", "Target: 55 reps", 15),
            (1, "Plank", "Target: 2 minutes", 12),
            (1, "High Knees", "Target: 80 reps (40 each)", 12),
            (1, "Glute Bridges", "Target: 60 reps", 12),
            (1, "Russian Twists", "Target: 60 reps (30 each)", 15),
            (1, "Jumping Jacks", "Target: 140 reps", 10),
            # Wednesday
            (2, "Burpees", "Target: 35 reps", 18),
            (2, "Wall Sit", "Target: 2 minutes", 12),
            (2, "Mountain Climbers", "Target: 70 reps (35 each)", 12),
            (2, "Lunges", "Target: 50 reps (25 each)", 15),
            (2, "Plank", "Target: 2 minutes", 12),
            (2, "Jumping Jacks", "Target: 160 reps", 10),
            (2, "Sit-ups", "Target: 60 reps", 15),
            # Thursday
            (3, "Jumping Jacks", "Target: 170 reps", 10),
            (3, "Lunges", "Target: 60 reps (30 each)", 15),
            (3, "Push-ups", "Target: 60 reps", 15),
            (3, "Plank", "Target: 2 minutes", 12),
            (3, "High Knees", "Target: 90 reps (45 each)", 12),
            (3, "Glute Bridges", "Target: 70 reps", 12),
            (3, "Wall Sit", "Target: 2 minutes", 12),
            # Friday
            (4, "Plank", "Target: 3 minutes (total time)", 18),
            (4, "High Knees", "Target: 100 reps (50 each)", 12),
            (4, "Burpees", "Target: 40 reps", 18),
            (4, "Push-ups", "Target: 65 reps", 15),
            (4, "Bodyweight Squats", "Target: 90 reps", 15),
            (4, "Russian Twists", "Target: 80 reps (40 each)", 15),
            (4, "Wall Sit", "Target: 2 minutes", 12),
            # Saturday
            (5, "Sit-ups", "Target: 100 reps", 20),
            (5, "Russian Twists", "Target: 90 reps (45 each)", 15),
            (5, "Bodyweight Squats", "Target: 100 reps", 15),
            (5, "Jumping Jacks", "Target: 200 reps", 10),
            (5, "Lunges", "Target: 70 reps (35 each)", 15),
            (5, "Plank", "Target: 3 minutes (total time)", 18),
            (5, "Glute Bridges", "Target: 90 reps", 12),
            # Sunday
            (6, "Active Recovery Walk", "Target: 15 minutes brisk walk", 10),
            (6, "Mobility Flow", "Target: 10 minutes full body mobility", 10),
            (6, "Stretching", "Target: 10 minutes full body stretch", 10),
            (6, "Plank", "Target: 2 minutes", 12),
            (6, "Jumping Jacks", "Target: 120 reps", 10),
            (6, "Bodyweight Squats", "Target: 70 reps", 15),
            (6, "Push-ups", "Target: 40 reps", 15),
        ]

        created = 0
        for day_idx, title, instruction, coins in predefined:
            obj, was_created = DailyChallenge.objects.get_or_create(
                day_of_week=day_idx,
                title=title,
                defaults={
                    "instruction": instruction,
                    "coins_reward": coins,
                    "is_active": True,
                },
            )
            if not was_created:
                # Keep existing admin edits, only fill missing instruction.
                changed = False
                if not obj.instruction and instruction:
                    obj.instruction = instruction
                    changed = True
                if obj.coins_reward == 0 and coins:
                    obj.coins_reward = coins
                    changed = True
                if changed:
                    obj.save(update_fields=["instruction", "coins_reward"])
            else:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Seed complete. Created {created} new challenges."))

