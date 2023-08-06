from django.shortcuts import redirect, get_object_or_404
from django.views.generic.simple import direct_to_template

from cart.models import Cart
from shop.models import Product


def redirect_url(request):
    referer = request.META['HTTP_REFERER']
    return referer or reverse(cart_show)


def cart_add(request, product_pk, quantity):
    product = get_object_or_404(Product, pk=product_pk)
    cart = Cart.objects.get_for_session(request.session)
    cart.add_product(product, product.price_rur, int(quantity))
    return redirect(redirect_url(request))


def cart_remove(request, product_pk, quantity):
    product = get_object_or_404(Product, pk=product_pk)
    cart = Cart.objects.get_for_session(request.session)
    cart.remove_product(product, int(quantity))
    return redirect(redirect_url(request))


def cart_show(request):
    cart = Cart.objects.get_for_session(request.session)
    return direct_to_template(request, 'cart/show.html',
                              {'cart': cart})
