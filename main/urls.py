from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery, name='gallery'),
    path('my-account/', views.my_account, name='my_account'),
    path('shop/', views.shop, name='shop'),
    path('shop-detail/', views.shop_detail, name='shop_detail'),
    path('wishlist/', views.wishlist, name='wishlist'),
]
