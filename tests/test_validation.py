import unittest
from Tiptabs.validation import (
    check_valid_currency_key,
    check_valid_currency_value,
    format_base,
    format_currency,
    check_available_bases,
)


class ValidationTests(unittest.TestCase):
    def test_check_valid_currency_key_valid(self):
        result = check_valid_currency_key("USD")
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], "Provided key: 'USD' is valid.")

    def test_check_valid_currency_key_lowercase(self):
        result = check_valid_currency_key("eur")
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], "Provided key: 'eur' is valid.")

    def test_check_valid_currency_key_with_spaces(self):
        result = check_valid_currency_key("  JPY  ")
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], "Provided key: 'JPY' is valid.")

    def test_check_valid_currency_key_none(self):
        result = check_valid_currency_key(None)
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "None values are not permitted as input.")

    def test_check_valid_currency_key_empty(self):
        result = check_valid_currency_key("")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Empty keys are not permitted as input.")

    def test_check_valid_currency_key_too_short(self):
        result = check_valid_currency_key("US")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Invalid input: 'US' is not permitted as a base key.")

    def test_check_valid_currency_key_too_long(self):
        result = check_valid_currency_key("EURO")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Invalid input: 'EURO' is not permitted as a base key.")

    def test_check_valid_currency_key_numeric(self):
        result = check_valid_currency_key("123")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Invalid input: '123' is not permitted as a base key.")

    def test_check_valid_currency_key_special_chars(self):
        result = check_valid_currency_key("US!")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Invalid input: 'US!' is not permitted as a base key.")

    def test_check_valid_currency_value_valid(self):
        result = check_valid_currency_value("10.221")
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], "Provided currency value: '10.221' is valid.")

    def test_check_valid_currency_value_integer(self):
        result = check_valid_currency_value("100")
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], "Provided currency value: '100' is valid.")

    def test_check_valid_currency_value_zero(self):
        result = check_valid_currency_value("0")
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], "Provided currency value: '0' is valid.")

    def test_check_valid_currency_value_decimal_string(self):
        result = check_valid_currency_value("1.0")
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], "Provided currency value: '1.0' is valid.")

    def test_check_valid_currency_value_none(self):
        result = check_valid_currency_value(None)
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "ERROR: None values are not permitted as input into function: check_valid_currency_value().")

    def test_check_valid_currency_value_empty(self):
        result = check_valid_currency_value("")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "ERROR: Empty strings are not permitted as input.")

    def test_check_valid_currency_value_negative(self):
        result = check_valid_currency_value("-10.5")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Invalid input: '-10.5' is not permitted as a currency value.")

    def test_check_valid_currency_value_alpha(self):
        result = check_valid_currency_value("USD")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Invalid input: 'USD' is not permitted as a currency value.")

    def test_check_valid_currency_value_special_chars(self):
        result = check_valid_currency_value("!@#$")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Invalid input: '!@#$' is not permitted as a currency value.")

    def test_format_base_valid(self):
        result = format_base("JPY")
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], "JPY")

    def test_format_base_lowercase(self):
        result = format_base("usd")
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], "USD")

    def test_format_base_with_spaces(self):
        result = format_base("  EUR  ")
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], "EUR")

    def test_format_base_none(self):
        result = format_base(None)
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "None values are not permitted as input.")

    def test_format_base_empty(self):
        result = format_base("")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Empty keys are not permitted as input.")

    def test_format_base_numeric_string(self):
        result = format_base("123")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "ERROR: Invalid base value! '123' cannot contain numeric characters.")

    def test_format_base_integer(self):
        result = format_base(1)
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "ERROR: Invalid base value! '1' cannot contain numeric characters.")

    def test_format_base_float(self):
        result = format_base(1.002)
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "ERROR: Invalid base value! '1.002' cannot contain numeric characters.")

    def test_format_currency_valid(self):
        result = format_currency("6.2125")
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], 6.2125)

    def test_format_currency_float_string(self):
        result = format_currency("1.0")
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], 1.0)

    def test_format_currency_integer_string(self):
        result = format_currency("100")
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], 100.0)

    def test_format_currency_none(self):
        result = format_currency(None)
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "ERROR: None values are not permitted as input into function: format_currency().")

    def test_format_currency_empty(self):
        result = format_currency("")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "ERROR: Empty strings are not permitted as input.")

    def test_format_currency_negative(self):
        result = format_currency("-2.0012")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Invalid input: '-2.0012' is not permitted as a currency value.")

    def test_format_currency_alpha(self):
        result = format_currency("USD")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "ERROR: Invalid currency value! 'USD' cannot contain alphanumeric characters.")

    def test_format_currency_special_chars(self):
        result = format_currency("!@#$%^&*()")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Invalid input: '!@#$%^&*()' is not permitted as a currency value.")

    def test_format_currency_rounds_to_6_places(self):
        result = format_currency("1.123456789")
        self.assertEqual(result[0], True)
        self.assertEqual(result[1], 1.123457)

    def test_check_available_bases_exists(self):
        currencies = {"EUR": 1.0, "USD": 1.1}
        self.assertTrue(check_available_bases("USD", currencies))

    def test_check_available_bases_case_insensitive(self):
        currencies = {"EUR": 1.0, "USD": 1.1}
        self.assertTrue(check_available_bases("usd", currencies))

    def test_check_available_bases_not_exists(self):
        currencies = {"EUR": 1.0, "USD": 1.1}
        self.assertFalse(check_available_bases("JPY", currencies))

    def test_check_available_bases_none(self):
        currencies = {"EUR": 1.0}
        self.assertFalse(check_available_bases(None, currencies))

    def test_check_available_bases_empty_dict(self):
        self.assertFalse(check_available_bases("EUR", {}))


if __name__ == "__main__":
    unittest.main()