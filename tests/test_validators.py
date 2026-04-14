from utils.validators import normalize_units, validate_country_code


def test_normalize_units_metric():
    assert normalize_units("metric") == "metric"


def test_normalize_units_imperial():
    assert normalize_units("imperial") == "imperial"


def test_normalize_units_invalid_defaults_to_metric():
    assert normalize_units("kelvin") == "metric"
    assert normalize_units(None) == "metric"


def test_validate_country_code_accepts_blank():
    assert validate_country_code("") is True


def test_validate_country_code_accepts_two_letters():
    assert validate_country_code("US") is True
    assert validate_country_code("np") is True


def test_validate_country_code_rejects_non_alpha():
    assert validate_country_code("U1") is False
    assert validate_country_code("9$") is False


def test_validate_country_code_rejects_wrong_length():
    assert validate_country_code("USA") is False
    assert validate_country_code("U") is False