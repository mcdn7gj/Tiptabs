import re
from decimal import Decimal, InvalidOperation

CURRENCY_CODE_PATTERN = re.compile(r'^[A-Z]{3}$', re.IGNORECASE)
CURRENCY_VALUE_PATTERN = re.compile(r'^\d*(\.\d+)?$')


def check_valid_currency_key(currency_key: str) -> list:
    """Validate a currency key against ISO 3-letter format."""
    if currency_key is None:
        return [False, "None values are not permitted as input."]

    stripped = str(currency_key).strip()
    if len(stripped) == 0:
        return [False, "Empty keys are not permitted as input."]

    valid_key_input = CURRENCY_CODE_PATTERN.match(stripped)

    if valid_key_input is None:
        invalid_key_input = "Invalid input: '{!s}' is not permitted as a base key.".format(stripped)
        return [False, invalid_key_input]

    valid_currency_key_resp = "Provided key: '{!s}' is valid.".format(stripped)
    return [True, valid_currency_key_resp]


def check_valid_currency_value(currency_value) -> list:
    """Validate a currency value is a positive number."""
    funct_name = "check_valid_currency_value()"

    if currency_value is None:
        none_currency_input_resp = "ERROR: None values are not permitted as input into function: {!s}.".format(funct_name)
        return [False, none_currency_input_resp]

    stripped = str(currency_value).strip()
    if len(stripped) == 0:
        return [False, "ERROR: Empty strings are not permitted as input."]

    valid_currency_value = CURRENCY_VALUE_PATTERN.match(stripped)

    if valid_currency_value is None:
        failed_value_regex = "Invalid input: '{!s}' is not permitted as a currency value.".format(stripped)
        return [False, failed_value_regex]

    valid_currency_value_resp = "Provided currency value: '{!s}' is valid.".format(stripped)
    return [True, valid_currency_value_resp]


def format_base(base: str) -> list:
    """Format and validate a base currency."""
    base_str = str(base).strip()
    
    # Check if it's numeric (int or float representation) BEFORE validating as currency key
    if base_str.replace('.', '', 1).isdigit():
        format_base_resp = "ERROR: Invalid base value! '{!s}' cannot contain numeric characters.".format(base_str)
        return [False, format_base_resp]

    valid_base_resp = check_valid_currency_key(base)

    if not valid_base_resp[0]:
        return valid_base_resp

    return [True, base_str.upper()]


def format_currency(currency: str) -> list:
    """Format and validate a currency value."""
    if currency is None:
        return [False, "ERROR: None values are not permitted as input into function: format_currency()."]

    currency_str = str(currency).strip()
    if len(currency_str) == 0:
        return [False, "ERROR: Empty strings are not permitted as input."]

    # Check if it's alphabetic BEFORE validating as currency value
    if currency_str.isalpha():
        format_currency_resp = "ERROR: Invalid currency value! '{!s}' cannot contain alphanumeric characters.".format(currency_str)
        return [False, format_currency_resp]

    valid_currency_resp = check_valid_currency_value(currency)

    if not valid_currency_resp[0]:
        return valid_currency_resp

    return [True, round(float(currency_str), 6)]


def check_available_bases(currency: str, currencies_dict: dict) -> bool:
    """Check if a currency exists in the provided dictionary."""
    if currency is None:
        return False
    formatted_base = format_base(str(currency))
    if not formatted_base[0]:
        return False
    return formatted_base[1] in currencies_dict.keys()