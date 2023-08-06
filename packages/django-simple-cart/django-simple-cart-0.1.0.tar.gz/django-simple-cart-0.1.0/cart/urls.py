# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('cart.views',
    url(r'^cart/add/(\d+)/$', 'cart_add', {'quantity': 1}, name='cart_add'),
    url(r'^cart/add/(\d+)/(\d+)/$', 'cart_add', name='cart_add_multiple'),
    url(r'^cart/remove/(\d+)/$', 'cart_remove', {'quantity': 0}, name='cart_remove'),
    url(r'^cart/remove/(\d+)/(\d+)/$', 'cart_remove', name='cart_remove_multiple'),
    url(r'^cart/contents/$', 'cart_show', name='cart_show'),
)
