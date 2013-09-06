from __future__ import division

from decimal import Decimal

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


def roundTo5(value):
    """
    Rounds to the nearest 5 cents and appends zeros to get a pretty result.
    See also http://en.wikipedia.org/wiki/Swedish_rounding#Rounding_with_5.C2.A2_intervals
    """
    if getattr(settings, 'ROUNDING_TO_THE_NEAREST_5_CENT', ):
        return (Decimal(str(round(Decimal(str(value))*Decimal("20"))))/Decimal("20")).quantize(Decimal('1.00'))
    return value 


class PercentDiscountMixin(models.Model):
    """
    Apply ``amount`` percent discount to whole cart.
    """
    amount = models.DecimalField(_('Amount'), max_digits=5, decimal_places=2)

 
    def get_extra_cart_price_field(self, cart, request):
        total = sum(item.product.unit_price * item.quantity for item in cart.items.all())
        discount = roundTo5(((self.amount / 100) * total).quantize(Decimal('1.00')))
        return (self.get_name(), -discount,)
 

    class Meta:
        abstract = True


class CartItemPercentDiscountMixin(models.Model):
    """
    Apply ``amount`` percent discount to eligible_products in Cart.
    """
    amount = models.DecimalField(_('Amount'), max_digits=5, decimal_places=2)

    def get_extra_cart_item_price_field(self, cart_item, request):
        if self.is_eligible_product(cart_item.product, cart_item.cart):
            return (self.get_name(),
                    self.calculate_discount(cart_item.line_subtotal))

    def calculate_discount(self, price):
        return roundTo5((self.amount/100) * price) 
        
    class Meta:
        abstract = True


class CartItemAbsoluteDiscountMixin(models.Model):
    """
    Apply ``amount`` discount to eligible_products in Cart.
    """
    amount = models.DecimalField(_('Amount'), max_digits=5, decimal_places=2)

    def get_extra_cart_item_price_field(self, cart_item, request):
        if self.is_eligible_product(cart_item.product, cart_item.cart):
            return (self.get_name(),
                    self.calculate_discount(cart_item.line_subtotal))

    def calculate_discount(self, price):
        return roundTo5(self.amount)

    class Meta:
        abstract = True
