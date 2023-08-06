from getpaid.luottokunta import LuottokuntaMessageFactory as _

ERROR_CODES = {
                '101' : (_(u'Amount is invalid'), _(u'The amount field or its content is formally incorrect or missing. Please check that the amount contains only numbers.')),
                '104' : (_(u'Card number is invalid'), _(u'The credit card number field or its content is formally incorrect or missing. Please check that the card number contains only numbers. The card number can be entered with or without spaces.')),
                '105' : (_(u'Card verification code is invalid'), _(u'The card verification code field or its content is formally incorrect or missing. Please check that the verification code (ie. Credit Card Verfication Number) contains only numbers.')),
                '106' : (_(u'Card validity is invalid'), _(u'The card validity field or its content is incorrect or missing. Please check that the card validity month and year are correct.')),
                '1403' : (_(u'Reversal message is pending'), _(u'Luottokunta is automatically reversing an authorisation that has not been completely processed or finished yet due to a temporary service break. Please try again later.')),
                '1404' : (_(u'Failed to send reversal message'), _(u'Luottokunta did not succeed to reverse an authorisation that was not completely processed or finished due to a temporary service break. Please try again later.')),
                '1901 ' : (_(u'Luottokunta internal error'), _(u'There have been an internal error in Luottokunta system. Please try again later.')),
                '2100' : (_(u'The card issuer declined the authorisation'), _(u'The card issuer has rejected the authorisation. The reasons for this can be e.g. that the card limit has been exceeded, or the card is restricted so that it cannot be used in E-commerce. Please contact card issuer for more detailed information.')),
                '2190' : (_(u'Card verification code not verified'), _(u'The card issuer has accepted the authorisation but has not checked the card verification code. Do not retry the transaction, as it will most likely result in the same outcome. The card cannot be used to pay through Luottokunta. Please contact card issuer for more detailed information.')),
                '2200' : (_(u'Card closed or suspicion of fraud'), _(u'The card in question is closed or there is suspicion of fraud. Do not retry the transaction. Please contact card issuer for more detailed information.')),
                '2900' : (_(u'System error'), _(u'The credit card number, validity or card verification code is invalid. Please try again.')),
                '3002' : (_(u'3DS authentication failed'), _(u'Verified by Visa or MasterCard SecureCode authentication failed. The reasons can be e.g. that the cardholder has given incorrect authentication password or cancelled the authentication by clicking the Cancel button in the authentication page.')),
                '3003' : (_(u'3DS no connection to directory'), _(u'Verified by Visa or MasterCard SecureCode authentication failed due to data communication error.')),
                }
