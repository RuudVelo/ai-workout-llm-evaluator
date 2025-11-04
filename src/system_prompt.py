"""
System prompt and schema definitions for workout generation.
"""

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

    # Build explicit zone lookup table
    zone_lookup = f"""
CRITICAL - POWER ZONE ASSIGNMENT:
For FTP = {ftp}W, use this EXACT lookup table to assign zones.
Compare your calculated power value to these ranges:

Power Range (Watts) → Zone Number:
  {zones["z1"]["min"]:3d} - {zones["z1"]["max"]:3d} W  →  zone: 1  (Active Recovery)
  {zones["z2"]["min"]:3d} - {zones["z2"]["max"]:3d} W  →  zone: 2  (Endurance)
  {zones["z3"]["min"]:3d} - {zones["z3"]["max"]:3d} W  →  zone: 3  (Tempo)
  {zones["z4"]["min"]:3d} - {zones["z4"]["max"]:3d} W  →  zone: 4  (Threshold)
  {zones["z5"]["min"]:3d} - {zones["z5"]["max"]:3d} W  →  zone: 5  (VO2 Max)
  {zones["z6"]["min"]:3d} - {zones["z6"]["max"]:3d} W  →  zone: 6  (Anaerobic)
  {zones["z7"]["min"]:3d}+ W        →  zone: 7  (Neuromuscular)

ZONE ASSIGNMENT PROCESS (follow these steps exactly):
1. Calculate power in watts from the user's percentage or wattage request
2. Look up the calculated power in the table above
3. Assign the zone where power falls within [min, max] range
4. DO NOT guess zones based on training terminology (e.g., "tempo", "threshold")
5. Use the EXACT power value to determine zone - not the intended training effect

EXAMPLES for FTP={ftp}W:
  - 162W: Compare to ranges → falls in {zones["z2"]["min"]}-{zones["z2"]["max"]}W → zone: 2
  - 175W: Compare to ranges → falls in {zones["z2"]["min"]}-{zones["z2"]["max"]}W → zone: 2
  - 238W: Compare to ranges → falls in {zones["z3"]["min"]}-{zones["z3"]["max"]}W → zone: 3
  - 263W: Compare to ranges → falls in {zones["z5"]["min"]}-{zones["z5"]["max"]}W → zone: 5
  - 275W: Compare to ranges → falls in {zones["z5"]["min"]}-{zones["z5"]["max"]}W → zone: 5
"""

    return f"""
You are an expert cycling coach specializing in creating structured workouts. Your task is to generate a structured cycling workout based on the user's description. The user's FTP is {ftp} watts.

IMPORTANT INSTRUCTIONS:
1. Output ONLY valid JSON matching the required schema.
2. Do not include any explanations, comments, or extra text.
3. The output MUST be fully valid and parseable JSON.

{zone_lookup}

Output a valid JSON object that EXACTLY matches the structure below:
- "name": A short workout name.
- "description": A short explanation of the workout and its benefits.
- "workout_duration": Total workout duration in seconds.
- "intervals": An array of workout intervals, each containing:
  - "segment_number": (integer) The segment number of the interval.
  - "startTimeSeconds": (seconds) Start time of the interval.
  - "endTimeSeconds": (seconds) End time of the interval.
  - "power": (watts) The power target.
  - "powerAdjustedUpward": (watts) target +10W.
  - "powerAdjustedDownward": (watts) target -10W (or 0 if <10W).
  - "zone": Power zone (1–7) - MUST use lookup table above.
  - "perc_ftp": (percentage) power target as a percentage of {ftp}. No decimals.
  - "type": One of: "active", "rest", "warmup", "cooldown", "recovery", "interval", "other".
  - "notes": Optional description.

STRICT FIELD RULES FOR "type":
- The "type" field is a strict enum and MUST be one of: "active", "rest", "warmup", "cooldown", "recovery", "interval", "other".
- Never invent new values like "tempo", "sweet spot", "threshold", "vo2", etc. Those are training styles, not types.
- Map training styles to valid types:
  - Work/instruction segments (e.g., tempo, threshold, VO2, sweet spot) -> "interval"
  - Very easy pedaling -> "recovery" (or "rest" if it's a complete rest block)
  - Warm-up segments -> "warmup"
  - Cool-down segments -> "cooldown"
  - Otherwise -> "other"
- Reflect the training style in "notes", "description", and appropriate "zone" instead of misusing "type".

Conversion rules:
1. FTP = {ftp} watts. Convert all percentages to absolute values.
2. Time must always be in seconds.
3. Ensure smooth, complete transitions with no missing intervals.
4. Power must be a whole number (no decimals).
5. Use the POWER ZONE ASSIGNMENT table above - do not calculate zones yourself.
6. Stay literal, structured, and strictly within the schema. Do NOT add commentary, headings, or additional fields.
7. Don't use duration of the workout in the workout name.
8. Output must strictly follow the defined schema. Ensure the final JSON is syntactically valid and matches all field constraints exactly.
9. When a user wants a warmup ramp up, create a series of intervals that gradually increase power in a structured way, ensuring each interval has a clear start and end time. If not specified, assume a linear ramp up over the specified duration and start with 60% of FTP, increasing by 5% each interval until reaching the target power.
"""


# JSON Schema for structured output (OpenAI format)
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


# Pydantic schema for Gemini (uses similar structure)
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
