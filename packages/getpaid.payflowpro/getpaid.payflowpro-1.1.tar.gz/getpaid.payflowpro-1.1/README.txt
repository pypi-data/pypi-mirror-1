This package provides paypal payflowpro payment processor functionality for the getpaid framework.

It uses python-payflowpro for the underlying access to paypal (http://code.google.com/p/python-payflowpro/ & http://pypi.python.org/pypi/python-payflowpro/)

What is Paypal PayFlowPro
=========================
For more information see https://www.paypal.com/cgi-bin/webscr?cmd=_payflow-pro-overview-outside

Create PayFlowPro test account
==============================
To create a test paypal payproflow account all you need to do is go to https://www.paypal.com/cgi-bin/webscr?cmd=_payflow-gateway-overview-outside and go through the registration flow.  When it asks you for your credit card information, just drop out (close browser) and a test account will be created.

This is only for US accounts.
 
FYI, you can use the same account for both testing and live transactions at the same time, so if you are going to activate the account, create the login id accordingly.

After completing that step you will receive an email with login instructions.

After logging in you should create a seperate user account for getpaid.payflowpro to use.

Plone Setup
===========

getpaid.payflowpro setup
========================
1) Enter Plone Site Setup -> GetPaid Setup
2) Under 'Payment Options' select Paypal PayFlowPro
3) Under Payment Processor Settings enter the login credentials for your PayFlowPro account.  (See Create PayFlowPro test account above if you do not have one)

Dependencies
============
getpaid.payflowpro requires the following:
  - GetPaid (http://www.plonegetpaid.com/)
  - A PayFlowPro account

TODO
====
- The login information should be encrypted (or minimally obfuscated) and not redisplayed to the user after it is entered.
- Test refund. It's imlemented, but I haven't tested it since I can't figure out how to refund an order in the UI.  Plus who really want's to give money back? ;)
