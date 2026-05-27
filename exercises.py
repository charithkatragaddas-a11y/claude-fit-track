EXERCISES = {
    # Chest
    "Bench Press":              {"primary": ["Chest"],           "secondary": ["Triceps", "Shoulders"]},
    "Incline Bench Press":      {"primary": ["Chest"],           "secondary": ["Triceps", "Shoulders"]},
    "Decline Bench Press":      {"primary": ["Chest"],           "secondary": ["Triceps"]},
    "Close Grip Bench Press":   {"primary": ["Triceps"],         "secondary": ["Chest"]},
    "Dumbbell Fly":             {"primary": ["Chest"],           "secondary": []},
    "Cable Fly":                {"primary": ["Chest"],           "secondary": []},
    "Push-up":                  {"primary": ["Chest"],           "secondary": ["Triceps", "Shoulders"]},
    "Diamond Push-up":          {"primary": ["Triceps"],         "secondary": ["Chest"]},
    "Chest Dip":                {"primary": ["Chest"],           "secondary": ["Triceps"]},

    # Back
    "Deadlift":                 {"primary": ["Back", "Hamstrings", "Glutes"], "secondary": ["Traps", "Core", "Quads"]},
    "Sumo Deadlift":            {"primary": ["Glutes", "Hamstrings"],         "secondary": ["Back", "Quads"]},
    "Bent Over Row":            {"primary": ["Back", "Lats"],   "secondary": ["Biceps", "Traps"]},
    "T-Bar Row":                {"primary": ["Back"],            "secondary": ["Biceps", "Traps"]},
    "Single Arm Row":           {"primary": ["Back", "Lats"],   "secondary": ["Biceps"]},
    "Seated Cable Row":         {"primary": ["Back", "Lats"],   "secondary": ["Biceps"]},
    "Lat Pulldown":             {"primary": ["Lats"],            "secondary": ["Biceps", "Back"]},
    "Pull-up":                  {"primary": ["Lats", "Back"],   "secondary": ["Biceps"]},
    "Chin-up":                  {"primary": ["Lats", "Back"],   "secondary": ["Biceps"]},
    "Face Pull":                {"primary": ["Traps", "Shoulders"], "secondary": []},
    "Reverse Fly":              {"primary": ["Shoulders", "Traps"], "secondary": []},

    # Shoulders
    "Overhead Press":           {"primary": ["Shoulders"],       "secondary": ["Triceps", "Traps"]},
    "Dumbbell Shoulder Press":  {"primary": ["Shoulders"],       "secondary": ["Triceps"]},
    "Arnold Press":             {"primary": ["Shoulders"],       "secondary": ["Triceps"]},
    "Lateral Raise":            {"primary": ["Shoulders"],       "secondary": []},
    "Front Raise":              {"primary": ["Shoulders"],       "secondary": []},
    "Upright Row":              {"primary": ["Shoulders", "Traps"], "secondary": ["Biceps"]},

    # Biceps
    "Barbell Curl":             {"primary": ["Biceps"],          "secondary": []},
    "Dumbbell Curl":            {"primary": ["Biceps"],          "secondary": []},
    "Hammer Curl":              {"primary": ["Biceps"],          "secondary": []},
    "Preacher Curl":            {"primary": ["Biceps"],          "secondary": []},
    "Cable Curl":               {"primary": ["Biceps"],          "secondary": []},
    "Concentration Curl":       {"primary": ["Biceps"],          "secondary": []},

    # Triceps
    "Tricep Pushdown":          {"primary": ["Triceps"],         "secondary": []},
    "Skull Crusher":            {"primary": ["Triceps"],         "secondary": []},
    "Overhead Tricep Extension":{"primary": ["Triceps"],         "secondary": []},
    "Dips":                     {"primary": ["Triceps", "Chest"],"secondary": ["Shoulders"]},

    # Legs — Quads
    "Squat":                    {"primary": ["Quads", "Glutes"], "secondary": ["Hamstrings", "Core"]},
    "Front Squat":              {"primary": ["Quads"],           "secondary": ["Glutes", "Core"]},
    "Hack Squat":               {"primary": ["Quads"],           "secondary": ["Glutes"]},
    "Leg Press":                {"primary": ["Quads", "Glutes"], "secondary": ["Hamstrings"]},
    "Leg Extension":            {"primary": ["Quads"],           "secondary": []},
    "Lunges":                   {"primary": ["Quads", "Glutes"], "secondary": ["Hamstrings"]},
    "Bulgarian Split Squat":    {"primary": ["Quads", "Glutes"], "secondary": ["Hamstrings"]},
    "Step-up":                  {"primary": ["Quads", "Glutes"], "secondary": ["Hamstrings"]},

    # Legs — Hamstrings
    "Romanian Deadlift":        {"primary": ["Hamstrings", "Glutes"], "secondary": ["Back"]},
    "Leg Curl":                 {"primary": ["Hamstrings"],      "secondary": []},
    "Good Morning":             {"primary": ["Hamstrings"],      "secondary": ["Back"]},
    "Nordic Curl":              {"primary": ["Hamstrings"],      "secondary": []},
    "Glute Ham Raise":          {"primary": ["Hamstrings", "Glutes"], "secondary": []},

    # Legs — Glutes
    "Hip Thrust":               {"primary": ["Glutes"],          "secondary": ["Hamstrings"]},
    "Glute Bridge":             {"primary": ["Glutes"],          "secondary": ["Hamstrings"]},
    "Cable Kickback":           {"primary": ["Glutes"],          "secondary": []},
    "Sumo Squat":               {"primary": ["Glutes", "Quads"], "secondary": ["Hamstrings"]},

    # Calves
    "Standing Calf Raise":      {"primary": ["Calves"],          "secondary": []},
    "Seated Calf Raise":        {"primary": ["Calves"],          "secondary": []},

    # Full Body / Power
    "Power Clean":              {"primary": ["Back", "Shoulders", "Traps"], "secondary": ["Quads", "Hamstrings"]},
    "Kettlebell Swing":         {"primary": ["Glutes", "Hamstrings"],       "secondary": ["Core", "Back"]},
    "Thruster":                 {"primary": ["Quads", "Shoulders"],         "secondary": ["Glutes", "Triceps", "Core"]},
    "Clean and Press":          {"primary": ["Shoulders", "Back", "Quads"], "secondary": ["Traps", "Core"]},

    # Core
    "Plank":                    {"primary": ["Core"],            "secondary": []},
    "Side Plank":               {"primary": ["Core"],            "secondary": []},
    "Crunches":                 {"primary": ["Core"],            "secondary": []},
    "Leg Raise":                {"primary": ["Core"],            "secondary": []},
    "Hanging Leg Raise":        {"primary": ["Core"],            "secondary": []},
    "Russian Twist":            {"primary": ["Core"],            "secondary": []},
    "Ab Wheel":                 {"primary": ["Core"],            "secondary": []},
    "Cable Crunch":             {"primary": ["Core"],            "secondary": []},
    "Bicycle Crunch":           {"primary": ["Core"],            "secondary": []},
    "Woodchop":                 {"primary": ["Core"],            "secondary": ["Shoulders"]},
}

MUSCLE_GROUPS = [
    "Chest", "Back", "Lats", "Shoulders", "Traps",
    "Biceps", "Triceps", "Quads", "Hamstrings", "Glutes", "Calves", "Core",
]
