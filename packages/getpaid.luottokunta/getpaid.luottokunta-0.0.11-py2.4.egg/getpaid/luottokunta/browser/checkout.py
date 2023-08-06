from Products.PloneGetPaid.browser.checkout import CheckoutReviewAndPay
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.PloneGetPaid.interfaces import IGetPaidManagementOptions

from Acquisition import aq_inner

from getpaid.luottokunta import LuottokuntaMessageFactory as _
from getpaid.luottokunta.interfaces import ILuottokuntaOptions, ILuottokuntaOrderInfo

from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

import datetime

from getpaid.core.interfaces import IOrderManager, IShoppingCartUtility
from zope.component import getUtility
from getpaid.luottokunta.config import ERROR_CODES

class LuottokuntaCheckoutReviewAndPay(CheckoutReviewAndPay):

    template = ZopeTwoPageTemplateFile("templates/checkout-luottokunta-pay.pt")
    _next_url = None

    def update( self ):
        siteroot = getToolByName(self.context, "portal_url").getPortalObject()
        manage_options = IGetPaidManagementOptions(siteroot)
        processor_name = manage_options.payment_processor
        order_manager = getUtility(IOrderManager)
        order = self.createOrder()
        order.processor_id = processor_name
        order.finance_workflow.fireTransition( "create" )
        order_manager.store(order)
        super( CheckoutReviewAndPay, self).update()

    def is_luottokunta(self):
        """
        Returns true if payment processor is luottokunta.
        """
        siteroot = getToolByName(self.context, "portal_url").getPortalObject()
        manage_options = IGetPaidManagementOptions(siteroot)
        processor_name = manage_options.payment_processor
        if processor_name == u'Luottokunta HTML form interface':
            return True
        else:
            return False

    def years(self):
        results = [_(u'Year')]
        this_year = datetime.date.today().year
        results += range(this_year, this_year + 30)
        return results

    def months(self):
        return [_(u'Month'), '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

#    def luottokunta_options(self):
#        context= aq_inner(self.context)
#        return ILuottokuntaOptions(context)

    def order_info(self):
        order = self.createOrder()
        return ILuottokuntaOrderInfo(order)()

#    def success_url(self):
#        context= aq_inner(self.context)
#        base_url = context.absolute_url()
#        order = self.createOrder()
#        order.finance_workflow.fireTransition( "create" )
#        state = order.finance_state
#        return base_url + '/@@luottokunta-thank-you?order_id=%s&finance_state=%s' %(order.order_id, state)

#    def failure_url(self):
#        context= aq_inner(self.context)
#        base_url = context.absolute_url()
#        return base_url + '/@@getpaid-cancelled-declined'

#    def customer_id(self):
#        context = aq_inner(self.context)
#        membership = getToolByName(context, 'portal_membership')
##        import pdb; pdb.set_trace()
#        member_id = membership.getAuthenticatedMember().getId()
#        return member_id

class LuottokuntaThankYou(BrowserView):

    template = ZopeTwoPageTemplateFile("templates/checkout-thank-you.pt")

    def __call__(self):

        self.wizard = getMultiAdapter(
                    ( self.context, self.request ),
                    name="getpaid-checkout-wizard"
                    )
        order_manager = getUtility(IOrderManager)
        form = self.request.form
        order_id = form.get('getpaid_order_id')
        order = order_manager.get(order_id)
        luottokunta_order_id = form.get('luottokunta_order_id')
        if order.finance_workflow.state().getState() == "CHARGED":
            self.finance_state = "CHARGED"
            getUtility(IShoppingCartUtility).destroy( self.context )
            return self.template()
        else:
            order.finance_workflow.fireTransition("authorize")
            template_key = 'order_template_entry_name'
            order_template_entry = self.wizard.data_manager.get(template_key)
            del self.wizard.data_manager[template_key]
            # if the user submits a name, it means he wants this order named
            if order_template_entry:
                uid = getSecurityManager().getUser().getId()
                if uid != 'Anonymous':
                    named_orders_list = getUtility(INamedOrderUtility).get(uid)
                    if order_template_entry not in named_orders_list:
                        named_orders_list[order.order_id] = order_template_entry
            order.finance_workflow.fireTransition("charge-charging")
            order.setOrderTransId(int(luottokunta_order_id))
            self.finance_state = "CHARGED"
            siteroot = getToolByName(self.context, "portal_url").getPortalObject()
            options = ILuottokuntaOptions(siteroot)
            if options.use_incremental_order_id and options.next_order_id:
                options.next_order_id = options.next_order_id + 1
            getUtility(IShoppingCartUtility).destroy( self.context )
            return self.template()

class LuottokuntaCancelledDeclinedView(BrowserView):

    template = ZopeTwoPageTemplateFile("templates/checkout-cancelled-declined.pt")

    def __call__(self):
        form = self.request.form
        error_code = form.get('LKSRC', None)
        self.error_message = ERROR_CODES.get(error_code)
        if self.error_message:
            self.error_title = self.error_message[0]
            self.error_description = self.error_message[1]
        return self.template()
