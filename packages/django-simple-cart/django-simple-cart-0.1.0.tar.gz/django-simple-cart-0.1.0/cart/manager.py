from django.db import models


class CartManager(models.Manager):
    def get_for_session(self, session):
        """
        Find cart associated with the session or create new cart.
        """

        pk = session.get('cart_pk')
        try:
            cart = self.get(pk=pk, checkout=False)
        except self.model.DoesNotExist:
            cart = None

        if not cart:
            cart = self.create()
            session['cart_pk'] = cart.pk
            
        return cart
