# main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URL Halaman Statis
    path('', views.index, name='index'), # Halaman beranda, diakses via '/'
    path('index/', views.index, name='index'), # Tambahkan baris ini untuk mengakses via '/index/'
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery, name='gallery'),
    path('shop-detail/', views.shop_detail, name='shop_detail'),
    path('wishlist/', views.wishlist, name='wishlist'),

    # URL Produk dan Keranjang Belanja
    path('shop/', views.shop, name='shop'), # Daftar produk
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'), # Menampilkan keranjang belanja (nama view: cart_view)
    
    # URL AJAX untuk update kuantitas. Perhatikan nama URL ini akan digunakan di JS Anda.
    path('update-cart-item-quantity/', views.update_cart_item_quantity, name='update_cart_item_quantity'),
    
    # URL untuk menghapus item dari keranjang (tetap pakai form submit)
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # URL Checkout dan Riwayat Pesanan
    path('checkout/', views.checkout, name='checkout'), # Halaman konfirmasi checkout
    path('checkout-process/', views.checkout_process, name='checkout_process'), # Proses finalisasi pesanan
    path('my-account/', views.my_account, name='my_account'), # Halaman akun saya
]