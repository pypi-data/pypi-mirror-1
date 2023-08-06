from zope.viewlet.interfaces import IViewletManager

class ILuottokuntaAbovePayment(IViewletManager):
    """A viewlet manager that sits above the luottokunta payment
    """

class ILuottokuntaBelowPayment(IViewletManager):
    """A viewlet manager that sits below the luottokunta payment
    """

