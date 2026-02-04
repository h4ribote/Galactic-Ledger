# Game Design Data

BUILDINGS = {
    "IRON_MINE": {
        "name": "Iron Mine",
        "description": "Extracts iron ore from the planet.",
        "cost_credits": 100.0,
        "cost_items": {
            "Iron": 10
        },
        "build_time_seconds": 60,  # 1 minute
        "production": {
            "item_name": "Iron",
            "rate_per_minute": 5
        }
    },
    # Add more buildings here
    "SOLAR_PLANT": {
        "name": "Solar Plant",
        "description": "Generates energy (not implemented yet).",
        "cost_credits": 50.0,
        "cost_items": {
            "Iron": 5
        },
        "build_time_seconds": 30,
        "production": {}
    }
}
