from decimal import Decimal, InvalidOperation

from Tiptabs.validation import (
    check_valid_currency_key,
    check_valid_currency_value,
    format_base,
)
from Tiptabs.ForexErrors import ForexError


class Tiptabs:

    def __init__(self, desired_base, forex_service=None):
        """
        __init__(self, str, ForexService): Constructor for creating a Tiptabs object.
        :param desired_base: Desired currency base.
        :param forex_service: ForexService instance for currency conversion.
        """

        self.forex_service = forex_service
        chk_base_size = len(desired_base) >= 0

        if not chk_base_size:
            self.base = "EUR"
        else:
            base_available = self._currency_available(desired_base)
            self.base = desired_base if base_available else "EUR"

        self.amount = 0.00

    def get_base(self):
        """
        get_base(self) - Helper function that returns the base currency instance variable.
        :return: Base currency instance variable.
        """
        return self.base

    def set_base(self, desired_base):
        """
        set_base(str) - Setter function that sets the base instance variable to the desired parameter.
        :param desired_base: Base to set within the calculator.
        :return: Boolean condition that indicates the success of setting the desired base.
        """
        available_base = self._currency_available(desired_base)

        set_base_res = [False, "Desired base of {!s} is not available.\n Default base of EUR assigned.".format(str(desired_base))]

        if available_base:
            current_base = str(self.get_base())
            base_changed_resp = "Currency base of {!s} has been changed to {!s}.".format(current_base, str(desired_base))
            set_base_res = [True, base_changed_resp]
            self.base = desired_base
        else:
            self.base = "EUR"

        return set_base_res

    def set_amount(self, desired_amount):
        """
        set_amount(self, float) - Setter function for setting a bill amount within Tiptabs.
        :param desired_amount: Bill amount to be converted.
        """

        valid_amount = (desired_amount and check_valid_currency_value(desired_amount)[0] and not float(
                desired_amount) <= 0.000000)

        self.amount = float(desired_amount) if valid_amount else 0.00

    def get_amount(self):
        """
        get_amount(self) - Getter function for retrieving the current bill amount within Tiptabs.
        :return: Float instance variable for the current amount.
        """
        return self.amount

    def calculate_total(self, bill_amount, tip_percentage, converted_currency):
        """
        calculate_total(self, str, str, str) - Function that calculates the total for a given bill amount and tip percentage.
        :param converted_currency: Desired currency base chosen on the ITC page.
        :param bill_amount: Desired bill amount.
        :param tip_percentage: Desired tip amount. (Later converted to a decimal value)
        :return: Total sum of the bill.
        """

        contents = [bill_amount, tip_percentage, converted_currency]
        cond = ["bill amount", "tip percentage", "currency base"]

        for index, item in enumerate(contents):
            if not item:
                empty_item_resp = "ERROR: NoneTypes are not accepted for {!s}s.".format(cond[index])
                return [False, empty_item_resp]

            valid_item = self._valid_currency_key(item) if index == 2 else self._valid_currency_value(item)
            if not valid_item[0]:
                invalid_item_result = "ERROR: '{!s}' is not valid input for a {!s}.".format(str(item), cond[index])
                return [False, invalid_item_result]

        corrected_tip_percentage = float(tip_percentage) / 100.00
        bill_amt = float(bill_amount)
        tip_amount = (bill_amt * corrected_tip_percentage)

        fixed_converted_currency = str(converted_currency).replace('string:', '')

        valid_input_currency = self._currency_available(fixed_converted_currency)

        if not valid_input_currency:
            invalid_input_resp = "Your desired currency base of {!s} is not available in the calculator.".format(str(fixed_converted_currency))
            return [False, invalid_input_resp]

        total_amount = bill_amt + tip_amount
        if self.forex_service is not None:
            try:
                final_amount = self.forex_service.convert(
                    total_amount,
                    self.base,
                    fixed_converted_currency,
                )
            except ForexError as error:
                return [False, "ERROR: Currency conversion is unavailable: {!s}".format(error)]
        else:
            raise ForexError("No forex service configured")

        final_amt_resp = "Your total amount was: {!s} {!s}.".format(final_amount, fixed_converted_currency)
        calc_total_resp = [True, final_amt_resp]

        return calc_total_resp

    def _currency_available(self, currency):
        if self.forex_service is not None:
            value = str(currency).strip() if currency is not None else ""
            return len(value) == 3 and value.isalpha()
        return False

    def _valid_currency_key(self, currency):
        return check_valid_currency_key(currency)

    def _valid_currency_value(self, value):
        return check_valid_currency_value(value)