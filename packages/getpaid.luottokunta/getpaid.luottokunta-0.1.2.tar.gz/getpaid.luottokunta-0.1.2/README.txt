Introduction
============
Luottokunta is Finnish major organization which provides credit card processors.
"getpaid.luottokunta" implements Luottokunta payment processors to gaipaid.

Caution
-------
* This package is intended for single payment processor.If you have multiple payment processor istanlled, there might be conflict error because of "checkout-review-pay" browser view override.
* Only Card_Details_Transmit value="1" is tested. value="0" might work as well.
