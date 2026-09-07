import unittest
from Tiptabs.Tiptabs import Tiptabs
from Tiptabs.ForexCache import ForexCache
from Tiptabs.ForexService import ForexService
from tests.forex_fixtures import forex_rate


class TiptabsTests(unittest.TestCase):

    def setUp(self):
        cache = ForexCache()
        cache.put(forex_rate("EUR/USD", "1.10"))
        cache.put(forex_rate("EUR/JPY", "150.0"))
        self.service = ForexService(cache)
        self.app = Tiptabs("EUR", forex_service=self.service)

    def testGetBase(self):
        expected = "EUR"
        result = self.app.get_base()
        self.assertEqual(expected, result)

    def testSetBase_validBase_BoolReturn(self):
        result = self.app.set_base("USD")
        self.assertEqual(True, result[0])

    def testSetBase_validBase_GetBase(self):
        result = self.app.set_base("JPY")
        self.assertEqual("JPY", str(self.app.get_base()))

    def testSetBase_invalidBase(self):
        result = self.app.set_base("asdfasdf")
        self.assertEqual(False, result[0])

    def testSetBase_numericalBase(self):
        result = self.app.set_base(1.002)
        self.assertEqual(False, result[0])
        self.assertEqual("EUR", self.app.get_base())

    def testSetBase_numericalString(self):
        result = self.app.set_base("10.244")
        self.assertEqual(False, result[0])

    def testSetBase_None(self):
        result = self.app.set_base(None)
        self.assertEqual(False, result[0])
        self.assertEqual("EUR", self.app.get_base())

    def testSetBase_EmptyString(self):
        result = self.app.set_base("")
        self.assertEqual(False, result[0])
        self.assertEqual("EUR", self.app.get_base())

    def testSetAmount(self):
        self.app.set_amount(10.00)
        self.assertEqual(10.00, self.app.get_amount())

    def testSetAmount_Negative(self):
        self.app.set_amount(-10.00)
        self.assertEqual(0.00, self.app.get_amount())

    def testSetAmount_None(self):
        self.app.set_amount(None)
        self.assertEqual(0.00, self.app.get_amount())

    def testSetAmount_EmptyString(self):
        self.app.set_amount("")
        self.assertEqual(0.00, self.app.get_amount())

    def testSetAmount_NumericalString(self):
        self.app.set_amount("10.00")
        self.assertEqual(10.00, self.app.get_amount())

    def testSetAmount_InvalidString(self):
        self.app.set_amount("asdf")
        self.assertEqual(0.00, self.app.get_amount())

    def testCalculateTotal(self):
        result = self.app.calculate_total(20.00, 15.00, "JPY")
        self.assertTrue(result[0])
        self.assertEqual(result[1], "Your total amount was: 3450.00 JPY.")

    def testCalculateTotal_None_BillAmount(self):
        result = self.app.calculate_total(None, 15.00, "EUR")
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERROR: NoneTypes are not accepted for bill amounts.")

    def testCalculateTotal_None_TipPercentage(self):
        result = self.app.calculate_total(20.00, None, "EUR")
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERROR: NoneTypes are not accepted for tip percentages.")

    def testCalculateTotal_None_CurrencyBase(self):
        result = self.app.calculate_total(20.00, 15.00, None)
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERROR: NoneTypes are not accepted for currency bases.")

    def testCalculateTotal_None_AllFields(self):
        result = self.app.calculate_total(None, None, None)
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERROR: NoneTypes are not accepted for bill amounts.")

    def testCalculateTotal_EmptyString_BillAmount(self):
        result = self.app.calculate_total("", 15.00, "USD")
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERROR: NoneTypes are not accepted for bill amounts.")

    def testCalculateTotal_EmptyString_CurrencyBase(self):
        result = self.app.calculate_total(20.00, 15.00, "")
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERROR: NoneTypes are not accepted for currency bases.")

    def testCalculateTotal_EmptyString_TipPercentage(self):
        result = self.app.calculate_total(20.00, "", "USD")
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERROR: NoneTypes are not accepted for tip percentages.")

    def testCalculateTotal_AlphanumericString_BillAmount(self):
        result = self.app.calculate_total("Test", 15.00, "USD")
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERROR: 'Test' is not valid input for a bill amount.")

    def testCalculateTotal_AlphanumericString_TipPercentage(self):
        result = self.app.calculate_total(20.00, "asdf", "USD")
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERROR: 'asdf' is not valid input for a tip percentage.")

    def testCalculateTotal_NumericValue_CurrencyBase(self):
        result = self.app.calculate_total(20.00, 15.00, 10.0)
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERROR: '10.0' is not valid input for a currency base.")

    def testCalculateTotal_NumericString_CurrencyBase(self):
        result = self.app.calculate_total(20.00, 15.00, "10.0")
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERROR: '10.0' is not valid input for a currency base.")

    def testCalculateTotal_uses_internal_forex_service(self):
        cache = ForexCache()
        cache.put(forex_rate("EUR/JPY", "150"))
        service = ForexService(cache)
        app = Tiptabs("EUR", forex_service=service)

        result = app.calculate_total(20, 15, "JPY")

        self.assertTrue(result[0])
        self.assertEqual(result[1], "Your total amount was: 3450.0 JPY.")

    def testCalculateTotal_missing_internal_rate_is_explicit(self):
        service = ForexService(ForexCache())
        app = Tiptabs("EUR", forex_service=service)

        result = app.calculate_total(20, 15, "JPY")

        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERROR: Currency conversion is unavailable: No usable rate is available for EUR/JPY")


if __name__ == "__main__":
    unittest.main()