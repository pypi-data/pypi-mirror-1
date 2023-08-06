"""
Models:
 * Cart - binds to the user session
 * Item - linked to the Cart instance
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from cart.manager import CartManager


def ct_lookup(obj):
    """
    Return ORM lookup arguments for refering to the obj when
    it is linked via GenericForeignKey.
    """

    return {'content_type': ContentType.objects.get_for_model(obj),
            'object_id': obj.pk,
            }


class Cart(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    checkout = models.BooleanField(blank=True, default=False)

    objects = CartManager()

    def __unicode__(self):
        return str(self.created)

    def add_product(self, product, price, quantity):
        try:
            item = self.items.get(**ct_lookup(product))
        except Item.DoesNotExist:
            item = Item(product=product, unit_price=price,
                        quantity=0, cart=self)
        item.quantity += quantity
        item.save()

    def remove_product(self, product, quantity):
        try:
            item = self.items.get(**ct_lookup(product))
        except Item.DoesNotExist:
            return
        else:
            if not quantity:
                item.delete()
            else:
                item.quantity -= quantity
                if item.quantity > 0:
                    item.save()
                else:
                    item.delete()

    def price(self):
        """
        Return overall  price of all items in the cart.
        """

        return sum(x.price() for x in self)

    def size(self):
        """
        Return overall number of products in the cart.
        """

        return sum(x.quantity for x in self)

    def __iter__(self):
        for item in self.items.all():
            yield item


class Item(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    product = generic.GenericForeignKey()
    cart = models.ForeignKey(Cart, related_name='items')
    quantity = models.IntegerField(blank=True, default=1)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)

    def __unicode__(self):
        return self.product

    def price(self):
        return self.unit_price * self.quantity
