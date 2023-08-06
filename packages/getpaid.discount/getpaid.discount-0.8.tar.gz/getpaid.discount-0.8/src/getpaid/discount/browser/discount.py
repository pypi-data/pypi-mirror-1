from zope import component
from zope import interface
from zope.formlib import form
from zope.interface import implements
from zope.app.annotation.interfaces import IAnnotations

from zope.component import getUtility

from Products.Five.formlib import formbase
from Products.Five.utilities import marker
from Products.Five.browser import BrowserView

from getpaid.discount.browser.interfaces import IDiscountable
from getpaid.discount.browser.interfaces import IBuyXGetXFreeable
from getpaid.discount.browser.interfaces import ICodeDiscountable
from getpaid.discount.browser.interfaces import IDiscountableMarker
from getpaid.discount.browser.interfaces import IBuyXGetXFreeableMarker
from getpaid.discount.browser.interfaces import ICodeDiscountableMarker

from Products.PloneGetPaid.interfaces import IPayableMarker

from getpaid.core import interfaces
from getpaid.core.interfaces import IShoppingCartUtility

class DiscountForm(formbase.EditForm):
    """
    """
    form_fields = form.FormFields(IDiscountable)
    marker = IDiscountableMarker
    actions = form.Actions()
    interface = IDiscountable
    
    def allowed( self ):
        adapter = component.queryAdapter( self.context, IPayableMarker)
        return not (adapter is None)

class DiscountEdit(DiscountForm):
    """
    """
    @form.action("Update", condition=form.haveInputWidgets)
    def update_discountable( self, action, data):
        self.handle_edit_action.success_handler( self, action, data )
        message = 'Changes saved.'
        self.request.response.redirect( '%s/view?portal_status_message=%s' % (self.context.absolute_url(), message) )

class DiscountCreation(DiscountForm):
    """
    """
    
    @form.action("Activate", condition=form.haveInputWidgets)
    def activate_discountable( self, action, data):
        #we set up the type as IDiscountable
        interface.alsoProvides(self.context, self.marker)
        self.handle_edit_action.success_handler( self, action, data )
        message = 'Changes saved.'
        self.request.response.redirect( '%s/view?portal_status_message=%s' % (self.context.absolute_url(), message) )

class DiscountDestruction(BrowserView):
    marker = IDiscountableMarker
    
    def __call__(self):
        marker.erase( self.context, self.marker )
        self.request.response.redirect( '%s/view' % self.context.absolute_url() )

class BuyXGetXFreeEdit(DiscountEdit):
    """
    """
    interface = IBuyXGetXFreeable
    form_fields = form.FormFields(IBuyXGetXFreeable)
    marker = IBuyXGetXFreeableMarker

class BuyXGetXFreeCreation(DiscountCreation):
    """
    """
    interface = IBuyXGetXFreeable
    form_fields = form.FormFields(IBuyXGetXFreeable)
    marker = IBuyXGetXFreeableMarker

class BuyXGetXFreeDestruction(DiscountDestruction):
    marker = IBuyXGetXFreeableMarker

class CodeDiscountableEdit(DiscountEdit):
    """
    """
    interface = ICodeDiscountable
    form_fields = form.FormFields(ICodeDiscountable)
    marker = ICodeDiscountableMarker

class CodeDiscountableCreation(DiscountCreation):
    """
    """
    interface = ICodeDiscountable
    form_fields = form.FormFields(ICodeDiscountable)
    marker = ICodeDiscountableMarker

class CodeDiscountableDestruction(DiscountDestruction):
    marker = ICodeDiscountableMarker

class DiscountAdapter(object):
    """
    """
    implements(IDiscountable)
    
    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)
        discount_title = self.annotations.get('discount_title', None)
        if discount_title is None:
            self.annotations['discount_title'] = ''
        discount_type = self.annotations.get('discount_type', None)
        if discount_type is None:
            self.annotations['discount_type'] = 'Dollars Off'
        discount_value = self.annotations.get('discount_value', None)
        if discount_value is None:
            self.annotations['discount_value'] = 0.0
    
    def getDiscountTitle(self):
        return self.annotations['discount_title']

    def setDiscountTitle(self, data):
        self.annotations['discount_title'] = data

    def getDiscountType(self):
        return self.annotations['discount_type']

    def setDiscountType(self, data):
        self.annotations['discount_type'] = data
    
    def getDiscountValue(self):
        return self.annotations['discount_value']

    def setDiscountValue(self, data):
        self.annotations['discount_value'] = data
    
    discount_title = property(fget=getDiscountTitle, fset=setDiscountTitle)
    discount_type = property(fget=getDiscountType, fset=setDiscountType)
    discount_value = property(fget=getDiscountValue, fset=setDiscountValue)

class BuyXGetXFreeAdapter(object):
    """
    """
    implements(IBuyXGetXFreeable)
    
    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)
        discount_title = self.annotations.get('discount_title', None)
        if discount_title is None:
            self.annotations['discount_title'] = ''
        number_to_buy = self.annotations.get('number_to_buy', None)
        if number_to_buy is None:
            self.annotations['number_to_buy'] = 0
        number_free = self.annotations.get('number_free', None)
        if number_free is None:
            self.annotations['number_free'] = 0
    
    def getDiscountTitle(self):
        return self.annotations['discount_title']

    def setDiscountTitle(self, data):
        self.annotations['discount_title'] = data

    def getNumberToBuy(self):
        return self.annotations['number_to_buy']

    def setNumberToBuy(self, data):
        self.annotations['number_to_buy'] = data
    
    def getNumberFree(self):
        return self.annotations['number_free']

    def setNumberFree(self, data):
        self.annotations['number_free'] = data
    
    discount_title = property(fget=getDiscountTitle, fset=setDiscountTitle)
    number_to_buy = property(fget=getNumberToBuy, fset=setNumberToBuy)
    number_free = property(fget=getNumberFree, fset=setNumberFree)

class CodeDiscountableAdapter(object):
    """
    """
    implements(ICodeDiscountable)
    
    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)
        discount_title = self.annotations.get('discount_title', None)
        if discount_title is None:
            self.annotations['discount_title'] = ''
        discount_code = self.annotations.get('discount_code', None)
        if discount_code is None:
            self.annotations['discount_code'] = ''
        discounted_price = self.annotations.get('discounted_price', None)
        if discounted_price is None:
            self.annotations['discounted_price'] = 0.0
    
    def getDiscountTitle(self):
        return self.annotations['discount_title']

    def setDiscountTitle(self, data):
        self.annotations['discount_title'] = data

    def getDiscountCode(self):
        return self.annotations['discount_code']

    def setDiscountCode(self, data):
        self.annotations['discount_code'] = data
    
    def getDiscountedPrice(self):
        return self.annotations['discounted_price']

    def setDiscountedPrice(self, data):
        self.annotations['discounted_price'] = data
    
    discount_title = property(fget=getDiscountTitle, fset=setDiscountTitle)
    discount_code = property(fget=getDiscountCode, fset=setDiscountCode)
    discounted_price = property(fget=getDiscountedPrice, fset=setDiscountedPrice)

class ApplyDiscountCode(BrowserView):
    """
    """
    # create form that:
    #   - accepts a code
    #   - iterates over cart and checks that an item provides ICodeDiscountable
    #   - it also does not provide IDiscountable
    #   - Creates new IDiscountable set appropiatly and drops item price
    def __call__(self):
        code = self.request.form.get('discount.code', None)

        self.cart = getUtility(IShoppingCartUtility).get(self.context) or {}

        if not self.cart:
            order_id = self.request.get("order_id", None)
            if order_id:
                order_manager = component.getUtility(interfaces.IOrderManager)
                self.cart = order_manager.get(order_id).shopping_cart

        if code is not None and self.cart:
            
            for item in self.cart.values():

                ref_obj = item.resolve()
                payable_quantity = item.quantity

                annotation = IAnnotations(item)

                if ref_obj \
                   and ICodeDiscountableMarker.providedBy(ref_obj) \
                   and not "getpaid.discount.code" in annotation:

                    adapter_obj = ICodeDiscountable(ref_obj)

                    if code == adapter_obj.getDiscountCode():

                        discounted_price = adapter_obj.getDiscountedPrice()

                        annotation["getpaid.discount.code"] = adapter_obj.getDiscountCode()

                        # Here I want to create a new IDiscountableMarker
                        # I also want to drop the price on this payable_line    
                        annotation["getpaid.discount.code.title"] = adapter_obj.getDiscountTitle()
                        discount = item.cost - adapter_obj.getDiscountedPrice()
                        item.cost = adapter_obj.getDiscountedPrice()
                        total_discount = discount * item.quantity
                        annotation["getpaid.discount.code.discount"] = total_discount

        self.request.response.redirect('@@getpaid-cart')

    
