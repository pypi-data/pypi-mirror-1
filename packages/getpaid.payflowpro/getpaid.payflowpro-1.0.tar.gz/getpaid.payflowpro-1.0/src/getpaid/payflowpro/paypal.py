"""
"""
import urllib
import logging

from Products.CMFCore.utils import getToolByName
from zope import component
from zope import interface
from zope.app.annotation.interfaces import IAnnotations

from interfaces import IPaypalPayFlowProOptions

from Products.PloneGetPaid.interfaces import IGetPaidManagementOptions
from getpaid.core import interfaces as GetPaidInterfaces

from payflowpro.classes import CreditCard, Amount, Profile, Address, Tracking, Response, CustomerInfo
from payflowpro.client import PayflowProClient

from datetime import date

RESULT = "getpaid.payflowpro.result"
RESPMSG = "getpaid.payflowpro.respmsg"
CVV2_MATCH = "getpaid.payflowpro.cvv2match"
AUTH_CODE = "getpaid.payflowpro.authcode"
LAST_FOUR = "getpaid.payflowpro.cc_last_four"
CREDIT_RESULT = "getpaid.payflowpro.credit_result"
CREDIT_RESPMSG = "getpaid.payflowpro.credit_respmsg"

logger = logging.getLogger('GetPaid.PayFlowPro')

class PayFlowPro( object ):
    interface.implements( GetPaidInterfaces.IPaymentProcessor )

    options_interface = IPaypalPayFlowProOptions

    _sites = {
        "Sandbox": "https://pilot-payflowpro.paypal.com",
        "Production": "https://payflowpro.paypal.com",
        }

    def __init__( self, context ):
        self.context = context
        self.options = IPaypalPayFlowProOptions( self.context )

    def authorize( self, order, payment ):
        logger.info('Authorize...')
        
        client = PayflowProClient(partner=self.options.partner,
                                  vendor=self.options.vendor,
                                  username=self.options.username,
                                  password=self.options.password,
                                  url_base=self._sites.get(self.options.server_url))

        card_exp_date = ''
        if hasattr(payment.cc_expiration, 'strftime'):
            card_exp_date = payment.cc_expiration.strftime('%m%y')
        else:
            # If cc_expiration is not of type date, then it should be 
            # a string like this: '2011-08-03 00:00'
            # This is a bug in getpaid.formgen's single page checkout
            # and the correct fix is to swap out it's expiration date
            # widget with one that returns a date.
            yearMonthDay = payment.cc_expiration.split(' ')[0].split('-')
            _date = date(int(yearMonthDay[0]), 
                         int(yearMonthDay[1]), 
                         int(yearMonthDay[2]))
            card_exp_date = _date.strftime('%m%y')

        credit_card = CreditCard(acct=payment.credit_card,
                                 expdate=card_exp_date,
                                 cvv2=payment.cc_cvc)

        ba = order.billing_address
        responses, unconsumed_data = client.authorization(credit_card,
                                                          Amount(amt=order.getTotalPrice(),
                                                                 currency=self.options.currency),
                                                          extras=[Address(street=ba.bill_first_line,
                                                                          city=ba.bill_city,
                                                                          state=ba.bill_state,
                                                                          zip=ba.bill_postal_code)])
        order.processor_order_id = responses[0].pnref

        annotation = IAnnotations(order)
        annotation[GetPaidInterfaces.keys.processor_txn_id] = responses[0].pnref
        annotation[RESULT] = responses[0].result
        annotation[RESPMSG] = responses[0].respmsg
        annotation[CVV2_MATCH] = responses[0].cvv2match
        annotation[AUTH_CODE] = responses[0].authcode
        annotation[LAST_FOUR] = payment.credit_card[-4:]

        if responses[0].result == '0':
            ret = GetPaidInterfaces.keys.results_success
        else:
            ret = responses[0].respmsg

        logger.info("PNREF: %s" % annotation[GetPaidInterfaces.keys.processor_txn_id])
        logger.info("RESULT: %s" % annotation[RESULT])
        logger.info("RESPMSG: %s" % annotation[RESPMSG])
        logger.info("CVV2_MATCH: %s" % annotation[CVV2_MATCH])
        logger.info("AUTH_CODE: %s" % annotation[AUTH_CODE])

        return ret
    
    def capture(self, order, price):
        logger.info('Capture...')

        annotation = IAnnotations(order)
        transaction_id = annotation[GetPaidInterfaces.keys.processor_txn_id]

        client = PayflowProClient(partner=self.options.partner,
                                  vendor=self.options.vendor,
                                  username=self.options.username,
                                  password=self.options.password,
                                  url_base=self._sites.get(self.options.server_url))

        responses, unconsumed_data = client.capture(transaction_id)
        
        annotation[RESULT] = responses[0].result
        annotation[RESPMSG] = responses[0].respmsg

        if responses[0].result == '0':
            ret = GetPaidInterfaces.keys.results_success
        else:
            ret = responses[0].respmsg

        logger.info("PNREF: %s" % annotation[GetPaidInterfaces.keys.processor_txn_id])
        logger.info("RESULT: %s" % annotation[RESULT])
        logger.info("RESPMSG: %s" % annotation[RESPMSG])

        return ret

    #
    # PayFlowPro does not accept an amount, so credits can only be done for the
    # full amount through this api.  To credit a partial amount use the 
    # PayFlowPro manager
    #
    def refund(self, order, amount):
        logger.info('Credit...')

        annotation = IAnnotations(order)
        transaction_id = annotation[GetPaidInterfaces.keys.processor_txn_id]

        client = PayflowProClient(partner=self.options.partner,
                                  vendor=self.options.vendor,
                                  username=self.options.username,
                                  password=self.options.password,
                                  url_base=self._sites.get(self.options.server_url))

        responses, unconsumed_data = client.credit_referenced(transaction_id)
        
        annotation[CREDIT_RESULT] = responses[0].result
        annotation[CREDIT_RESPMSG] = responses[0].respmsg

        if responses[0].result == '0':
            ret = GetPaidInterfaces.keys.results_success
        else:
            ret = responses[0].respmsg

        logger.info("CREDIT_PNREF: %s" % annotation[GetPaidInterfaces.keys.processor_txn_id])
        logger.info("CREDIT_RESULT: %s" % annotation[CREDIT_RESULT])
        logger.info("CREDIT_RESPMSG: %s" % annotation[CREDIT_RESPMSG])

        return ret
