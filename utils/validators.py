def normalize_units(units: str | None) -> str:
    if units in {"metric", "imperial"}:
        return units
    return "metric"


def validate_country_code(country: str) -> bool:
    if not country:
        return True
    return len(country) == 2 and country.isalpha()