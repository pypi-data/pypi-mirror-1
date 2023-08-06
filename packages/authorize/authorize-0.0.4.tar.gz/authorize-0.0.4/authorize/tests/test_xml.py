# -*- encoding: utf-8 -*-
from unittest import TestCase
import os
import decimal
up = os.path.dirname
j = os.path.join

from schema import SCHEMA

from lxml.etree import XMLSchema, XMLParser, fromstring

from authorize import xml as x, responses, cim, arb

parser = XMLParser()
schema_validator = XMLSchema(fromstring(SCHEMA, parser))

DELIMITER = "---------------------------------------------------------------------------------------"

def to_tree(s):
    return fromstring(s, parser)

def assertValid(s):
    schema_validator.assertValid(to_tree(s))

class TestXML(TestCase):

    def setUp(self):
        self.cim_old = cim.Api.request
        cim.Api.request = lambda self, body: assertValid(body)
        self.cim = cim.Api(u'foo', u'bar', is_test=True)
        
        self.arb_old = arb.Api.request
        arb.Api.request = lambda self, body: assertValid(body)
        self.arb = arb.Api(u"foo", u"bar", is_test=True)

    def tearDown(self):
        cim.Api.request = self.cim_old
        arb.Api.request = self.arb_old

    def test_general_examples(self):
        """
        Test that response parser don't break with example patterns
        given by Authorize.Net
        """
        examples = file(j(up(os.path.abspath(__file__)), 'CIMXMLExamples.txt')).read().split(DELIMITER)
        for example in examples:
            example = example.strip()
            try:
                resp = x.to_dict(example, responses.cim_map)
            except responses.AuthorizeError:
                resp = x.to_dict(example, responses.cim_map, do_raise=False)
                assert resp.messages.message.code.text_ in responses.cim_map
            else:
                assert resp.messages.message.code.text_ == u'I00001'

    def test_parser_to_dict(self):
        """
        Test that the dict parser works as expected
        """
        xml = """\
<foo>
    <bar>baz</bar>
    <quz>
        <wow>works!</wow>
    </quz>
</foo>
"""
        d = x.to_dict(xml, {})
        assert d.bar.text_ == u'baz'
        assert d.quz.wow.text_ == u'works!'
        
        
    def test_create_profile(self):
        """
        Test that the XML generated for create_profile is valid according
        to the XMLSchema.
        """
        self.cim.create_profile(
            card_number=u"42222222222",
            expiration_date=u"2010-04",
            customer_id=u"dialtone"
        )

        message = x.cim_create_profile(
            u'foo',
            u"bar",
            customer_id=u"dialtone",
            profile_type=u"bank",
            name_on_account=u"John Doe",
            routing_number=u"12345678",
            account_number=u"1234567890"
        )
        assertValid(message)
        assert 'creditCardNumber' not in message
        assert 'bankAccount' in message
    
        self.cim.create_profile(
            card_number=u"42222222222",
            expiration_date=u"2010-04",
            customer_id=u"dialtone",
            ship_phone=u'415-415-4154',
            ship_first_name=u'valentino'
        )
        
        payment_profiles = [
            dict(card_number=u"43333333333",
                 expiration_date=u"2010-04"),
            dict(profile_type=u"bank",
                 name_on_account=u"John Doeð",
                 routing_number=u"12345678",
                 account_number=u"1234567890")
        ]
        
        message = x.cim_create_profile(
            u'foo',
            u"bar",
            customer_id=u"dialtone",
            payment_profiles=payment_profiles,
            ship_phone=u"415-415-4154",
            ship_first_name=u"valentino"
        )
        
        assertValid(message)
        assert 'John Doe' in message
        assert '43333333333' in message
        assert 'valentino' in message

    def test_create_payment_profile(self):
        """
        Test that the XML generated for create_payment_profile is valid
        according to the XMLSchema.
        """
        self.cim.create_payment_profile(
            customer_profile_id=u'300',
            customer_type=u'individual',
            card_number=u'42222222222',
            expiration_date=u'2009-10'
        )

    def test_create_shipping_address(self):
        """
        Test that the XML generated for create_shipping_address is valid
        according to the XMLSchema.
        """
        self.cim.create_shipping_address(
            customer_profile_id=100,
            ship_phone=u'415-415-4154',
            ship_first_name=u'valentino'
        )
    
    def test_create_profile_transaction(self):
        """
        Test that the XML generated for create_profile_transaction is
        valid according to the XMLSchema, and that approval_code is
        only required when capture_only is used as profile_type.
        """
        line_items=[{'item_id': u"45",
                     'name': u'hello',
                     'description': u"foobar",
                     'quantity': 5,
                     'unit_price': decimal.Decimal("30.4")}]
        self.cim.create_profile_transaction(
            profile_type=u"auth_only",
            amount=12.34,
            tax_amount=3.0,
            ship_amount=3.0,
            duty_amount=3.0,
            line_items=line_items,
            customer_profile_id=u"123",
            customer_payment_profile_id=u"123",
            invoice_number=u"12345",
            tax_exempt=True
        )
        try:
            self.cim.create_profile_transaction(
                profile_type=u"capture_only",
                amount=12.34,
                tax_amount=3.0,
                ship_amount=3.0,
                duty_amount=3.0,
                line_items=line_items,
                customer_profile_id=123,
                customer_payment_profile_id=223,
                invoice_number=12345,
                tax_exempt=True
            )
        except KeyError, e:
            assert 'approval_code' in e.message # error was caused by
                                                # this key missing
            self.cim.create_profile_transaction(
                profile_type=u"capture_only",
                amount=12.34,
                tax_amount=3.0,
                ship_amount=3.0,
                duty_amount=3.0,
                line_items=line_items,
                customer_profile_id=123,
                customer_payment_profile_id=223,
                invoice_number=12345,
                tax_exempt=True,
                approval_code=134323
            )

    def test_delete_profile(self):
        """
        Test that the XML generated for delete_profile is valid
        according to the XMLSchema.
        """
        self.cim.delete_profile(customer_profile_id=u"123")

    def test_delete_payment_profile(self):
        """
        Test that the XML generated for delete_payment_profile is valid
        according to the XMLSchema.
        """
        self.cim.delete_payment_profile(
            customer_profile_id=u"123",
            customer_payment_profile_id=u"432"
        )

    def test_delete_shipping_address(self):
        """
        Test that the XML generated for delete_shipping_address is valid
        according to the XMLSchema.
        """
        self.cim.delete_shipping_address(
            customer_profile_id=u"123",
            customer_address_id=u"543"
        )
    
    def test_get_profile(self):
        """
        Test that the XML generated for get_profile is valid
        according to the XMLSchema.
        """
        self.cim.get_profile(customer_profile_id=u"123")
    
    def test_get_payment_profile(self):
        """
        Test that the XML generated for get_payment_profile is valid
        according to the XMLSchema.
        """
        self.cim.get_payment_profile(
            customer_profile_id=u"655",
            customer_payment_profile_id=u"999"
        )
    
    def test_get_shipping_address(self):
        """
        Test that the XML generated for get_shipping_address is valid
        according to the XMLSchema.
        """
        self.cim.get_shipping_address(
            customer_profile_id=u"900",
            customer_address_id=u"344"
        )
    
    def test_update_profile(self):
        """
        Test that the XML generated for update_profile is valid
        according to the XMLSchema.
        """
        self.cim.update_profile(
            customer_id=u"222",
            description=u"Foo bar baz quz",
            email=u"dialtone@gmail.com",
            customer_profile_id=u"122"
        )

    def test_update_payment_profile(self):
        """
        Test that the XML generated for update_payment_profile is valid
        according to the XMLSchema.
        """
        self.cim.update_payment_profile(
            customer_profile_id=u"122",
            customer_payment_profile_id=u"444",
            card_number=u"422222222222",
            expiration_date=u"2009-10"
        )
        
    def test_update_shipping_address(self):
        """
        Test that the XML generated for update_shipping_address is valid
        according to the XMLSchema.
        """
        self.cim.update_shipping_address(
            customer_profile_id=u"222",
            customer_address_id=u"444",
            first_name=u"pippo",
            phone=u"415-415-4154"
        )
        
    def test_validate_payment_profile(self):
        """
        Test that the XML generated for validate_payment_profile is valid
        according to the XMLSchema.
        """
        self.cim.validate_payment_profile(
            customer_profile_id=u"222",
            customer_payment_profile_id=u"444",
            customer_address_id=u"555",
        )

    def test_create_subscription(self):
        """
        Test that XML generated for arb subscription creation is valid
        according to XMLSchema.
        """
        try:
            self.arb.create_subscription(
                trial_occurrences=4,
                interval_length=1,
                interval_unit=arb.MONTHS_INTERVAL,
                start_date=u"2008-09-09",
                amount=39.99,
                card_number=u"4222222222222",
                expiration_date=u"2009-10"
            )
        except KeyError:
            pass
        self.arb.create_subscription(
            trial_amount=5.00,
            trial_occurrences=4,
            interval_length=1,
            interval_unit=arb.MONTHS_INTERVAL,
            start_date=u"2008-09-09",
            amount=39.99,
            card_number=u"4222222222222",
            expiration_date=u"2009-10"
        )
        self.arb.create_subscription(
            trial_amount=5.00,
            trial_occurrences=4,
            interval_length=1,
            interval_unit=arb.MONTHS_INTERVAL,
            start_date=u"2008-09-09",
            amount=39.99,
            card_number=u"4222222222222",
            expiration_date=u"2009-10",
            ship_first_name=u"valentino",
            first_name=u"valentino",
            bill_first_name=u"valentino",
            driver_number=u"55555",
            driver_state=u"CA",
            driver_birth=u"1990-09-09"
        )
    
    def test_update_subscription(self):
        """
        Test that XML generated for arb subscription creation is valid
        according to XMLSchema.
        """
        args = dict(trial_amount=5.00,
                    trial_occurrences=4,
                    interval_length=1,
                    interval_unit=arb.MONTHS_INTERVAL,
                    start_date=u"2008-09-09",
                    amount=39.99,
                    card_number=u"4222222222222",
                    expiration_date=u"2009-10",
                    ship_first_name=u"valentino",
                    first_name=u"valentino",
                    bill_first_name=u"valentino",
                    driver_number=u"55555",
                    driver_state=u"CA",
                    driver_birth=u"1990-09-09"
        )
        
        try:
            self.arb.update_subscription(**args)
        except KeyError:
            self.arb.update_subscription(subscription_id=u"1234", **args)
    
    def test_cancel_subscription(self):
        try:
            self.arb.cancel_subscription()
        except KeyError:
            self.arb.cancel_subscription(subscription_id=u"1234")
        