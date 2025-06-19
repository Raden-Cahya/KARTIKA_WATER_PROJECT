# main/admin.py
from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem # Sesuaikan dengan model yang Anda daftarkan

admin.site.register(Product)
# Tambahkan juga model lain jika ingin bisa mengelola di admin
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)