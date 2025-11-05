"""System prompt and schema definitions for workout generation."""

from typing import Dict


def calculate_zones(ftp: int) -> Dict[str, Dict[str, int]]:
    """Calculate power zones based on FTP."""
    z1max = round(ftp * 0.55)
    z2max = round(ftp * 0.75)
    z3max = round(ftp * 0.95)
    z4max = round(ftp * 1.05)
    z5max = round(ftp * 1.20)
    z6max = round(ftp * 1.50)

    return {
        "z1": {"min": 0, "max": z1max},
        "z2": {"min": z1max + 1, "max": z2max},
        "z3": {"min": z2max + 1, "max": z3max},
        "z4": {"min": z3max + 1, "max": z4max},
        "z5": {"min": z4max + 1, "max": z5max},
        "z6": {"min": z5max + 1, "max": z6max},
        "z7": {"min": z6max + 1, "max": float("inf")},
    }


def build_system_prompt_generate(ftp: int) -> str:
    """Build the system prompt for workout generation."""
    zones = calculate_zones(ftp)

    zone_table = (
        "\n".join(
            [
                f"  {zones[z]['min']:3d}-{zones[z]['max']:3d}W → zone {i}"
                for i, z in enumerate(
                    ["z1", "z2", "z3", "z4", "z5", "z6"], 1
                )
            ]
        )
        + f"\n  {zones['z7']['min']:3d}+W → zone 7"
    )

    return f"""You are a cycling coach creating structured cycling workouts.

FTP: {ftp}W
POWER ZONES:
{zone_table}

OUTPUT RULES:
- Return ONLY valid JSON matching the schema
- No extra text, explanations, or markdown
- type field MUST be one of: active, rest, warmup, cooldown, recovery, interval, other

FIELD REQUIREMENTS:
- All times in seconds
- All power values in watts (whole numbers)
- segment_number: sequential starting at 1
- powerAdjustedUpward: power + 10
- powerAdjustedDownward: max(0, power - 10)
- perc_ftp: round((power/{ftp}) * 100)
- zone: Lookup power in table above
- workout_duration: Must equal endTimeSeconds of last interval

SPECIAL WORKOUT FORMATS:
When the user mentions these workout names/formats, use these standard structures.
All percentages are relative to FTP={ftp}W. Adjust durations if user specifies otherwise.

1. TABATA
   Structure: 10x (40sec @ 120%+ FTP / 20sec @ 50% FTP)
   Total: 10 minutes of work

2. BILLAT 30-30
   Structure: 10x (30sec @ 150% FTP / 30sec @ 50% FTP)

3. OVER-UNDERS
   Structure: 3-4x [8-12min alternating (2-3min @ 105% FTP / 2-3min @ 95% FTP)] / 5min recovery

4. RONNESTAD
   Structure: 13x (30sec @ 125% FTP / 15sec @ 50% FTP)

5. FARTLEK
   Structure: 30-60min with random surges of varying duration (30sec-3min) and intensity (85-150% FTP)

6. PYRAMID
   Structure: Ascending then descending durations at same intensity
   Example: 1-2-3-4-3-2-1 min @ 95-105% FTP 

7. 4x4 NORWEGIAN METHOD
   Structure: 4x (4min @ 112% FTP / 3min recovery @ 60% FTP)

8. GIMENEZ INTERVALS
   Structure: 3-4 sets of [(3min @ 120% FTP / 3min @ 60% FTP) x 3 reps] / 5min between sets

9. SEILER 4x8 or 4x16
   Structure: 4x (8min @ 95-100% FTP / 2min recovery) OR 4x (16min @ 90-95% FTP / 2min recovery)

10. HOUR OF POWER
   Structure: 60 min continuous at ~95–100% FTP with 10–15 second bursts every 2–3 minutes at 110–120% FTP

APPLYING SPECIAL WORKOUT FORMATS:
- If user mentions format name: Apply the structure above
- If user requests modifications (e.g., "longer Tabata"): Adapt the structure while keeping the format's core characteristics

OTHER WORKOUT RELATED INSTRUCTIONS:
- When the user describes a ramp (e.g., “make a ramp of 10 minutes starting at 50% FTP to 100% FTP”), interpret it as a continuous power block that linearly increases or decreases from the starting intensity to the ending intensity over the specified duration. Create then a series of intervals that gradually increase or decrease power in a structured way, ensuring each interval has a clear start and end time.
- When a user refers to a "free ride" create a some intervals fluctuating between 55-75% FTP for the specified duration. Total duration of those intervals should match the user's requested free ride duration.

WORKOUT DESIGN:
- Ensure smooth transitions between intervals
- Include warmup/cooldown for hard sessions
- Minimum interval length: 5 seconds
- Be literal and structured"""


# JSON Schema for structured output
WORKOUT_JSON_SCHEMA = {
    "name": "workout_response",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "description": {"type": "string"},
            "workout_duration": {"type": "integer"},
            "intervals": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "segment_number": {"type": "integer"},
                        "startTimeSeconds": {"type": "integer"},
                        "endTimeSeconds": {"type": "integer"},
                        "power": {"type": "integer"},
                        "powerAdjustedUpward": {"type": "integer"},
                        "powerAdjustedDownward": {"type": "integer"},
                        "zone": {"type": "integer"},
                        "perc_ftp": {"type": "integer"},
                        "type": {
                            "type": "string",
                            "enum": [
                                "active",
                                "rest",
                                "warmup",
                                "cooldown",
                                "recovery",
                                "interval",
                                "other",
                            ],
                        },
                        "notes": {"type": "string"},
                    },
                    "required": [
                        "segment_number",
                        "startTimeSeconds",
                        "endTimeSeconds",
                        "power",
                        "powerAdjustedUpward",
                        "powerAdjustedDownward",
                        "zone",
                        "perc_ftp",
                        "type",
                        "notes",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": [
            "name",
            "description",
            "workout_duration",
            "intervals",
        ],
        "additionalProperties": False,
    },
}

# Pydantic schema for Gemini
GEMINI_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "workout_duration": {"type": "integer"},
        "intervals": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "segment_number": {"type": "integer"},
                    "startTimeSeconds": {"type": "integer"},
                    "endTimeSeconds": {"type": "integer"},
                    "power": {"type": "integer"},
                    "powerAdjustedUpward": {"type": "integer"},
                    "powerAdjustedDownward": {"type": "integer"},
                    "zone": {"type": "integer"},
                    "perc_ftp": {"type": "integer"},
                    "type": {
                        "type": "string",
                        "enum": [
                            "active",
                            "rest",
                            "warmup",
                            "cooldown",
                            "recovery",
                            "interval",
                            "other",
                        ],
                    },
                    "notes": {"type": "string"},
                },
                "required": [
                    "segment_number",
                    "startTimeSeconds",
                    "endTimeSeconds",
                    "power",
                    "powerAdjustedUpward",
                    "powerAdjustedDownward",
                    "zone",
                    "perc_ftp",
                    "type",
                    "notes",
                ],
            },
        },
    },
    "required": [
        "name",
        "description",
        "workout_duration",
        "intervals",
    ],
}


# """
# System prompt and schema definitions for workout generation.
# """

# from typing import Dict


# def calculate_zones(ftp: int) -> Dict[str, Dict[str, int]]:
#     """Calculate power zones based on FTP."""
#     z1max = round(ftp * 0.55)
#     z2max = round(ftp * 0.75)
#     z3max = round(ftp * 0.95)
#     z4max = round(ftp * 1.05)
#     z5max = round(ftp * 1.20)
#     z6max = round(ftp * 1.50)

#     return {
#         "z1": {"min": 0, "max": z1max},
#         "z2": {"min": z1max + 1, "max": z2max},
#         "z3": {"min": z2max + 1, "max": z3max},
#         "z4": {"min": z3max + 1, "max": z4max},
#         "z5": {"min": z4max + 1, "max": z5max},
#         "z6": {"min": z5max + 1, "max": z6max},
#         "z7": {"min": z6max + 1, "max": float("inf")},
#     }


# def build_system_prompt_generate(ftp: int) -> str:
#     """Build the system prompt for workout generation."""
#     zones = calculate_zones(ftp)

#     # Build explicit zone lookup table
#     zone_lookup = f"""
# CRITICAL - POWER ZONE ASSIGNMENT:
# For FTP = {ftp}W, use this EXACT lookup table to assign zones.
# Compare your calculated power value to these ranges:

# Power Range (Watts) → Zone Number:
#   {zones["z1"]["min"]:3d} - {zones["z1"]["max"]:3d} W  →  zone: 1  (Active Recovery)
#   {zones["z2"]["min"]:3d} - {zones["z2"]["max"]:3d} W  →  zone: 2  (Endurance)
#   {zones["z3"]["min"]:3d} - {zones["z3"]["max"]:3d} W  →  zone: 3  (Tempo)
#   {zones["z4"]["min"]:3d} - {zones["z4"]["max"]:3d} W  →  zone: 4  (Threshold)
#   {zones["z5"]["min"]:3d} - {zones["z5"]["max"]:3d} W  →  zone: 5  (VO2 Max)
#   {zones["z6"]["min"]:3d} - {zones["z6"]["max"]:3d} W  →  zone: 6  (Anaerobic Capacity)
#   {zones["z7"]["min"]:3d}+ W        →  zone: 7  (Neuromuscular)

# ZONE ASSIGNMENT PROCESS (follow these steps exactly):
# 1. Calculate power in watts from the user's percentage or wattage request
# 2. Look up the calculated power in the table above
# 3. Assign the zone where power falls within [min, max] range
# 4. DO NOT guess zones based on training terminology (e.g., "tempo", "threshold")
# 5. Use the EXACT power value to determine zone - not the intended training effect

# EXAMPLES for FTP={ftp}W:
#   - 162W: Compare to ranges → falls in {zones["z2"]["min"]}-{zones["z2"]["max"]}W → zone: 2
#   - 175W: Compare to ranges → falls in {zones["z2"]["min"]}-{zones["z2"]["max"]}W → zone: 2
#   - 238W: Compare to ranges → falls in {zones["z3"]["min"]}-{zones["z3"]["max"]}W → zone: 3
#   - 225W: Compare to ranges → falls in {zones["z3"]["min"]}-{zones["z3"]["max"]}W → zone: 3
#   - 263W: Compare to ranges → falls in {zones["z5"]["min"]}-{zones["z5"]["max"]}W → zone: 5
#   - 275W: Compare to ranges → falls in {zones["z5"]["min"]}-{zones["z5"]["max"]}W → zone: 5
# """

#     return f"""
# You are an expert cycling coach specializing in creating structured workouts. Your task is to generate a structured cycling workout based on the user's description. The user's FTP is {ftp} watts.

# IMPORTANT INSTRUCTIONS:
# 1. Output ONLY valid JSON matching the required schema.
# 2. Do not include any explanations, comments, or extra text.
# 3. The output MUST be fully valid and parseable JSON.

# {zone_lookup}

# Output a valid JSON object that EXACTLY matches the structure below:
# - "name": A short workout name.
# - "description": A short explanation of the workout and its benefits.
# - "workout_duration": Total workout duration in seconds. field MUST equal the endTimeSeconds of the LAST interval.
# - "intervals": An array of workout intervals, each containing:
#   - "segment_number": (integer) The segment number of the interval. Should start at 1 and increment sequentially
#   - "startTimeSeconds": (seconds) Start time of the interval.
#   - "endTimeSeconds": (seconds) End time of the interval.
#   - "power": (watts) The power target.
#   - "powerAdjustedUpward": (watts) target +10W.
#   - "powerAdjustedDownward": (watts) target -10W (or 0 if <10W).
#   - "zone": Power zone (1–7) - MUST use lookup table above.
#   - "perc_ftp": (percentage) power target as a percentage of {ftp}. No decimals.
#   - "type": One of: "active", "rest", "warmup", "cooldown", "recovery", "interval", "other".
#   - "notes": Optional description.

# STRICT FIELD RULES FOR "type":
# - The "type" field is a strict enum and MUST be one of: "active", "rest", "warmup", "cooldown", "recovery", "interval", "other".
# - Never invent new values like "tempo", "sweet spot", "threshold", "vo2", etc. Those are training styles, not types.
# - Map training styles to valid types:
#   - Work/instruction segments (e.g., tempo, threshold, VO2, sweet spot) -> "interval"
#   - Very easy pedaling -> "recovery" (or "rest" if it's a complete rest block)
#   - Warm-up segments -> "warmup"
#   - Cool-down segments -> "cooldown"
#   - Otherwise -> "other"
# - Reflect the training style in "notes", "description", and appropriate "zone" instead of misusing "type".

# Conversion rules:
# 1. FTP = {ftp} watts. Convert all percentages to absolute values.
# 2. Time must always be in seconds.
# 3. Ensure smooth, complete transitions with no missing intervals.
# 4. Power must be a whole number (no decimals).
# 5. Use the POWER ZONE ASSIGNMENT table above - do not calculate zones yourself.
# 6. Stay literal, structured, and strictly within the schema. Do NOT add commentary, headings, or additional fields.
# 7. Don't use duration of the workout in the workout name.
# 8. An interval segment must be at least 5 seconds long.
# 9. Output must strictly follow the defined schema. Ensure the final JSON is syntactically valid and matches all field constraints exactly.
# 10. When a user wants a warmup ramp up, create a series of intervals that gradually increase power in a structured way, ensuring each interval has a clear start and end time. If not specified, assume a linear ramp up over the specified duration and start with 60% of FTP, increasing by 5% each interval until reaching the target power.
# """


# # JSON Schema for structured output (OpenAI format)
# WORKOUT_JSON_SCHEMA = {
#     "name": "workout_response",
#     "strict": True,
#     "schema": {
#         "type": "object",
#         "properties": {
#             "name": {"type": "string"},
#             "description": {"type": "string"},
#             "workout_duration": {"type": "integer"},
#             "intervals": {
#                 "type": "array",
#                 "items": {
#                     "type": "object",
#                     "properties": {
#                         "segment_number": {"type": "integer"},
#                         "startTimeSeconds": {"type": "integer"},
#                         "endTimeSeconds": {"type": "integer"},
#                         "power": {"type": "integer"},
#                         "powerAdjustedUpward": {"type": "integer"},
#                         "powerAdjustedDownward": {"type": "integer"},
#                         "zone": {"type": "integer"},
#                         "perc_ftp": {"type": "integer"},
#                         "type": {
#                             "type": "string",
#                             "enum": [
#                                 "active",
#                                 "rest",
#                                 "warmup",
#                                 "cooldown",
#                                 "recovery",
#                                 "interval",
#                                 "other",
#                             ],
#                         },
#                         "notes": {"type": "string"},
#                     },
#                     "required": [
#                         "segment_number",
#                         "startTimeSeconds",
#                         "endTimeSeconds",
#                         "power",
#                         "powerAdjustedUpward",
#                         "powerAdjustedDownward",
#                         "zone",
#                         "perc_ftp",
#                         "type",
#                         "notes",
#                     ],
#                     "additionalProperties": False,
#                 },
#             },
#         },
#         "required": [
#             "name",
#             "description",
#             "workout_duration",
#             "intervals",
#         ],
#         "additionalProperties": False,
#     },
# }


# # Pydantic schema for Gemini (uses similar structure)
# GEMINI_SCHEMA = {
#     "type": "object",
#     "properties": {
#         "name": {"type": "string"},
#         "description": {"type": "string"},
#         "workout_duration": {"type": "integer"},
#         "intervals": {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "segment_number": {"type": "integer"},
#                     "startTimeSeconds": {"type": "integer"},
#                     "endTimeSeconds": {"type": "integer"},
#                     "power": {"type": "integer"},
#                     "powerAdjustedUpward": {"type": "integer"},
#                     "powerAdjustedDownward": {"type": "integer"},
#                     "zone": {"type": "integer"},
#                     "perc_ftp": {"type": "integer"},
#                     "type": {
#                         "type": "string",
#                         "enum": [
#                             "active",
#                             "rest",
#                             "warmup",
#                             "cooldown",
#                             "recovery",
#                             "interval",
#                             "other",
#                         ],
#                     },
#                     "notes": {"type": "string"},
#                 },
#                 "required": [
#                     "segment_number",
#                     "startTimeSeconds",
#                     "endTimeSeconds",
#                     "power",
#                     "powerAdjustedUpward",
#                     "powerAdjustedDownward",
#                     "zone",
#                     "perc_ftp",
#                     "type",
#                     "notes",
#                 ],
#             },
#         },
#     },
#     "required": [
#         "name",
#         "description",
#         "workout_duration",
#         "intervals",
#     ],
# }


# 2. Ramp Segments
# When a segment shows progression or decrease "from X% to Y% FTP" or diagonal lines on graphs:
# Split into equal sub-segments with discrete power values
# For ramps ≤5 minutes: use 1-minute sub-segments
# For ramps 5-10 minutes: use 1-2 minute sub-segments
# For ramps >10 minutes: use 2-minute sub-segments
# Minimum sub-segment duration: 30 seconds
# Calculate linear progression: power_at_time = start_power + ((end_power - start_power) × (time_elapsed / total_duration))
# Round each sub-segment's power to nearest watt
